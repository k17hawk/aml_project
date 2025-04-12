#!/bin/bash
set -e

echo "Starting container at $(date)"
echo "Kafka Bootstrap Servers: $KAFKA_BOOTSTRAP_SERVERS"
echo "GCS Bucket: $GCS_BUCKET_NAME"
echo "GCS File Pattern: $GCS_FILE_PATTERN"

if [[ "$RUN_MODE" == "producer" ]]; then
  echo "Running Kafka Producer..."
  python /app/run_producer.py
elif [[ "$RUN_MODE" == "consumer" ]]; then
  echo "Running Kafka Consumer..."
  python /app/run_consumer.py
else
  echo "Unknown RUN_MODE: '$RUN_MODE'. Please set RUN_MODE to 'producer' or 'consumer'."
  exit 1
fi