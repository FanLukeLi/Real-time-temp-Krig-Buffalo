import geopandas as gpd
from math import sqrt
from shapely import Point, within, unary_union

import json
with open('./kriging_app/config.json', 'r') as f: 
    config = json.load(f)


def generate_request_grid(minx, miny, lon_span, lat_span): 
    unit_length = config['unit_length']
    coords = []
    startx1, starty1 = (lon_span % unit_length) / 2 + minx, (lat_span % (unit_length * sqrt(3))) / 2 + miny
    startx2, starty2 = startx1 + unit_length / 2, starty1 + unit_length * sqrt(3) / 2
    xspan1, yspan1 = int(lon_span // unit_length) + 1, int(lat_span // (unit_length * sqrt(3))) + 1
    xspan2, yspan2 = int((lon_span - lon_span % unit_length - unit_length / 2) // unit_length) + 1, int((lat_span - lat_span % (unit_length * sqrt(3)) - unit_length / 2 * sqrt(3)) // (unit_length * sqrt(3))) + 1
    for i1 in range(xspan1): 
        for j1 in range(yspan1): 
            coords.append(Point(startx1 + i1 * unit_length, starty1 + j1 * unit_length * sqrt(3)))
    for i2 in range(xspan2):
        for j2 in range(yspan2): 
            coords.append(Point(startx2 + i2 * unit_length, starty2 + j2 * unit_length * sqrt(3)))
    return gpd.GeoSeries(coords).set_crs(config['crs']).to_crs(4326)


def main(): 
    coords = generate_request_grid(config['minx'], config['miny'], config['lon_span'], config['lat_span'])
    gdf = gpd.read_file('./data/Buffalo_CS.shp')
    buf_coords = coords[within(coords, unary_union(gdf.geometry.tolist()))]
    buf_coords.to_file('./data/temp_request_grid.json', driver='GeoJSON')


if __name__ == '__main__': 
    main()
