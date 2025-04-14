from src.kafka_fetch.producer import GcsEventDrivenProducer
from gcs_notification import setup_gcs_notification
from src.constants import  PREDICTION_BUCKET_NAME, TOPIC_NAME, GCP_PROJECT_ID,KAFKA_BOOTSTRAP_SERVERS,GCP_PROJECT_ID,\
    TOPIC_NAME_SUB,FILE_PATTERN

if __name__ == "__main__":
    #i have created manually the topic in pubsub and the subscription 
    # and i have created the bucket in gcs manually
    #but will be created autmatically by the code below also
    setup_gcs_notification(PREDICTION_BUCKET_NAME, TOPIC_NAME,GCP_PROJECT_ID)
    
    producer = GcsEventDrivenProducer(
        project_id=GCP_PROJECT_ID,
        subscription_name=TOPIC_NAME_SUB,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        topic_name=TOPIC_NAME,
        bucket_name=PREDICTION_BUCKET_NAME,
        file_pattern=FILE_PATTERN,  
    )
    producer.start_consuming()
