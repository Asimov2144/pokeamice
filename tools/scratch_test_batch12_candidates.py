import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

candidates = [
    ("PKMN-0091", "https://news.denfaminicogamer.jp/interview/170703/2"),
    ("PKMN-0678", "https://news.denfaminicogamer.jp/interview/180608/2"),
    ("PKMN-0050", "https://www.famitsu.com/news/202104/30218824.html"),
    ("PKMN-0694", "https://cgworld.jp/interview/creatures-201707.html")
]

for pid, url in candidates:
    try:
        req = urllib.request.Request(url, headers=headers)
        raw = urllib.request.urlopen(req, timeout=10).read()
        text = raw.decode('utf-8', errors='replace')
        m_title = re.search(r'<title>(.*?)</title>', text, re.I | re.DOTALL)
        title = html.unescape(m_title.group(1)).strip() if m_title else "No Title"
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.I)
        content_imgs = [i for i in imgs if any(k in i for k in ['upload', 'article', 'images', 'interview', 'photo', 'wp-content'])]
        print(f"[{pid}] {title[:60]}")
        print(f"  URL: {url} | Bytes: {len(raw)} | Content Imgs: {len(content_imgs)}")
        if content_imgs:
            print("  Sample img:", content_imgs[0])
    except Exception as e:
        print(f"[{pid}] ERR: {e}")
