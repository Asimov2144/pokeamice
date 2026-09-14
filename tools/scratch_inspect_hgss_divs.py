import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')

divs = re.findall(r'<div([^>]*)>(.*?)</div>', raw, re.DOTALL | re.I)
for attr, content in divs:
    txt = re.sub(r'<[^>]+>', '', content).strip()
    if any(spk in txt for spk in ["岩田", "石原", "増田", "森本"]) and len(txt) > 10:
        print(f"ATTR: {attr.strip()}")
        print(f"TEXT: {txt[:100]}...\n")
