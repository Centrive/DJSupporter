import concurrent.futures
from ogp import *
from artwork import *

data = {'setting':'', 'title': '', 'artist': '', 'comment': ''}

def revision(output):
  if output:
    genre, title, summary, result = comment(output)

    with concurrent.futures.ThreadPoolExecutor() as executor:
      executor.submit(artwork(output))
      executor.submit(ogp(genre, title))

    global data
    data['setting'] = 'True'
    data['title'] = output[1]
    data['artist'] = output[2]
    data['comment'] = result

def comment(output):
  genre, title, summary, result = '', '', '', ''

  try:
    if '『' in str(output[-1]): # コメントが存在する場合
      comments = output[7] # Comments
      genre = comments[:comments.find('『')]
      title = comments[comments.find('『')+1:comments.find('』')]
      summary = comments[comments.find('』')+1:]

      # 番組分類を書き換える
      if '企画' in genre: genre = genre.replace('企画', '')

      # 摘要を書き換える
      # if 'OP' in summary: summary = summary.replace('OP', 'オープニング')
      # if 'ED' in summary: summary = summary.replace('ED', 'エンディング')
      if 'IN' in summary: summary = summary.replace('IN', '挿入歌')
      if 'IM' in summary: summary = summary.replace('IM', 'イメージソング')
      if 'TM' in summary: summary = summary.replace('TM', 'テーマソング')

      result = genre + '『' + title + '』' + summary
      print('番組名: ' + result)

  except:
    pass

  return genre, title, summary, result