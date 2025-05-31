import logging
import time
import requests
import json
import datetime
import geopandas as gpd
from kafka import KafkaProducer

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


def get_batch(): 
    buf_coords = gpd.read_file('./data/temp_request_grid.json')
    n = buf_coords.shape[0]
    temps = []
    for i, coord in enumerate(buf_coords.geometry): 
        try: 
            res = get_temp(coord.x, coord.y)
            temp = res['current']['temperature_2m']
        except Exception as e: 
            logging.debug(str(e.args))
            temp = float('inf')
        logging.debug(f"[{datetime.now().strftime(r'%d/%m/%Y %H:%M:%S')}]: {i+1} of {n}")
        temps.append(temp)
    buf_coords['temperature'] = temps
    temp_gdf = buf_coords.to_crs(config['crs'])
    mean_temp = temp_gdf[temp_gdf['temperature'] != float('inf')]['temperature'].mean()
    temp_gdf[temp_gdf['temperature']==float('inf')]['temperature'].apply(lambda x: mean_temp)
    temp_gdf[temp_gdf['temperature'].isna()]['temperature'].apply(lambda x: mean_temp)
    return temp_gdf


def main(): 
    app = Application(
        broker_address="localhost:9092", 
        loglevel="DEBUG"
    )

    with app.get_producer() as producer: 
        while True: 
            temp_gdf = get_batch()
            logging.debug("Got weather")
            for _, row in temp_gdf.iterrows(): 
                producer.produce(
                    topic = "temperature_data_buffalo", 
                    key = "buffalo_ny", 
                    value = row.to_json()
                )
            producer.produce(
                topic="temperature_data_buffalo", 
                key="buffalo_ny", 
                value=json.dumps(weather)
            )
            logging.info("Produced. Sleeping...")
            time.sleep(600)
