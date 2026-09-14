import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')

# Look for table or div or dt/dd
for tag in ['div', 'table', 'dl', 'dt', 'dd', 'span', 'tr', 'td']:
    matches = re.findall(rf'<{tag}[^>]*>(.*?)</{tag}>', raw, re.DOTALL | re.I)
    if matches:
        print(f"Tag <{tag}> count: {len(matches)}")
        for m in matches[:3]:
            txt = re.sub(r'<[^>]+>', '', m).strip()
            if txt:
                print(f"  <{tag}>: {txt[:60]}")
