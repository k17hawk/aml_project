from src.entity.artifcat_entity import (ModelEvaluationArtifact, DataValidationArtifact,
    ModelTrainerArtifact)
from src.entity.config_entity import ModelEvaluationConfig
from src.entity.schema import TransactionDataSchema
from src.exception import AMLException
from src.logger import logger
import sys
from pyspark.sql import DataFrame
from pyspark.ml.feature import StringIndexerModel
from pyspark.ml.pipeline import PipelineModel
# from src.config.spark_manager import spark_session
from src.utils import get_score
from src.ml.estimator import  ModelResolver,AMLIdntifierEstimator
from src.data_access.model_eval_artifact import ModelEvaluationArtifactData
from pathlib import Path
import importlib.util
from src.config.spark_manager import SparkManager
spark_session = SparkManager.get_spark_session()
# spec = importlib.util.spec_from_file_location(
#     "spark_manager", 
#     Path("/app/config/spark_manager.py")
# )
# spark_manager = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(spark_manager)
# spark_session = spark_manager.SparkManager.get_spark_session()
class ModelEvaluation:

    def __init__(self,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact,
                 model_eval_config: ModelEvaluationConfig,
                 schema=TransactionDataSchema()
                 ):
        try:
            logger.info(f"{'>>' * 20}Starting Model Validation..{'<<' * 20}")
            self.model_eval_artifact_data = ModelEvaluationArtifactData()
            self.data_validation_artifact = data_validation_artifact
            self.model_eval_config = model_eval_config
            self.model_trainer_artifact = model_trainer_artifact
            self.schema = schema
            self.model_resolver = ModelResolver()
            self.aml_identifier = AMLIdntifierEstimator()
        except Exception as e:
            raise AMLException(e, sys)

    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_validation_artifact.accepted_file_path
            dataframe: DataFrame = spark_session.read.parquet(file_path)
            return dataframe
        except Exception as e:
            # Raising an exception.
            raise AMLException(e, sys)


    def evaluate_trained_model(self) -> ModelEvaluationArtifact:
        try:
            if not self.model_resolver.is_model_present:
                model_evaluation_artifact = ModelEvaluationArtifact(
                    model_accepted=True,
                    changed_accuracy= None,
                    trained_model_path = self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path,
                    best_model_path = None,
                    active=True
                )
                print(f"Model is  accepted run first{model_evaluation_artifact}")
                return  model_evaluation_artifact
                

            #set initial flag
            is_model_accepted, is_active = False, False

            #obtain required directory path
            trained_model_file_path = self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path
            label_indexer_model_path = self.model_trainer_artifact.model_trainer_ref_artifact.label_indexer_model_file_path

            #load required model and label index
            label_indexer_model = StringIndexerModel.load(label_indexer_model_path)
            print(label_indexer_model)
            trained_model = PipelineModel.load(trained_model_file_path)
            # print(trained_model)

            #Read the dataframe
            dataframe: DataFrame = self.read_data()
            # print(dataframe.show())

            dataframe = label_indexer_model.transform(dataframe)

            best_model_path = self.model_resolver.get_best_model_path()
            # print(best_model_dataframe)

            best_model_dataframe = self.aml_identifier.transform(dataframe)

            #prediction using trained model
            trained_model_dataframe = trained_model.transform(dataframe)

            #compute f1 score for trained model
            trained_model_f1_score = get_score(dataframe=trained_model_dataframe, metric_name="f1",
                                            label_col=self.schema.target_indexed_label,
                                            prediction_col=self.schema.prediction_column_name)
            #compute f1 score for best model
            best_model_f1_score = get_score(dataframe=best_model_dataframe, metric_name="f1",
                                            label_col=self.schema.target_indexed_label,
                                            prediction_col=self.schema.prediction_column_name)

            logger.info(f"Trained_model_f1_score: {trained_model_f1_score}, Best model f1 score: {best_model_f1_score}")
            #improved accuracy
            changed_accuracy = trained_model_f1_score - best_model_f1_score
            print(f"the changed in accuracy is:{changed_accuracy}")
            print(f"the threshold is self.model_eval_config.threshold ")

            
            if changed_accuracy >= self.model_eval_config.threshold:
                is_model_accepted, is_active = True, True
            model_evaluation_artifact = ModelEvaluationArtifact(model_accepted=is_model_accepted,
                                                                changed_accuracy=changed_accuracy,
                                                                trained_model_path=trained_model_file_path,
                                                                best_model_path=best_model_path,
                                                                active=is_active
                                                                )
            return model_evaluation_artifact
        except Exception as e:
            raise AMLException(e,sys)

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            logger.info(f"{'>>' * 20}Starting model Evaluation.{'<<' * 20}")
            model_accepted = True
            is_active = True
            model_evaluation_artifact = self.evaluate_trained_model()
            logger.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            self.model_eval_artifact_data.save_eval_artifact(model_eval_artifact=model_evaluation_artifact)
            logger.info(f"{'>>' * 20}model Evaluation completed...{'<<' * 20}")
            spark_session.stop()
            return model_evaluation_artifact
        except Exception as e:
            raise AMLException(e, sys)