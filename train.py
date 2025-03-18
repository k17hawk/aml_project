import gc
from pyspark.sql import SparkSession
from src.entity.artifcat_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact, \
    ModelTrainerArtifact, ModelEvaluationArtifact, ModelPusherArtifact
from src.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, \
    DataTransformationConfig, ModelEvaluationConfig, ModelTrainerConfig, ModelPusherConfig
from src.component.data_ingestion import DataIngestion
from src.component.data_validation import DataValidation
from src.component.data_transformation import DataTransformation
from src.component.model_evaluation import ModelEvaluation
from src.component.model_trainer import ModelTrainer
from src.component.model_push import ModelPusher
from src.data_access.data_ingestion_artifact import DataIngestionArtifactData
from src.data_access.data_validation_artifact import DataValidationArtifactData
from src.data_access.data_transformation_artifact import DataTransformationArtifactData
from src.data_access.model_trainer_artifact import ModelTrainerArtifactData
from src.data_access.model_eval_artifact import ModelEvaluationArtifactData
from src.data_access.model_push_artifact import ModelPusherArtifactData
from src.exception import AMLException
import sys


def run_data_ingestion():
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        del data_ingestion
        gc.collect()
        return data_ingestion_artifact
    except Exception as e:
        raise AMLException(e, sys)


def run_data_validation():
    try:
        data_ingestion_artifact = DataIngestionArtifactData().get_ingestion_artifact()
        training_pipeline_config = TrainingPipelineConfig()
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        del data_validation, data_ingestion_artifact
        gc.collect()
        return data_validation_artifact
    except Exception as e:
        raise AMLException(e, sys)

def run_data_transformation():
    try:
        data_validation_artifact = DataValidationArtifactData().get_valid_artifact()
        training_pipeline_config = TrainingPipelineConfig()
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        del data_transformation, data_validation_artifact
        gc.collect()
        return data_transformation_artifact
    except Exception as e:
        raise AMLException(e, sys)

def run_model_training():
    try:
        data_transformation_artifact = DataTransformationArtifactData().get_transformation_artifact()
        training_pipeline_config = TrainingPipelineConfig()
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=training_pipeline_config)
        model_trainer = ModelTrainer(data_transformation_artifact, model_trainer_config)
        model_trainer_artifact = model_trainer.initiate_model_training()
        del model_trainer, data_transformation_artifact
        gc.collect()
        return model_trainer_artifact
    except Exception as e:
        raise AMLException(e, sys)

def run_model_evaluation():
    try:
        data_validation_artifact = DataValidationArtifactData().get_valid_artifact()
        model_trainer_artifact = ModelTrainerArtifactData().get_trainer_artifact()
        training_pipeline_config = TrainingPipelineConfig()
        model_eval_config = ModelEvaluationConfig(training_pipeline_config=training_pipeline_config)
        model_eval = ModelEvaluation(data_validation_artifact, model_trainer_artifact, model_eval_config)
        model_eval_artifact = model_eval.initiate_model_evaluation()
        del model_eval, data_validation_artifact, model_trainer_artifact
        gc.collect()
        return model_eval_artifact
    except Exception as e:
        raise AMLException(e, sys)

def run_model_pusher():
    try:
        model_trainer_artifact = ModelTrainerArtifactData().get_trainer_artifact()
        training_pipeline_config = TrainingPipelineConfig()
        model_pusher_config = ModelPusherConfig(training_pipeline_config=training_pipeline_config)
        model_pusher = ModelPusher(model_trainer_artifact, model_pusher_config)
        model_pusher_artifact = model_pusher.initiate_model_pusher()
        del model_pusher, model_trainer_artifact
        gc.collect()
        return model_pusher_artifact
    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    artifact = run_data_ingestion()
    artifact = run_data_validation()
    artifact = run_data_transformation()
    artifact = run_model_training()
    artifact = run_model_evaluation()
    artifact = run_model_pusher()
