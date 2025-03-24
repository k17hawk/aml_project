from pyspark.sql import SparkSession
import os
import json


spark_config_paths = [
    'config/spark_config.json', 
    '/app/config/spark_config.json'  
]


spark_config = None
for path in spark_config_paths:
    if os.path.exists(path):
        with open(path, 'r') as f:
            spark_config = json.load(f)
            print(f"Loaded Spark config from {path}:", spark_config)
        break
else:
    print("Error: Spark config file not found in any of the following paths:")
    for path in spark_config_paths:
        print(f" - {path}")
    raise FileNotFoundError("Spark config file not found.")

# Build the Spark session using the configuration
spark_session = SparkSession.builder \
    .master(spark_config['master']) \
    .config("spark.kubernetes.container.image", spark_config['spark.kubernetes.container.image']) \
    .config("spark.kubernetes.namespace", spark_config['spark.kubernetes.namespace']) \
    .config("spark.driver.memory", spark_config['spark.driver.memory']) \
    .config("spark.executor.memory", spark_config['spark.executor.memory']) \
    .config("spark.executor.instances", spark_config['spark.executor.instances']) \
    .config("spark.executor.cores", spark_config['spark.executor.cores']) \
    .config("spark.sql.shuffle.partitions", spark_config['spark.sql.shuffle.partitions']) \
    .config("spark.kubernetes.authenticate.driver.serviceAccountName", spark_config['spark.kubernetes.authenticate.driver.serviceAccountName']) \
    .getOrCreate()

# Your Spark application logic here

# spark_session = SparkSession.builder \
#     .master('local[*]').config("spark.driver.memory", "4g").\
#         config("spark.executor.memory", "8g").\
#         config("spark.memory.fraction", "0.8").\
#         config("spark.memory.storageFraction", "0.5").\
#         config("spark.sql.shuffle.partitions", "100").\
#         config("spark.executor.cores", "4").\
#         config("spark.driver.maxResultSize", "2g").getOrCreate()
