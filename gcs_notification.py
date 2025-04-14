from google.cloud import pubsub_v1, storage

from google.cloud import pubsub_v1, storage
from google.api_core.exceptions import AlreadyExists, GoogleAPIError
from src.constants import credentials
def setup_gcs_notification(bucket_name, topic_name, project_id):
    """Delete existing GCS notifications and create a new one for the given Pub/Sub topic."""
    storage_client = storage.Client(credentials=credentials)
    publisher = pubsub_v1.PublisherClient(credentials=credentials)

    # Create or get the Pub/Sub topic
    topic_path = publisher.topic_path(project_id, topic_name)
    try:
        publisher.create_topic(request={"name": topic_path})
        print(f"Created Pub/Sub topic: {topic_name}")
    except AlreadyExists:
        print(f"Pub/Sub topic {topic_name} already exists.")
    except GoogleAPIError as e:
        print(f"Error creating topic: {e}")
        return

    # Access the GCS bucket
    bucket = storage_client.bucket(bucket_name)

    # Delete all existing notifications
    notifications = list(bucket.list_notifications())
    for notif in notifications:
        print(f"Deleting notification ID: {notif.notification_id}")
        notif.delete()
    print(f"Deleted {len(notifications)} existing notifications from bucket: {bucket_name}")
    try:
        notification = bucket.notification(
            topic_name=topic_name,
            event_types=['OBJECT_FINALIZE'],  
            payload_format='JSON_API_V1'
        )
        notification.create()
        print(f" Notification created: GCS bucket {bucket_name} will publish to topic {topic_name}")
    except GoogleAPIError as e:
        print(f" Error creating GCS notification: {e}")
