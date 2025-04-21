import os
import sys
from collections import namedtuple
from typing import List, Dict

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from src.entity.artifcat_entity import DataIngestionArtifact
from src.entity.config_entity import DataValidationConfig
from src.entity.schema import TransactionDataSchema
from src.exception import AMLException
from src.logger import  logger

from pyspark.sql.functions import lit
from src.entity.artifcat_entity import DataValidationArtifact
from src.data_access.data_validation_artifact import DataValidationArtifactData

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

ERROR_MESSAGE = "error_msg"
MissingReport = namedtuple("MissingReport", ["total_row", "missing_row", "missing_percentage"])


class DataValidation():

    def __init__(self,
                 data_validation_config: DataValidationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 schema=TransactionDataSchema()
                ):
        try:
            logger.info(f"{'>>' * 20}Starting data validation.{'<<' * 20}")
            self.data_validation_artifact_data = DataValidationArtifactData()
            self.data_ingestion_artifact: DataIngestionArtifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema = schema
        except Exception as e:
            raise AMLException(e, sys) from e

    def read_data(self) -> DataFrame:
        try:
            dataframe: DataFrame = spark_session.read.parquet(
                self.data_ingestion_artifact.feature_store_file_path,header=True
            )
            
            logger.info(f"Data frame is created using file: {self.data_ingestion_artifact.feature_store_file_path}")
            # logger.info(f"Number of row: {dataframe.count()} and column: {len(dataframe.columns)}")
            return dataframe
        except Exception as e:
            raise AMLException(e, sys)
    


    @staticmethod
    def get_missing_report(dataframe: DataFrame, ) -> Dict[str, MissingReport]:
        try:
            missing_report: Dict[str:MissingReport] = dict()
            logger.info(f"Preparing missing reports for each column")
            number_of_row = dataframe.count()

            for column in dataframe.columns:
                missing_row = dataframe.filter(f"{column} is null").count()
                missing_percentage = (missing_row * 100) / number_of_row
                missing_report[column] = MissingReport(total_row=number_of_row,
                                                       missing_row=missing_row,
                                                       missing_percentage=missing_percentage
                                                       )
            logger.info(f"Missing report prepared: {missing_report}")
            return missing_report

        except Exception as e:
            raise AMLException(e, sys)
    


    def get_unwanted_and_high_missing_value_columns(self, dataframe: DataFrame, threshold: float = 0.2) -> List[str]:
        try:
            missing_report: Dict[str, MissingReport] = self.get_missing_report(dataframe=dataframe)

            unwanted_column: List[str] = self.schema.unwanted_columns
            for column in missing_report:
                if missing_report[column].missing_percentage > (threshold * 100):
                    unwanted_column.append(column)
                    logger.info(f"Missing report {column}: [{missing_report[column]}]")
            unwanted_column = list(set(unwanted_column))
            return unwanted_column

        except Exception as e:
            raise AMLException(e, sys)

    def drop_unwanted_columns(self, dataframe: DataFrame) -> DataFrame:
        try:
            unwanted_columns: List = self.get_unwanted_and_high_missing_value_columns(dataframe=dataframe, )
            logger.info(f"Dropping feature: {','.join(unwanted_columns)}")
            unwanted_dataframe: DataFrame = dataframe.select(unwanted_columns)

            unwanted_dataframe = unwanted_dataframe.withColumn(ERROR_MESSAGE, lit("Contains many missing values"))


            rejected_dir = os.path.join(self.data_validation_config.rejected_data_dir, "missing_data")
            os.makedirs(rejected_dir, exist_ok=True)
            file_path = os.path.join(rejected_dir, self.data_validation_config.file_name)

            logger.info(f"Writing dropped column into file: [{file_path}]")
            unwanted_dataframe.write.mode("append").parquet(file_path)
            dataframe: DataFrame = dataframe.drop(*unwanted_columns)
            logger.info(f"Remaining number of columns: [{dataframe.columns}]")
            return dataframe
        except Exception as e:
            raise AMLException(e, sys)

    def is_required_columns_exist(self, dataframe: DataFrame):
        try:
            if not isinstance(dataframe, DataFrame):
                raise ValueError("Expected a DataFrame but got a dictionary or other type.")
            
            logger.info(f"required columns {self.schema.required_columns}")
            missing_columns = set(self.schema.required_columns) - set(dataframe.columns)

            if missing_columns:
                raise Exception(f"Required column(s) missing:\n"
                                f"Expected columns: {self.schema.required_columns}\n"
                                f"Missing columns: {missing_columns}")

        except Exception as e:
            raise AMLException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            
            logger.info(f"Initiating data preprocessing.")
            dataframe: DataFrame = self.read_data()

            logger.info(f"get missing  columns")
            missing_report = self.get_missing_report(dataframe=dataframe)

            # validation to ensure that all require column available
            self.is_required_columns_exist(dataframe=dataframe)
            logger.info("Saving preprocessed data.")
            # print(f"Row: [{dataframe.count()}] Column: [{len(dataframe.columns)}]")
            print(f"Expected Column: {self.schema.required_columns}\nPresent Columns: {dataframe.columns}")
            os.makedirs(self.data_validation_config.accepted_data_dir, exist_ok=True)
            accepted_file_path = os.path.join(self.data_validation_config.accepted_data_dir,
                                              self.data_validation_config.file_name
                                              )
            dataframe.write.parquet(accepted_file_path)
            artifact = DataValidationArtifact(accepted_file_path=accepted_file_path,
                                              rejected_dir=self.data_validation_config.rejected_data_dir
                                              )
            
            logger.info(f"Data validation artifact: [{artifact}]")
            logger.info(f"{'>>' * 20} Data Validation completed.{'<<' * 20}")
            # artifact = DataValidationArtifact(
            #     accepted_file_path=r"C:\Users\lang-chain\Documents\aml_project\artifact\data_validation\20250317_202947\accepted_data\aml_prediction",
            #     rejected_dir=r"C:\Users\lang-chain\Documents\aml_project\artifact\data_ingestion"
            # )
            self.data_validation_artifact_data.save_validation_artifact(data_valid_artifact=artifact)
            spark_session.stop()
            return artifact
        except Exception as e:
            raise AMLException(e, sys)