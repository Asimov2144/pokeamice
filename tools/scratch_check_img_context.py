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
    # find where img occurs
    for match in re.finditer(r'<img[^>]+>', body):
        start = max(0, match.start() - 100)
        end = min(len(body), match.end() + 100)
        print(f"--- IMG in {url} ---")
        print(body[start:end].strip())
