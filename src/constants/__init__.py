from pathlib import Path

# SQL_SERVER = r"DESKTOP-JSV1UOD\USER_ROOT"
SQL_SERVER = "192.168.X.XX,1433" 
SQL_DATABASE = "master_3"
SQL_USERNAME = "newuser"  
SQL_PASSWORD = "toor"  
TABLE_NAME = 'Transactions'

BUCKET_NAME = 'abc_aml_data_bucket'
GCS_FILE_NAME = 'aml_input_data.csv'


import os
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("C:/Users/lang-chain/Documents/aml_project/datastorage.json"))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("datastorage.json"))