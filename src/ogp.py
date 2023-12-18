import re
import time
import requests
import wikipediaapi
from PIL import Image
from urllib.parse import unquote
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from process import *
from config import  *
from filepath import *

# Selenium設定
option = Options()
option.add_argument('--headless')
option.add_argument('--disable-logging')
option.add_argument('--log-level=3')
option.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=option)

def ogp(genre, title):
  if title:
    if (genre == 'TVアニメ') or (genre == '映画'):
      synopsis_url = primevideo_coverimage_get(title)
      if synopsis_url: # 取得成功
        # synopsis = primevideo_synopsis_get(synopsis_url) # PrimeVideoのあらすじを取得
        detail_text_mode = 'synopsis'
      else: # 取得失敗
        annict_og_image_get(title) # Annict経由でOGP画像を取得
        # wiki_summary = wikipedia_overview_get(title) # Wikipediaの概要を取得
        detail_text_mode = 'wikipedia'
    else:
      ogp_to_artwork()
      # wiki_summary = wikipedia_overview_get(title) # Wikipediaの概要を取得
      detail_text_mode = 'wikipedia'

    if detail_text_mode == 'synopsis':
      pass
    elif detail_text_mode == 'wikipedia':
      pass

  else:
    ogp_to_artwork()

  # OGP画像の縦横比を維持した状態でリサイズ
  image_resize_aspect_ratio_fixed()

def primevideo_coverimage_get(title):
  synopsis_url = ''

  try:
    url = 'https://www.amazon.co.jp/Amazon-Video/b/?ie=UTF8&node=2351649051'
    driver.get(url)

    form = driver.find_element(By.XPATH, '//*[@id="twotabsearchtextbox"]')
    form.send_keys(title)
    form.submit()

    check = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[1]')
    pattern = re.compile(r'ありません|見つかりませんでした')
    if bool(pattern.search(check.text)):
      return synopsis_url

    for i in range(primevideoSearchRange):
      try:
        target = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{}]/div/div/span/div/div/div[2]/div[3]/div[1]/a'.format(i+1))
        if target.text == 'Prime Video':
          title_text = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{}]/div/div/span/div/div/div[2]/div[1]/h2/a/span'.format(i+1)).text
          if SequenceMatcher(None, title, title_text).ratio() > primevideoRatio:
            image = driver.find_element(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{}]/div/div/span/div/div/div[1]/span/a/div/img'.format(i+1))
            image_url = image.get_attribute('src')
            image_url = image_url.replace('UL320', 'UL960_FWwebp')
            synopsis_url = target.get_attribute('href')

            if image_url:
              image = requests.get(image_url).content
              with open(og_img_path, 'wb') as img:
                img.write(image)
              convert_img = Image.open(og_img_path).convert('RGBA')
              convert_img = image_add_margin(convert_img)
              convert_img.save(og_img_path)
              print('作品イメージを取得しました(Prime) -> {}'.format(title_text))
              break

      except:
        pass

  except:
    ogp_to_artwork()

  return synopsis_url

def primevideo_synopsis_get(url):
  output = ''

  try:
    driver.get(url)
    target_area = driver.find_element(By.CLASS_NAME, 'dv-dp-node-synopsis')
    synopsis = target_area.find_element(By.TAG_NAME, 'span')
    output = synopsis.text
    print('あらすじを取得しました')

  except:
    pass

  return output

def annict_og_image_get(title):
  try:
    shape_title = shaping(title, shaping_name_list)
    results = annict.works(filter_title=shape_title, sort_id='asc')
    if results:
      image_list = results[0].images
      image_url = image_list['recommended_url']

      if image_url:
        image = requests.get(image_url).content
        with open(og_img_path, 'wb') as img:
          img.write(image)
          convert_img = Image.open(og_img_path).convert('RGBA')
          convert_img.save(og_img_path)
        print('作品イメージを取得しました(Annict)')

      else:
        ogp_to_artwork()

    else:
      ogp_to_artwork()

  except:
    ogp_to_artwork()

def wikipedia_overview_get(title):
  shape_title = shaping(title, shaping_name_list)
  wiki = wikipediaapi.Wikipedia('ja')
  output = ''

  try:
    results = annict.works(filter_title=shape_title, sort_id='asc')
    wiki_url = results[0].wikipedia_url
    word = wiki_url.split('/')[-1]
    page = wiki.page(unquote(word))

  except:
    try:
      page = wiki.page(shape_title)
    except:
      pass

  try:
    if page.summary:
      output = page.summary#.replace('\n', '')
      output = output + '\n（Wikipediaより引用）'
      print('Wikipediaの概要を取得しました')

  except:
    pass

  return output