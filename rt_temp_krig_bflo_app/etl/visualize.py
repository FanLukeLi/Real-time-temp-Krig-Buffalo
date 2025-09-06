import folium.raster_layers
import numpy as np
import folium
import branca
import matplotlib
import logging
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

import json
with open('./config.json', 'r') as f:
    config = json.load(f)


def create_logger():
    logger = logging.getLogger('visulaize_logger')
    logger.setLevel(logging.INFO)
    consumer_console_handler = logging.StreamHandler()
    consumer_console_handler.setLevel(logging.INFO)
    consumer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consumer_console_handler.setFormatter(consumer_formatter)
    logger.addHandler(consumer_console_handler)
    logger.propagate = False
    logger.info("Visualizer logger initialized.")
    return logger


def main(x, y, temps, logger: logging.Logger = None):
    if not logger:
        logger = create_logger()

    logger.info("A new thread is started to visualize Kriging result")
    latitudes = np.linspace(min(y), max(y), 100)  # Latitude range
    longitudes = np.linspace(min(x), max(x), 100)  # Longitude range
    temperature_field = temps

    m = folium.Map(location=[(latitudes.min() + latitudes.max()) / 2,
                         (longitudes.min() + longitudes.max()) / 2],
               zoom_start=11)
    
    colormap = branca.colormap.LinearColormap(
        colors=['blue', 'green', 'yellow', 'red'], 
        vmin=temperature_field.min(),
        vmax=temperature_field.max(),
        caption='Temerature (℉)'
    )

    logger.info("Created image of temperature field")
    plt.imshow(temperature_field, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
           origin='lower', cmap='coolwarm')
    plt.axis('off')
    plt.savefig("./result/temperature_png.png", bbox_inches='tight', pad_inches=0, transparent=True)

    logger.info("Created folium map with temperature overlay")
    folium.raster_layers.ImageOverlay(
        image='./result/temperature_png.png', 
        bounds=[[latitudes.min(), longitudes.min()], [latitudes.max(), longitudes.max()]], 
        opacity=0.6
    ).add_to(m)
    colormap.add_to(m)

    logger.info("Saving map to HTML")
    try:
        m.save('./result/raster_map.html')
    except Exception as e:
        logger.error(f"Error saving map: {e}")



if __name__ == '__main__':
    print("Kriging interp")