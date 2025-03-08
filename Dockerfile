FROM ubuntu:22.04



ENV DEBIAN_FRONTEND=noninteractive

ENV TZ=UTC



# Install necessary dependencies and Java 8

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
 libabsl-dev && \
 ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
 dpkg-reconfigure --frontend noninteractive tzdata



# Set Java environment variables

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

ENV PATH="$JAVA_HOME/bin:$PATH"


# Install Hadoop (needed for Spark)
RUN curl -O https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz && \
    tar -xvzf hadoop-3.3.6.tar.gz && \
    mv hadoop-3.3.6 /opt/hadoop && \
    rm hadoop-3.3.6.tar.gz

# Install Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz && \
    tar -xvzf spark-3.5.5-bin-hadoop3.tgz && \
    mv spark-3.5.5-bin-hadoop3 /opt/spark && \
    rm spark-3.5.5-bin-hadoop3.tgz

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

RUN pip3 install --no-cache-dir -r requirements.txt



# Default command to start your Python script
CMD ["spark-submit", "ingestion_pipeline.py"]