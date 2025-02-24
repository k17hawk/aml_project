import os
import pandas as pd
import pyodbc
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

storage_client = storage.Client()

#creating new bucket
bucket_name = 'abc_aml_data_bucket'

#checking if bucket already exist
try:
    bucket = storage_client.get_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' already exists. Skipping creation.")

#if not creating new bucket
except Exception as e:
    print(f"Bucket not found. Creating new bucket: {bucket_name}")
    try:
        #creating  bucket
        bucket = storage_client.create_bucket(bucket_name, location='US')
        print(f"Bucket '{bucket_name}' created successfully.")
        
    except Exception as e:
        print(f"Bucket creation failed: {e}")

#uploading the data into bucket
def upload_files(blob_name,file_path,bucket_name):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        print(e)
        return False

if __name__=='__main__':
    #making os independent
    file_path = Path("Data") / "SAML-D.csv"
    if file_path.exists():
        absolute_path = file_path.resolve()
        upload_files('aml_input_data.csv', absolute_path, bucket_name)
    else:
        print(f"File not found: {file_path}")