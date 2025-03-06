from src.entity.artifcat_entity import ModelEvaluationArtifact, DataValidationArtifact, ModelTrainerArtifact
from src.entity.config_entity import ModelEvaluationConfig, TrainingPipelineConfig
from src.component.model_evaluation import ModelEvaluation
from src.exception import AMLException
import sys

def run_model_evaluation(data_validation_artifact: DataValidationArtifact, model_trainer_artifact: ModelTrainerArtifact):
    try:
        training_pipeline_config = TrainingPipelineConfig()
        model_eval_config = ModelEvaluationConfig(training_pipeline_config=training_pipeline_config)
        model_eval = ModelEvaluation(
            data_validation_artifact=data_validation_artifact,
            model_trainer_artifact=model_trainer_artifact,
            model_eval_config=model_eval_config
        )

        model_eval_artifact = model_eval.initiate_model_evaluation()
        return model_eval_artifact  

    except Exception as e:
        raise AMLException(e, sys)

if __name__ == "__main__":
    data_validation_artifact = load_data_validation_artifact()  # Implement this function
    model_trainer_artifact = load_model_trainer_artifact()  # Implement this function
    artifact = run_model_evaluation(data_validation_artifact, model_trainer_artifact)
    print(f"Model Evaluation Completed: {artifact}")
