import os
import pandas as pd
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


BUCKET_NAME = 'abc_aml_data_bucket'
GCS_FILE_NAME = 'aml_input_data.csv'  


# Connect to Google Cloud Storage
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(GCS_FILE_NAME)

cwd = Path.cwd()
tmp_dir = cwd / "tmp"
tmp_dir.mkdir(exist_ok=True) 


LOCAL_FILE_PATH = tmp_dir / "aml_data.csv"



blob.download_to_filename(LOCAL_FILE_PATH)
print(f"Downloaded {GCS_FILE_NAME} from GCS to {LOCAL_FILE_PATH}")

