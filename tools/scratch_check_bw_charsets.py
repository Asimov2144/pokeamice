import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 6):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irbj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    charset = re.search(rb'charset=([a-zA-Z0-9_\-]+)', raw, re.I)
    enc = charset.group(1).decode('ascii') if charset else "unknown"
    print(f"{fn}: charset in HTML = {enc}")
