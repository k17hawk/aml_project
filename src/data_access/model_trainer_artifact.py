from src.config import mongo_client 
from src.entity.artifcat_entity import ModelTrainerArtifact

class ModelTrainerArtifactData:

    def __init__(self):
        self.client = mongo_client
        self.database_name = "AML_artifact"
        self.collection_name = "model_trainer"
        self.collection = self.client[self.database_name][self.collection_name]

    def save_model_artifact(self, model_trainer_artifact: ModelTrainerArtifact):
        self.collection.insert_one(model_trainer_artifact.to_dict())

    # def get_model_artifact(self, query):
    #     self.collection.find_one(query)
    
    def get_trainer_artifact(self, query={}):
        """Retrieve the latest ModelTrainerArtifact from MongoDB"""
        artifact_data = self.collection.find_one(query, sort=[("_id", -1)])

        if artifact_data:
            artifact_data.pop("_id", None) 
            return ModelTrainerArtifact.construct_object(**artifact_data)  
        else:
            raise Exception("No model trainer artifact found in MongoDB!")

        
        
