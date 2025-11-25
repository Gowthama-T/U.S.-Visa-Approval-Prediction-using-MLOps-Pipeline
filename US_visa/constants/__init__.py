import os
from datetime import date

# =========================
# DATABASE DETAILS
# =========================
DATABASE_NAME = "US_VISA"
COLLECTION_NAME = "visa_data"

MONGO_DB_URL = "mongodb+srv://gowthugowthu000_db_user:HqKW38AlG7maV0ph@cluster0.rt0zh1e.mongodb.net/?appName=Cluster0"
MONGODB_URL_KEY = "MONGO_DB_URL"

# Path to schema file
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")

# =========================
# PIPELINE SETTINGS
# =========================
PIPELINE_NAME = "usvisa"
ARTIFACT_DIR = "artifact"

MODEL_FILE_NAME = "model.pkl"

TARGET_COLUMN = "case_status"
CURRENT_YEAR = date.today().year
PREPROCSSING_OBJECT_FILE_NAME = "preprocessing.pkl"
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")

# =========================
# DATA INGESTION CONSTANTS
# =========================
DATA_INGESTION_COLLECTION_NAME = "visa_data"
DATA_INGESTION_DIR_NAME = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2



FILE_NAME = "visa_data.csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"

# =========================
# DATA VALIDATION CONSTANTS
# =========================
DATA_VALIDATION_DIR_NAME = "data_validation"
DATA_VALIDATION_DRIFT_REPORT_DIR = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "drift_report.yaml"

# =========================
# DATA TRANSFORMATION CONSTANTS
# =========================
DATA_TRANSFORMATION_DIR_NAME = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = "transformed_object"
PREPROCSSING_OBJECT_FILE_NAME = "preprocessing.pkl"

# Target column (VERY IMPORTANT)
TARGET_COLUMN = "case_status"     # Change if your schema.yaml uses another name

# Additional feature engineering constant
CURRENT_YEAR = date.today().year

# =========================
# MODEL TRAINER CONSTANTS
# =========================
MODEL_TRAINER_DIR_NAME = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR = "trained_model"
MODEL_TRAINER_EXPECTED_SCORE = 0.80
MODEL_TRAINER_MODEL_CONFIG_FILE_PATH = os.path.join("config", "model.yaml")

# =========================
# MODEL EVALUATION CONSTANTS
# =========================
MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE = 0.02
MODEL_BUCKET_NAME = "us-visa-model"

# =========================
# MODEL PUSHER CONSTANTS
# =========================
MODEL_PUSHER_S3_KEY = MODEL_FILE_NAME
