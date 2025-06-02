import logging
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def main(): 
    logging.info("START")
    spark = SparkSession.builder.appName('rt-krig-map').getOrCreate()

    batch_id_df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "temp_data_bflo") \
        .option("startingOffsets", "latest") \
        .load()

    data_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "temp_data_bflo") \
        .option("startingOffsets", "earliest") \
        .load()

    data_df = data_df.join(batch_id_df, data_df.data_value.startwith(batch_id_df.batch_id))
