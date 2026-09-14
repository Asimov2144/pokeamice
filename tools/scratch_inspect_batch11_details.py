import urllib.request, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_targets = [
    ("PKMN-0043", "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx"),
    ("PKMN-0056", "https://dengekionline.com/elem/000/000/518/518926/"),
    ("PKMN-0826", "https://www.gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx"),
    ("PKMN-0676", "https://news.denfaminicogamer.jp/projectbook/xevious")
]

for pid, url in test_targets:
    try:
        req = urllib.request.Request(url, headers=headers)
        raw = urllib.request.urlopen(req, timeout=10).read()
        try:
            text = raw.decode('utf-8')
        except:
            text = raw.decode('shift_jis', errors='replace')
            
        m_title = re.search(r'<title>(.*?)</title>', text, re.I | re.DOTALL)
        title = html.unescape(m_title.group(1)).strip() if m_title else "No Title"
        print(f"\n=== [{pid}] {title} ===")
        print(f"  URL: {url} | Raw bytes: {len(raw)}")
        
        # sample some text or h1/h2
        headings = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', text, re.I | re.DOTALL)
        print(f"  Headings ({len(headings)}):", [re.sub(r'<[^>]+>', '', h).strip() for h in headings[:5]])
        
        # check image tags
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.I)
        content_imgs = [img for img in imgs if any(k in img.lower() for k in ['gameinformer', 'dengeki', 'denfami', 'upload', 'article', 'wp-content'])]
        print(f"  Images ({len(imgs)} total, {len(content_imgs)} content):", content_imgs[:3])
    except Exception as e:
        print(f"[{pid}] ERR: {e}")
