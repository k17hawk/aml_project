from src.config import mongo_client 
from src.entity.artifcat_entity import DataValidationArtifact

class DataValidationArtifactData:

    def __init__(self):
        self.client = mongo_client
        self.database_name = "AML_artifact"
        self.collection_name = "Data-validation"
        self.collection = self.client[self.database_name][self.collection_name]

    def save_validation_artifact(self, data_valid_artifact: DataValidationArtifact):
        self.collection.insert_one(data_valid_artifact.to_dict())

    # def get_valid_artifact(self, query):
    #     self.collection.find_one(query)
    
    def get_valid_artifact(self, query={}):
        """Retrieve the latest DataValidationArtifact from MongoDB"""
        artifact_data = self.collection.find_one(query, sort=[("_id", -1)]) 
        
        if artifact_data:
            artifact_data.pop("_id", None) 
            return DataValidationArtifact(**artifact_data)  
        else:
            raise Exception("No data validation artifact found in MongoDB!")
    
