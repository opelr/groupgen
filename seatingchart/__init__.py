"""[summary]
"""

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from .backend import create_seating_chart
# from app import routes
