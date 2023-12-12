import os
import csv
import pathlib
import pandas as pd
from xml.etree import ElementTree
from datetime import datetime, timedelta
from filepath import *

def check():
  if not os.path.exists(xml_path): #ライブラリファイルが存在しない場合
    # スクリプトを終了
    print('iTunesライブラリファイルが見つかりません。プログラムを終了します。')
    exit()

  if os.path.exists(database_path[0]) and os.path.exists(database_path[1]): # CSVファイルが存在する場合
    # データベースの更新日時を取得(Unixtime)
    db_o = pathlib.Path(database_path[0]).stat().st_mtime
    db_t = pathlib.Path(database_path[1]).stat().st_mtime

    # スクリプト起動時の日時を取得(Unixtime)
    today = (datetime.now() - timedelta(days=+1)).timestamp()

    # 最終更新日時が1日以上前の場合、データベースを更新する
    if (db_o < today) or (db_t < today):
      print('データベースを更新します。')
      return True

    else:
      last_update = str(datetime.fromtimestamp(db_o).strftime('%Y-%m-%d %H:%M:%S'))
      print('データベースは更新されませんでした。(Last updated: ' + last_update + ')')
      return False

  else:
    # データベースを作成する
    print('ファイルが見つかりませんでした。データベースを新規作成します。')
    return True

def update():
  # 外部テキストファイルから、存在が考えられるカラム名を読み込む
  columns = []
  with open(columns_list, 'r') as f:
    for row in f:
      columns.append(row.strip())

  # カラム名だけのDataFrameを作成
  df_init = pd.DataFrame(data=None, index=None, columns=columns)

  # 出力ファイルを生成
  select_columns = columns[0:8]
  select_columns_edit = ','.join(select_columns).replace(' ', '')
  os.makedirs('./database', exist_ok=True)
  with open(database_path[0], mode='w') as f:
    f.write(select_columns_edit + '\n')

  # XML取得
  tree = ElementTree.parse(xml_path)
  root = tree.getroot()

  replace = []
  with open(shaping_name_list, 'r', encoding='UTF-8') as f:
    for task in f:
      shaping = task.replace('\n', '').split(':')
      if shaping[0] == 'replace': replace.append(shaping[1])

  exclude = []
  with open(exclude_name_list, 'r', encoding='UTF-8') as f:
    for task in f:
      exclude.append(task.split('\n'))

  # XMLから必要なものだけを抽出
  for i, r in enumerate(root):
    track_list = r.find('dict').findall('dict')

    for track in track_list:
      track_data_list = []
      for data in track:
        track_data_list.append(data.text)

      header_list = []
      data_list = []
      for i in range(len(track_data_list)):
        if (i == 0) or (i % 2 == 0):
          header_list.append(track_data_list[i]) # インデックスが偶数番目をヘッダー
        else:
          data_list.append(track_data_list[i]) # インデックスが奇数番目をデータ

      # リストから辞書型ファイルに変換
      track_dict = dict(zip(header_list, data_list))
      df_data = pd.DataFrame(track_dict.values(), index=header_list, columns=None).T

      # Nameに特定の文字列を含まないものを出力
      if((replace[0] not in str(df_data['Name'])) and \
         (replace[1] not in str(df_data['Name'])) and \
         (replace[2] not in str(df_data['Name'])) and \
         (replace[3] not in str(df_data['Name']))) or \
         (str(df_data['Name']) not in exclude):
        pd.concat([df_init,df_data]).to_csv(database_path[0], columns=select_columns, \
          encoding='UTF-8', mode='a', index=False, header=False, quoting=csv.QUOTE_ALL)

  # 出力したCSVファイルから半角スペースを削除した別ファイルを生成
  fr = open(database_path[0], 'r', encoding='UTF-8')
  csv_data = fr.read()
  fr.close()

  csv_data = csv_data.replace(' ', '')
  fw = open(database_path[1], 'w', encoding='UTF-8')
  fw.write(csv_data)
  fw.close()

  print('データベースの更新が完了しました。')