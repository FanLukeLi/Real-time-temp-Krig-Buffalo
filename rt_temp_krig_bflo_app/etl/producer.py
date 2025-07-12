import logging
import json
import time

import requests
import datetime
import geopandas as gpd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

with open('./config.json', 'r') as f:
    config = json.load(f)

def create_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers='kafka:9092',
        client_id='producer-admin'
    )

    topics = [
        NewTopic(name='temp_data_bflo', num_partitions=1, replication_factor=1),
        NewTopic(name='batch_end_mark', num_partitions=1, replication_factor=1)
    ]

    try:
        # existing_topics = admin_client.list_topics()
        # topics_to_delete = [topic for topic in ['temp_data_bflo', 'batch_end_mark'] if topic in existing_topics]
        # if topics_to_delete:
        #     admin_client.delete_topics(topics_to_delete)
        #     logging.info(f"Deleted topics: {topics_to_delete}")
        # time.sleep(5)
        admin_client.create_topics(new_topics=topics, validate_only=False)
        logging.info("Topics created successfully. ")
    except Exception as e:
        logging.warning(f"Error creating topics: {e}")
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


def main():
    # create_topics()

    buf_coords = gpd.read_file('./data/temp_request_grid.json')
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    def send_msgs():
        id_prefix = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        for i, coord in buf_coords.iterrows():
            x = coord.geometry.x
            y = coord.geometry.y
            try:
                res = get_temp(x, y)
                temp = res['current']['temperature_2m']
            except Exception as e:
                logging.info(str(e))
                temp = float('inf')
            logging.info(f"Batch id {id_prefix}: {temp}, {x}, {y}")
            producer.send('temp_data_bflo', f"{temp},{x},{y}")
        producer.send('batch_end_mark', id_prefix)

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_msgs, "interval", seconds=config['interval'])

    while True:
        send_msgs()
        time.sleep(300)

    # try:
    #     scheduler.start()
    # except Exception as e:
    #     logging.info(f"Error occurred: {str(e)}")
    # finally:
    #     producer.close()


if __name__ == "__main__":
    logging.info("START", )
    main()
