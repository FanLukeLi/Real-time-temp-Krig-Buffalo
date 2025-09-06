import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from producer import main as produce
from consumer import main as consume
