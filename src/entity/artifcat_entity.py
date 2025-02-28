from dataclasses import dataclass,asdict
from datetime import datetime
@dataclass
class DataIngestionArtifact:
    feature_store_file_path:str
    metadata_file_path:str
    download_dir:str
