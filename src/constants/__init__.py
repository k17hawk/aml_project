from pathlib import Path

# SQL_SERVER = r"DESKTOP-JSV1UOD\USER_ROOT"
SQL_SERVER = "192.168.0.23,1433" 
SQL_DATABASE = "AMLDb"
SQL_USERNAME = "newuser"  
SQL_PASSWORD = "toor"  
TABLE_NAME = 'Transactions'

BUCKET_NAME = 'abc_aml_data_bucket'
GCS_FILE_NAME = 'aml_input_data.csv'


import os
from dataclasses import dataclass
from datetime import datetime


#developer env
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("C:/Users/lang-chain/Documents/aml_project/datastorage.json"))
#docker env
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("datastorage.json"))


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


