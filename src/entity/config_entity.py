import os,sys
from dataclasses import dataclass
from datetime import datetime
from exception import AMLException
from constants import TIMESTAMP,DATA_INGESTION_DIR,DATA_INGESTION_METADATA_FILE_NAME,DATA_INGESTION_DOWNLOADED_DATA_DIR,\
    DATA_INGESTION_FAILED_DIR,DATA_INGESTION_FILE_NAME,DATA_INGESTION_FEATURE_STORE_DIR,SQL_SERVER,\
    SQL_DATABASE,SQL_USERNAME,SQL_PASSWORD,TABLE_NAME
from constants import *
from .metadeta_info import DataIngestionMetadata

#training pipeline config
@dataclass
class TrainingPipelineConfig:
    pipeline_name:str="artifact"
    artifact_dir:str = os.path.join(pipeline_name,TIMESTAMP)

#Data Ingestion Config
class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig,
                        fetch_date = TIMESTAMP):
        try:
            self.data_fetch=fetch_date

            data_ingestion_master_dir = os.path.join(os.path.dirname(training_pipeline_config.artifact_dir),DATA_INGESTION_DIR)
            
            self.data_ingestion_dir = os.path.join(data_ingestion_master_dir,TIMESTAMP)
            self.metadata_file_path = os.path.join(data_ingestion_master_dir, DATA_INGESTION_METADATA_FILE_NAME)

            data_ingestion_metadata = DataIngestionMetadata(metadata_file_path=self.metadata_file_path)
            self.date_fetch = TIMESTAMP
            if data_ingestion_metadata.is_metadata_file_present:
                metadata_info = data_ingestion_metadata.get_metadata_info()
                self.date_fetch = metadata_info.fetch_date

            self.download_dir=os.path.join(self.data_ingestion_dir, DATA_INGESTION_DOWNLOADED_DATA_DIR)
            self.failed_dir =os.path.join(self.data_ingestion_dir, DATA_INGESTION_FAILED_DIR)
            self.file_name = DATA_INGESTION_FILE_NAME
            self.feature_store_dir=os.path.join(data_ingestion_master_dir, DATA_INGESTION_FEATURE_STORE_DIR)
            self.datasource_url = SQL_SERVER
            self.database = SQL_DATABASE
            self.username = SQL_USERNAME
            self.password = SQL_PASSWORD
            self.table = TABLE_NAME
        except Exception as e:
            raise AMLException(e,sys)

class DataValidationConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig) -> None:
        try:
            data_validation_master_dir = os.path.join(os.path.dirname(training_pipeline_config.artifact_dir),
                                                   DATA_VALIDATION_DIR)
            data_validation_dir = os.path.join(data_validation_master_dir,TIMESTAMP)
            self.accepted_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_ACCEPTED_DATA_DIR)
            self.rejected_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_REJECTED_DATA_DIR)
            self.file_name=DATA_VALIDATION_FILE_NAME
        except Exception as e:
            raise AMLException(e,sys)

class DataTransformationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig) -> None:
        try:
            data_transformation_master_dir = os.path.join(os.path.dirname(training_pipeline_config.artifact_dir),
                                                   DATA_TRANSFORMATION_DIR)
            data_transformation_dir = os.path.join(data_transformation_master_dir,TIMESTAMP)
            self.transformed_train_dir = os.path.join( data_transformation_dir, DATA_TRANSFORMATION_TRAIN_DIR)
            self.transformed_test_dir = os.path.join(data_transformation_dir, DATA_TRANSFORMATION_TEST_DIR)
            self.export_pipeline_dir = os.path.join(data_transformation_dir, DATA_TRANSFORMATION_PIPELINE_DIR)
            self.file_name = DATA_TRANSFORMATION_FILE_NAME
            self.test_size = DATA_TRANSFORMATION_TEST_SIZE
        except Exception as e:
            raise AMLException(e,sys)

class ModelTrainerConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig) -> None:
        model_trainer_dir = os.path.join(training_pipeline_config.artifact_dir,
                                             MODEL_TRAINER_DIR)
        self.trained_model_file_path = os.path.join(model_trainer_dir, 
        MODEL_TRAINER_TRAINED_MODEL_DIR, MODEL_TRAINER_MODEL_NAME)
        self.label_indexer_model_dir = os.path.join(
            model_trainer_dir, MODEL_TRAINER_LABEL_INDEXER_DIR
        )
        self.base_accuracy = MODEL_TRAINER_BASE_ACCURACY
        self.metric_list = MODEL_TRAINER_MODEL_METRIC_NAMES
