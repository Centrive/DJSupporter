import os

# 解析画像ファイル
share_imgs = '../share/*.png'

# 出力画像ファイル
artwork_img_path = './static/artwork_img.png'
artwork_img_fail_path = '../images/artwork_img_fail.png'
og_img_path = './static/og_img.png'
og_img_fail_path = '../images/og_img_fail.png'

# 設定ファイル
columns_list = '../config/db_columns.txt'
shaping_name_list = '../config/shaping_name.txt'
exclude_name_list = '../config/exclude_name.txt'

# データベース
database_path = ['../database/db_original.csv', '../database/db_trim.csv']
if os.name == 'nt': # Windows
  xml_path = r'\\CERI-NAS\\music\\iTunes\\iTunes Library.xml'
elif os.name == 'posix': # Mac or Linux
  xml_path = '../test/iTunes Library.xml'