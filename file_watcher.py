import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.entity.config_entity import BatchPredictionConfig
from src.pipeline.batch_prediction import BatchPrediction
from src.logger import logger
INBOX_DIR = os.path.join("data", "inbox-data")

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            try:
                logger.info(f"New file detected: {event.src_path}")
            
                config = BatchPredictionConfig() 
                # Triggering prediction
                predictor = BatchPrediction(batch_config=config, input_data=event.src_path)
                predictor.start_prediction()

                logger.info(f"Prediction completed for file: {event.src_path}")
            except Exception as e:
                logger.warning(f" Error processing file {event.src_path}: {e}")

if __name__ == "__main__":
    logger.info(f"Starting file watcher on: {INBOX_DIR}")
    
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=INBOX_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        logger.info(" File watcher stopped.")
    observer.join()