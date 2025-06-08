import logging
import json
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
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def send_msgs():
        id_prefix = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        for i, coord in enumerate(buf_coords):
            try:
                res = get_temp(coord.x, coord.y)
                temp = res['current']['temperature_2m']
            except Exception as e:
                logging.info(str(e))
                temp = float('inf')
            msg = {id_prefix: f"{temp},{coord.y},{coord.x}"}
            producer.send('temp_data_bflo', msg)

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_msgs(), "interval", seconds=config['interval'])

    try:
        scheduler.start()
    except Exception as e:
        logging.info(f"Error occurred: {str(e)}")
    finally:
        producer.close()


if __name__ == "__main__":
    logging.info("START")
    main()
