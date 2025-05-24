import logging
from quixstreams import Application


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

    def spark_transform(): 
        pass

    sdf = app.dataframe(input_topic)
    sdf = sdf.apply(spark_transform)
    sdf = sdf.to_topic(output_topic)

    app.run(sdf)

