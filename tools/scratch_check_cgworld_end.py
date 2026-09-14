import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html"
req = urllib.request.Request(url, headers=headers)
raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')

# Look for end of article in raw HTML
print("Article end indicators:")
for kw in ["月刊CGWORLD + digital video vol.227", "TEXT＿", "1メッシュ／1マテリアルのマルチテクスチャ"]:
    idx = raw.find(kw)
    print(f"Keyword '{kw}' at index {idx}")
    if idx != -1:
        print("  Snippet:", raw[idx:idx+250].replace('\n', ' '))
