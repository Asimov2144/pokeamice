import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

u = 'https://www.famitsu.com/news/202104/30218824.html'
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
f_imgs = [i for i in imgs if '/images/000/' in i]
print('Found', len(f_imgs), 'Famitsu photos')
for img in f_imgs:
    full_u = 'https://www.famitsu.com' + img if img.startswith('/') else img
    try:
        req = urllib.request.Request(full_u, headers=headers)
        data = urllib.request.urlopen(req, timeout=5).read()
        print(' ', full_u.split('/')[-1], len(data), 'bytes OK')
    except Exception as e:
        print(' ', full_u.split('/')[-1], 'ERR:', e)
