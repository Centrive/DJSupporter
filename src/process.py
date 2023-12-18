from PIL import Image
from config import  *
from filepath import *

def og_img_fail():
  # OGP画像の取得に失敗した場合は画像更新
  Image.open(og_img_fail_path).save(og_img_path)

def artwork_img_fail():
  # アートワーク画像の取得に失敗した場合は画像更新
  Image.open(artwork_img_fail_path).save(artwork_img_path)

def ogp_to_artwork():
  # OGP画像をアートワーク画像に差し替え
  Image.open(artwork_img_path).save(og_img_path)

def image_add_margin(image):
  w1, h1 = image.size
  aw, ah = ogpAddMargin
  w2 = w1 + aw + aw
  h2 = h1 + ah + ah
  color = (255, 255, 255)
  result = Image.new(image.mode, (w2, h2), color)
  result.paste(image, (aw, ah))
  return result

def image_resize_aspect_ratio_fixed():
  image = Image.open(og_img_path).convert('RGBA')
  w, h = ogpResizeSize
  ratio = min(w / image.width, h / image.height)
  resize_size = (round(ratio * image.width), round(ratio * image.height))
  resize_image = image.resize(resize_size)

  color = (0, 0, 0, 255)
  rw, rh = resize_image.width, resize_image.height
  if w == rw:
    margin_height = int((h - rh) / 2)
    result = Image.new(resize_image.mode, (w, h), color)
    result.paste(resize_image, (0, margin_height))
  elif h == rh:
    margin_width = int((w - rw) / 2)
    result = Image.new(resize_image.mode, (w, h), color)
    result.paste(resize_image, (margin_width, 0))

  result.save(og_img_path)

def shaping(text):
  with open(shaping_name_list, 'r', encoding='UTF-8') as f:
    for task in f:
      shaping = task.replace('\n', '').split(':')
      if shaping[0] == 'split': text = text.split(shaping[1])[0].rstrip()
      if shaping[0] == 'replace': text = text.replace(shaping[1], '').rstrip()
      if shaping[0] == 'lstrip': text = text.lstrip(shaping[1]).rstrip()
      if shaping[0] == 'rstrip': text = text.rstrip(shaping[1]).rstrip()
  return text