import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

for fn in ['index.html', 'index2.html', 'index3.html']:
    u = f'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/{fn}'
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    print("=== FN:", fn)
    for m in re.findall(r'<div class=["\']interview__movie["\']>(.*?)</div>', raw, re.DOTALL):
        print("Movie block:", m.strip())
    for m in re.findall(r'<div class=["\']interview__note["\']>(.*?)</div>', raw, re.DOTALL):
        print("Note block:", m.strip().replace('\n', ' '))
