from pyspark.sql import SparkSession
import os
import socket
from typing import Dict, Union

class SparkConstants:
    """Centralized configuration constants for Spark sessions"""
    
    # Network Configuration
    DRIVER_HOST = os.getenv('SPARK_DRIVER_HOST', socket.gethostbyname(socket.gethostname()))
    DRIVER_PORT = os.getenv('SPARK_DRIVER_PORT', '29413')
    UI_PORT = os.getenv('SPARK_UI_PORT', '4040').split(':')[-1] 
    UI_HOST = '0.0.0.0'
    
    # Cluster Configuration
    MASTER = os.getenv('SPARK_MASTER', 'local[2]')
    APP_NAME = os.getenv('SPARK_APP_NAME', 'my-python-app')
    
    # Kubernetes Configuration
    K8S_IMAGE = os.getenv('SPARK_K8S_IMAGE', 'mypyspark:latest')
    K8S_NAMESPACE = os.getenv('SPARK_K8S_NAMESPACE', 'default')
    K8S_SERVICE_ACCOUNT = os.getenv('SPARK_K8S_SERVICE_ACCOUNT', 'spark')
    K8S_BATCH_DELAY = os.getenv('SPARK_K8S_BATCH_DELAY', '5s')
    
    # Resource Configuration
    DRIVER_MEMORY = os.getenv('SPARK_DRIVER_MEMORY', '14g')
    EXECUTOR_MEMORY = os.getenv('SPARK_EXECUTOR_MEMORY', '14g')
    MEMORY_FRACTION = os.getenv('SPARK_MEMORY_FRACTION', '0.75')
    STORAGE_FRACTION = os.getenv('SPARK_STORAGE_FRACTION', '0.3')
    
    # Performance Configuration
    SHUFFLE_PARTITIONS = os.getenv('SPARK_SHUFFLE_PARTITIONS', '4')
    DEFAULT_PARALLELISM = os.getenv('SPARK_DEFAULT_PARALLELISM', '4')
    
    # Serialization Configuration
    SERIALIZER = os.getenv('SPARK_SERIALIZER', 'org.apache.spark.serializer.KryoSerializer')
    KRYO_BUFFER_MAX = os.getenv('SPARK_KRYO_BUFFER_MAX', '512m')
    
    # UI Configuration
    UI_ENABLED = os.getenv('SPARK_UI_ENABLED', 'true')
    UI_REVERSE_PROXY = os.getenv('SPARK_UI_REVERSE_PROXY', 'true')
    
    # Security Configuration
    CA_CERT_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    OAUTH_TOKEN_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/token'
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, str]:
        """Return all configurations as a dictionary"""
        return {
            # Network
            'spark.driver.host': cls.DRIVER_HOST,
            'spark.driver.port': cls.DRIVER_PORT,
            'spark.ui.port': cls.UI_PORT,
            'spark.ui.host': cls.UI_HOST,
            
            # Kubernetes
            'spark.kubernetes.container.image': cls.K8S_IMAGE,
            'spark.kubernetes.namespace': cls.K8S_NAMESPACE,
            'spark.kubernetes.authenticate.driver.serviceAccountName': cls.K8S_SERVICE_ACCOUNT,
            'spark.kubernetes.allocation.batch.delay': cls.K8S_BATCH_DELAY,
            
            # Resources
            'spark.driver.memory': cls.DRIVER_MEMORY,
            'spark.executor.memory': cls.EXECUTOR_MEMORY,
            'spark.memory.fraction': cls.MEMORY_FRACTION,
            'spark.memory.storageFraction': cls.STORAGE_FRACTION,
            
            # Performance
            'spark.sql.shuffle.partitions': cls.SHUFFLE_PARTITIONS,
            'spark.default.parallelism': cls.DEFAULT_PARALLELISM,
            
            # Serialization
            'spark.serializer': cls.SERIALIZER,
            'spark.kryoserializer.buffer.max': cls.KRYO_BUFFER_MAX,
            
            # UI
            'spark.ui.enabled': cls.UI_ENABLED,
            'spark.ui.reverseProxy': cls.UI_REVERSE_PROXY,
            
            # Security
            'spark.kubernetes.authenticate.caCertFile': cls.CA_CERT_PATH,
            'spark.kubernetes.authenticate.oauthTokenFile': cls.OAUTH_TOKEN_PATH
        }

class SparkManager:
    @staticmethod
    def get_spark_session(app_name: str = None) -> SparkSession:
        """Create or get a Spark session with centralized configuration"""
        
        # Initialize builder with core config
        builder = SparkSession.builder \
            .appName(app_name or SparkConstants.APP_NAME) \
            .master(SparkConstants.MASTER)
        
        # Apply all configurations
        for config_key, config_value in SparkConstants.get_all_configs().items():
            builder.config(config_key, config_value)
        
        return builder.getOrCreate()
# Your Spark application logic here

# spark_session = SparkSession.builder \
#     .master('local[*]').config("spark.driver.memory", "4g").\
#         config("spark.executor.memory", "8g").\
#         config("spark.memory.fraction", "0.8").\
#         config("spark.memory.storageFraction", "0.5").\
#         config("spark.sql.shuffle.partitions", "100").\
#         config("spark.executor.cores", "4").\
#         config("spark.driver.maxResultSize", "2g").getOrCreate()
