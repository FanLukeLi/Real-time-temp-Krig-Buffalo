import logging
import json
import time

import requests
import datetime
import geopandas as gpd
from kafka import KafkaProducer
from apscheduler.schedulers.background import BackgroundScheduler

with open('./config.json', 'r') as f:
    config = json.load(f)

def get_temp(x, y): 
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": y, 
        "longitude": x, 
        "current": "temperature_2m", 
        "temperature_unit": "fahrenheit"
    }, timeout=10)
    return response.json()


def main():
    buf_coords = gpd.read_file('./data/temp_request_grid.json')
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    def send_msgs():
        id_prefix = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        for i, coord in buf_coords.iterrows():
            x = coord.geometry.x
            y = coord.geometry.x
            try:
                res = get_temp(x, y)
                temp = res['current']['temperature_2m']
            except Exception as e:
                logging.info(str(e))
                temp = float('inf')
            msg = {id_prefix: f"{temp},{x},{y}"}
            print(msg)
            producer.send('temp_data_bflo', msg)

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
    logging.info("START")
    main()
