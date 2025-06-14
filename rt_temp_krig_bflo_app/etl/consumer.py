import os
os.environ["HADOOP_HOME"] = "C:\\hadoop"

import sys
import logging
import pandas as pd
from pyspark.sql import SparkSession


def main(): 
    logging.info("START")
    spark = SparkSession.builder \
        .appName("rt-krig-map") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    data_df = spark.read.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "temp_data_bflo") \
        .load() \
        .selectExpr("CAST(value AS STRING) as raw_data", "CAST(key AS STRING) as batch_id")

    grouped_df = data_df.groupBy("batch_id").agg({"raw_data": "collect_list"})

    # grouped_df.writeStream.format("console").outputMode("append").start()

    pd_df = grouped_df.toPandas()

    pd_df[["temperature", "longitude", "latitude"]] = pd_df["raw_data"].apply(lambda x: pd.Series(x.split(","))).astype(float)

    pd_df.to_string(sys.stdout)


if __name__ == '__main__':
    main()
