import os
import cv2
import glob
import pytesseract
import concurrent.futures
import numpy as np
from database import database_match
from revision import data
from process import *
from config import *
from filepath import *

# OCR設定
if os.name == 'nt': # Windows
  pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
elif os.name == 'posix': # Mac or Linux
  pass

g_track_number = 0

def get_master_track():
  global g_track_number
  global data

  # 共有フォルダの画像を読み込み
  filelist = {}
  for file in glob.glob(share_imgs):
    filelist[os.path.getmtime(file)] = file
  img_capture = list(sorted(filelist.items()))[1][1]
  img = cv2.imread(img_capture)

  # マスタートラック検出
  def deck_1():
    return track_detect(img[392 : 420, 1210 : 1326])
  def deck_2():
    return track_detect(img[392 : 420, 2758 : 2874])

  with concurrent.futures.ThreadPoolExecutor() as executor:
    master_track_1 = executor.submit(deck_1).result()
    master_track_2 = executor.submit(deck_2).result()

  # マスタートラック遷移判定
  check = False
  if (master_track_1 == 'MASTER') and (g_track_number != 1): # 2->1 / 0->1
    check = True
    g_track_number = 1
    print('\nMASTER TRACK: ' + str(g_track_number))
    txt_title, txt_artist = song_analysis(img, 340, 386, 110, 1100, 382, 420, 110, 430)
  elif (master_track_2 == 'MASTER') and (g_track_number != 2): # 1->2 / 0->2
    check = True
    g_track_number = 2
    print('\nMASTER TRACK: ' + str(g_track_number))
    txt_title, txt_artist = song_analysis(img, 340, 386, 1656, 2646, 382, 420, 1656, 1976)
  elif (master_track_1 == 'MASTER') and (g_track_number != 2): # 1->1
    check = False
    g_track_number = 1
  elif (master_track_2 == 'MASTER') and (g_track_number != 1): # 2->2
    check = False
    g_track_number = 2

  # 前回からマスタートラックが遷移していた時
  if check:
    og_img_fail()
    artwork_img_fail()
    database_match(txt_title, txt_artist)

def track_detect(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  hsv_min = np.array([0, 100, 10])
  hsv_max = np.array([50, 255, 255])
  img = cv2.inRange(img, hsv_min, hsv_max)
  return pytesseract.image_to_string(img, lang='jpn+eng', config='--psm 7 --oem 1 -c preserve_interword_spaces=1').strip()

def song_analysis(img, t_top, t_bottom, t_left, t_right, a_top, a_bottom, a_left, a_right):
  def title_analysis():
    img_title = img[t_top : t_bottom, t_left : t_right]
    txt_title = pytesseract.image_to_string(img_title, lang='jpn+eng', config='--psm 7 --oem 1 -c preserve_interword_spaces=1').strip()
    if masterTitle: txt_title = masterTitle # Debug
    print('楽曲名: ' + txt_title)
    return txt_title

  def artist_analysis():
    img_artist = img[a_top : a_bottom, a_left : a_right]
    txt_artist = pytesseract.image_to_string(img_artist, lang='jpn+eng', config='--psm 7 --oem 1 -c preserve_interword_spaces=1').strip()
    if masterArtist: txt_artist = masterArtist # Debug
    if ('...' in txt_artist[-3:]) or ('…' in txt_artist[-3:]): txt_artist = txt_artist[:-3]
    print('歌手名: ' + txt_artist)
    return txt_artist

  try:
    with concurrent.futures.ThreadPoolExecutor() as executor:
      txt_title = executor.submit(title_analysis).result() # 楽曲名を解析
      txt_artist = executor.submit(artist_analysis).result() # アーティスト名を解析

  except:
    txt_title, txt_artist = '', ''

  return txt_title, txt_artist