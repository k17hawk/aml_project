import time
import pyodbc
from functools import wraps
from src.logger import logger

def retry_on_connection_error(max_retries=3, delay=5):
    """Decorator to retry a function on connection errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except pyodbc.OperationalError as e:
                    if '08S01' in str(e) or '10054' in str(e):  # TCP connection errors
                        retries += 1
                        print(f"Connection failed (attempt {retries}/{max_retries}): {e}")
                        if retries < max_retries:
                            logger.info(f"Retrying in {delay} seconds...")
                            time.sleep(delay)
                        continue
                    raise  # Re-raise if not a connection error
            raise pyodbc.OperationalError(f"Failed after {max_retries} retries")
        return wrapper
    return decorator

class DatabaseConnector:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None

    def get_connection_string(self, database=None):
        """Helper to generate connection strings"""
        db = database or self.database
        return (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={db};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=Optional;'
            f'TrustServerCertificate=Yes;'
            f'Connection Timeout=30;'  
        )

    @retry_on_connection_error(max_retries=3, delay=5)
    def connect(self):
        """Establishes a connection with retry logic for transient errors"""
        try:
            # Connect to master to check/create database
            master_conn = pyodbc.connect(self.get_connection_string("master"))
            master_conn.autocommit = True
            
            with master_conn.cursor() as cursor:
                # Check if database exists
                cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{self.database}'")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"CREATE DATABASE {self.database}")
                    logger.info(f"Database '{self.database}' created successfully.")

            # Connect to our target database
            self.connection = pyodbc.connect(self.get_connection_string())
            logger.info(f"Connected to '{self.database}' successfully")
            return self.connection

        except pyodbc.Error as e:
            logger.info(f"Critical database error: {str(e)}")
            raise
    def close_connection(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")
   

# # Usage
# SQL_SERVER = "***.***.*.**,1433"  
# SQL_DATABASE = "master_2"
# SQL_USERNAME = "newuser"  
# SQL_PASSWORD = "toor"  #

# db = DatabaseConnector(SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD)
# db.connect()
# db.close_connection()
