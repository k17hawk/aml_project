# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set environment variables for Java, Airflow, and PySpark
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

# Update system and install required dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
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

# Set timezone
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools unixodbc-dev && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Create app directory
RUN mkdir /app

# Copy files to the container
COPY . /app/

# Set working directory
WORKDIR /app/

# Install Python dependencies using Airflow's constraints file
ARG AIRFLOW_VERSION=2.10.5
ARG PYTHON_VERSION=3.11
# ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# RUN pip3 install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
RUN pip3 install --no-cache-dir -r requirements.txt

# Set permissions for the start script
RUN chmod +x start.sh

# Set entrypoint to the start script
ENTRYPOINT ["/app/start.sh"]