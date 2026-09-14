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
    wrappers = re.findall(r'<div class="image-wrapper[^"]*">(.*?)</div>', body, re.DOTALL)
    print(f"\nImage wrappers in {url}: {len(wrappers)}")
    for w in wrappers:
        src = re.search(r'src=["\']([^"\']+)["\']', w)
        alt = re.search(r'alt=["\']([^"\']*)["\']', w)
        cap = re.search(r'<p[^>]*class="caption[^"]*"[^>]*>(.*?)</p>', w, re.DOTALL)
        print("  SRC:", src.group(1) if src else "None")
        print("  ALT:", alt.group(1) if alt else "None")
        print("  CAP:", cap.group(1).strip() if cap else "None")
