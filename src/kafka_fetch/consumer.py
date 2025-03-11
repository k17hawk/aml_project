from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import json
import os
import pandas as pd

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',  
    'group.id': 'csv-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

topic = 'gcs-data'

# Subscribe to the topic
consumer.subscribe([topic])

# Path to save the data in CSV format
csv_file = os.path.join("data", "inbox-data", "data.csv")
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Initialize an empty DataFrame to collect messages
df = pd.DataFrame()

# Set up a callback to handle assignments
def print_assignment(consumer, partitions):
    print('Assignment:', partitions)

# Set up a callback to handle assignments
consumer.subscribe([topic], on_assign=print_assignment)

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' % 
                                 (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            # Proper message
            print('Received message: {}'.format(msg.value().decode('utf-8')))
            data = json.loads(msg.value().decode('utf-8'))
            print(data)

            # Convert the message to a DataFrame
            new_data = pd.DataFrame([data])

            # Append the new data to the existing DataFrame
            df = pd.concat([df, new_data], ignore_index=True)

            # Save the DataFrame to a CSV file
            df.to_csv(csv_file, index=False)

            print(f"Saved data to CSV: {data}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
