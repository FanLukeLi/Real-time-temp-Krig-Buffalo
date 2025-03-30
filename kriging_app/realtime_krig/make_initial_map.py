import folium
from prepare_grid import main as prepare_grid

import json
with open('./realtime_krig/config.json', 'r') as f: 
    config = json.load(f)


if __name__ == '__main__': 
    prepare_grid()

    m = folium.Map(location=[(config['min_lat'] + config['max_lat']) / 2,
                         (config['min_lon'] + config['max_lon']) / 2],
               zoom_start=11)
    m.save('./result/raster_map.html')
