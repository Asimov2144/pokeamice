import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in [
    'https://www.famitsu.com/news/201710/19143850.html',
    'https://www.famitsu.com/news/201801/02148529.html'
]:
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', raw, re.DOTALL)
    body = m.group(1) if m else raw
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']([^>]*)>', body, re.I)
    print(f"\nImages in {url}:")
    for src, extra in imgs:
        print(" ", src)
