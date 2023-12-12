import os
import cv2
import time
import glob
import pyocr
from PIL import Image
from ogp import og_img_fail
from artwork import artwork_img_fail
from database import database_match
from revision import data
from config import masterTitle, masterArtist
from filepath import *

# OCR設定
if os.name == 'nt': # Windows
  pyocr.tesseract.TESSERACT_CMD = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
elif os.name == 'posix': # Mac or Linux
  pass
tools = pyocr.get_available_tools()
tool = tools[0]
builder = pyocr.builders.TextBuilder(tesseract_layout=6)

# トラックナンバー初期値
track_number = 0

def capture():
  global track_number
  data['check'] = 'False'

  # 共有フォルダの画像を読み込み
  filelist = {}
  for file in glob.glob('./share/*.png'):
    filelist[os.path.getmtime(file)] = file

  img_capture_path = sorted(filelist.items())[1][1]
  img = cv2.imread(img_capture_path)

  # マスタートラック画像取得
  img1 = img[392 : 420, 1210 : 1326]
  img2 = img[392 : 420, 2758 : 2874]
  master_track_1 = ocr(img1, img_master_track_1, 150, cv2.THRESH_BINARY)
  master_track_2 = ocr(img2, img_master_track_2, 150, cv2.THRESH_BINARY)

  # マスタートラック判定
  if (master_track_1 == 'MASTER') and (track_number != 1):
    track_number = 1
    print('\nMASTER TRACK: ' + str(track_number))
    txt_title, txt_artist = song_analysis(img, 340, 386, 110, 1100, 382, 420, 110, 430)
    check = True
  elif (master_track_2 == 'MASTER') and (track_number != 2):
    track_number = 2
    print('\nMASTER TRACK: ' + str(track_number))
    txt_title, txt_artist = song_analysis(img, 340, 386, 1656, 2646, 382, 420, 1656, 1976)
    check = True
  elif (master_track_1 == 'MASTER') and (track_number != 2):
    check = False
  elif (master_track_2 == 'MASTER') and (track_number != 1):
    check = False

  if check:
    og_img_fail()
    artwork_img_fail()
    database_match(txt_title, txt_artist)

def ocr(image, path, threshold, flag):
  ret, binaried = cv2.threshold(image, threshold, 255, flag)
  cv2.imwrite(path, binaried)
  img_ocr = Image.open(path)
  return tool.image_to_string(img_ocr, lang='jpn', builder=builder)


def song_analysis(img, t_top, t_bottom, t_left, t_right, a_top, a_bottom, a_left, a_right):
  for _ in range(10):
    try:
      # 楽曲名を解析
      img_title = img[t_top : t_bottom, t_left : t_right]
      txt_title = ocr(img_title, img_title_path, 190, cv2.THRESH_BINARY_INV)

      # 取得した楽曲名を補整
      txt_title = txt_title.split('\n')[0]
      txt_title = txt_title.replace(' ', '')
      if masterTitle: txt_title = masterTitle # DEBUG
      print('楽曲名: ' + txt_title)

      # アーティスト名を解析
      img_artist = img[a_top : a_bottom, a_left : a_right]
      txt_artist = ocr(img_artist, img_artist_path, 40, cv2.THRESH_BINARY_INV)

      # 取得したアーティスト名を補整
      txt_artist = txt_artist.split('\n')[0]
      txt_artist = txt_artist.replace(' ', '')
      if masterArtist: txt_artist = masterArtist # DEBUG
      if ('...' in txt_artist[-3:]) or ('…' in txt_artist[-3:]): txt_artist = txt_artist[:-3]
      print('歌手名: ' + txt_artist)

    except:
      time.sleep(1)

    else:
      return txt_title, txt_artist

  else:
    txt_title, txt_artist = '', ''
    return txt_title, txt_artist
