from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCols
from pyspark.sql.functions import to_date, to_timestamp, year, month, dayofmonth, hour, minute, second, col
from pyspark.sql import DataFrame
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from typing import List
from pyspark.ml.param.shared import Param, Params

from pyspark.ml import Transformer
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import col
from pyspark.sql import DataFrame
from typing import List

from pyspark.ml import Transformer
from pyspark.ml.param.shared import Param, Params
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import col
from pyspark.sql import DataFrame
from typing import List

class TypeCastTransformer(Transformer, DefaultParamsReadable, DefaultParamsWritable):
    def __init__(self, inputCols: List[str], outputCols: List[str], targetCol: str, targetType: str = "int"):
        super().__init__()
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
        other_cols = [col(c) for c in df.columns if c not in self.inputCols and c != self.targetCol]
        return df.select(*other_cols,*casted_feature_cols, casted_target_col)


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
        return df



class DateTimeFeatureExtractor(Transformer, HasInputCols, HasOutputCols,
                               DefaultParamsReadable, DefaultParamsWritable):
    def __init__(self, inputCols=None, outputCols=None):
        super(DateTimeFeatureExtractor, self).__init__()
        self._setDefault(inputCols=["Date", "Time"], outputCols=[])
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
    
    def setParams(self, inputCols=None, outputCols=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataframe: DataFrame):
        inputCols = self.getInputCols()
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
