import geopandas as gpd
import requests
import logging
from datetime import datetime

import json
with open('./realtime_krig/config.json', 'r') as f: 
    config = json.load(f)


def get_temp(x, y): 
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": y, 
        "longitude": x, 
        "current": "temperature_2m"
    }, timeout=10)
    return response.json()


def main(): 
    buf_coords = gpd.read_file('./data/temp_request_grid.json')
    n = buf_coords.shape[0]
    temps = []
    for i, coord in enumerate(buf_coords.geometry): 
        try: 
            res = get_temp(coord.x, coord.y)
            temp = res['current']['temperature_2m']
        except Exception as e: 
            print(str(e.args))
            temp = float('inf')
        print(f"[{datetime.now().strftime(r'%d/%m/%Y %H:%M:%S')}]: {i+1} of {n}")
        temps.append(temp)
    buf_coords['temperature'] = temps
    temp_gdf = buf_coords.to_crs(config['crs'])
    mean_temp = temp_gdf[temp_gdf['temperature'] != float('inf')]['temperature'].mean()
    temp_gdf[temp_gdf['temperature']==float('inf')]['temperature'].apply(lambda x: mean_temp)
    temp_gdf[temp_gdf['temperature'].isna()]['temperature'].apply(lambda x: mean_temp)
    temp_gdf.to_file('./data/temperature_data.json', driver='GeoJSON')


if __name__ == '__main__': 
    logging.basicConfig(level='DEBUG')
    buf_coords = gpd.read_file('./data/temp_request_grid.json')
    logging.info("START")
    n = buf_coords.shape[0]
    temps = []
    for i, coord in enumerate(buf_coords.geometry): 
        temp = get_temp(coord.x, coord.y)
        logging.debug(f"[{datetime.now().strftime(r'%d/%m%Y %H:%M:%S')}]: {i+1} of {n}")
        temps.append(temp['current']['temperature_2m'])
    buf_coords['temperature'] = temps
    temp_gdf = buf_coords.to_crs(config['crs'])
    temp_gdf.to_file('./data/temperature_data.json', driver='GeoJSON')

