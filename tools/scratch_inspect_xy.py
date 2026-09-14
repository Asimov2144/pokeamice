import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

for fn in ['index.html', 'index2.html', 'index3.html']:
    u = f'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/{fn}'
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    try:
        decoded = raw.decode('utf-8')
    except:
        decoded = raw.decode('shift_jis', errors='replace')
    
    print('===', fn, 'len:', len(decoded))
    title_m = re.search(r'<title>(.*?)</title>', decoded, re.I | re.DOTALL)
    if title_m:
        print('  Title:', title_m.group(1).strip())
    headings = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', decoded, re.I | re.DOTALL)
    for h in headings[:5]:
        print('  Heading:', re.sub(r'<[^>]+>', '', h).strip())
    
    classes = set(re.findall(r'class=["\']([^"\']+)["\']', decoded, re.I))
    print('  Classes:', [c for c in classes if any(k in c.lower() for k in ['name', 'text', 'int', 'talk', 'box', 'main', 'movie', 'photo', 'voice', 'body'])])
    
    m = re.search(r'(岩田|石原|増田)', decoded)
    if m:
        pos = m.start()
        print('  Snippet around speaker:', decoded[pos-50:pos+250].replace('\n', ' '))
