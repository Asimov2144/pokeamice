import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

u = 'https://www.famitsu.com/article/202411/23904'
try:
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers), timeout=8).read().decode('utf-8')
    m = re.search(r'<title>(.*?)</title>', raw)
    print("Title:", html.unescape(m.group(1)).strip() if m else 'No Title')
    print("Bytes:", len(raw))
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw)
    content_imgs = [i for i in imgs if 'images' in i or 'article' in i or 'media' in i]
    print("Images count:", len(imgs), "Content imgs:", len(content_imgs))
    if content_imgs:
        print("Sample content img:", content_imgs[0])
except Exception as e:
    print("ERR:", e)
