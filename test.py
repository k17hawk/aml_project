from datetime import datetime
from src.entity.artifcat_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig
from src.entity.config_entity import  TrainingPipelineConfig
from src.exception import AMLException
from component.data_ingestion import DataIngestion
import os
from src.pipeline.training import TrainingPipeline

training_pipeline_config = TrainingPipelineConfig()
tr = TrainingPipeline(training_pipeline_config=training_pipeline_config)
tr.start() 