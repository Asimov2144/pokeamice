import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for pid, u in [
    ('PKMN-0010', 'https://dengekionline.com/elem/000/000/753/753933/'),
    ('PKMN-0011', 'https://dengekionline.com/elem/000/000/737/737734/')
]:
    try:
        req = urllib.request.Request(u, headers=headers)
        raw = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        m = re.search(r'<title>(.*?)</title>', raw)
        ttl = html.unescape(m.group(1)).strip() if m else 'No Title'
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
        elem_imgs = [i for i in imgs if 'elem' in i]
        print(f'{pid}: {ttl[:60]} | {len(raw)} bytes | {len(elem_imgs)} images')
        if elem_imgs:
            print('  Sample img:', elem_imgs[:2])
    except Exception as e:
        print(pid, 'ERR:', e)
