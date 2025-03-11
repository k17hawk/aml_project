from src.entity.artifcat_entity import DataTransformationArtifact, DataValidationArtifact
from src.entity.config_entity import DataTransformationConfig, TrainingPipelineConfig
from src.component.data_transformation import DataTransformation
from src.exception import AMLException
import sys
from src.data_access.data_validation_artifact import DataValidationArtifactData

if __name__ == "__main__":
    try:
        # Fetch the latest Data Validation artifact
        artifact_storage = DataValidationArtifactData()
        validation_artifact_dict = artifact_storage.get_valid_artifact()

        training_pipeline_config = TrainingPipelineConfig()
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)

        data_transformation = DataTransformation(data_validation_artifact=validation_artifact_dict, 
                                                 data_transformation_config=data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print("Data Transformation Completed:", data_transformation_artifact.to_dict())

    except Exception as e:
        raise AMLException(e, sys)
