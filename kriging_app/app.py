from flask import Flask
from extract_data import main as extract_data
from kriging_app import main as kriging_interp

app = Flask(__name__)

@app.route("/")
def hello(): 
    return "Hello, World!"