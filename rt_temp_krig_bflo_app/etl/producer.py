import logging
import json
import signal
import threading

import requests
import datetime
import geopandas as gpd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from apscheduler.schedulers.background import BackgroundScheduler


def create_logger():
    logger = logging.getLogger('producer_logger')
    logger.setLevel(logging.INFO)

    producer_console_handler = logging.StreamHandler()
    producer_console_handler.setLevel(logging.INFO)

    producer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    producer_console_handler.setFormatter(producer_formatter)

    logger.addHandler(producer_console_handler)
    logger.propagate = False

    logger.info("Producer logger initialized.")
    return logger


with open('./config.json', 'r') as f:
    config = json.load(f)


def create_topics(logger: logging.Logger):
    admin_client = KafkaAdminClient(
        bootstrap_servers='kafka:9092',
        client_id='producer-admin'
    )

    try:
        logger.info("Creating topics if they do not exist...")
        existing_topics = admin_client.list_topics()
        topics_to_add = [NewTopic(name=topic, num_partitions=1, replication_factor=1)
                         for topic in ['temp_data_bflo', 'batch_end_mark']
                         if topic not in existing_topics]
        if topics_to_add:
            admin_client.create_topics(new_topics=topics_to_add, validate_only=False)
            logger.info(f"Created topics: {[topic.name for topic in topics_to_add]}")
        else:
            logger.info("No new topics to create.")
    except Exception as e:
        logger.warning(f"Error creating topics: {e}")
    finally:
        admin_client.close()

def get_temp(x, y): 
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": y, 
        "longitude": x, 
        "current": "temperature_2m", 
        "temperature_unit": "fahrenheit"
    }, timeout=10)
    return response.json()


def main(logger: logging.Logger, lock: threading.Lock = None):
    if not logger:
        logger = create_logger()

    producer = None
    try:
        create_topics(logger)
        buf_coords = gpd.read_file('./data/temp_request_grid.json')
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8')
        )

        def send_msgs():
            id_prefix = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
            nrows = buf_coords.shape[0]
            for i, coord in buf_coords.iterrows():
                with lock:
                    x = coord.geometry.x
                    y = coord.geometry.y
                    try:
                        res = get_temp(x, y)
                        temp = res['current']['temperature_2m']
                    except Exception as e:
                        logger.info(str(e))
                        temp = float('inf')
                    logger.info(f"Batch id {id_prefix} {i+1} in {nrows}: {temp}, {x}, {y}")
                    if id_prefix:
                        producer.send(
                            topic='temp_data_bflo',
                            key=id_prefix,
                            value={"temperature": temp, "longitude": x, "latitude": y}
                        )
            producer.send(topic='batch_end_mark', key=id_prefix, value=id_prefix)

        scheduler = BackgroundScheduler()
        scheduler.add_job(send_msgs, "interval",
                          seconds=config['interval'],
                          id='send_temp_data_job',
                          next_run_time=datetime.datetime.now())

        scheduler.start()
        logger.info("Scheduler started successfully.")
        logging.getLogger('apscheduler.executors.default').setLevel(logging.INFO)
        # while True:
        #     send_msgs()
        #     time.sleep(300)
        signal.pause()
    except Exception as e:
        logger.error(f"Error in producer main function: {e}")
        return
    finally:
        if producer:
            logger.info("Closing producer...")
            producer.close()


if __name__ == "__main__":
    main(create_logger(), threading.Lock())
