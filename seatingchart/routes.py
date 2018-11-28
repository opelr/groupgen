from flask import render_template, request
from seatingchart import app


@app.route("/")
@app.route("/index")
def index():
    None
    return render_template("index.html")
