from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCols,TypeConverters
from pyspark.sql.functions import to_date, to_timestamp, year, month, dayofmonth, hour, minute, second, col
from pyspark.sql import DataFrame
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from typing import List
from pyspark.ml.param.shared import Param, Params
from pyspark import keyword_only


class TypeCastTransformer(Transformer, HasInputCols, HasOutputCols, DefaultParamsReadable, DefaultParamsWritable):
    def __init__(self, inputCols=None, outputCols=None):
        super(TypeCastTransformer, self).__init__()
        self._setDefault(inputCols=[], outputCols=[])
        if inputCols is not None:
            self._set(inputCols=inputCols)
        if outputCols is not None:
            self._set(outputCols=outputCols)

    def setInputCols(self, value):
        return self._set(inputCols=value)

    def setOutputCols(self, value):
        return self._set(outputCols=value)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_cols = self.getOutputCols()

        for in_col, out_col in zip(input_cols, output_cols):
            dataset = dataset.withColumn(out_col, col(in_col).cast("double"))

        return dataset

class DropColumnsTransformer(Transformer, HasInputCols, DefaultParamsReadable, DefaultParamsWritable):
    """
    A custom transformer to drop specified columns from a DataFrame.
    """
    def __init__(self, inputCols=None):
        super(DropColumnsTransformer, self).__init__()
        self._setDefault(inputCols=[])
        if inputCols is not None:
            self._set(inputCols=inputCols)

    def setInputCols(self, value):
        """
        Sets the value of :py:attr:`inputCols`.
        """
        return self._set(inputCols=value)

    def _transform(self, dataset):
        """
        Drops the specified input columns from the DataFrame.
        """
        input_cols = self.getInputCols()
        return dataset.drop(*input_cols)


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

