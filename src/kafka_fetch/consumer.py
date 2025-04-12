import os
import csv
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from typing import Dict, Any

from src.constants import KAFKA_BOOTSTRAP_SERVERS, TOPIC_NAME,OUTPUT_DIR, BATCH_SIZE,MAX_FILE_AGE_MINUTES
from src.logger import logger

class KafkaCSVConsumer:
    def __init__(self):
        self.consumer = self._init_consumer()
        self.current_file = None
        self.current_writer = None
        self.file_start_time = None
        self.message_count = 0
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _init_consumer(self) -> KafkaConsumer:
        """Initialize Kafka consumer with error handling."""
        try:
            return KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=10000
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            raise

    def _rotate_file(self):
        """Close current file and open a new one based on time/size."""
        if self.current_file:
            self.current_file.close()
            logger.info(f"Closed file: {self.current_file.name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(OUTPUT_DIR, f"output_{timestamp}.csv")
        self.current_file = open(filename, 'w', newline='')
        self.current_writer = csv.writer(self.current_file)
        self.file_start_time = datetime.now()
        self.message_count = 0
        logger.info(f"Created new file: {filename}")

    def _should_rotate(self) -> bool:
        """Check if we need to rotate the output file."""
        if not self.current_file:
            return True
        if self.message_count >= BATCH_SIZE:
            return True
        if (datetime.now() - self.file_start_time).total_seconds() > MAX_FILE_AGE_MINUTES * 60:
            return True
        return False

    def _write_record(self, record: Dict[str, Any]):
        """Write a single record to CSV."""
        try:
            # Extract data from Kafka message
            data = record['data']  # Assuming producer sends {'data': 'csv,row,here'}
            if isinstance(data, str):
                # If data is a CSV string, split into columns
                self.current_writer.writerow(data.split(','))
            elif isinstance(data, dict):
                # If data is a dict, write as key-value pairs
                self.current_writer.writerow(data.values())
            else:
                logger.warning(f"Unsupported data format: {type(data)}")
            
            self.message_count += 1
        except Exception as e:
            logger.error(f"Failed to write record: {str(e)}")

    def run(self):
        """Main consumption loop."""
        logger.info(f"Starting consumer writing to {OUTPUT_DIR}")
        try:
            for message in self.consumer:
                if self._should_rotate():
                    self._rotate_file()
                
                self._write_record(message.value)
                
                # Commit offsets manually for at-least-once semantics
                self.consumer.commit()
                
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}", exc_info=True)
        finally:
            if self.current_file:
                self.current_file.close()
            self.consumer.close()
            logger.info("Consumer stopped")

