from src.entity.artifcat_entity import ModelTrainerArtifact, DataTransformationArtifact
from src.entity.config_entity import ModelTrainerConfig, TrainingPipelineConfig
from src.component.model_trainer import ModelTrainer
from src.exception import AMLException
import sys
from src.data_access.data_transformation_artifact import DataTransformationArtifactData
if __name__ == "__main__":
    try:

        artifact_storage = DataTransformationArtifactData()
        data_transformation_artifact_dict = artifact_storage.get_transformation_artifact()

        training_pipeline_config = TrainingPipelineConfig()
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=training_pipeline_config)
        model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact_dict, 
                                     model_trainer_config=model_trainer_config)
        model_trainer_artifact = model_trainer.initiate_model_training()

        print("Model Training Completed:", model_trainer_artifact)
    except Exception as e:
        raise AMLException(e, sys)