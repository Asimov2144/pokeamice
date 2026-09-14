import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for i in [1, 2, 3]:
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/ipkj/vol1/{fn}"
    req = urllib.request.Request(u, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('shift_jis', errors='replace')
    
    # Check images
    imgs = re.findall(r'<img[^>]+(?:src|alt)=["\']([^"\']+)["\']', raw, re.I)
    alts = re.findall(r'alt=["\']([^"\']+)["\']', raw, re.I)
    
    print(f"\n================ Chapter {i} ({fn}) ================")
    print("Alts found:", [a for a in alts if len(a) > 2][:8])
    
    # Check text paragraphs
    clean = re.sub(r'<script.*?</script>', '', raw, flags=re.DOTALL | re.I)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.I)
    
    ps = re.findall(r'<p[^>]*>(.*?)</p>', clean, re.DOTALL)
    print(f"Total <p> tags: {len(ps)}")
    for p in ps[:6]:
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        if t:
            print("  P:", t[:90])
