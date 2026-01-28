import sys
import numpy as np
import pandas as pd

from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer

from us_visa.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from us_visa.entity.config_entity import DataTransformationConfig
from us_visa.entity.artifact_entity import (
    DataTransformationArtifact,
    DataIngestionArtifact,
    DataValidationArtifact
)
from us_visa.exception import USvisaException
from us_visa.logger import logging
from us_visa.utils.main_utils import (
    save_object,
    save_numpy_array_data,
    read_yaml_file,
    drop_columns
)
from us_visa.entity.estimator import TargetValueMapping


class DataTransformation:

    def __init__(self,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise USvisaException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        return pd.read_csv(file_path)

    # -----------------------------
    # DATA CLEANING
    # -----------------------------

    @staticmethod
    def normalize_salary(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "unit_of_wage" in df.columns and "prevailing_wage" in df.columns:
            df["prevailing_wage"] = np.where(
                df["unit_of_wage"] == "Hour",
                df["prevailing_wage"] * 2080,
                df["prevailing_wage"]
            )
        return df

    @staticmethod
    def normalize_education(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "education_of_employee" in df.columns:
            df["education_of_employee"] = df["education_of_employee"].replace({
                "PhD": "Doctorate",
                "PHD": "Doctorate",
                "Doctoral": "Doctorate"
            })
        return df

    # -----------------------------
    # PREPROCESSOR
    # -----------------------------

    def get_data_transformer_object(self) -> Pipeline:

        numeric_transformer = StandardScaler()

        oh_transformer = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )

        ordinal_encoder = OrdinalEncoder(
            categories=[["High School", "Bachelor's", "Master's", "Doctorate"]],
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )

        oh_columns = self._schema_config['oh_columns']
        or_columns = self._schema_config['or_columns']
        transform_columns = self._schema_config['transform_columns']
        num_features = self._schema_config['num_features']

        transform_pipe = Pipeline(
            steps=[("power", PowerTransformer(method="yeo-johnson"))]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("onehot", oh_transformer, oh_columns),
                ("ordinal", ordinal_encoder, or_columns),
                ("power", transform_pipe, transform_columns),
                ("scaler", numeric_transformer, num_features)
            ],
            remainder="drop"
        )

        return preprocessor

    # -----------------------------
    # PIPELINE
    # -----------------------------

    def initiate_data_transformation(self) -> DataTransformationArtifact:

        try:
            if not self.data_validation_artifact.validation_status:
                raise Exception(self.data_validation_artifact.message)

            logging.info("Starting data transformation")

            preprocessor = self.get_data_transformer_object()

            train_df = self.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)

            X_train = train_df.drop(columns=[TARGET_COLUMN])
            y_train = train_df[TARGET_COLUMN]

            X_test = test_df.drop(columns=[TARGET_COLUMN])
            y_test = test_df[TARGET_COLUMN]

            # Feature engineering
            X_train["company_age"] = (CURRENT_YEAR - X_train["yr_of_estab"]).clip(0, 100)
            X_test["company_age"] = (CURRENT_YEAR - X_test["yr_of_estab"]).clip(0, 100)

            # Cleaning
            X_train = self.normalize_salary(X_train)
            X_test = self.normalize_salary(X_test)

            X_train = self.normalize_education(X_train)
            X_test = self.normalize_education(X_test)

            # Drop unwanted columns
            drop_cols = self._schema_config["drop_columns"]
            X_train = drop_columns(X_train, drop_cols)
            X_test = drop_columns(X_test, drop_cols)

            # Target mapping
            y_train = y_train.replace(TargetValueMapping()._asdict())
            y_test = y_test.replace(TargetValueMapping()._asdict())

            # Preprocessing
            X_train_arr = preprocessor.fit_transform(X_train)
            X_test_arr = preprocessor.transform(X_test)

            # SMOTE only on training set
            smt = SMOTEENN(sampling_strategy="minority", random_state=42)
            X_train_final, y_train_final = smt.fit_resample(X_train_arr, y_train)

            # Combine arrays
            train_arr = np.c_[X_train_final, np.array(y_train_final)]
            test_arr = np.c_[X_test_arr, np.array(y_test)]

            # Save
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, test_arr)

            artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            logging.info("Data transformation completed successfully")

            return artifact

        except Exception as e:
            raise USvisaException(e, sys)
