import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.entity.config_entity import BatchPredictionConfig
from src.pipeline.batch_prediction import BatchPrediction
from src.logger import logging


class FileWatcher(FileSystemEventHandler):
    def __init__(self, batch_config: BatchPredictionConfig):
        self.batch_config = batch_config

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_name = os.path.basename(event.src_path)
        logging.info(f"New file detected: {file_name}")
        print("no files detected..")
        
        # Trigger the batch prediction pipeline
        try:
            batch_prediction = BatchPrediction(self.batch_config)
            batch_prediction.start_prediction()
            logging.info(f" Batch prediction completed for: {file_name}")
        except Exception as e:
            logging.error(f" Error in batch prediction: {e}")


def start_file_watcher(batch_config: BatchPredictionConfig):
    event_handler = FileWatcher(batch_config)
    observer = Observer()
    observer.schedule(event_handler, batch_config.inbox_dir, recursive=False)
    observer.start()
    
    logging.info(f" Monitoring directory: {batch_config.inbox_dir} for new files...")

    try:
        while True:
            time.sleep(5)  # Keep script running

            # Check if files exist in inbox
            files = os.listdir(batch_config.inbox_dir)
            if files:
                logging.info(f"Pending files detected: {', '.join(files)}")
            else:
                logging.info(" No new files detected, still watching...")

    except KeyboardInterrupt:
        observer.stop()
        logging.info("File watcher stopped.")

    observer.join()


if __name__ == "__main__":
    batch_config = BatchPredictionConfig()
    start_file_watcher(batch_config)
