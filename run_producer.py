from src.kafka_fetch.producer import GCSKafkaProducer
if __name__ == "__main__":
    producer = GCSKafkaProducer()
    producer.run()
