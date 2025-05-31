import logging
from quixstreams import Application
from pyspark.sql import SparkSession
from pyspark import SparkContext


def main(): 
    logging.info("START")
    app = Application(
        broker_address="localhost:9092", 
        loglevel="DEBUG", 

        auto_offset_reset="latest", 
        consumer_group="temperature_processor"
    )

    input_topic = app.topic("temperature_data_buffalo")
    output_topic = app.topic("temperature_output")

    sc = SparkContext(appName="MySparkApplication")
    spark = SparkSession.builder.appName('rt-krig-map').getOrCreate()

    def spark_transform(): 
        df = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "temperature_data_buffalo") \
            .load()
        logging.info(df.select(col("geometry")))

    sdf = app.dataframe(input_topic)
    sdf = sdf.apply(spark_transform)
    sdf = sdf.to_topic(output_topic)

    app.run(sdf)

