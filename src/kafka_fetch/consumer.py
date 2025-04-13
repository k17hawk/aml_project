import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from src.logger import logger

class SimpleKafkaConsumer:
    def __init__(
        self,
        topic_name: str = 'my-gcs-data',
        bootstrap_servers: str = '127.0.0.1:9092'
    ):
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers
        self._consumer = None
        logger.info("SimpleKafkaConsumer initialized")

    def _initialize_consumer(self):
        """Set up the Kafka consumer"""
        self._consumer = KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='latest',  
            enable_auto_commit=False,
            group_id=None,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        logger.info(f"KafkaConsumer subscribed to topic: {self.topic_name}")

    def consume_messages(self):
        """Start consuming messages continuously"""
        try:
            self._initialize_consumer()
            logger.info("Started consuming messages...")

            for message in self._consumer:
                self._handle_message(message.value)

        except KafkaError as e:
            logger.error(f"Kafka error occurred: {str(e)}", exc_info=True)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt detected, shutting down...")
        finally:
            if self._consumer:
                self._consumer.close()
                logger.info("Kafka consumer closed")

    def _handle_message(self, message: dict):
        """Handle a single Kafka message (can be extended)"""
        logger.info(f"Received message: {message}")
        # You can add custom logic here (e.g., save to DB, trigger workflow, etc.)


