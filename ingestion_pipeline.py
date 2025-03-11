from component.data_ingestion import DataIngestion
from src.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
from src.entity.artifcat_entity import DataIngestionArtifact
from src.exception import AMLException
import sys

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        print("Data Ingestion Completed:", data_ingestion_artifact)
    except Exception as e:
        raise AMLException(e, sys)
