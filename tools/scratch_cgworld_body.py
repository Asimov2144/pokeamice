import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html"
raw = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8', errors='replace')

# Cut between start and end
start_marker = "ニンテンドー3DSにおけるシリーズ第3弾"
end_marker = "1メッシュ／1マテリアルのマルチテクスチャも使用されている"

start_pos = raw.find(start_marker)
end_pos = raw.find(end_marker) + len(end_marker)

sub = raw[start_pos:end_pos]
clean = re.sub(r'<script.*?</script>', '', sub, flags=re.DOTALL | re.I)
clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.I)

# Extract paragraphs, headings
blocks = re.findall(r'<(h2|h3|h4|p)[^>]*>(.*?)</\1>', clean, re.DOTALL)
print(f"Blocks in range: {len(blocks)}")

meaningful = []
for tag, c in blocks:
    t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
    if not t or len(t) < 8:
        continue
    if any(bad in t for bad in ["TEXT＿", "EDIT＿", "PHOTO＿", "information"]):
        continue
    meaningful.append((tag, t))

print(f"Meaningful blocks: {len(meaningful)}")
for i, (tag, t) in enumerate(meaningful):
    print(f"[{i:02d}][{tag.upper()}] {t[:60]}...")
