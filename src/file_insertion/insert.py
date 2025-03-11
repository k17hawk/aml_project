from DB import DatabaseConnector
from constants import *
import pandas as pd
import pyodbc
import os
from google.cloud import storage
from io import StringIO

class DataInserter:
    def __init__(self,db_connector,table_name):
        self.conn = db_connector
        self.database = SQL_DATABASE
        self.server = SQL_SERVER
        self.table = table_name
    
    def ensure_table_exists(self):
        """Creates the table if it doesn't already exist."""
        create_table_query = f"""
            IF OBJECT_ID('{self.table}', 'U') IS NULL
            CREATE TABLE {self.table} (
                Time VARCHAR(255),
                Date VARCHAR(255),
                Sender_account BIGINT,
                Receiver_account BIGINT,
                Amount DECIMAL(18, 2),
                Payment_currency VARCHAR(500),
                Received_currency VARCHAR(255),
                Sender_bank_location VARCHAR(255),
                Receiver_bank_location VARCHAR(255),
                Payment_type VARCHAR(255),
                Is_laundering INT,
                Laundering_type VARCHAR(255)
            );
        """
        cursor = self.conn.connection.cursor()
        cursor.execute(create_table_query)
        self.conn.connection.commit()
        print(f"Table '{self.table}' is ready.")
        cursor.close()

    def insert_data_from_csv(self, batch_size=5000):
        """Reads data from a CSV file and inserts it into the database."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(GCS_FILE_NAME)
            csv_data = blob.download_as_text()
            df = pd.read_csv(StringIO(csv_data), encoding="utf-8")


            df["Sender_account"] = df["Sender_account"].astype(str)  
            df["Receiver_account"] = df["Receiver_account"].astype(str)
            df["Amount"] = df["Amount"].astype(float)
            df["Is_laundering"] = df["Is_laundering"].astype(int)

            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

            insert_query = f"""
                INSERT INTO {self.table} (Time, Date, Sender_account, Receiver_account, Amount, Payment_currency, 
                Received_currency, Sender_bank_location, Receiver_bank_location, Payment_type, Is_laundering, Laundering_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            cursor = self.conn.connection.cursor()
            cursor.fast_executemany = True

            values = [tuple(row) for row in df.itertuples(index=False, name=None)]
            for i in range(0, len(values), batch_size):
                batch = values[i : i + batch_size]
                cursor.executemany(insert_query, batch)
                self.conn.connection.commit()
                print(f"Inserted {len(batch)} rows...")

            print(f"Successfully inserted {len(df)} rows into '{self.table}'.")
            cursor.close()


        except pyodbc.Error as e:
            print("Database Error:", e)


db_connector = DatabaseConnector(SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD)
db_connector.connect()

data_inserter = DataInserter(db_connector, TABLE_NAME)
data_inserter.ensure_table_exists()
data_inserter.insert_data_from_csv()

db_connector.close_connection()