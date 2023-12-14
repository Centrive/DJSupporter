import time
import platform
from smb.SMBConnection import SMBConnection
from PIL import ImageGrab

def connect():
  conn = SMBConnection(
    'ceri_akina',
    'birthday',
    platform.uname().node,
    'CERI-PC')
  conn.connect('192.168.11.17', 139)
  print(conn.echo('echo success'))
  return conn

conn = connect()

i = 1
while True:
  for _ in range(3):
    try:
      filename = 'screenshot_{}.png'.format(i)
      screenshots = ImageGrab.grab()
      screenshots.save(filename)
      with open(filename, 'rb') as file:
        conn.storeFile('share', filename, file)

      if i == 3:
        i = 0
      i = i + 1

    except Exception as e:
      conn = connect()
      print('reconnect')

    else:
      print('screenshot')
      time.sleep(1)

  else:
    time.sleep(1)