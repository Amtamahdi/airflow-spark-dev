FROM apache/airflow:2.7.1

USER root

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    curl \
    netcat \
    wget \
    && apt-get clean

# Installation de Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark

RUN curl -L "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -o spark.tgz && \
    tar -xf spark.tgz && \
    mv "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" ${SPARK_HOME} && \
    rm spark.tgz

# Téléchargement du driver JDBC PostgreSQL
RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.18.jar -O /opt/airflow/postgresql-42.2.18.jar

# Configuration des variables d'environnement
ENV PATH=$PATH:${SPARK_HOME}/bin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Installation des dépendances Python
USER airflow
RUN pip install --no-cache-dir \
    requests \
    pyspark==${SPARK_VERSION}

COPY entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh

USER airflow
ENTRYPOINT ["/entrypoint.sh"]