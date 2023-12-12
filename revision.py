from artwork import artwork_img_get
from ogp import ogp_core

data = {'check':'', 'title': '', 'artist': '', 'comment': ''}

def comment(output):
  try:
    if '『' in str(output[-1]): # コメントが存在する場合
      comments = output[7] # Comments
      title = comments[comments.find('『')+1:comments.find('』')]
      genre = comments[:comments.find('『')]
      summary = comments[comments.find('』')+1:]

      # 番組分類を書き換える
      # if '企画' in genre: genre = genre.replace('企画', 'プロジェクト')

      # 摘要を書き換える
      # if 'OP' in summary: summary = summary.replace('OP', 'オープニング')
      # if 'ED' in summary: summary = summary.replace('ED', 'エンディング')
      if 'IN' in summary: summary = summary.replace('IN', '挿入歌')
      if 'IM' in summary: summary = summary.replace('IM', 'イメージソング')
      if 'TM' in summary: summary = summary.replace('TM', 'テーマソング')

      result = genre + '『' + title + '』' + summary
      print('番組名: ' + result)

    else:
      title, genre, summary, result = '', '', '', ''

    # 追加情報取得
    ogp_core(output, title, genre)

    # アートワーク取得
    artwork_img_get(output)

    global data
    data['check'] = 'True'
    data['title'] = output[1]
    data['artist'] = output[2]
    data['comment'] = result

  except:
    pass