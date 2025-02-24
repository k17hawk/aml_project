from pathlib import Path

SQL_SERVER = r"DESKTOP-JSV1UOD\USER_ROOT"
SQL_DATABASE = "master_2"
TABLE_NAME = 'Transactions'

BUCKET_NAME = 'abc_aml_data_bucket'
GCS_FILE_NAME = 'aml_input_data.csv'


import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path("C:/Users/lang-chain/Documents/aml_project/datastorage.json"))