#!/usr/bin/env python
import base64
import pyotp
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from random import randint
import datetime

inkyphat = auto()
img = Image.new("P", (inkyphat.WIDTH, inkyphat.HEIGHT))

def draw_text(position, text, font=None, colour=inkyphat.BLACK):
 x, y = position
 x = x+5
 if font is None:
  font = ImageFont.truetype(FredokaOne,12) # The font size here must match test_font 
  w, h = font.getsize(text)
  mask = Image.new('1', (w, h))
  draw = ImageDraw.Draw(mask)
  draw.text((0, 0), text, 1, font)
  position = x,y
  img.paste(colour, position, mask)

# Test font size to determine the maximum number of characters per line and should match the default font used in draw_text
test_font = ImageFont.truetype(FredokaOne,12)
w, h = test_font.getsize("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ")
max_char = int((inkyphat.WIDTH/(w/45)))

quotes = open("accounts", "r")
lines = quotes.readlines()
quotes.close()
maximum = len(lines)

tokens = []
for line in lines:
  if line.strip().startswith("#"):
      pass
  elif line.__contains__(":::"):
    line_contents = line.split(":::")
    email = line_contents[0].strip()
    secret = line_contents[1].strip().upper().replace(" ", "")
    issuer = line_contents[2].strip()
    # base64.b32encode(bytes(secret, 'utf-8'))
    totp_uri_str = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)
    #print(totp_uri_str)
    totp = pyotp.parse_uri(totp_uri_str)
    token = totp.now()
    time_remaining = int(totp.interval - datetime.datetime.now().timestamp() % totp.interval)
    tokens.append({ 
      'issuer': issuer,
      'email': email,
      'token': token,
      'time_rem': time_remaining
    })

last_line = 0
for index, token in enumerate(tokens):
  try:
    draw_text((0,(last_line * 10)), str(token["email"]), colour=inkyphat.BLACK)
    last_line = last_line + 1
    draw_text((0,(last_line * 10)), str(token["issuer"]), colour=inkyphat.BLACK)
    last_line = last_line + 1
    draw_text((0,(last_line * 10)), str(token["token"]) + "  " + str(token["time_rem"]) + "secs", colour=inkyphat.BLACK)
    last_line = last_line + 1
  except IndexError:
    pass

inkyphat.set_image(img)
inkyphat.show()
