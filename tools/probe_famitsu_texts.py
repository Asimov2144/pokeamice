import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def print_clean_famitsu(name, url):
    print(f"\n==================================================")
    print(f"=== {name} ===")
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    clean = re.sub(r'<script.*?</script>', '', raw, flags=re.DOTALL | re.I)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.I)
    m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', clean, re.DOTALL)
    body = m.group(1) if m else clean
    items = re.findall(r'<(h2|p)[^>]*>(.*?)</\1>', body, re.DOTALL)
    for i, (tag, c) in enumerate(items):
        t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
        if not t:
            continue
        print(f"[{i:02d}][{tag.upper()}] {t}\n")

if __name__ == '__main__':
    print_clean_famitsu('PKMN-0016 Famitsu USUM 2017', 'https://www.famitsu.com/news/201710/19143850.html')
    print_clean_famitsu('PKMN-0015 Famitsu USUM Story 2018', 'https://www.famitsu.com/news/201801/02148529.html')
