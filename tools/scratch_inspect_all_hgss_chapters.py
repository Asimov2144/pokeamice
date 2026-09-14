import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 7):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/ipkj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')
    h3_alt = re.findall(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', raw, re.I)
    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', raw, re.DOTALL | re.I)
    print(f"Chapter {i} ({fn}):")
    print(f"  Title: {h3_alt[0] if h3_alt else 'Unknown'}")
    print(f"  Dialogue turns: {len(boxes)}")
    speakers = set(b[0] for b in boxes)
    print(f"  Speakers: {speakers}")
