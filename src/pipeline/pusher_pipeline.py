from src.entity.artifcat_entity import ModelTrainerArtifact
from src.entity.config_entity import ModelPusherConfig, TrainingPipelineConfig
from src.component.model_push import ModelPusher
from src.exception import AMLException
import sys
from src.data_access.model_trainer_artifact import ModelTrainerArtifactData
def run_model_pusher(model_trainer_artifact: ModelTrainerArtifact):
    try:
        training_pipeline_config = TrainingPipelineConfig()
        model_pusher_config = ModelPusherConfig(training_pipeline_config=training_pipeline_config)
        model_pusher = ModelPusher(
            model_trainer_artifact=model_trainer_artifact,
            model_pusher_config=model_pusher_config
        )

        return model_pusher.initiate_model_pusher()

    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    model_trainer_artifact_data = ModelTrainerArtifactData()
    artifact = run_model_pusher(model_trainer_artifact_data.get_model_artifact())
    print(f"Model Push Completed: {artifact}")
