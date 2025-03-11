from src.entity.artifcat_entity import DataValidationArtifact, DataIngestionArtifact
from src.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from src.component.data_validation import DataValidation
from src.exception import AMLException
import sys
from bson.json_util import loads
from src.data_access.data_ingestion_artifact import DataIngestionArtifactData

if __name__ == "__main__":
    try:
        # Fetch the latest Data Ingestion artifact
        artifact_storage = DataIngestionArtifactData()
        ingestion_artifact_dict = artifact_storage.get_ingestion_artifact()
        print(ingestion_artifact_dict)

        training_pipeline_config = TrainingPipelineConfig()
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        
        data_validation = DataValidation(data_ingestion_artifact=ingestion_artifact_dict, 
                                         data_validation_config=data_validation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        print("Data Validation Completed:", data_validation_artifact.to_dict())

    except Exception as e:
        raise AMLException(e, sys)


