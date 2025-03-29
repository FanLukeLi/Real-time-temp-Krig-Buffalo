import geopandas as gpd
import skgstat as skg
import numpy as np

import json
with open('./config.json', 'r') as f: 
    config = json.load(f)


def main(): 
    temp_gdf = gpd.read_file('./data/temperature_data.json')
    
    x = temp_gdf.geometry.apply(lambda geom: geom.x)
    y = temp_gdf.geometry.apply(lambda geom: geom.y)

    coords = list(zip(x.tolist(), y.tolist()))

    V = skg.Variogram(coords, temp_gdf['temperature'].tolist(), 
                      maxlag=config['maxlag'], 
                      n_lags=config['n_lags'], 
                      normalize=bool(config['normalize']))
    ok = skg.OrdinaryKriging(V, min_points=config['min_points'], 
                             max_points=config['max_points'], 
                             mode=config['mode'])
    
    xx, yy = np.mgrid[x.min():x.max():100j, y.min():y.max():100j]
    field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
    temp_gdf.to_crs(4326, inplace=True)
    return {"coord_x": temp_gdf.geometry.apply(lambda geom: geom.x).tolist(), 
            "coord_y": temp_gdf.geometry.apply(lambda geom: geom.y).tolist(), 
            "temperature": field.T}


if __name__ == '__main__': 
    main()
