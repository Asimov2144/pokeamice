import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in [
    'https://www.famitsu.com/news/201710/19143850.html',
    'https://www.famitsu.com/news/201801/02148529.html',
    'https://cgworld.jp/feature/201707-cgw227GG-pokemon.html'
]:
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    pages = re.findall(r'href=[\'"]([^\'"]*page=\d+[^\'"]*)[\'"]', raw, re.I)
    print(f"URL: {url}")
    print(f"Pagination links found: {set(pages)}")
