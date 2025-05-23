from dataclasses import dataclass,asdict
from datetime import datetime

@dataclass
class DataIngestionArtifact:
    feature_store_file_path:str
    metadata_file_path:str
    download_dir:str

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return str(self.to_dict())
    

@dataclass
class DataValidationArtifact:
    accepted_file_path:str
    rejected_dir:str

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return str(self.to_dict())

@dataclass
class DataTransformationArtifact:
    transformed_train_file_path:str
    exported_pipeline_file_path:str
    transformed_test_file_path:str

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return str(self.to_dict())

@dataclass
class PartialModelTrainerMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float

    def to_dict(self):
        return self.__dict__



@dataclass
class PartialModelTrainerRefArtifact:
    trained_model_file_path:str
    label_indexer_model_file_path:str

    def to_dict(self):
        return self.__dict__


class ModelTrainerArtifact:

    def __init__(self, model_trainer_ref_artifact: PartialModelTrainerRefArtifact,
                 model_trainer_train_metric_artifact: PartialModelTrainerMetricArtifact,
                 model_trainer_test_metric_artifact: PartialModelTrainerMetricArtifact
                 ):
        self.model_trainer_ref_artifact = model_trainer_ref_artifact
        self.model_trainer_train_metric_artifact = model_trainer_train_metric_artifact
        self.model_trainer_test_metric_artifact = model_trainer_test_metric_artifact



    def to_dict(self):
        return {
            "model_trainer_ref_artifact": self.model_trainer_ref_artifact.to_dict(),
            "model_trainer_train_metric_artifact": self.model_trainer_train_metric_artifact.to_dict(),
            "model_trainer_test_metric_artifact": self.model_trainer_test_metric_artifact.to_dict()
        }
    
    def __str__(self):
        return str(self.to_dict())
    
    @staticmethod
    def construct_object(**kwargs):
        """Convert dictionary from MongoDB into ModelTrainerArtifact object"""

        def convert_to_object(class_type, value):
            """Helper function to convert dictionary to object if needed"""
            return class_type(**value) if isinstance(value, dict) else value

        # Convert nested dictionaries into objects
        model_trainer_ref_artifact = convert_to_object(PartialModelTrainerRefArtifact, kwargs.get('model_trainer_ref_artifact', {}))
        model_trainer_train_metric_artifact = convert_to_object(PartialModelTrainerMetricArtifact, kwargs.get('model_trainer_train_metric_artifact', {}))
        model_trainer_test_metric_artifact = convert_to_object(PartialModelTrainerMetricArtifact, kwargs.get('model_trainer_test_metric_artifact', {}))

        # Return the actual object
        return ModelTrainerArtifact(
            model_trainer_ref_artifact=model_trainer_ref_artifact,
            model_trainer_train_metric_artifact=model_trainer_train_metric_artifact,
            model_trainer_test_metric_artifact=model_trainer_test_metric_artifact
        )

    
class ModelEvaluationArtifact:

    def __init__(self, model_accepted, changed_accuracy, trained_model_path, best_model_path, active,*args,**kwargs):
        self.model_accepted = model_accepted
        self.changed_accuracy = changed_accuracy
        self.trained_model_path = trained_model_path
        self.best_model_path = best_model_path
        self.active = active
        self.created_timestamp = datetime.now()

    def to_dict(self):
        return  self.__dict__
        

    def __str__(self):
        return str(self.to_dict())

@dataclass
class ModelPusherArtifact:
    model_pushed_dir:str
    saved_model_dir:str
    
    def to_dict(self):
        return  self.__dict__
        

    def __str__(self):
        return str(self.to_dict())
