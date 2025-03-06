from src.entity.artifcat_entity import DataTransformationArtifact, DataValidationArtifact
from src.entity.config_entity import DataTransformationConfig, TrainingPipelineConfig
from src.component.data_transformation import DataTransformation
from src.exception import AMLException
import sys
from src.data_access.data_validation_artifact import DataValidationArtifactData

def run_data_transformation(data_validation_artifact: DataValidationArtifact):
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config
        )

        data_transformation_artifact = data_transformation.initiate_data_transformation()
        return data_transformation_artifact  

    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    data_validation_artifact_data = DataValidationArtifactData()
    data_validation_artifact =  data_validation_artifact_data.get_valid_artifact()
    artifact = run_data_transformation(data_validation_artifact)
    print(f"Data Transformation Completed: {artifact}")
