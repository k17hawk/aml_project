from src.config import mongo_client 
from src.entity.artifcat_entity import ModelPusherArtifact

class ModelPusherArtifactData:

    def __init__(self):
        self.client = mongo_client
        self.database_name = "AML_artifact"
        self.collection_name = "model_pusher"
        self.collection = self.client[self.database_name][self.collection_name]

    def save_pusher_artifact(self, model_pusher_artifact: ModelPusherArtifact):
        self.collection.insert_one(model_pusher_artifact.to_dict())

    def get_pusher_artifact(self, query):
        self.collection.find_one(query)