import os
import threading

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"

import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, FloatType
from kafka import KafkaConsumer
from transform import main as transform
from visualize import main as visualize


with open('./config.json', 'r') as f:
    config = json.load(f)


def create_logger():
    logger = logging.getLogger('consumer_logger')
    logger.setLevel(logging.INFO)
    consumer_console_handler = logging.StreamHandler()
    consumer_console_handler.setLevel(logging.INFO)
    consumer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consumer_console_handler.setFormatter(consumer_formatter)
    logger.addHandler(consumer_console_handler)
    logger.propagate = False
    logger.info("Consumer logger initialized.")
    return logger


def main(logger: logging.Logger, lock: threading.Lock):
    if not logger:
        logger = create_logger()

    consumer = None
    try:
        logger.info("START")
        spark = SparkSession.builder \
            .appName("rt-krig-map") \
            .master("spark://spark-master:7077") \
            .config("spark.driver.port", "4041") \
            .config("spark.blockManager.port", "4042") \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0") \
            .getOrCreate()

        spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

        consumer = KafkaConsumer(
            'batch_end_mark',
            bootstrap_servers='kafka:9092',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='rt_temp_krig_bflo_group',
            session_timeout_ms=30000,
        )

        json_schema = StructType([
            StructField("temperature", FloatType(), True),
            StructField("longitude", FloatType(), True),
            StructField("latitude", FloatType(), True)
        ])

        for message in consumer:
            with lock:
                id_prefix = message.value.decode('utf-8').strip('""')
                logger.info(f"id_prefix: {id_prefix}")
                data_df = spark.read.format("kafka") \
                    .option("kafka.bootstrap.servers", "kafka:9092") \
                    .option("subscribe", "temp_data_bflo") \
                    .load() \
                    .selectExpr("CAST(value AS STRING) as raw_data", "CAST(key AS STRING) as batch_id") \
                    .filter(f"batch_id = '{id_prefix}'")

                data_df.repartition(4)
                data_df.persist()
                data_df = data_df.withColumn("decoded_data", from_json(col("raw_data"), json_schema)) \
                    .selectExpr(
                        "CAST(decoded_data.temperature AS FLOAT) as temperature",
                        "CAST(decoded_data.longitude AS FLOAT) as longitude",
                        "CAST(decoded_data.latitude AS FLOAT) as latitude"
                    )
                data_df.show()
                pdf = data_df.filter("temperature != float('inf')")
                logger.info(f"Data Frame transformed to pandas with shape: {pdf.count()}, {len(pdf.columns)}")
                column_dtypes = dict(pdf.dtypes)
                logger.info(f"Data Frame columns dtype: longitude: {str(column_dtypes['longitude'])}" +
                            f", latitude: {str(column_dtypes['latitude'])}" +
                            f", temperature: {str(column_dtypes['temperature'])}")
                res = transform(pdf, logger)
                visualize(res['coord_x'], res['coord_y'], res['temperature'], logger)
    except Exception as e:
        logger.error(f"Error in consumer main function: {e}")
        raise e
    finally:
        if consumer:
            logger.info("Closing consumer...")
            consumer.close()


if __name__ == '__main__':
    main(create_logger(), threading.Lock())
