from src.kafka_fetch.producer import GcsEventDrivenProducer
from gcs_notification import setup_gcs_notification

if __name__ == "__main__":
    #i have created manually the topic in pubsub and the subscription 
    # and i have created the bucket in gcs manually
    #but will be created autmatically by the code below also
    setup_gcs_notification('aml-data-bucket', 'my-gcs-data', 'data-prediction-pipe-data')
    
    producer = GcsEventDrivenProducer(
        project_id='data-prediction-pipe-data',
        subscription_name='my-gcs-data-sub',
        bootstrap_servers='localhost:9092',
        topic_name='my-gcs-data'
    )
    producer.start_consuming()
