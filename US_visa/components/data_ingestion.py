import os
import sys

from pandas import DataFrame
from sklearn.model_selection import train_test_split

# ❌ REMOVE this (causes circular import)
# from us_visa.entity.config_entity import DataIngestionConfig

from us_visa.entity.artifact_entity import DataIngestionArtifact
from us_visa.exception import USvisaException
from us_visa.logger import logging
from us_visa.data_access.usvisa_data import USvisaData


class DataIngestion:
    def __init__(self, data_ingestion_config=None):
        """
        :param data_ingestion_config: configuration for data ingestion
        """
        try:
            # Lazy import to avoid circular import problem
            if data_ingestion_config is None:
                from us_visa.entity.config_entity import DataIngestionConfig
                data_ingestion_config = DataIngestionConfig()

            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise USvisaException(e, sys)

    def export_data_into_feature_store(self) -> DataFrame:
        """
        Method Name :   export_data_into_feature_store
        Description :   This method exports data from mongodb to csv file
        
        Output      :   data is returned as artifact of data ingestion components
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info("Exporting data from mongodb")
            usvisa_data = USvisaData()
            dataframe = usvisa_data.export_collection_as_dataframe(
                collection_name=self.data_ingestion_config.collection_name
            )
            logging.info(f"Shape of dataframe: {dataframe.shape}")

            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info(f"Saving exported data into feature store: {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe

        except Exception as e:
            raise USvisaException(e, sys)

    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        """
        Method Name :   split_data_as_train_test
        Description :   This method splits the dataframe into train and test sets
        """
        logging.info("Entered split_data_as_train_test method of DataIngestion class")

        try:
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio
            )

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Saving train and test datasets")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)

            logging.info("Train and test datasets saved successfully")

        except Exception as e:
            raise USvisaException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Method Name :   initiate_data_ingestion
        Description :   Executes data ingestion workflow
        """
        logging.info("Started initiate_data_ingestion")

        try:
            dataframe = self.export_data_into_feature_store()
            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            logging.info(f"Data Ingestion Artifact created: {data_ingestion_artifact}")

            return data_ingestion_artifact

        except Exception as e:
            raise USvisaException(e, sys)
