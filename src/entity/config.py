from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from src.exception import AMLException
import sys
from typing import List
class TransactionDataSchema:

    def __init__(self):
        # Define column names as attributes
        self.col_time: str = 'Time'
        self.col_date: str = 'Date'
        self.col_sender_account: str = 'Sender_account'
        self.col_receiver_account: str = 'Receiver_account'
        self.col_amount: str = 'Amount'
        self.col_payment_currency: str = 'Payment_currency'
        self.col_received_currency: str = 'Received_currency'
        self.col_sender_bank_location: str = 'Sender_bank_location'
        self.col_receiver_bank_location: str = 'Receiver_bank_location'
        self.col_payment_type: str = 'Payment_type'
        self.col_is_laundering: str = 'Is_laundering'
        self.col_laundering_type: str = 'Laundering_type'
        self.col_hour:str = 'Hour'
        self.col_minutes:str = 'Minutes'
        self.col_second:str = 'Minutes'
        self.col_year:str = 'Year'
        self.col_month:str = 'Month'
        self.col_day:str = 'Day'

    @property
    def dataframe_schema(self) -> StructType:
        """Returns the schema for the transaction data."""
        try:
            schema = StructType([
                StructField(self.col_time, StringType(), nullable=True),
                StructField(self.col_date, StringType(), nullable=True),
                StructField(self.col_sender_account, IntegerType(), nullable=True),
                StructField(self.col_receiver_account, IntegerType(), nullable=True),
                StructField(self.col_amount, DoubleType(), nullable=True),
                StructField(self.col_payment_currency, StringType(), nullable=True),
                StructField(self.col_received_currency, StringType(), nullable=True),
                StructField(self.col_sender_bank_location, StringType(), nullable=True),
                StructField(self.col_receiver_bank_location, StringType(), nullable=True),
                StructField(self.col_payment_type, StringType(), nullable=True),
                StructField(self.col_is_laundering, IntegerType(), nullable=True),
                StructField(self.col_laundering_type, StringType(), nullable=True),
                StructField(self.col_hour, StringType(), nullable=True),
                StructField(self.col_minutes, StringType(), nullable=True),
                StructField(self.col_second, StringType(), nullable=True),
                StructField(self.col_year, StringType(), nullable=True),
                StructField(self.col_month, StringType(), nullable=True),
                StructField(self.col_day, StringType(), nullable=True)
            ])
            return schema
        except Exception as e:
            raise AMLException(e, sys) from e
    @property
    def target_column(self) -> str:
        return self.col_is_laundering

    @property
    def string_indexing_input_features(self) -> List[str]:
        features = [
            self.col_payment_currency,
            self.col_received_currency,
            self.col_receiver_bank_location,
            self.col_sender_bank_location,
            self.col_payment_type,
            self.col_laundering_type
        ]
        return features
    
    @property
    def string_indexing_out_features(self) -> List[str]:
        return [f"im_{col}" for col in self.string_indexing_input_features]
    
    @property
    def derived_input_features(self) -> List[str]:
        features = [
            self.col_hour,
            self.col_minutes,
            self.col_second,
            self.col_year,
            self.col_month,
            self.col_day
        ]
        return features
    
    @property
    def numerical_columns(self) -> List[str]:
        return self.derived_input_features+self.col_sender_account+self.col_receiver_account+self.col_amount+self.col_is_laundering
    
    @property
    def numerical_out_columns(self) -> List[str]:
        return [f"num_{col}"for col in self.numerical_columns ]
    
    @property
    def unwanted_columns(self) -> List[str]:
        features = [
            self.col_date,
            self.col_time
        ]
        return features
    
    @property
    def vector_assembler_input_cols(self) -> List[str]:
        features = [
            f"num_{self.col_sender_account}",
            f"num_{self.col_receiver_account}",
           f"num_{self.col_amount}"
        ] + [f"num_{col}"for col in self.derived_input_features]+self.string_indexing_out_features
        return features
    
    @property
    def vector_assembler_out_cols(self) -> List[str]:
        return 'features'
    
    @property
    def target_cols(self) -> List[str]:
        return f'num_{self.col_is_laundering}'
    
    
    

