import json
import requests
from io import BytesIO
from mutagen.id3 import ID3
from urllib.parse import unquote
from difflib import SequenceMatcher
from config import *
from process import *

def artwork(output):
  audio_file_path = unquote(output[6].replace('file://localhost/', ''))
  if audio_file_path[audio_file_path.rfind('.'):] == '.mp3':
    artwork_img_get_offline(output, audio_file_path)
  else:
    if artwork_img_get_online(output):
      artwork_img_fail()

def artwork_img_get_offline(output, path):
  try:
    apic = ID3(path).get('APIC:')
    if apic is not None:
      artwork_img = Image.open(BytesIO(apic.data))
      resized_img = artwork_img.resize((artworkResizeSize, artworkResizeSize))
      resized_img.save(artwork_img_path)
      print('アートワークを取得しました(OFFLINE)')
    else:
      if artwork_img_get_online(output):
        artwork_img_fail()

  except:
    if artwork_img_get_online(output):
      artwork_img_fail()

def artwork_img_get_online(output):
  def itunes_api_search_encoder(params):
    s = ''
    for i, j in params.items():
      if i == 'term':
        str(j).replace('', '+')
      s += i + '=' + str(j) + '&'
    s = s[0:-1]
    return s

  def itunes_api_song_parser(json_data):
    lst_in = json_data.get('results')
    lst_ret = []
    for d_in in lst_in:
      d_ret = {
        'title':     d_in.get('trackName'),
        'artist':    d_in.get('artistName'),
        'album':     d_in.get('collectionName'),
        'artwork':   d_in.get('artworkUrl100'),
      }
      lst_ret.append(d_ret)
    return lst_ret

  def url_conversion(url):
    base_url = url.split('/')[:-1]
    base_ext = '.' + url.split('/')[-1].split('.')[-1]
    base_url.append('100000x100000-999' + base_ext)
    return '/'.join(base_url)

  try:
    title = output[1]
    artist = output[2]
    params = {
      'term':       title,
      'media':      'music',
      'entity':     'song',
      'country':    'JP',
      'lang':       'ja_jp',
      'limit':      itunesSearchLimit,
    }
    uri = 'https://itunes.apple.com/search'
    uri = uri + '?' + itunes_api_search_encoder(params)
    response = requests.get(uri)
    json_data = json.loads(response.text)
    result = itunes_api_song_parser(json_data)

    url_list = []
    for data in result:
      if SequenceMatcher(None, data['artist'], artist).ratio() > itunesRatio:
        url_list.append(url_conversion(data['artwork']))

    if url_list:
      artwork_img = Image.open(BytesIO(requests.get(url_conversion(url_list[0])).content))
      resized_img = artwork_img.resize((artworkResizeSize, artworkResizeSize))
      resized_img.save(artwork_img_path)
      print('アートワークを取得しました(ONLINE)')
      return False

  except:
    return True