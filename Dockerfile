# Base image
FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=UTC

# Airflow and Python versions
ARG AIRFLOW_VERSION=2.10.5
ARG PYTHON_VERSION=3.11
ARG HADOOP_VERSION=3.3.6
ARG SPARK_VERSION=3.5.5


# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
ENV AIRFLOW_HOME="/app/airflow"
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV PYSPARK_PYTHON=/usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__DAGS_FOLDER="/app/dags"
ENV PYTHONPATH="/app/src"

# Switch to root user
USER root

# Install required dependencies, including tzdata
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    openjdk-8-jdk \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    wget \
    curl \
    unzip \
    software-properties-common \
    tzdata \
    cmake \
    git \
    libabsl-dev 

# Set timezone explicitly
ENV TZ=UTC
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Hadoop (needed for Spark)
RUN curl -O https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} /opt/hadoop && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Install Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Set environment variables for Spark and Hadoop
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

RUN echo 'export SPARK_DIST_CLASSPATH="$(hadoop classpath)"' >> ~/.bashrc

# Install Microsoft ODBC Drivers
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools unixodbc-dev && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Create app directory and set working directory
RUN mkdir /app
COPY . /app/
WORKDIR /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the default command to run the pipeline script dynamically
CMD ["/app/entrypoint.sh"]
