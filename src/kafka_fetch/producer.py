import time
import json
import pandas as pd
import re
import threading
from kafka import KafkaProducer
from google.cloud import storage
import io
from src.logger import logger
from typing import List, Dict, Any
from google.cloud import storage, pubsub_v1
from kafka.errors import KafkaError
from google.api_core.exceptions import GoogleAPIError, RetryError

class GcsEventDrivenProducer:
    def __init__(
        self,
        project_id: str,
        subscription_name: str,
        bootstrap_servers: str = '127.0.0.1:9092',
        topic_name: str = 'my-gcs-data',
        bucket_name: str = 'aml-data-bucket',
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        self.topic_name = topic_name
        self.bucket_name = bucket_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._shutdown_event = threading.Event()
        
        # Pub/Sub client
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_name)
        
        # Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3
        )
        
        # GCS client
        self.storage_client = storage.Client()
        
        logger.info("GcsEventDrivenProducer initialized")

    def _delivery_report(self, err=None, metadata=None):
        """Callback for message delivery reports"""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(
                f'Message delivered to {self.topic_name} '
                f'[Partition: {metadata.partition if metadata else "N/A"}]'
            )

    def _download_with_retry(self, blob):
        """Download blob content with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return blob.download_as_text()
            except (GoogleAPIError, RetryError) as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                time.sleep(self.retry_delay)

    def _process_gcs_event(self, event: dict):
        """Process a single GCS event notification with robust error handling"""
        try:
            blob_name = event['name']
            if not re.search(r'Transactions_\d{8}_\d{6}\.csv$', blob_name):
                logger.info(f"Skipping non-matching file: {blob_name}")
                return 0
            
            logger.info(f"Processing new file: {blob_name}")
            blob = self.storage_client.bucket(self.bucket_name).blob(blob_name)
            
            try:
                content = self._download_with_retry(blob)
                
                logger.debug(f"File content: {content[:200]}...")  # Log first 200 chars
                
                df = pd.read_csv(io.StringIO(content))
                records = df.to_dict(orient="records")
                
                for record in records:
                    if self._shutdown_event.is_set():
                        logger.info("Shutdown detected, aborting message sending")
                        return 0
                    
                    future = self.producer.send(self.topic_name, value=record)
                    future.add_callback(
                        lambda metadata: self._delivery_report(None, metadata))
                    future.add_errback(
                        lambda err: self._delivery_report(err, None))
                
                self.producer.flush()
                logger.info(f"Successfully sent {len(records)} records from {blob_name}")
                return len(records)
                
            except Exception as download_error:
                logger.error(f"Failed to process file {blob_name}: {str(download_error)}")
                raise
            
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}", exc_info=True)
            raise

    def start_consuming(self):
        """Start listening for GCS events with robust error handling"""
        def callback(message: pubsub_v1.subscriber.message.Message):
            try:
                if self._shutdown_event.is_set():
                    logger.info("Shutdown detected, skipping message processing")
                    message.nack()  # Will be redelivered after shutdown
                    return
                
                event = json.loads(message.data.decode('utf-8'))
                self._process_gcs_event(event)
                message.ack()
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                message.nack()  # Negative acknowledgment - redeliver
        
        logger.info("Starting to listen for GCS events...")
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=callback)
        
        try:
            while not self._shutdown_event.is_set():
                try:
                    streaming_pull_future.result(timeout=1)  # Check more frequently
                except TimeoutError:
                    continue  # Normal operation, just checking for shutdown
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, initiating shutdown...")
            self._shutdown_event.set()
        except Exception as e:
            logger.error(f"Unexpected error in event consumer: {str(e)}")
            self._shutdown_event.set()
        finally:
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown procedure"""
        if not self._shutdown_event.is_set():
            self._shutdown_event.set()
        
        logger.info("Initiating shutdown...")
        try:
            # Close Kafka producer
            if hasattr(self, 'producer'):
                self.producer.close(timeout=5)
                logger.info("Kafka producer closed")
            
            # Close Pub/Sub subscriber
            if hasattr(self, 'subscriber'):
                self.subscriber.close()
                logger.info("Pub/Sub subscriber closed")
            
            logger.info("Shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def force_shutdown(self):
        """Force immediate shutdown without waiting for cleanups"""
        logger.warning("FORCE SHUTDOWN INITIATED!")
        self._shutdown_event.set()
        
        # Immediately close resources without waiting
        if hasattr(self, 'producer'):
            self.producer.close(timeout=0)
        if hasattr(self, 'subscriber'):
            self.subscriber.close()
        
        logger.warning("FORCE SHUTDOWN COMPLETED")