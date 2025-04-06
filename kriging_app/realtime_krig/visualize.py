import folium.raster_layers
import numpy as np
import folium
import branca
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from osgeo import gdal, osr
from datetime import datetime

import json
with open('./realtime_krig/config.json', 'r') as f: 
    config = json.load(f)


def create_geotiff(latitudes, longitudes, temperature_field): 
    print("Create geotiff")
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = temperature_field.shape
    string_id = datetime.now().strftime(r"%H_%M_%S_%m_%d_%Y")
    output_raster = driver.Create(f"./result/temperature_{string_id}.tif", cols, rows, 1, gdal.GDT_Float32)

    output_raster.SetGeoTransform((longitudes.min(), 
                                  longitudes[1] - longitudes[0], 0, 
                                  latitudes.max(), 
                                  latitudes[1] - latitudes[0], 0
                                  ))
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(config['crs'])
    output_raster.SetProjection(srs.ExportToWkt())

    output_raster.GetRasterBand(1).WriteArray(temperature_field)
    output_raster.FlushCache()


def main(x, y, temps): 
    latitudes = np.linspace(min(y), max(y), 100)  # Latitude range
    longitudes = np.linspace(min(x), max(x), 100)  # Longitude range
    temperature_field = temps

    m = folium.Map(location=[(latitudes.min() + latitudes.max()) / 2,
                         (longitudes.min() + longitudes.max()) / 2],
               zoom_start=11)
    
    colormap = branca.colormap.LinearColormap(
        colors=['blue', 'green', 'yellow', 'red'], 
        # vmin=temperature_field.min(), 
        vmin=0, 
        # vmax=temperature_field.max(), 
        vmax=100, 
        caption='Temerature (℉)'
    )

    # create_geotiff(latitudes=latitudes, longitudes=longitudes, temperature_field=temperature_field)

    plt.imshow(temperature_field, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
           origin='lower', cmap='coolwarm')
    plt.axis('off')
    plt.savefig("./result/temperature_png.png", bbox_inches='tight', pad_inches=0, transparent=True)

    folium.raster_layers.ImageOverlay(
        image='./result/temperature_png.png', 
        bounds=[[latitudes.min(), longitudes.min()], [latitudes.max(), longitudes.max()]], 
        opacity=0.6
    ).add_to(m)

    colormap.add_to(m)
    m.save('./result/raster_map.html')



if __name__ == '__main__': 
    # from kriging_app.realtime_krig.prepare_grid import main as prepare_grid
    # from kriging_app.realtime_krig.extract_data import main as extract_data
    from kriging_interp import main as kriging_interp
    # print("Prepare grid")
    # prepare_grid()
    # print("Extract data")
    # extract_data()
    print("Kriging interp")
    res = kriging_interp()
    main(res['coord_x'], res['coord_y'], res['temperature'])