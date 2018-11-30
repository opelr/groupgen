"""[summary]
"""

from flask import Flask
from config import Config

from .backend import create_seating_chart

app = Flask(__name__)
app.config.from_object(Config)
