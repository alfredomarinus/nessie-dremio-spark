#!/bin/bash
# Spark environment configuration for cluster with Nessie/Iceberg support

# Master configuration
export SPARK_MASTER_HOST="spark-master"
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8080

# Worker configuration
export SPARK_WORKER_CORES=2
export SPARK_WORKER_MEMORY=2g
export SPARK_WORKER_WEBUI_PORT=8081

# Common configuration
export SPARK_LOCAL_IP="0.0.0.0"

# JVM options
export SPARK_DAEMON_MEMORY=1g

# Log directory
export SPARK_LOG_DIR=/opt/spark/logs

# Python configuration (for PySpark)
export PYTHONUNBUFFERED=1
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
