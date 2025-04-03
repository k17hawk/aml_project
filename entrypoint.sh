#!/bin/bash

# Set Java options using the correct JAVA_HOME from the Dockerfile
export JAVA_HOME=${JAVA_HOME:-/opt/java/openjdk}
export PATH="${JAVA_HOME}/bin:${PATH}"

# Debugging output
echo "Using JAVA_HOME: ${JAVA_HOME}"
echo "Java version:"
java -version

# Initialize Spark environment
export SPARK_HOME=${SPARK_HOME:-/opt/spark}
export HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
export SPARK_DIST_CLASSPATH=$(${HADOOP_HOME}/bin/hadoop classpath)

# Copy original config files if conf directory is empty
if [ -d "${SPARK_HOME}/conf-org" ] && [ ! "$(ls -A ${SPARK_HOME}/conf)" ]; then
  cp -r ${SPARK_HOME}/conf-org/* ${SPARK_HOME}/conf/
fi

# Add Spark to PYTHONPATH
export PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.9.7-src.zip:${PYTHONPATH}"
/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip

# Handle different execution modes
case "$1" in
  'spark-master')
    echo "Starting Spark Master..."
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.master.Master
    ;;
  'spark-worker')
    echo "Starting Spark Worker..."
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.worker.Worker spark://spark-master:7077
    ;;
  'spark-submit')
    shift
    exec "${SPARK_HOME}/bin/spark-submit" "$@"
    ;;
  'spark-shell')
    shift
    exec "${SPARK_HOME}/bin/spark-shell" "$@"
    ;;
  'pyspark')
    shift
    exec "${SPARK_HOME}/bin/pyspark" "$@"
    ;;
  'python')
    shift
    exec "python" "$@"
    ;;
  *)
    echo "No command provided, starting Spark Master and PySpark..."
    
    # Start Spark Master in the background
    "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.master.Master &

    # Wait a bit to ensure the master starts before running PySpark
    sleep 5  

    # Start PySpark in the foreground
    exec "${SPARK_HOME}/bin/pyspark"
    ;;
esac
