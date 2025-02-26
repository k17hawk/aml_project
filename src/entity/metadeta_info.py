from exception import AMLException
from src.logger import logging
from src.utils import read_yaml_file,write_yaml_file
from collections import namedtuple
import os,sys
DataIngestionMetadataInfo = namedtuple("DataIngestionMetadataInfo", ["fetch_date","file_path"])

class DataIngestionMetadata:

    
    def __init__(self, metadata_file_path):
        self.metadata_file_path = metadata_file_path
    
        
    @property
    def is_metadata_file_present(self)->bool:
        #checking either file path exist or not
        return os.path.exists(self.metadata_file_path)

    def write_metadata_info(self, fetch_date: str,file_path:str):
        try:
            metadata_info = DataIngestionMetadataInfo(
                fetch_date=fetch_date,
                file_path= file_path
            )
            write_yaml_file(file_path=self.metadata_file_path, data=metadata_info._asdict())

        except Exception as e:
            raise AMLException(e, sys)

    def get_metadata_info(self) -> DataIngestionMetadataInfo:
        try:
            if not self.is_metadata_file_present:
                logging.warning("No metadata file available.")
                return None
            metadata = read_yaml_file(self.metadata_file_path)
            metadata_info = DataIngestionMetadataInfo(**(metadata))
            logging.info(f"Loaded metadata: {metadata}")
            return metadata_info
        except Exception as e:
            raise AMLException(e, sys)