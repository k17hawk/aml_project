from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCols,TypeConverters
from pyspark.sql.functions import to_date, to_timestamp, year, month, dayofmonth, hour, minute, second, col
from pyspark.sql import DataFrame
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from typing import List
from pyspark.ml.param.shared import Param, Params
from pyspark import keyword_only


class TypeCastTransformer(Transformer, DefaultParamsReadable, DefaultParamsWritable):
    def __init__(self,otherCols:List[str], inputCols: List[str], outputCols: List[str], targetCol: str, targetType: str = "int"):
        super().__init__()
        self.othercols = otherCols
        self.inputCols = inputCols  
        self.outputCols = outputCols  
        self.targetCol = targetCol  
        self.targetType = targetType

    def _transform(self, df: DataFrame) -> DataFrame:
        # Ensuring input and output column lists match
        if len(self.inputCols) != len(self.outputCols):
            raise ValueError("inputCols and outputCols must have the same length!")
      
        # Casting input feature columns
        casted_feature_cols = [col(inp).cast("double").alias(out) for inp, out in zip(self.inputCols, self.outputCols)]

        # Casting target column separately
        casted_target_col = col(self.targetCol).cast(self.targetType).alias(self.targetCol)
        # Selecting all other columns that are not transformed
        selected_other_cols = [col(c) for c in self.othercols]  
    
        return df.select(*selected_other_cols,*casted_feature_cols, casted_target_col)


class DropColumnsTransformer(Transformer, DefaultParamsReadable, DefaultParamsWritable):
    input_cols = Param(Params._dummy(), "input_cols", "List of columns to drop")

    def __init__(self, input_cols: List[str] = None):
        super().__init__()
        self.setParams(input_cols)

    def setParams(self, input_cols: List[str]):
        """Setting parameters"""
        self._set(input_cols=input_cols)

    def _transform(self, df: DataFrame) -> DataFrame:
        """Dropping specified columns from DataFrame"""
        cols_to_drop = self.getOrDefault(self.input_cols)
        if cols_to_drop:
            return df.drop(*cols_to_drop)
        print(df.show())
        return df



class DateTimeFeatureExtractor(Transformer, HasInputCols, HasOutputCols,
                               DefaultParamsReadable, DefaultParamsWritable):

    frequencyInfo = Param(Params._dummy(), "getfrequencyInfo", "getfrequencyInfo",
                          typeConverter=TypeConverters.toList)

    @keyword_only
    def __init__(self, inputCols: List[str] = None, outputCols: List[str] = None, ):
        super(DateTimeFeatureExtractor, self).__init__()
        kwargs = self._input_kwargs
        
    
        self.frequencyInfo = Param(self, "frequencyInfo", "")
        self._setDefault(frequencyInfo="")
        # self._set(**kwargs)
        self.setParams(**kwargs)

    def setfrequencyInfo(self, frequencyInfo: list):
        return self._set(frequencyInfo=frequencyInfo)

    def getfrequencyInfo(self):
        return self.getOrDefault(self.frequencyInfo)

    @keyword_only
    def setParams(self, inputCols: List[str] = None, outputCols: List[str] = None, ):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def setInputCols(self, value: List[str]):
        """
        Sets the value of :py:attr:`inputCol`.
        """
        return self._set(inputCol=value)

    def setOutputCols(self, value: List[str]):
        """
        Sets the value of :py:attr:`outputCol`.
        """
        return self._set(outputCols=value)
    
    def _transform(self, dataframe: DataFrame):
        inputCols = self.getInputCols()
        if len(inputCols) < 2:
            raise ValueError("inputCols must contain at least two columns: [date_col, time_col]")
        
        date_col, time_col = inputCols[0], inputCols[1]

        # Convert Date and Time to proper formats
        dataframe = dataframe.withColumn(date_col, to_date(col(date_col), "yyyy-MM-dd"))
        dataframe = dataframe.withColumn(time_col, to_timestamp(col(time_col), "HH:mm:ss"))

        # Extract features
        dataframe = dataframe.withColumn("year", year(col(date_col))) \
                             .withColumn("month", month(col(date_col))) \
                             .withColumn("day", dayofmonth(col(date_col))) \
                             .withColumn("hour", hour(col(time_col))) \
                             .withColumn("minute", minute(col(time_col))) \
                             .withColumn("second", second(col(time_col)))
        
        return dataframe

