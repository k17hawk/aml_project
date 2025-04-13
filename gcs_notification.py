from google.cloud import pubsub_v1, storage

def setup_gcs_notification(bucket_name, topic_name, project_id):
    """Configure GCS to send notifications to Pub/Sub"""
    storage_client = storage.Client()
    publisher = pubsub_v1.PublisherClient()
    
    # Create or get the Pub/Sub topic
    topic_path = publisher.topic_path(project_id, topic_name)
    try:
        publisher.create_topic(request={"name": topic_path})
    except Exception as e:
        print(f"Topic may already exist: {e}")
    
    # Configure GCS notifications
    bucket = storage_client.bucket(bucket_name)
    notification = bucket.notification(
        topic_name=topic_name,
        event_types=['OBJECT_FINALIZE'],  # Trigger on new file creation
        payload_format='JSON_API_V1'
    )
    notification.create()
    
    print(f"Configured GCS bucket {bucket_name} to publish to {topic_name}")
    