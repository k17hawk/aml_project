from src.entity.artifcat_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
from src.component.data_ingestion import DataIngestion
from src.exception import AMLException
import sys
import pickle

def run_data_ingestion():
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()

        return data_ingestion_artifact  

    except Exception as e:
        raise AMLException(e, sys)

def save_artifact(artifact, file_path):
    """Save artifact as a pickle file."""
    with open(file_path, "wb") as f:
        pickle.dump(artifact, f)


if __name__ == "__main__":
    artifact = run_data_ingestion()
    print(f"Data Ingestion Completed: {artifact}")
