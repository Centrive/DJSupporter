import io
import ast
import csv
import pandas as pd
from difflib import SequenceMatcher
from revision import revision
from process import shaping
from config import  *
from filepath import *

# データベース取得
track_list = []
for path in database_path:
  with open(path, mode='r', encoding='UTF-8') as f:
    lines = csv.reader(f)
    for line in lines:
      if lines.line_num == 1: continue
      track_list.append(line)

def database_match(title, artist):
  # 最終出力
  output = ''

  # 抽出結果格納用リスト
  title_ratio_list = []
  title_name_list = []
  title_ratio_max_list = []
  artist_ratio_list = []

  # 表記揺れ防止
  title = shaping(title.upper())
  artist = artist.upper()

  # 解析
  try:
    if title: # OCRに成功している時
      # データベースとOCR結果の類似度を保存(Name)
      for i, track in enumerate(track_list):
        ratio = SequenceMatcher(None, track[1].upper(), title).ratio()
        if ratio >= minAccuracy: # 最低類似度以上の要素を抽出
          title_ratio_list.append(ratio)
          title_name_list.append(track_list[i])

      if title_name_list: # 最低類似度以上の要素が1つでも存在する時
        # リストの中で類似度が最大のインデックスを複数取得
        title_ratio_max_indexes = [i for i, x in enumerate(title_ratio_list) if x >= (max(title_ratio_list) - expansion)]
        for index in title_ratio_max_indexes:
          title_ratio_max_list.append(title_name_list[index])

        # 抽出した行から歌手名が部分一致した項目を抽出
        for i, track in enumerate(title_ratio_max_list):
          # データベースとOCR結果の類似度を保存(Artist)
          artist_ratio = SequenceMatcher(None, track[2].upper(), artist).ratio()
          artist_ratio_list.append(artist_ratio)

        # リストの中で類似度が最大のインデックスを取得
        ratio_max_index = artist_ratio_list.index(max(artist_ratio_list))

        # 楽曲IDを元にデータベースの情報を抽出
        with open(database_path[0], mode='r', encoding='UTF-8') as f:
          lines = f.readlines()
          id = title_ratio_max_list[ratio_max_index][0] # TrackID が完全一致する要素を抽出
          output = [line for line in lines if id in line][0].replace('\n', '')
          output = pd.read_csv(io.StringIO(output), header=None, skipinitialspace=True).values[0].tolist()
          if not output[7]: # Commentsが存在しない場合、別の楽曲から取得を試みる
            for track in title_ratio_max_list:
              if (track[1] == output[1]) and (track[2] == output[2]) and (track[7] != ''): # 楽曲名と歌手名が一致かつ、コメントが存在する要素を抽出
                output[7] = track[7] # 出力用リストに追加する
                break

        average_ratio = (max(title_ratio_list) + max(artist_ratio_list)) / 2
        if average_ratio < averageAccuracy: output = '' # 平均類似度が低い場合はスキップ

        print('類似度: Title=' + str(round(max(title_ratio_list)*100, 1)) + \
          '%, Artist=' + str(round(max(artist_ratio_list)*100, 1)) + \
          '%, Average=' + str(round(average_ratio*100, 1)) + '%')

  except:
    pass

  revision(output)
