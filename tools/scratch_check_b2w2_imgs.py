import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}

imgs = set()
for i in range(1, 7):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irej/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    try:
        text = raw.decode("utf-8")
    except:
        text = raw.decode("shift_jis", errors="replace")
    found = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.I)
    for f in found:
        if "img/" in f:
            imgs.add(f)

print("Images found on B2W2 pages:")
for img in sorted(imgs):
    print(" ", img)
