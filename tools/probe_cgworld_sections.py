import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html"
req = urllib.request.Request(url, headers=headers)
raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
clean = re.sub(r'<script.*?</script>', '', raw, flags=re.DOTALL | re.I)
clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.I)

m = re.search(r'<div class="main-content">(.*?)<div class="footer', clean, re.DOTALL)
body = m.group(1) if m else clean

blocks = re.findall(r'<(h2|h3|p)[^>]*>(.*?)</\1>', body, re.DOTALL)
print(f"Total blocks in CGWORLD: {len(blocks)}")

meaningful = []
for tag, c in blocks:
    t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
    if not t or len(t) < 10:
        continue
    if any(bad in t for bad in ["TEXT＿", "EDIT＿", "information", "©2016 Pokémon", "月刊CGWORLD + digital video vol.227"]):
        continue
    meaningful.append((tag, t))

print(f"Meaningful blocks: {len(meaningful)}")
for i, (tag, t) in enumerate(meaningful[:20]):
    print(f"[{i:02d}][{tag.upper()}] {t[:80]}...")
print("...")
for i, (tag, t) in enumerate(meaningful[-10:]):
    print(f"[-{10-i:02d}][{tag.upper()}] {t[:80]}...")
