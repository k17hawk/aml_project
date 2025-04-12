from pathlib import Path
import os
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

GCP_CREDENTIAL_PATH = os.getenv('GCP_CREDENTIAL_PATH', '/etc/gcp-key/key.json') 
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka.default.svc.cluster.local:9092')

TOPIC_NAME = os.getenv('KAFKA_TOPIC', 'my-gcs-data')
PREDICTION_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'prediction-data-pipe')
STATE_BUCKET = os.getenv('GCS_STATE_BUCKET', 'pipeline-state-bucket')
FILE_PREFIX = os.getenv('GCS_FILE_PREFIX', 'predictions/')  
FILE_PATTERN = os.getenv('GCS_FILE_PATTERN', r'prediction_\d{8}_\d{6}\.csv$') 
POLL_INTERVAL_SEC = int(os.getenv('POLL_INTERVAL_SEC', '300')) 
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
PROCESSED_LOG_PATH = os.getenv('PROCESSED_LOG_PATH', '/var/processed-files/state.log')


POLL_TIMEOUT_MS = 5000
OUTPUT_DIR = os.path.join('data', 'inbox-data') 
BATCH_SIZE = os.getenv('BATCH_SIZE', 1000) 
MAX_FILE_AGE_MINUTES = 5  # Rotate files after X minutes

import os
from dataclasses import dataclass
from datetime import datetime


#developer env
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("C:/Users/lang-chain/Documents/aml_project/cloud-api.json"))

#docker env
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("cloud-api.json"))


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
