import urllib.request
import re
import html

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def test_article(title, url, base_host):
    print(f"\n==========================================")
    print(f"=== {title} ===")
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    
    # Check img tags
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']([^>]*)>', raw, re.I)
    print(f"Images count: {len(img_matches)}")
    for src, extra in img_matches:
        if any(kw in src for kw in ["/images/", "feature/images", "201707-cgw227GG-pokemon", "upload"]):
            full_url = src if src.startswith("http") else base_host + src
            print(f"  IMAGE: {full_url}")
            
    # Check structure
    clean = re.sub(r'<script.*?</script>', '', raw, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Famitsu or CGWORLD article body
    if "famitsu.com" in url:
        m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', clean, re.DOTALL)
        body = m.group(1) if m else clean
        # Extract headers and p
        items = re.findall(r'<(h2|p)[^>]*>(.*?)</\1>', body, re.DOTALL)
        print(f"Famitsu extracted tags: {len(items)}")
        for tag, c in items:
            t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
            if not t:
                continue
            if tag == 'h2':
                print(f"  [H2] {t}")
            else:
                prefix = t[:25].replace('\n', ' ')
                print(f"    [P] {prefix}...")
    else:
        # CGWORLD
        m = re.search(r'<div class="main-content">(.*?)<div class="footer', clean, re.DOTALL)
        body = m.group(1) if m else clean
        items = re.findall(r'<(h2|h3|p)[^>]*>(.*?)</\1>', body, re.DOTALL)
        print(f"CGWORLD extracted tags: {len(items)}")
        for tag, c in items[:25]:
            t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
            if not t or len(t) < 5:
                continue
            if tag in ['h2', 'h3']:
                print(f"  [{tag.upper()}] {t}")
            else:
                prefix = t[:30].replace('\n', ' ')
                print(f"    [P] {prefix}...")

if __name__ == "__main__":
    test_article("PKMN-0016 Famitsu USUM 2017", "https://www.famitsu.com/news/201710/19143850.html", "https://www.famitsu.com")
    test_article("PKMN-0015 Famitsu USUM Story 2018", "https://www.famitsu.com/news/201801/02148529.html", "https://www.famitsu.com")
    test_article("PKMN-0012 CGWORLD SM 2017", "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html", "https://cgworld.jp")
