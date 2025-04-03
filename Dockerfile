# Start from JDK base image (build + runtime)
FROM eclipse-temurin:17-jdk-jammy

# Versions
ARG SPARK_VERSION=3.5.0
ARG HADOOP_VERSION=3.3.6
ARG SCALA_VERSION=2.13
ARG KUBERNETES_CLIENT_VERSION=29.0.0
ARG MONGODB_VERSION=8.0
ARG MONGOSH_VERSION=2.4.2
ARG PYTHON_VERSION=3.11
ARG ODBC_DRIVER_VERSION=18
ARG RETRY_COUNT=5
ARG RETRY_DELAY=10

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    procps \
    gnupg \
    dos2unix \
    unixodbc-dev \
    software-properties-common \
    && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} && \
    rm -rf /var/lib/apt/lists/*

# Environment variables

ENV SPARK_HOME=/opt/spark \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    JAVA_HOME=/opt/java/openjdk \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip" \
    PATH="${JAVA_HOME}/bin:/opt/hadoop/bin:/opt/spark/bin:/opt/venv/bin:${PATH}"

# Install MongoDB
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-${MONGODB_VERSION}.asc | gpg --dearmor -o /usr/share/keyrings/mongodb.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mongodb.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/${MONGODB_VERSION} multiverse" | tee /etc/apt/sources.list.d/mongodb-org-${MONGODB_VERSION}.list && \
    apt-get update && \
    apt-get install -y mongodb-org-shell mongodb-mongosh && \
    rm -rf /var/lib/apt/lists/*

# Install ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql${ODBC_DRIVER_VERSION} && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.so /usr/lib/x86_64-linux-gnu/




RUN mkdir -p /opt && \
    (for i in $(seq 1 ${RETRY_COUNT}); do \
        echo "Attempt $i/${RETRY_COUNT}: Downloading Hadoop ${HADOOP_VERSION}..."; \
        if curl -L --retry ${RETRY_COUNT} --retry-delay ${RETRY_DELAY} \
            https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
            -o /tmp/hadoop.tar.gz; then \
            \
            echo "Download completed, verifying checksum..."; \
            if ! tar -tzf /tmp/hadoop.tar.gz >/dev/null; then \
                echo "ERROR: Downloaded file is corrupt"; \
                rm -f /tmp/hadoop.tar.gz; \
                continue; \
            fi; \
            \
            echo "Extracting Hadoop..."; \
            if tar -xzf /tmp/hadoop.tar.gz -C /opt; then \
                rm -f /tmp/hadoop.tar.gz; \
                \
                # Verify extraction
                if [ -d "/opt/hadoop-${HADOOP_VERSION}" ]; then \
                    echo "Hadoop successfully extracted"; \
                    break; \
                else \
                    echo "ERROR: Extraction failed - directory not found"; \
                    continue; \
                fi; \
            else \
                echo "ERROR: Extraction failed"; \
                continue; \
            fi; \
        else \
            echo "ERROR: Download failed"; \
        fi; \
        \
        [ $i -eq ${RETRY_COUNT} ] && echo "FATAL: All retries exhausted" && exit 1; \
        sleep ${RETRY_DELAY}; \
    done) && \
    \
# Post-installation setup
ln -sfn /opt/hadoop-${HADOOP_VERSION} /opt/hadoop && \
    chown -R root:root /opt/hadoop-${HADOOP_VERSION} && \
    rm -rf /opt/hadoop/share/doc && \
    find /opt/hadoop -name "*-sources.jar" -delete && \
    \
    # Verify installation
    if [ ! -f "/opt/hadoop/bin/hadoop" ]; then \
        echo "ERROR: Hadoop installation verification failed"; \
        exit 1; \
    fi

# Install Spark with conf-org approach
RUN (for i in $(seq 1 ${RETRY_COUNT}); do \
        curl -L --retry ${RETRY_COUNT} --retry-delay ${RETRY_DELAY} \
        https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3-scala${SCALA_VERSION}.tgz | \
        tar -xz -C /opt && \
        mv /opt/spark-${SPARK_VERSION}-bin-hadoop3-scala${SCALA_VERSION} /opt/spark-${SPARK_VERSION} && \
        break || \
        (echo "Spark download failed $i/${RETRY_COUNT}, retrying..." && \
         sleep ${RETRY_DELAY} && \
         rm -rf /opt/spark-* && \
         [ $i -eq ${RETRY_COUNT} ] && exit 1); \
    done) && \
    ln -s /opt/spark-${SPARK_VERSION} /opt/spark && \
    # Create conf-org and move original configs there \
    mkdir -p /opt/spark/conf-org && \
    mv /opt/spark/conf/* /opt/spark/conf-org/ 2>/dev/null || true && \
    # Setup spark-env.sh in conf-org \
    cp /opt/spark/conf-org/spark-env.sh.template /opt/spark/conf-org/spark-env.sh && \
    echo "export SPARK_DIST_CLASSPATH=\$(/opt/hadoop/bin/hadoop classpath)" >> /opt/spark/conf-org/spark-env.sh && \
    echo "export SPARK_EXTRA_CLASSPATH=\$(/opt/hadoop/bin/hadoop classpath)" >> /opt/spark/conf-org/spark-env.sh && \
    # Cleanup \
    rm -rf /opt/spark/examples /opt/spark/data

RUN cp /opt/spark/conf-org/spark-env.sh.template /opt/spark/conf-org/spark-env.sh && \
    echo "export SPARK_DIST_CLASSPATH=\$(/opt/hadoop/bin/hadoop classpath)" >> /opt/spark/conf-org/spark-env.sh && \
    echo "export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop" >> /opt/spark/conf-org/spark-env.sh

# Create symlink for Spark's expected Java path
RUN mkdir -p /usr/lib/jvm && \
    ln -s ${JAVA_HOME} /usr/lib/jvm/java-17-openjdk-amd64

# Set up Python environment
RUN python${PYTHON_VERSION} -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip

WORKDIR /app  
COPY . /app   

RUN if [ -f requirements.txt ]; then /opt/venv/bin/pip install --no-cache-dir -r requirements.txt; fi && \
    find /opt/venv -name "*.pyc" -delete && \
    chmod +x /app/entrypoint.sh && dos2unix /app/entrypoint.sh

# Ensure proper permissions and configurations
RUN chmod -R a+rwx /opt/spark && \
    mkdir -p /opt/spark/conf && \
    touch /opt/spark/conf/spark-defaults.conf && \
    echo "spark.driver.extraJavaOptions -Dio.netty.tryReflectionSetAccessible=true" >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.executor.extraJavaOptions -Dio.netty.tryReflectionSetAccessible=true" >> /opt/spark/conf/spark-defaults.conf && \
    echo "source /opt/spark/conf-org/spark-env.sh" >> /etc/profile

    # Critical Spark configs
RUN echo "spark.ui.port=4040" >> /opt/spark/conf/spark-defaults.conf && \
echo "spark.driver.bindAddress=0.0.0.0" >> /opt/spark/conf/spark-defaults.conf

EXPOSE 4040 
EXPOSE 7078 
EXPOSE 5000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["pyspark"]

# FROM debian:12

# # Set environment variables early to avoid redundancy
# ENV SPARK_VERSION=3.5.5
# ENV HADOOP_VERSION=3.3.6
# ENV SPARK_HOME=/opt/spark
# ENV HADOOP_HOME=/opt/hadoop

# ENV PATH="$SPARK_HOME/bin:/opt/venv/bin:$PATH"
# ENV PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:/opt/venv/lib/python3.11/site-packages"
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONHASHSEED=0

# # Install system dependencies, including unixODBC
#     apt-get install -y \
#     procps \
#     wget \
#     curl \
#     openjdk-17-jdk \
#     python3.11 \
#     python3.11-venv \
#     unixodbc \
#     unixodbc-dev \
#     gnupg && \
#     rm -rf /var/lib/apt/lists/*

# # Set Python 3.11 as the default
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
#     update-alternatives --set python3 /usr/bin/python3.11

# # Create virtual environment and install pip
# RUN python3.11 -m venv /opt/venv && \
#     /opt/venv/bin/python -m pip install --upgrade pip && \
#     find /opt/venv -name "*.pyc" -delete

# # Install Microsoft ODBC Driver 18 for SQL Server
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
#     echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft-prod.list && \
#     apt-get update && \
#     ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
#     rm -rf /var/lib/apt/lists/*

# # Download & verify Hadoop
# RUN wget -O hadoop-${HADOOP_VERSION}.tar.gz https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
#     tar -xvzf hadoop-${HADOOP_VERSION}.tar.gz && \
#     mv hadoop-${HADOOP_VERSION} /opt/hadoop && \
#     rm hadoop-${HADOOP_VERSION}.tar.gz

# # Verify Spark tarball integrity
# RUN wget -O spark-${SPARK_VERSION}-bin-hadoop3.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
#     tar -tzf spark-${SPARK_VERSION}-bin-hadoop3.tgz > /dev/null || (echo "Corrupt Spark tarball, exiting..." && exit 1) && \
#     tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
#     mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
#     rm spark-${SPARK_VERSION}-bin-hadoop3.tgz


# # Install MongoDB 8.0 and Mongosh 2.4.2
# RUN wget -qO - https://pgp.mongodb.com/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-keyring.gpg && \
#     echo "deb [signed-by=/usr/share/keyrings/mongodb-server-keyring.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list && \
#     apt-get update && \
#     apt-get install -y mongodb-org-shell=8.0.5 mongodb-mongosh=2.4.2 && \
#     rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy application files
# COPY . /app

# # Install required Python packages
# RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# # Expose Flask port
# EXPOSE 5000

# # Debugging - keep container running
# CMD ["/bin/sh", "-c", "sleep infinity"]


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
