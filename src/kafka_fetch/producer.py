import time
import json
import pandas as pd
from kafka import KafkaProducer
from google.cloud import storage
from constants import BUCKET_NAME, GCS_FILE_NAME
from src.logger import logger
import io

# Initialize Google Cloud Storage Client
storage_client = storage.Client()
topic = 'gcs-data'

producer = KafkaProducer(
    bootstrap_servers='127.0.0.1:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def fetch_gcs_data():
    """Fetch file from GCS and send to Kafka topic."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_FILE_NAME)
    content = blob.download_as_text()

    if GCS_FILE_NAME.endswith(".csv"):
        df = pd.read_csv(io.StringIO(content))
        data = df.to_dict(orient="records")
    else:
        print("No file found")

    if 'data' in locals(): 
        for record in data:
            # Print the data passing through
            print(f"Sending data: {json.dumps(record, indent=2)}")
            producer.send(topic, record).add_callback(delivery_report)

        print(f"{len(data)} records are being sent to Kafka.")

# Run every hour
while True:
    fetch_gcs_data()
    time.sleep(3600)
