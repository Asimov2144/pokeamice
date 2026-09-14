import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

u = "https://www.famitsu.com/news/202104/30218824.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
body = m_body.group(1) if m_body else raw

items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
clean_items = []
for tag, content in items:
    c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
    c = re.sub(r'<[^>]+>', '', c).strip()
    if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', '関連記事', '(C)20', '※', '株式会社']):
        clean_items.append((tag, c))

print(f"\n=== PKMN-0050 (Famitsu New Pokemon Snap) ===")
print(f"Extracted {len(clean_items)} elements:")
for tag, c in clean_items[:6]:
    print(f"  <{tag}> {c[:70]}...")
