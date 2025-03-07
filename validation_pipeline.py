from src.entity.artifcat_entity import DataValidationArtifact, DataIngestionArtifact
from src.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from src.component.data_validation import DataValidation
from src.exception import AMLException
import sys
from bson.json_util import loads
from src.data_access.data_ingestion_artifact import DataIngestionArtifactData

def run_data_validation(data_ingestion_artifact: DataIngestionArtifact):
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )
       

        data_validation_artifact = data_validation.initiate_data_validation()
        return data_validation_artifact  

    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    data_ingestion_artifact_data  = DataIngestionArtifactData()
    data_ingestion_artifact =  data_ingestion_artifact_data.get_ingestion_artifact()
    artifact = run_data_validation(data_ingestion_artifact)
    print(f"Data Validation Completed: {artifact}")


