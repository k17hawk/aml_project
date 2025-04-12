import time
import json
import pandas as pd
from kafka import KafkaProducer
from google.cloud import storage
from src.constants import PREDICTION_BUCKET_NAME,PROCESSED_LOG_PATH,\
    FILE_PREFIX,GCP_CREDENTIAL_PATH, KAFKA_BOOTSTRAP_SERVERS, TOPIC_NAME,MAX_RETRIES,FILE_PATTERN,POLL_INTERVAL_SEC
from src.logger import logger
import io
import re,os
from datetime import datetime, timedelta
from kafka.errors import KafkaError
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Optional


class GCSKafkaProducer:
    def __init__(self):
        self.storage_client = self._init_gcs_client()
        self.producer = self._init_kafka_producer()
        self._ensure_processed_log()
    
    def _ensure_processed_log(self):
        """Ensure the processed files log exists."""
        os.makedirs(os.path.dirname(PROCESSED_LOG_PATH), exist_ok=True)
        if not os.path.exists(PROCESSED_LOG_PATH):
            open(PROCESSED_LOG_PATH, 'w').close()
    

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _init_gcs_client(self) -> storage.Client:
        """Initialize GCS client with retry on connection issues."""
        try:
            if os.path.exists(GCP_CREDENTIAL_PATH):
                credentials = service_account.Credentials.from_service_account_file(
                    GCP_CREDENTIAL_PATH,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                logger.info("GCS client initialized with service account")
                return storage.Client(credentials=credentials)
            logger.info("GCS client initialized with default credentials")
            return storage.Client()
        except Exception as e:
            logger.error(f"GCS client initialization failed: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3))
    def _init_kafka_producer(self) -> KafkaProducer:
        """Initialize Kafka producer with retry on connection issues."""
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=MAX_RETRIES,
                compression_type='gzip',
                linger_ms=500,
                batch_size=16384,
                request_timeout_ms=15000
            )
        except Exception as e:
            logger.error(f"Kafka producer initialization failed: {str(e)}")
            raise

    def _delivery_report(self, err: Optional[KafkaError], msg) -> None:
        """Callback for Kafka message delivery status."""
        if err:
            logger.error(f"Message failed delivery: {err}")
        else:
            logger.debug(f"Delivered to {msg.topic()} [Partition {msg.partition()}]")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _get_new_files(self) -> List[str]:
        """List new files in GCS with retry on API failures."""
        try:
            bucket = self.storage_client.bucket(PREDICTION_BUCKET_NAME)
            processed_files = self._load_processed_files()
            
            new_files = []
            for blob in bucket.list_blobs(prefix=FILE_PREFIX):
                if (re.fullmatch(FILE_PATTERN, blob.name) and 
                    blob.name not in processed_files):
                    new_files.append(blob.name)
                    logger.info(f"New file detected: {blob.name}")

            return new_files
        except Exception as e:
            logger.error(f"Failed to list GCS files: {str(e)}")
            return []

    def _load_processed_files(self) -> set:
        """Load already processed files from persistent log."""
        with open(PROCESSED_LOG_PATH, 'r') as f:
            return set(line.strip() for line in f.readlines())

    def _mark_processed(self, filename: str):
        """Record processed file in persistent log."""
        with open(PROCESSED_LOG_PATH, 'a') as f:
            f.write(f"{filename}\n")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _download_file(self, blob) -> str:
        """Download file content with retry on failures."""
        return blob.download_as_text()

    @retry(stop=stop_after_attempt(3))
    def _archive_file(self, blob, new_path: str):
        """Move file to archive location with retry."""
        bucket = self.storage_client.bucket(PREDICTION_BUCKET_NAME)
        bucket.rename_blob(blob, new_path)

    def _process_file(self, file_path: str) -> bool:
        """Process a single file end-to-end."""
        try:
            blob = self.storage_client.bucket(PREDICTION_BUCKET_NAME).blob(file_path)
            content = self._download_file(blob)
            
            # Parse CSV (assuming CSV format per Helm config)
            records = []
            for line in content.split('\n'):
                if line.strip():
                    records.append({"data": line, "source_file": file_path})
            
            # Publish to Kafka
            for record in records:
                self.producer.send(
                    TOPIC_NAME,
                    value=record
                ).add_callback(self._delivery_report)
            
            # Archive and mark processed
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = f"processed/{timestamp}/{os.path.basename(file_path)}"
            self._archive_file(blob, archive_path)
            self._mark_processed(file_path)
            
            logger.info(f"Processed {len(records)} records from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Permanent failure processing {file_path}: {str(e)}")
            return False

    def run(self):
        """Main processing loop."""
        logger.info("Starting GCS to Kafka producer")
        try:
            while True:
                start_time = time.time()
                
                new_files = self._get_new_files()
                if new_files:
                    logger.info(f"Processing {len(new_files)} new files")
                    for file_path in new_files:
                        self._process_file(file_path)
                
                # Flush Kafka producer periodically
                self.producer.flush()
                
                # Sleep for remaining poll interval
                elapsed = time.time() - start_time
                sleep_time = max(0, POLL_INTERVAL_SEC - elapsed)
                logger.info(f"Next poll in {sleep_time:.1f}s")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully")
        except Exception as e:
            logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        finally:
            self.producer.close()
            logger.info("Kafka producer closed")

