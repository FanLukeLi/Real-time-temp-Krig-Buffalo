import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from consumer_logging import create_logger as create_clogger
from producer_logging import create_logger as create_plogger
