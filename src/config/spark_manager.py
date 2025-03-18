from pyspark.sql import SparkSession
import os



spark_session = SparkSession.builder \
    .master('local[*]').config("spark.driver.memory", "4g").\
        config("spark.executor.memory", "16g").\
        config("spark.memory.fraction", "0.8").\
        config("spark.memory.storageFraction", "0.5").\
        config("spark.sql.shuffle.partitions", "100").\
        config("spark.executor.cores", "6").\
        config("spark.driver.maxResultSize", "2g").getOrCreate()


