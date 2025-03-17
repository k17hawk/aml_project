from src.file_insertion.insert import DataInserter
from src.DB import DatabaseConnector
from src.constants import *


db_connector = DatabaseConnector(SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD)
db_connector.connect()

# Initialize DataInserter
data_inserter = DataInserter(db_connector, TABLE_NAME)
data_inserter.ensure_table_exists()
data_inserter.insert_data_from_csv()

db_connector.close_connection()
