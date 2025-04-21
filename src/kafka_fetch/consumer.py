import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from src.logger import logger
import os
import csv
from datetime import datetime

from src.constants import (
    TOPIC_NAME,
    KAFKA_BOOTSTRAP_SERVERS,
    MAX_POLL_RECORDS,
    FETCH_MAX_BYTES,
    FETCH_MAX_WAIT_MS,
    OUTPUT_DIR
)

class SimpleKafkaConsumer:
    def __init__(
        self,
        topic_name: str = TOPIC_NAME,
        bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS,
        group_id: str = None,
        max_poll_records: int = MAX_POLL_RECORDS,
        fetch_max_bytes: int = FETCH_MAX_BYTES,
        fetch_max_wait_ms: int = FETCH_MAX_WAIT_MS,
        auto_offset_reset: str = 'latest',
        enable_auto_commit: bool = False
    ):
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.max_poll_records = max_poll_records
        self.fetch_max_bytes = fetch_max_bytes
        self.fetch_max_wait_ms = fetch_max_wait_ms
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self._consumer = None


        self.current_file_timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.csv_file = os.path.join(OUTPUT_DIR, f"data_{self.current_file_timestamp}.csv")
        self._file_initialized = False  

        logger.info("SimpleKafkaConsumer initialized")

    def _initialize_consumer(self):
        """Set up the Kafka consumer with batch configuration"""
        self._consumer = KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=self.enable_auto_commit,
            group_id=self.group_id,
            max_poll_records=self.max_poll_records,
            fetch_max_bytes=self.fetch_max_bytes,
            fetch_max_wait_ms=self.fetch_max_wait_ms,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        logger.info(
            f"KafkaConsumer subscribed to topic: {self.topic_name} "
            f"with max_poll_records={self.max_poll_records}, "
            f"fetch_max_bytes={self.fetch_max_bytes}, "
            f"fetch_max_wait_ms={self.fetch_max_wait_ms}"
        )

    def consume_messages(self):
        """Start consuming messages continuously in batches"""
        try:
            self._initialize_consumer()
            logger.info("Started consuming messages...")

            while True:
                messages = self._consumer.poll(timeout_ms=1000)
                batch = []

                for _, records in messages.items():
                    for record in records:
                        print(f"fetching data..{records}")
                        batch.append(record.value)

                if batch:
                    print(f"Batch size: {len(batch)}")
                    logger.info(f"Processing batch of {len(batch)} messages")
                    self._handle_batch(batch)

        except KafkaError as e:
            logger.error(f"Kafka error occurred: {str(e)}", exc_info=True)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt detected, shutting down...")
        finally:
            if self._consumer:
                self._consumer.close()
                logger.info("Kafka consumer closed")
    
    

    def _handle_batch(self, batch: list):
        """Handle a batch of Kafka messages"""
        try:
           
            current_timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            if current_timestamp != self.current_file_timestamp:
                self.current_file_timestamp = current_timestamp
                self.csv_file = os.path.join(OUTPUT_DIR, f"data_{self.current_file_timestamp}.csv")
                self._file_initialized = False  
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = None
                for message in batch:
                    if not writer:
                        writer = csv.DictWriter(csvfile, fieldnames=message.keys())
                        if not self._file_initialized:
                            writer.writeheader()
                            self._file_initialized = True
                    writer.writerow(message)

            logger.info(f"Successfully saved batch to {self.csv_file}")

        except Exception as e:
            logger.error(f"Failed to process batch: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _flatten_dict(d, parent_key='', sep='_'):
        """Helper method to flatten nested dictionaries"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(SimpleKafkaConsumer._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
