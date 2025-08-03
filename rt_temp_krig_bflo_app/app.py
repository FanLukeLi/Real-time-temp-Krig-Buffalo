import threading
from flask import Flask, render_template
from etl.producer import main as produce
from etl.consumer import main as consume

import json
with open('./config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)

threading.Thread(target=produce, daemon=True).start()
threading.Thread(target=consume, daemon=True).start()

@app.route('/')
def home():
    return render_template(config['html_file_path'])

@app.route('/raster_map')
def serve_raster_map():
    # Example: Return updated content dynamically
    with open(config['raster_map_path']) as f:
        content = f.read()
    return content
