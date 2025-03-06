from src.entity.artifcat_entity import DataValidationArtifact, DataIngestionArtifact
from src.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from src.component.data_validation import DataValidation
from src.exception import AMLException
import sys
from bson.json_util import loads

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



def load_data_ingestion_artifact(collection_name="artifacts"):
    """Load the latest DataIngestionArtifact from MongoDB."""
    artifact_data = db[collection_name].find_one(sort=[("_id", -1)])  # Get the latest artifact
    if artifact_data:
        return DataIngestionArtifact(**artifact_data)  # Convert back to object
    else:
        raise Exception("No artifact found in MongoDB!")

if __name__ == "__main__":
    data_ingestion_artifact = load_data_ingestion_artifact()  # Load artifact
    artifact = run_data_validation(data_ingestion_artifact)
    print(f"Data Validation Completed: {artifact}")


