import logging
from threading import Timer
from functools import partial
from flask import Flask, render_template

from config import captureInterval
from capture import capture
from update import database_update

def repeat(func, interval):
  func()
  Timer(interval, partial(repeat, func, interval)).start()

database_update()
repeat(capture, captureInterval)

# Flask settings
app = Flask(__name__)

# Flask routes
@app.route("/")
def index():
  return render_template('index.html')

# Run flask
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run()