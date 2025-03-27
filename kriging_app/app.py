from flask import Flask
import time
from collections import deque
from datetime import datetime
from threading import Thread
from extract_data import main as extract_data
from kriging_app import main as kriging_interp
from visualize import main as visualize

app = Flask(__name__)


@app.route("/")
def hello(): 
    queue = deque([datetime.now().hour])

    def maintain_queue(): 
        queue.append(queue[-1] + 1)

    
    def make_html(): 
        extract_data()
        res = kriging_interp()
        visualize(res['coord_x'], res['coord_y'], res['temperature'])
        # Reload html


    while queue: 
        maintain_queue()
        Thread(make_html).start()
        time.sleep(3600)

    return "Hello, World!"