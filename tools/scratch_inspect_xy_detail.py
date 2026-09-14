import urllib.request, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

for i, fn in enumerate(['index.html', 'index2.html', 'index3.html'], 1):
    u = f'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/{fn}'
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    decoded = raw.decode('utf-8', errors='replace')
    
    # H3 or interview__ttl
    subttls = re.findall(r'<h3[^>]*class=["\']interview__ttl["\'][^>]*>(.*?)</h3>', decoded, re.I | re.DOTALL)
    print(f"\n==================== CHAPTER {i}: {fn} ====================")
    for st in subttls:
        print("  Subttl:", re.sub(r'<[^>]+>', '', st).strip())
        
    boxes = re.findall(r'<div class=["\']interview__name["\']><p>(.*?)</p></div>\s*<div class=["\']interview__text["\']><p>(.*?)</p></div>', decoded, re.DOTALL | re.I)
    print(f"  Turns count: {len(boxes)}")
    for j, (spk, body) in enumerate(boxes[:3]):
        b_clean = re.sub(r'<br\s*/?>', ' ', body)
        b_clean = re.sub(r'<[^>]+>', '', b_clean).strip()
        print(f"    [{spk}] {b_clean[:60]}...")
    print("    ...")
    for j, (spk, body) in enumerate(boxes[-2:]):
        b_clean = re.sub(r'<br\s*/?>', ' ', body)
        b_clean = re.sub(r'<[^>]+>', '', b_clean).strip()
        print(f"    [{spk}] {b_clean[:60]}...")
        
    # Check notes and images/videos
    notes = re.findall(r'<div class=["\']interview__note["\']>(.*?)</div>', decoded, re.DOTALL | re.I)
    print(f"  Notes count: {len(notes)}")
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', decoded, re.I)
    print(f"  Imgs count: {len(imgs)} =>", [img for img in imgs if 'interview' in img or 'photo' in img or 'movie' in img or 'chara' in img or 'pkg' in img or 'main' in img])
    movies = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', decoded, re.I)
    print(f"  Iframes/Videos: {movies}")
