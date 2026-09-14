import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')

idx = raw.find("※1")
if idx != -1:
    last_idx = raw.rfind("※1")
    print(raw[last_idx:last_idx+800].replace('\r', ''))
