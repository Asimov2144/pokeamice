import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')

# Look around first 3 occurrences of CLASS="int-text"
for m in list(re.finditer(r'CLASS="int-text"', raw, re.I))[:4]:
    start = max(0, m.start() - 250)
    end = min(len(raw), m.end() + 250)
    print("--------------------------------------------------")
    print(raw[start:end])
