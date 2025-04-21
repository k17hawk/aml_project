from src.exception import AMLException
from src.logger import logging 
from src.ml.estimator import AMLIdntifierEstimator
# from src.config.spark_manager import spark_session
# from src.config.spark_manager import SparkSessionManager
# spark_session = SparkSessionManager().create_session()

from src.config.spark_manager import SparkManager
spark_session = SparkManager.get_spark_session()

from pyspark.sql.functions import col, concat_ws, to_timestamp, lpad
from src.constants import TIMESTAMP
import os,sys
from src.entity.config_entity import BatchPredictionConfig
from src.constants import TIMESTAMP
from pyspark.sql import DataFrame
from pyspark.sql.types import FloatType

class BatchPrediction:
    def __init__(self,batch_config:BatchPredictionConfig,input_data:str=None):
        try:
            self.batch_config=batch_config 
            self.prediction_data = input_data
        except Exception as e:
            raise AMLException(e, sys)
    def start_prediction(self):
        try:
            if not self.prediction_data or not os.path.exists(self.prediction_data):
                logging.info(f"No file found at {self.prediction_data}")
                print(f"No file found at {self.prediction_data}")
                return None 

            finance_estimator = AMLIdntifierEstimator()

            df: DataFrame = spark_session.read.csv(
                self.prediction_data,
                header=True,
                inferSchema=True
            )

            archive_file_path = os.path.join(self.batch_config.archive_dir,f"Transactions_{TIMESTAMP}")
            df.write.csv(archive_file_path,header=True,mode="overwrite")
            print("writing to archive file path")

            df.write.mode("overwrite").parquet(self.batch_config.parquet_dir)
            df:DataFrame = spark_session.read.parquet(self.batch_config.parquet_dir,multiline=True)
            prediction_df = finance_estimator.transform(dataframe=df)
            print("transform done")
    
            columns_to_drop = [c for c in prediction_df.columns if any(keyword in c for keyword in ["index_", "num_", "num_index_", "scaled_", "va_input_features","rawPrediction","probability","prediction_Is_laundering"])]
            prediction_df = prediction_df.drop(*columns_to_drop)
            
            prediction_df = prediction_df.withColumn("year", col("year").cast("string")) \
                .withColumn("month", lpad(col("month").cast("string"), 2, "0")) \
                .withColumn("day", lpad(col("day").cast("string"), 2, "0")) \
                .withColumn("hour", lpad(col("hour").cast("string"), 2, "0")) \
                .withColumn("minute", lpad(col("minute").cast("string"), 2, "0")) \
                .withColumn("second", lpad(col("second").cast("string"), 2, "0"))
            prediction_df = prediction_df.withColumn(
                "timestamp_str",
                concat_ws(" ",
                    concat_ws("-", col("year"), col("month"), col("day")),
                    concat_ws(":", col("hour"), col("minute"), col("second"))
                )
            )

            prediction_df = prediction_df.drop("year", "month", "day", "hour", "minute", "second")
            
            columns_to_convert = [
                "prediction",
                "Amount",
            ]
            for column_name in columns_to_convert:
                prediction_df = prediction_df.withColumn(column_name, col(column_name).cast(FloatType()))
        
            prediction_file_path = os.path.join(self.batch_config.outbox_dir,f"Predictions_{TIMESTAMP}")
            prediction_df.write.csv(prediction_file_path, header=True, mode="overwrite")
            print("writing to prediction file path")
            print(f"Prediction file written to {prediction_file_path}")
            return prediction_file_path
        except Exception as e:
            raise AMLException(e, sys)