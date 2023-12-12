import io
import csv
import difflib
import pandas as pd
from revision import comment
from config import minAccuracy, expansion, averageAccuracy
from filepath import *

# データベース読み込み
track_list = []
for path in database_path:
  with open(path, mode='r', encoding='UTF-8') as f:
    lines = csv.reader(f)
    for line in lines:
      if lines.line_num == 1: continue
      track_list.append(line)

def database_match(title, artist):
  # 最終出力
  output_list = ''

  # 抽出結果格納用リスト
  title_name_list = []
  title_ratio_list = []
  artist_ratio_list = []
  ratio_max_title = []

  # 表記揺れ防止
  title = title.upper()
  artist = artist.upper()
  title = data_shaping(title, shaping_name_list)

  try:
    if title: # OCRに成功している時
      # データベースと画像解析結果の類似度を保存
      for track in range(len(track_list)):
        ratio = difflib.SequenceMatcher(None, track_list[track][1].upper(), title).ratio() #Name
        if ratio >= minAccuracy: #最低類似度
          title_ratio_list.append(ratio)
          title_name_list.append(track_list[track])

      # 最低類似度以上の要素が1つでも存在する場合
      if title_name_list:
        # リストの中で類似度が最大のインデックスを複数取得
        title_ratio_max_indexes = [i for i, x in enumerate(title_ratio_list) if x >= (max(title_ratio_list) - expansion)]
        for index in title_ratio_max_indexes:
          ratio_max_title.append(title_name_list[index])

        # 抽出した行から歌手名が部分一致した項目を抽出
        if artist and ratio_max_title:
          for track in range(len(ratio_max_title)):
            # データベースと画像解析結果の類似度を保存
            artist_ratio = difflib.SequenceMatcher(None, ratio_max_title[track][2].upper(), artist).ratio() #Artist
            artist_ratio_list.append(artist_ratio)

          # 最低類似度以上の要素が1つでも存在する場合
          if artist_ratio_list:
            # リストの中で類似度が最大のインデックスを取得（単一）
            ratio_max_value = max(artist_ratio_list)
            ratio_max_index = artist_ratio_list.index(ratio_max_value)

            # 楽曲IDからオリジナルデータベースの情報を抽出
            with open(database_path[0], mode='r', encoding='UTF-8') as f:
              lines = f.readlines()
              id = ratio_max_title[ratio_max_index][0] # TrackID（完全一致）
              output = [line for line in lines if id in line][0]

            if not output[7]: # Commentsが存在しない場合、別の楽曲から取得を試みる
              for item in ratio_max_title:
                if (item[1] == output[1]) and (item[2] == output[2]) and item[7]: # 楽曲名と歌手名が一致かつ、コメントが存在する要素を抽出
                  output[7] = item[7] # 出力用リストに追加する
                  break

          average_ratio = (max(title_ratio_list) + max(artist_ratio_list)) / 2
          if average_ratio < averageAccuracy: output = '' # 平均類似度が低い場合はスキップ

          print('類似度: Title=' + str(round(max(title_ratio_list)*100, 1)) + \
            '%, Artist=' + str(round(max(artist_ratio_list)*100, 1)) + \
            '%, Average=' + str(round(average_ratio*100, 1)) + '%')

          output.replace('\n', '')

          if output:
            output_list = pd.read_csv(io.StringIO(output), header=None, skipinitialspace=True).values[0].tolist()

  except:
    pass

  comment(output_list)

def data_shaping(txt, path):
  text = txt
  with open(path, 'r', encoding='UTF-8') as f:
    for task in f:
      shaping = task.replace('\n', '').split(':')
      if shaping[0] == 'split': text = text.split(shaping[1])[0].rstrip()
      if shaping[0] == 'replace': text = text.replace(shaping[1], '').rstrip()
      if shaping[0] == 'lstrip': text = text.lstrip(shaping[1]).rstrip()
      if shaping[0] == 'rstrip': text = text.rstrip(shaping[1]).rstrip()
  return text