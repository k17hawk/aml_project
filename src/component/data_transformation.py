from src.entity.schema import TransactionDataSchema
from pyspark.ml.feature import MinMaxScaler, VectorAssembler, StringIndexer
from pyspark.ml.pipeline import Pipeline
from src.config.spark_manager import spark_session
from src.exception import AMLException
from src.logger import  logging as logger
from src.entity.artifcat_entity import DataValidationArtifact, DataTransformationArtifact
from src.entity.config_entity import DataTransformationConfig
from pyspark.sql import DataFrame
from src.ml.features import DateTimeFeatureExtractor
from pyspark.sql.functions import col, rand
import os,sys

class DataTransformation:

    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig,
                 schema=TransactionDataSchema()
                 ):
        try:
            self.data_val_artifact = data_validation_artifact
            self.data_tf_config = data_transformation_config
            self.schema = schema
        except Exception as e:
            raise AMLException(e, sys)

    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_val_artifact.accepted_file_path
            dataframe: DataFrame = spark_session.read.parquet(file_path)
            dataframe.printSchema()
            return dataframe
        except Exception as e:
            raise AMLException(e, sys)
    
    def get_data_transformation_pipeline(self, ) -> Pipeline:
        try:
            
            stages = []
            derived_feature = DateTimeFeatureExtractor(inputCols=self.schema.derived_input_features,
                                                      outputCols=self.schema.derived_output_features)
            

        except Exception as e:
            raise AMLException(e, sys)
        
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logger.info(f">>>>>>>>>>>Started data transformation <<<<<<<<<<<<<<<")
            dataframe: DataFrame = self.read_data()
            logger.info(f"Number of row: [{dataframe.count()}] and column: [{len(dataframe.columns)}]")

            test_size = self.data_tf_config.test_size
            logger.info(f"Splitting dataset into train and test set using ration: {1 - test_size}:{test_size}")
            train_dataframe, test_dataframe = dataframe.randomSplit([1 - test_size, test_size])
            logger.info(f"Train dataset has number of row: [{train_dataframe.count()}] and"
                        f" column: [{len(train_dataframe.columns)}]")

            logger.info(f"Test dataset has number of row: [{test_dataframe.count()}] and"
                        f" column: [{len(test_dataframe.columns)}]")
            
        except Exception as e:
            raise AMLException(e,sys)