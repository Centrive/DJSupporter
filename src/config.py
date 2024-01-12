from annict.api import API

# デバッグ用（本番稼働時は空にする）
masterTitle   = '爆ぜて咲く'
masterArtist  = 'トゲンシトゲアリ'

# インターバル
captureInterval = 1 # seconds

# 楽曲解析パラメータ
minAccuracy     = 0.4 # 精度最低値
expansion       = 0.1 # 精度許容範囲
averageAccuracy = 0.4 # 精度平均閾値
itunesRatio       = 0.5 # iTunes検索結果との類似度
itunesSearchLimit = 30  # iTunes検索上限
primevideoRatio       = 0.82 # Amazon検索結果との類似度
primevideoSearchRange = 10 # Amazon検索上限

# 画像加工パラメータ
artworkResizeSize = 500 # アートワーク画像のリサイズサイズ（正方形）
ogpResizeSize = (920, 700) # OGP画像のリサイズサイズ
ogpAddMargin = (0, 0) # OGP画像に追加する余白サイズ

# Annict設定
annict = API('icl9hHdf_GNVWse-XxPOC6hOiN37vJfRwvswnXvtjSI')