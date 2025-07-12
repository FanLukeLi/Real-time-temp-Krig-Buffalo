import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"

import sys
import logging
import pandas as pd
from pyspark.sql import SparkSession
from kafka import KafkaConsumer


def main():
    logging.info("START")
    spark = SparkSession.builder \
        .appName("rt-krig-map") \
        .master("spark://spark:7077") \
        .config("spark.driver.port", "4041") \
        .config("spark.blockManager.port", "4042") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0") \
        .getOrCreate()
        # .config("spark.executor.memory", "4g") \
        # .config("spark.driver.memory", "4g") \

    consumer = KafkaConsumer(
        'batch_end_mark',
        bootstrap_servers='kafka:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='rt_temp_krig_bflo_group',
        session_timeout_ms=30000,
    )

    for message in consumer:
        id_prefix = message.value
        data_df = spark.read.format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "temp_data_bflo") \
            .load() \
            .selectExpr("CAST(value AS STRING) as raw_data", "CAST(key AS STRING) as batch_id") \
            .filter(f"batch_id = '{id_prefix}'")

        print(data_df)


if __name__ == '__main__':
    main()
