from us_visa.components.data_ingestion import DataIngestion
from us_visa.entity.config_entity import DataIngestionConfig

if __name__ == "__main__":
    ingestion = DataIngestion(DataIngestionConfig())
    artifact = ingestion.initiate_data_ingestion()

    print("\n✅ DATA INGESTION COMPLETED SUCCESSFULLY")
    print("Train File :", artifact.trained_file_path)
    print("Test File  :", artifact.test_file_path)
