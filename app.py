import threading
import time
from flask import Flask, render_template
from kriging_app.extract_data import main as extract_data
from kriging_app.kriging_interp import main as kriging_interp
from kriging_app.visualize import main as visualize

app = Flask(__name__)

# Path to HTML file (make sure this file is in the 'templates' folder)
html_file_path = 'homepage.html'

def make_map(): 
    extract_data()
    res = kriging_interp()
    visualize(res['coord_x'], res['coord_y'], res['temperature'])

# Function to reload homepage
def reload_homepage():
    while True:
        print("Making new map...")
        threading.Thread(target=make_map).start()
        time.sleep(180)  # Wait for 1 hour before reloading again

# Start the reload thread
threading.Thread(target=reload_homepage, daemon=True).start()

@app.route('/')
def home():
    return render_template(html_file_path)

@app.route('/raster_map')
def serve_raster_map():
    # Example: Return updated content dynamically
    with open('./result/raster_map.html') as f:
        content = f.read()
    return content


if __name__ == '__main__':
    app.run()

