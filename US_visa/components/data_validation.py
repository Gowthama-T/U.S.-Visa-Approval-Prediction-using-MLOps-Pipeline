import json
import sys

import pandas as pd
from pandas import DataFrame

from evidently.report import Report
from evidently.metrics import DataDriftTable

from us_visa.exception import USvisaException
from us_visa.logger import logging
from us_visa.utils.main_utils import read_yaml_file, write_yaml_file
from us_visa.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from us_visa.entity.config_entity import DataValidationConfig
from us_visa.constants import SCHEMA_FILE_PATH


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise USvisaException(e, sys)

    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])
            logging.info(f"Is required column present: [{status}]")
            return status
        except Exception as e:
            raise USvisaException(e, sys)

    def is_column_exist(self, df: DataFrame) -> bool:
        try:
            dataframe_columns = df.columns
            missing_numerical_columns = []
            missing_categorical_columns = []

            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns) > 0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")

            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns) > 0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            return len(missing_categorical_columns) == 0 and len(missing_numerical_columns) == 0

        except Exception as e:
            raise USvisaException(e, sys)

    @staticmethod
    def read_data(file_path) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise USvisaException(e, sys)

    # 🔥 NEW DRIFT DETECTION FOR EVIDENTLY 0.2.8
    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame) -> bool:
        try:
            drift_report = Report(metrics=[DataDriftTable()])

            drift_report.run(reference_data=reference_df, current_data=current_df)

            report_json = json.loads(drift_report.json())

            write_yaml_file(
                file_path=self.data_validation_config.drift_report_file_path,
                content=report_json
            )

            result = report_json["metrics"][0]["result"]

            dataset_drift = result["dataset_drift"]
            n_features = result["number_of_columns"]
            n_drifted = result["number_of_drifted_columns"]

            logging.info(f"{n_drifted}/{n_features} columns drifted.")

            return dataset_drift

        except Exception as e:
            raise USvisaException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            validation_error_msg = ""
            logging.info("Starting data validation")

            train_df = self.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)

            if not self.validate_number_of_columns(train_df):
                validation_error_msg += "Columns are missing in training dataframe. "

            if not self.validate_number_of_columns(test_df):
                validation_error_msg += "Columns are missing in testing dataframe. "

            if not self.is_column_exist(train_df):
                validation_error_msg += "Required columns missing in training dataframe. "

            if not self.is_column_exist(test_df):
                validation_error_msg += "Required columns missing in test dataframe. "

            validation_status = len(validation_error_msg) == 0

            if validation_status:
                drift_status = self.detect_dataset_drift(train_df, test_df)
                validation_error_msg = "Drift detected" if drift_status else "Drift not detected"
            else:
                logging.info(f"Validation error: {validation_error_msg}")

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                message=validation_error_msg,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise USvisaException(e, sys)
