# from src import SQL_SERVER, SQL_DATABASE, TABLE_NAME,SQL_USERNAME,SQL_PASSWORD
# import logging
# import pendulum
# from airflow.decorators import dag, task
# from airflow.utils.dates import days_ago
# from src import DatabaseConnector
# from src import DataInserter

# import logging

# # Set up logging
# logger = logging.getLogger(__name__)

# @dag(
#     schedule_interval="0 */6 * * *",  
#     start_date=pendulum.datetime(2023, 10, 1, tz="UTC"), 
#     catchup=False,  
#     tags=['database_insertion'],
# )
# def database_insertion_dag():
#     """
#     ### Database Insertion DAG
#     This DAG connects to SQL Server, ensures the table exists, and inserts data from a CSV file.
#     """

#     @task()
#     def connect_to_database():
#         """Connect to the SQL Server database."""
#         try:
#             logger.info("Connecting to the database...")
#             db_connector = DatabaseConnector(SQL_SERVER, SQL_DATABASE,SQL_USERNAME,SQL_PASSWORD)
#             db_connector.connect()
#             return db_connector
#         except Exception as e:
#             logger.error(f"Failed to connect to the database: {e}")
#             raise

#     @task()
#     def ensure_table_exists(db_connector):
#         """Ensure the table exists in the database."""
#         try:
#             logger.info("Ensuring the table exists...")
#             data_inserter = DataInserter(db_connector, TABLE_NAME)
#             data_inserter.ensure_table_exists()
#             return db_connector
#         except Exception as e:
#             logger.error(f"Failed to ensure table exists: {e}")
#             raise

#     @task()
#     def insert_data_from_csv(db_connector):
#         """Insert data from CSV into the database."""
#         try:
#             logger.info("Inserting data from CSV...")
#             data_inserter = DataInserter(db_connector, TABLE_NAME)
#             data_inserter.insert_data_from_csv()
#         except Exception as e:
#             logger.error(f"Failed to insert data from CSV: {e}")
#             raise
#         finally:
#             logger.info("Closing the database connection...")
#             db_connector.close_connection()

#     db_connector = connect_to_database()
#     table_exists = ensure_table_exists(db_connector)
#     insert_data = insert_data_from_csv(table_exists)

# # Instantiate the DAG
# database_insertion_dag = database_insertion_dag()