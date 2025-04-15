from pathlib import Path
import os
from google.oauth2 import service_account
# SQL_SERVER = r"DESKTOP-JSV1UOD\USER_ROOT"

TABLE_NAME =  os.getenv("SQL_SERVER_TABLE")

SQL_HOST = os.getenv("SQL_SERVER_HOST")
SQL_PORT = os.getenv("SQL_SERVER_PORT")
SQL_DATABASE = os.getenv("SQL_SERVER_DATABASE")
SQL_USERNAME = os.getenv("SQL_SERVER_USERNAME")
SQL_PASSWORD = os.getenv("SQL_SERVER_PASSWORD")
SQL_SERVER = f"{SQL_HOST},{SQL_PORT}"

DRIVER_HOST = os.getenv('SPARK_DRIVER_HOST')
DRIVER_PORT = os.getenv('SPARK_DRIVER_PORT')
SPARK_MASTER = os.getenv('SPARK_MASTER')
EXECUTOR_MEMORY = os.getenv('SPARK_EXECUTOR_MEMORY')
DRIVER_MEMORY = os.getenv('SPARK_DRIVER_MEMORY')

BUCKET_NAME = 'abc_aml_data_bucket'
GCS_FILE_NAME = 'aml_input_data.csv'

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID','data-prediction-pipe-data')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GCP_CREDENTIAL_PATH', '/etc/gcp-key/key.json') 

# credentials = service_account.Credentials.from_service_account_file(
#     os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# )

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

TOPIC_NAME =  os.getenv('TOPIC_NAME','my-gcs-data')
PREDICTION_BUCKET_NAME = os.getenv('PREDICTION_BUCKET_NAME','aml-data-bucket')
FILE_PATTERN = os.getenv('FILE_PATTERN',r'Transactions_\d{8}_\d{6}\.csv$')
TOPIC_NAME_SUB = os.getenv('TOPIC_NAME_SUB',"my-gcs-data-sub")

OUTPUT_DIR = os.path.join('data', 'inbox-data') 
os.makedirs(OUTPUT_DIR, exist_ok=True)
MAX_POLL_RECORDS = 1000
FETCH_MAX_BYTES = 52428800
FETCH_MAX_WAIT_MS = 500  

import os
from dataclasses import dataclass
from datetime import datetime


#developer env
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("C:/Users/lang-chain/Documents/aml_project/cloud-api.json"))

#docker env
credentials= str(Path("data-prediction-pipe-data-61d5e9bb16fa.json"))
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


DATA_INGESTION_DIR = "data_ingestion"
DATA_INGESTION_DOWNLOADED_DATA_DIR = "downloaded_files"
DATA_INGESTION_FILE_NAME = "Transaction"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_FAILED_DIR = "failed_downloaded_files"
DATA_INGESTION_METADATA_FILE_NAME = "meta_info.yaml"

DATA_VALIDATION_DIR = "data_validation"
DATA_VALIDATION_FILE_NAME = "aml_prediction"
DATA_VALIDATION_ACCEPTED_DATA_DIR = "accepted_data"
DATA_VALIDATION_REJECTED_DATA_DIR = "rejected_data"

DATA_TRANSFORMATION_DIR = "data_transformation"
DATA_TRANSFORMATION_PIPELINE_DIR = "transformed_pipeline"
DATA_TRANSFORMATION_TRAIN_DIR = "train"
DATA_TRANSFORMATION_FILE_NAME = "aml_data"
DATA_TRANSFORMATION_TEST_DIR = "test"
DATA_TRANSFORMATION_TEST_SIZE = 0.3


MODEL_TRAINER_BASE_ACCURACY = 0.6
MODEL_TRAINER_DIR = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR = "trained_model"
MODEL_TRAINER_MODEL_NAME = "AML_identifier"
MODEL_TRAINER_LABEL_INDEXER_DIR = "label_indexer"
MODEL_TRAINER_MODEL_METRIC_NAMES = ['f1',
                                    "weightedPrecision",
                                    "weightedRecall",
                                    "weightedTruePositiveRate",
                                    "weightedFalsePositiveRate",
                                    "weightedFMeasure",
                                    "truePositiveRateByLabel",
                                    "falsePositiveRateByLabel",
                                    "precisionByLabel",
                                    "recallByLabel",
                                    "fMeasureByLabel"]

MODEL_EVALUATION_DIR = "model_evaluation"
MODEL_EVALUATION_REPORT_DIR = "report"
MODEL_EVALUATION_REPORT_FILE_NAME = "evaluation_report"
MODEL_EVALUATION_THRESHOLD_VALUE = 0.002
MODEL_EVALUATION_METRIC_NAMES = ['f1',]
MODEL_EVALUATION_DIR = "model_evaluation"
MODEL_EVALUATION_REPORT_DIR = "report"
MODEL_EVALUATION_REPORT_FILE_NAME = "evaluation_report"
MODEL_EVALUATION_THRESHOLD_VALUE = 0.002
MODEL_EVALUATION_METRIC_NAMES = ['f1',]


MODEL_PUSHER_SAVED_MODEL_DIRS = "saved_models"
MODEL_PUSHER_DIR = "model_pusher"
MODEL_PUSHER_MODEL_NAME = MODEL_TRAINER_MODEL_NAME


@dataclass
class EnvironmentVariable:
    mongo_db_url = os.getenv("MONGO_DB_URL")


env_var = EnvironmentVariable()
