from src.entity.artifcat_entity import DataValidationArtifact, DataIngestionArtifact
from src.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from src.component.data_validation import DataValidation
from src.exception import AMLException
import sys

def run_data_validation(data_ingestion_artifact: DataIngestionArtifact):
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )

        data_validation_artifact = data_validation.initiate_data_validation()
        return data_validation_artifact  # Output for next stage

    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    # Load previous stage artifact (from file, database, etc.)
    data_ingestion_artifact = load_data_ingestion_artifact()  # Implement this function
    artifact = run_data_validation(data_ingestion_artifact)
    print(f"Data Validation Completed: {artifact}")
