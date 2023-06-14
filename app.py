import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/", methods=("GET", "POST"))
def index():
    
    return render_template("index.html")

