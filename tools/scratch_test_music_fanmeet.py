import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for pid, u in [
    ('PKMN-0005', 'https://www.4gamer.net/games/198/G019893/20131116014/'),
    ('PKMN-0072', 'https://www.famitsu.com/news/201311/16043307.html'),
    ('PKMN-0086', 'https://www.famitsu.com/news/201208/05019240.html')
]:
    try:
        req = urllib.request.Request(u, headers=headers)
        raw = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        m = re.search(r'<title>(.*?)</title>', raw)
        ttl = html.unescape(m.group(1)).strip() if m else 'No Title'
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
        content_imgs = [i for i in imgs if any(k in i for k in ['4gamer', 'famitsu', 'image', 'photo', 'news'])]
        print(f"{pid}: {ttl[:60]} | {len(raw)} bytes | {len(content_imgs)} imgs")
        if content_imgs:
            print("  Sample img:", content_imgs[:3])
    except Exception as e:
        print(pid, "ERR:", e)
