from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCols
from pyspark.sql.functions import to_date, to_timestamp, year, month, dayofmonth, hour, minute, second, col
from pyspark.sql import DataFrame
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable

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
