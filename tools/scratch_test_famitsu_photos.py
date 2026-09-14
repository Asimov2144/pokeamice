import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for pid, u in [
    ('PKMN-0086', 'https://www.famitsu.com/news/201208/05019240.html'),
    ('PKMN-0072', 'https://www.famitsu.com/news/201311/16043307.html')
]:
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
    f_imgs = [i for i in imgs if '/images/000/' in i]
    print(pid, 'found', len(f_imgs), 'photos:')
    for img in f_imgs[:5]:
        full_u = 'https://www.famitsu.com' + img if img.startswith('/') else img
        try:
            req = urllib.request.Request(full_u, headers=headers)
            size = len(urllib.request.urlopen(req, timeout=5).read())
            print(' ', full_u.split('/')[-1], size, 'bytes')
        except Exception as e:
            print(' ', full_u.split('/')[-1], 'ERR:', e)
