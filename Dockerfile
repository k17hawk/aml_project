FROM debian:12

# Set environment variables early to avoid redundancy
ENV SPARK_VERSION=3.5.5
ENV HADOOP_VERSION=3.3.6
ENV SPARK_HOME=/opt/spark
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$SPARK_HOME/bin:/opt/venv/bin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:/opt/venv/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=0

# Install system dependencies, including unixODBC
RUN apt-get update && \
    apt-get install -y \
    procps \
    wget \
    curl \
    openjdk-17-jdk \
    python3.11 \
    python3.11-venv \
    unixodbc \
    unixodbc-dev \
    gnupg && \
    rm -rf /var/lib/apt/lists/*




# Set Python 3.11 as the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11

# Create virtual environment and install pip
RUN python3.11 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --upgrade pip && \
    find /opt/venv -name "*.pyc" -delete

# Install Microsoft ODBC Driver 18 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# Download & verify Hadoop
RUN wget --progress=dot:giga --retry-connrefused --waitretry=5 --timeout=30 \
    https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} /opt/hadoop && \
    rm hadoop-${HADOOP_VERSION}.tar.gz && \
    ls -lah /opt/hadoop/share/hadoop/client/hadoop-client-api-${HADOOP_VERSION}.jar

# Verify Hadoop tarball integrity
RUN wget -O hadoop-${HADOOP_VERSION}.tar.gz https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    echo "Checking Hadoop tarball integrity..." && \
    tar -tzf hadoop-${HADOOP_VERSION}.tar.gz > /dev/null || (echo "Corrupt Hadoop tarball, exiting..." && exit 1) && \
    tar -xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} /opt/hadoop && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Verify Spark tarball integrity
RUN wget -O spark-${SPARK_VERSION}-bin-hadoop3.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    echo "Checking Spark tarball integrity..." && \
    tar -tzf spark-${SPARK_VERSION}-bin-hadoop3.tgz > /dev/null || (echo "Corrupt Spark tarball, exiting..." && exit 1) && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Install MongoDB 8.0 and Mongosh 2.4.2
RUN wget -qO - https://pgp.mongodb.com/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mongodb-server-keyring.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org-shell=8.0.5 mongodb-mongosh=2.4.2 && \
    rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

# Copy application files
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
# Expose Flask port
EXPOSE 5000

# Debugging - keep container running
CMD ["/bin/sh", "-c", "sleep infinity"]

# # Base image
# FROM ubuntu:22.04
# ARG DEBIAN_FRONTEND=noninteractive
# ARG TZ=UTC

# # Airflow and Python versions
# ARG AIRFLOW_VERSION=2.10.5
# ARG PYTHON_VERSION=3.11
# ARG HADOOP_VERSION=3.3.6
# ARG SPARK_VERSION=3.5.5

# # Set environment variables
# ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
# ENV AIRFLOW_HOME="/app/airflow"
# ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000
# ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
# ENV PYSPARK_PYTHON=/usr/bin/python3
# ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3
# ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
# ENV AIRFLOW__CORE__DAGS_FOLDER="/app/dags"
# ENV PYTHONPATH="/app/src"

# # Switch to root user
# USER root

# # Reinstall Perl and tzdata
# RUN apt-get update && \
#     apt-get install --reinstall -y perl perl-base perl-modules-5.34 tzdata && \
#     ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
#     dpkg-reconfigure --frontend noninteractive tzdata && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # Install required dependencies
# RUN apt-get update -y && \
#     apt-get upgrade -y && \
#     apt-get install -y \
#     openjdk-8-jdk \
#     python3 \
#     python3-pip \
#     python3-dev \
#     build-essential \
#     gcc \
#     libssl-dev \
#     libffi-dev \
#     wget \
#     curl \
#     unzip \
#     software-properties-common \
#     cmake \
#     git \
#     libabsl-dev && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # Set Java environment variables
# ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
# ENV PATH="$JAVA_HOME/bin:$PATH"

# # Install Hadoop (needed for Spark)
# RUN curl -O https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
#     tar -xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
#     mv hadoop-${HADOOP_VERSION} /opt/hadoop && \
#     rm hadoop-${HADOOP_VERSION}.tar.gz

# # Install Spark
# RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
#     tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
#     mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
#     rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# # Set environment variables for Spark and Hadoop
# ENV SPARK_HOME=/opt/spark
# ENV PATH=$SPARK_HOME/bin:$PATH
# ENV HADOOP_HOME=/opt/hadoop
# ENV PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
# ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

# RUN echo 'export SPARK_DIST_CLASSPATH="$(hadoop classpath)"' >> ~/.bashrc

# # Install Microsoft ODBC Drivers
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
#     curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
#     apt-get update && \
#     ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools unixodbc-dev && \
#     echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# # Create app directory and set working directory
# RUN mkdir /app
# COPY . /app/
# WORKDIR /app/

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy entrypoint script
# COPY entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh

# # Set the default command to run the pipeline script dynamically
# CMD ["/app/entrypoint.sh"]