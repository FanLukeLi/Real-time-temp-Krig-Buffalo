import threading

import skgstat as skg
import numpy as np
from pyspark.sql import DataFrame
from pyproj import Transformer
import logging
import json


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

with open('./config.json', 'r') as f:
    config = json.load(f)


def create_logger():
    logger = logging.getLogger('kriging_logger')
    logger.setLevel(logging.INFO)
    consumer_console_handler = logging.StreamHandler()
    consumer_console_handler.setLevel(logging.INFO)
    consumer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consumer_console_handler.setFormatter(consumer_formatter)
    logger.addHandler(consumer_console_handler)
    logger.propagate = False
    logger.info("Kriging logger initialized.")
    return logger


def main(df: DataFrame, logger: logging.Logger = None, lock: threading.Lock = None) -> dict:
    if not logger:
        logger = create_logger()

    logger.info("Kriging interpolation started")

    df.toPandas().to_csv('./df.csv', index=False)
    trans = Transformer.from_crs(
        "epsg:4326",
        f"epsg:{config['crs']}",
        always_xy=True
    )

    x, y = (df.select('longitude').rdd.flatMap(lambda x: x).collect(),
            df.select('latitude').rdd.flatMap(lambda x: x).collect())

    logger.info("Coordinates extracted: ")
    coords = list(zip(x, y))

    logger.info(f"Coordinates shape: {len(coords)}")
    logger.info("Creating Variogram...")
    V = skg.Variogram(coords, np.array(df.select('temperature').rdd.flatMap(lambda x: x).collect()),
                      maxlag=config['maxlag'],
                      n_lags=config['n_lags'],
                      normalize=bool(config['normalize']))
    logger.info(f"Variogram created with maxlag: {config['maxlag']}, n_lags: {config['n_lags']}, normalize: {config['normalize']}")
    ok = skg.OrdinaryKriging(V, min_points=config['min_points'],
                             max_points=config['max_points'],
                             mode=config['mode'])

    logger.info(f"OrdinaryKriging created with min_points: {config['min_points']}, max_points: {config['max_points']}, mode: {config['mode']}")
    xx, yy = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]
    field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
    return {"coord_x": x, "coord_y": y, "temperature": field.T}
