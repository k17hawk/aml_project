from src.entity.artifcat_entity import ModelEvaluationArtifact, DataValidationArtifact, ModelTrainerArtifact
from src.entity.config_entity import ModelEvaluationConfig, TrainingPipelineConfig
from src.component.model_evaluation import ModelEvaluation
from src.exception import AMLException
import sys
from src.data_access.data_validation_artifact import DataValidationArtifactData
from src.data_access.model_trainer_artifact import ModelTrainerArtifactData

if __name__ == "__main__":
    try:
        artifact_storage = DataValidationArtifactData()
        validation_artifact_dict = artifact_storage.get_valid_artifact()
        
        model_storage = ModelTrainerArtifactData()
        model_trainer_artifact_dict = model_storage.get_trainer_artifact()
        print(model_trainer_artifact_dict)
        print(type(model_trainer_artifact_dict)) 
    
        training_pipeline_config = TrainingPipelineConfig()
        model_eval_config = ModelEvaluationConfig(training_pipeline_config=training_pipeline_config)
        model_eval = ModelEvaluation(data_validation_artifact=validation_artifact_dict, 
                                     model_trainer_artifact=model_trainer_artifact_dict, 
                                     model_eval_config=model_eval_config)
        model_eval_artifact = model_eval.initiate_model_evaluation()

        print("Model Evaluation Completed:", model_eval_artifact)
    except Exception as e:
        raise AMLException(e, sys)
