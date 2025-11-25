from us_visa.components.data_validation import DataValidation
from us_visa.entity.artifact_entity import DataIngestionArtifact
from us_visa.entity.config_entity import DataValidationConfig

# Correct ingested CSV paths from artifact folder
TRAIN_PATH = "artifact/11_24_2025_14_02_10/data_ingestion/ingested/train.csv"
TEST_PATH  = "artifact/11_24_2025_14_02_10/data_ingestion/ingested/test.csv"

# Create ingestion artifact (only two arguments needed)
ingestion_artifact = DataIngestionArtifact(
    trained_file_path=TRAIN_PATH,
    test_file_path=TEST_PATH
)

# Load data validation config
data_validation_config = DataValidationConfig()

# Create validator
validator = DataValidation(
    data_ingestion_artifact=ingestion_artifact,
    data_validation_config=data_validation_config
)

# Run validation
artifact = validator.initiate_data_validation()

print("\n✨ DATA VALIDATION COMPLETED ✨")
print(artifact)
