from pyspark.sql import SparkSession
import os

jdbc_jar_path = r"mssql-jdbc-12.8.1.jre11.jar"  
hadoop_home = r"C:\hadoop\hadoop-3.3.6" 
os.environ['HADOOP_HOME'] = hadoop_home

spark_session = SparkSession.builder \
    .master('local[*]').config("spark.driver.memory", "4g").\
        config("spark.executor.memory", "16g").\
        config("spark.memory.fraction", "0.8").\
        config("spark.memory.storageFraction", "0.5").\
        config("spark.sql.shuffle.partitions", "100").\
        config("spark.executor.cores", "6").\
        config("spark.driver.maxResultSize", "2g").getOrCreate()


