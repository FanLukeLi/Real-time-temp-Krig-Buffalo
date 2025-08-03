import skgstat as skg
import numpy as np
from pandas import DataFrame
from geopandas import GeoDataFrame, points_from_xy
import logging
import json


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

with open('./config.json', 'r') as f:
    config = json.load(f)


def main(df: DataFrame) -> dict:
    logging.info("Kriging interpolation started")

    gdf = GeoDataFrame(df, geometry=points_from_xy(df['longitude'], df['latitude']))
    gdf.set_crs(4326, inplace=True)
    gdf.to_crs(config['crs'], inplace=True)
    x = gdf.geometry.apply(lambda geom: geom.x)
    y = gdf.geometry.apply(lambda geom: geom.y)

    logging.info("Coordinates extracted: ")
    coords = list(zip(x.tolist(), y.tolist()))

    logging.info(f"Coordinates shape: {len(coords)}")
    try:
        V = skg.Variogram(coords, df['temperature'].tolist(),
                          maxlag=config['maxlag'],
                          n_lags=config['n_lags'],
                          normalize=bool(config['normalize']))
    except Exception as e:
        logging.error(f"Error creating Variogram: {e}")
        logging.info("Dtype of temperature column" + df['temperature'].dtype)
        raise e
    logging.info(f"Variogram created with maxlag: {config['maxlag']}, n_lags: {config['n_lags']}, normalize: {config['normalize']}")
    ok = skg.OrdinaryKriging(V, min_points=config['min_points'],
                             max_points=config['max_points'],
                             mode=config['mode'])

    logging.info(f"OrdinaryKriging created with min_points: {config['min_points']}, max_points: {config['max_points']}, mode: {config['mode']}")
    xx, yy = np.mgrid[x.min():x.max():100j, y.min():y.max():100j]
    field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
    gdf.to_crs(4326, inplace=True)
    return {"coord_x": df['longitude'].tolist(),
            "coord_y": df['latitude'].tolist(),
            "temperature": field.T}
