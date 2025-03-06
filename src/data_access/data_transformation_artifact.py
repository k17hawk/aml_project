from src.config import mongo_client 
from src.entity.artifcat_entity import DataTransformationArtifact


class DataTransformationArtifactData:

    def __init__(self):
        self.client = mongo_client
        self.database_name = "AML_artifact"
        self.collection_name = "data-transformation"
        self.collection = self.client[self.database_name][self.collection_name]

    def save_transformation_artifact(self, data_transformation_artifact: DataTransformationArtifact):
        self.collection.insert_one(data_transformation_artifact.to_dict())

    def get_transformation_artifact(self, query):
        self.collection.find_one(query)