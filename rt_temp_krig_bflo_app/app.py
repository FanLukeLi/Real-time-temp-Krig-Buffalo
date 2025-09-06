import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template
from etl import produce, consume
from loggers import create_clogger, create_plogger

import json

with open('./config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)

lock = threading.Lock()

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.submit(produce, create_plogger(), lock)
    executor.submit(consume, create_clogger(), lock)

@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/raster-map')
def serve_raster_map():
    # Example: Return updated content dynamically
    with open(config['raster_map_path']) as f:
        content = f.read()
    return content


@app.route('/test')
def test():
    return True
