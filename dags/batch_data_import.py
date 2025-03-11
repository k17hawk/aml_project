from airflow.decorators import dag, task
import subprocess
import logging
import pendulum

# Set up logging
logger = logging.getLogger(__name__)

@dag(
    schedule_interval="0 */6 * * *",  # Every 6 hours
    start_date=pendulum.datetime(2023, 10, 1, tz="UTC"), 
    catchup=False, 
    tags=["kafka_producer_consumer"],  
)
def kafka_producer_consumer_dag():
    """
    This DAG triggers Kafka producer and consumer every 6 hours.
    """

    @task()
    def run_producer():
        """Run Kafka producer script."""
        try:
            logger.info("Starting Kafka producer...")
            result = subprocess.run(["python", "src/kafka_fetch/producer.py"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Producer ran successfully")
            else:
                logger.error(f"Producer failed with error: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to run Kafka producer: {e}")
            raise

    @task()
    def run_consumer():
        """Run Kafka consumer script."""
        try:
            logger.info("Starting Kafka consumer...")
            result = subprocess.run(["python", "src/kafka_fetch/consumer.py"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Consumer ran successfully")
            else:
                logger.error(f"Consumer failed with error: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to run Kafka consumer: {e}")
            raise

    # Run producer and consumer
    producer = run_producer()
    consumer = run_consumer()


    producer >> consumer  

kafka_producer_consumer_dag = kafka_producer_consumer_dag()
