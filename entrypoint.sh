#!/bin/bash
set -e

# Define available pipeline stages
STAGES=("ingestion_pipeline.py" "validation_pipeline.py" "transformation_pipeline.py" "training_pipeline.py","evaluation_pipeline.py", "pusher_pipeline.py" "file_watcher.py")

# Check if the user provided a stage as an argument
if [[ -z "$1" ]]; then
    echo "No pipeline stage specified."
    echo "Available stages: ${STAGES[*]}"
    exit 1
fi

STAGE="$1"

# Check if the specified stage is valid
if [[ ! " ${STAGES[@]} " =~ " ${STAGE} " ]]; then
    echo "Invalid pipeline stage: $STAGE"
    echo "Available stages: ${STAGES[*]}"
    exit 1
fi

echo "Running pipeline stage: $STAGE"
exec spark-submit "/app/$STAGE"
