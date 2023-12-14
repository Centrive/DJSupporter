import shutil
import time

i = 0
while True:
  if i == 0:
    shutil.copy('./1/screenshot.png', '../share/screenshot_1.png')
    print('1 -> 1')
    i = i + 1
  elif i == 1:
    shutil.copy('./2/screenshot.png', '../share/screenshot_2.png')
    print('2 -> 2')
    i = i + 1
  elif i == 2:
    shutil.copy('./1/screenshot.png', '../share/screenshot_3.png')
    print('1 -> 3')
    i = i + 1

  if i == 3:
    i = 0

  time.sleep(20)