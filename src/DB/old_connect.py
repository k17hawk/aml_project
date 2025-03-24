import pyodbc

class DatabaseConnector:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        """Establishes a connection to the SQL Server database, creating it if it doesn't exist."""
        try:
            master_conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.server};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'Encrypt=Optional;' 
                f'TrustServerCertificate=Yes;'
            )
   
            cursor = master_conn.cursor()
            master_conn.autocommit = True
            print("Connected to SQL Server...")

            # Check if the database exists
            cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{self.database}'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"CREATE DATABASE {self.database}")
                master_conn.commit()
                print(f"Database '{self.database}' created successfully.")

            cursor.close()
            master_conn.close()
            
            # Connect to the specific database
            self.connection = pyodbc.connect(
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'Encrypt=Optional;'
                f'TrustServerCertificate=Yes;'
            )
            print(f"Connected to the database '{self.database}' successfully.")

        except pyodbc.Error as e:
            print(f"Error connecting to the database: {e}")