from src.kafka_fetch.consumer import KafkaCSVConsumer
if __name__ == "__main__":
    consumer = KafkaCSVConsumer()
    consumer.run()