from src.entity.metadeta_info import DataIngestionMetadata
from src.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig
from src.exception import AMLException
from src.logger import logger
import os,sys 
import pandas as pd
from src.config.spark_manager import spark_session
import pyodbc
from tqdm import tqdm
from src.entity.artifcat_entity import DataIngestionArtifact
from src.data_access.data_ingestion_artifact import DataIngestionArtifactData
class DataIngestion:

        # Used to download data in chunks.
    def __init__(self, data_ingestion_config: DataIngestionConfig ):
        """
        data_ingestion_config: Data Ingestion config
        """
        try:
            logger.info(f"{'>>' * 20}Starting data ingestion.{'<<' * 20}")
            self.data_ingestion_config = data_ingestion_config
            self.data_ingestion_artifact_data = DataIngestionArtifactData()

        except Exception as e:
            raise AMLException(e, sys)
    
    def connect(self,server,database,username,password):
        """Establishes a connection to the SQL Server database, creating it if it doesn't exist."""
        try:
           
            self.connection = pyodbc.connect(
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
                f'Encrypt=Optional;'
                f'TrustServerCertificate=Yes;'
            )
            logger.info(f"Connected to the database '{database}' successfully.")
            return self.connection

        except pyodbc.Error as e:
            logger.info(f"Error connecting to the database: {e}")

    def fetch_data(self, table, connection, storePath, chunksize=1000):
        query = f"SELECT * FROM {table}" 
        os.makedirs(storePath,exist_ok=True)
        file_path = os.path.join(storePath, f"{table}.csv")
        first_chunk = True 
        total_rows_query = f"SELECT COUNT(*) FROM {table}"
        logger.info('reading the data...')
        total_rows = pd.read_sql(total_rows_query, connection).iloc[0, 0]
        with tqdm(total=total_rows, desc="Fetching Data", unit="rows") as pbar:
            for chunk in pd.read_sql(query, connection, chunksize=chunksize):
                chunk.to_csv(file_path, mode='w' if first_chunk else 'a', header=first_chunk, index=False)
                first_chunk = False  
                pbar.update(len(chunk))  
        logger.info(f"writing to csv completed at {file_path}")
        return file_path
    
    def write_metadata(self, file_path: str) -> None:
        """
        This function help us to update metadata information 
        so that we can avoid redundant download and merging.

        """
        try:
            logger.info(f"Writing metadata info into metadata file...")
            metadata_info = DataIngestionMetadata(metadata_file_path=self.data_ingestion_config.metadata_file_path)

            metadata_info.write_metadata_info(fetch_date=self.data_ingestion_config.date_fetch,
                                              file_path=file_path
                                              )
            logger.info(f"Metadata has been written.")
        except Exception as e:
            raise AMLException(e, sys)
        
    def convert_files_to_parquet(self,fetched_file_path ) -> str:
        try:
            logger.info(f"converting file into parquet...")
            data_dir = self.data_ingestion_config.feature_store_dir
            output_file_name = f"{self.data_ingestion_config.file_name}"
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, output_file_name)

            logger.info(f"Parquet file will be created at: {file_path}")

            df = spark_session.read.csv(fetched_file_path, header=True, inferSchema=True,multiLine=True)
            if df.count() > 0:
                df.write.mode("overwrite").parquet(file_path)
                logger.info("Conversion to Parquet completed successfully.")

            return file_path
        except Exception as e:
            raise AMLException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            datasource_url: str = self.data_ingestion_config.datasource_url
            datasource_database: str = self.data_ingestion_config.database
            datasource_username: str = self.data_ingestion_config.username
            datasource_password: str = self.data_ingestion_config.password
            datasource_tableName: str = self.data_ingestion_config.table
            datasource_storePath: str = self.data_ingestion_config.download_dir

            connection = self.connect(datasource_url, datasource_database, datasource_username, datasource_password)
            try:
                fetched_file_path = self.fetch_data(datasource_tableName, connection, datasource_storePath)
                logger.info(f"Data ingestion completed successfully.{fetched_file_path}")
            except Exception as e:
                raise AMLException(e, sys)
            file_path = self.convert_files_to_parquet(fetched_file_path)
            self.write_metadata(file_path)
            feature_store_file_path = os.path.join(self.data_ingestion_config.feature_store_dir,
                                                    self.data_ingestion_config.file_name)
            artifact = DataIngestionArtifact(
                    feature_store_file_path=feature_store_file_path,
                    download_dir=self.data_ingestion_config.download_dir,
                    metadata_file_path=self.data_ingestion_config.metadata_file_path,

                )
            self.data_ingestion_artifact_data.save_ingestion_artifact(data_ingestion_artifact=artifact)
            # artifact = DataIngestionArtifact(
            #     feature_store_file_path=r"C:\Users\lang-chain\Documents\aml_project\artifact\data_ingestion\feature_store\Transaction",
            #     metadata_file_path=r"C:\Users\lang-chain\Documents\aml_project\artifact\data_ingestion",
            #     download_dir=r"C:\Users\lang-chain\Documents\aml_project\artifact\data_ingestion\20250301_104259\downloaded_files"
            # )
            logger.info(f"{'>>' * 20}Data Ingestion completed.{'<<' * 20}")
            logger.info(f"Data ingestion artifact: {artifact}")
            return artifact
        except Exception as e:
            raise AMLException(e, sys)


    


