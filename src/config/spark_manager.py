from pyspark.sql import SparkSession
import os

# Define the path to the JDBC JAR file
jdbc_jar_path = r"mssql-jdbc-12.8.1.jre11.jar"  
hadoop_home = r"C:\hadoop\hadoop-3.3.6" 
os.environ['HADOOP_HOME'] = hadoop_home

# Create a Spark session with the JDBC JAR configured
spark_session =  SparkSession.builder\
    .master('local[*]')\
    .config("spark.driver.memory", "6g")\
    .appName('AML_project')\
    .getOrCreate()