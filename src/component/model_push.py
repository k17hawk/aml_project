from src.exception import AMLException
# from src.config.spark_manager import spark_session
import sys
from src.logger import logging as  logger
from src.entity.config_entity import ModelPusherConfig
from src.entity.artifcat_entity import ModelPusherArtifact, ModelTrainerArtifact
from src.ml.estimator import ModelResolver
from pyspark.ml.pipeline import PipelineModel
import os
from src.data_access.model_push_artifact import ModelPusherArtifactData
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "spark_manager", 
    Path("/app/config/spark_manager.py")
)
spark_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spark_manager)
spark_session = spark_manager.SparkManager.get_spark_session()
class ModelPusher:

    def __init__(self, model_trainer_artifact: ModelTrainerArtifact, model_pusher_config: ModelPusherConfig):
        logger.info(f"{'>>' * 20}Starting Model pusher.{'<<' * 20}")
        self.model_trainer_artifact = model_trainer_artifact
        self.model_pusher_artifact_data = ModelPusherArtifactData()
        self.model_pusher_config = model_pusher_config
        self.model_resolver = ModelResolver(model_dir=self.model_pusher_config.saved_model_dir)

    def push_model(self) -> str:
        try:
            trained_model_path=self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path
            saved_model_path = self.model_resolver.get_save_model_path
            model = PipelineModel.load(trained_model_path)
            model.save(saved_model_path)
            model.save(self.model_pusher_config.pusher_model_dir)
            return saved_model_path
        except Exception as e:
            raise AMLException(e, sys)
    

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            saved_model_path = self.push_model()
            model_pusher_artifact = ModelPusherArtifact(model_pushed_dir=self.model_pusher_config.pusher_model_dir,
                                    saved_model_dir=saved_model_path)
            self.model_pusher_artifact_data.save_pusher_artifact(model_pusher_artifact = model_pusher_artifact)
            logger.info(f"Model pusher artifact: {model_pusher_artifact}")
            logger.info(f"{'>>' * 20} Model pusher completed.{'<<' * 20}")
            return model_pusher_artifact
        except Exception as e:
            raise AMLException(e, sys)
        finally:
            logger.info("Stopping Spark Session...")
            spark_session.stop() 