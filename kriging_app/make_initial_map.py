from realtime_krig.prepare_grid import main as prepare_grid
from realtime_krig.extract_data import main as extract_data
from realtime_krig.kriging_interp import main as kriging_interp
from realtime_krig.visualize import main as visualize


if __name__ == '__main__': 
    prepare_grid()
    extract_data()
    res = kriging_interp()
    visualize(res['coord_x'], res['coord_y'], res['temperature'])