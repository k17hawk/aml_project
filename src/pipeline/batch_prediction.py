from src.exception import AMLException
from src.logger import logging 
from src.ml.estimator import AMLIdntifierEstimator
from src.config.spark_manager import spark_session
import os,sys
from src.entity.config_entity import BatchPredictionConfig
from src.constants import TIMESTAMP
from pyspark.sql import DataFrame

class BatchPrediction:
    def __init__(self,batch_config:BatchPredictionConfig):
        try:
            self.batch_config=batch_config 
        except Exception as e:
            raise AMLException(e, sys)
    def start_prediction(self):
        try:
            input_files = os.listdir(self.batch_config.inbox_dir)
            
            if len(input_files)==0:
                logging.info(f"No file found hence closing the batch prediction")
                return None 

            finance_estimator = AMLIdntifierEstimator()
            for file_name in input_files:
                data_file_path = os.path.join(self.batch_config.inbox_dir,file_name)
                df:DataFrame = spark_session.read.parquet(data_file_path,multiline=True)
                prediction_df = finance_estimator.transform(dataframe=df)
                prediction_file_path = os.path.join(self.batch_config.outbox_dir,f"{file_name}_{TIMESTAMP}")
                prediction_df.write.parquet(prediction_file_path)

                archive_file_path = os.path.join(self.batch_config.archive_dir,f"{file_name}_{TIMESTAMP}")
                df.write.parquet(archive_file_path)
        except Exception as e:
            raise AMLException(e, sys)