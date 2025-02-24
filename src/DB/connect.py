import pyodbc

class DatabaseConnector:
    def __init__(self, server, database):
        self.server = server
        self.database = database
        self.connection = None

    def connect(self):
        """Establishes a connection to the SQL Server database, creating it if it doesn't exist."""
        try:
            master_conn = pyodbc.connect(
                f'DRIVER={{SQL Server}};'
                f'SERVER={self.server};'
                f'Trusted_Connection=yes;'
                f'Encrypt=Mandatory;'
                f'TrustServerCertificate=Yes;'
            )
            #f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SQL_SERVER};Trusted_Connection=yes;Encrypt=Mandatory;TrustServerCertificate=Yes;"
            cursor = master_conn.cursor()
            master_conn.autocommit = True
            cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{self.database}'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"CREATE DATABASE {self.database}")
                master_conn.commit()
                print(f"Database '{self.database}' created successfully.")
            cursor.close()
            master_conn.close()
            
            self.connection = pyodbc.connect(
                f'DRIVER={{SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
            )
            print("Connected to the database successfully.")
        except pyodbc.Error as e:
            print(f"Error connecting to the database: {e}")

    def close_connection(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

# Usage
SQL_SERVER = r"DESKTOP-JSV1UOD\USER_ROOT"
SQL_DATABASE = "master_2"

db = DatabaseConnector(SQL_SERVER, SQL_DATABASE)
db.connect()
db.close_connection()
