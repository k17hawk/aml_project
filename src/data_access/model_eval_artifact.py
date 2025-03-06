from src.config import mongo_client 
from src.entity.artifcat_entity import ModelEvaluationArtifact

class ModelEvaluationArtifactData:

    def __init__(self):
        self.client = mongo_client
        self.database_name = "AML_artifact"
        self.collection_name = "evaluation"
        self.collection = self.client[self.database_name][self.collection_name]

    def save_eval_artifact(self, model_eval_artifact: ModelEvaluationArtifact):
        self.collection.insert_one(model_eval_artifact.to_dict())

    # def get_eval_artifact(self, query):
    #     self.collection.find_one(query)
    
    def get_eval_artifact(self, query={}):
        """Retrieve the latest ModelEvaluationArtifact from MongoDB"""
        artifact_data = self.collection.find_one(query, sort=[("_id", -1)])  
    
        if artifact_data:
            artifact_data.pop("_id", None)  
            return ModelEvaluationArtifact(**artifact_data)  
        else:
            raise Exception("No model eval artifact found in MongoDB!")