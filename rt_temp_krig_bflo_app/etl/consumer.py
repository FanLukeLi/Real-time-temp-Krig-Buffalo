import sys
import logging
import pandas as pd
from pyspark.sql import SparkSession


def main(): 
    logging.info("START")
    spark = SparkSession.builder.appName('rt-krig-map').getOrCreate()

    data_df = spark.read.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "temp_data_bflo") \
        .load() \
        .selectExpr("CAST(value AS STRING) as raw_data", "CAST(key AS STRING) as batch_id")

    grouped_df = data_df.groupBy("batch_id").agg({"raw_data": "collect_list"})

    pd_df = grouped_df.toPandas()

    pd_df[["temperature", "latitude", "longitude"]] = pd_df["raw_data"].apply(lambda x: pd.Series(x.split(","))).astype(float)

    pd_df.to_string(sys.stdout)


if __name__ == '__main__':
    main()
