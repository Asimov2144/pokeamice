import urllib.request, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for pid, u in [
    ('PKMN-0086', 'https://www.famitsu.com/news/201208/05019240.html'),
    ('PKMN-0072', 'https://www.famitsu.com/news/201311/16043307.html')
]:
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    # find images and captions
    # Usually in table or div or p
    items = re.findall(r'(<img[^>]+src=["\']([^"\']+)["\'][^>]*>.*?(?:<p[^>]*>(.*?)</p>|<span[^>]*>(.*?)</span>|</td>))', raw, re.DOTALL | re.I)
    print(f"\n=== {pid} Captions ===")
    for full, src, p_text, span_text in items[:8]:
        if '/images/000/' in src:
            cap = p_text or span_text or ""
            cap_clean = html.unescape(re.sub(r'<[^>]+>', '', cap)).strip().replace('\n', ' ')
            print(f"  {src.split('/')[-1]}: {cap_clean[:70]}")
