from src.entity.artifcat_entity import ModelTrainerArtifact
from src.entity.config_entity import ModelPusherConfig, TrainingPipelineConfig
from src.component.model_push import ModelPusher
from src.exception import AMLException
import sys
from src.data_access.model_trainer_artifact import ModelTrainerArtifactData


if __name__ == "__main__":
    try:
       
        model_store = ModelTrainerArtifactData()
        model_trainer_artifact_dict = model_store.get_trainer_artifact()

        training_pipeline_config = TrainingPipelineConfig()
        model_pusher_config = ModelPusherConfig(training_pipeline_config=training_pipeline_config)
        model_pusher = ModelPusher(model_trainer_artifact=model_trainer_artifact_dict, 
                                   model_pusher_config=model_pusher_config)
        model_pusher.initiate_model_pusher()

        print("Model Pusher Completed")
    except Exception as e:
        raise AMLException(e, sys)
