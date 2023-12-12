import sys
from threading import Timer
from functools import partial
from flask import Flask, render_template, jsonify
from capture import capture
from updateDB import check, update
from revision import data
from config import captureInterval
from filepath import *

args = sys.argv

def repeat(func, interval):
  func()
  Timer(interval, partial(repeat, func, interval)).start()

# データベース更新（1日周期）
if check() == True: update()
if len(args) > 1:
  if args[1] == 'update': update()

# メイン処理
repeat(capture, captureInterval)

# Flask設定
app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/get_data')
def get_data():
  global data
  check = data['check']
  title = data['title']
  artist = data['artist']
  comment = data['comment']
  artwork = artwork_img_path
  ogp = og_img_path

  return jsonify({
    'check': f'{check}',
    'title': f'{title}',
    'artist': f'{artist}',
    'comment': f'{comment}',
    'artwork': f'{artwork}',
    'ogp': f'{ogp}',
  })

# Flask実行
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run()