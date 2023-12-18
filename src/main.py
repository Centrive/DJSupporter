# http://127.0.0.1:5000/

import sys
import logging
from flask import Flask, render_template, jsonify
from threading import Timer
from functools import partial
from update import check, update
from capture import get_master_track
from revision import data
from config import captureInterval
from filepath import artwork_img_path, og_img_path

args = sys.argv

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.ERROR)

def repeat(func, interval):
  func()
  Timer(interval, partial(repeat, func, interval)).start()

# データベース更新
if len(args) > 1:
  if args[1] == 'update':
    print('データベースを強制更新します')
    update()
else:
  if check() == True: update()

# メイン処理
repeat(get_master_track, captureInterval)

# Flask設定
app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/setting')
def setting():
  global data
  return jsonify({
    'setting':    data['setting'],
  })

@app.route('/get_data')
def get_data():
  global data
  data['setting'] = 'False'
  return jsonify({
    'title':    data['title'],
    'artist':   data['artist'],
    'comment':  data['comment'],
    'artwork':  artwork_img_path,
    'ogp':      og_img_path,
  })

# Flask実行
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run()