from src.kafka_fetch.consumer import SimpleKafkaConsumer

if __name__ == "__main__":
    consumer = SimpleKafkaConsumer()
    consumer.consume_messages()