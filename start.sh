#!/bin/sh

# Initialize the Airflow database (if not already initialized)
if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    echo "Initializing Airflow database..."
    airflow db init
    echo "Creating Airflow admin user..."
    airflow users create \
        --username admin \
        --password admin \
        --firstname Kumar \
        --lastname Dahal \
        --role Admin \
        --email kumardahal5@gmail.com
fi

# Start the scheduler in the background
echo "Starting Airflow scheduler..."
airflow scheduler &

# Start the webserver in the foreground
echo "Starting Airflow webserver..."
exec airflow webserver