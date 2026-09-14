import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

all_spks = set()
for fn in ['index.html', 'index2.html', 'index3.html', 'index4.html']:
    u = f'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/{fn}'
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    boxes = re.findall(r'<div class=["\']interview__name["\']><p>(.*?)</p></div>', raw, re.DOTALL | re.I)
    for spk in boxes:
        all_spks.add(re.sub(r'<[^>]+>', '', spk).strip())

print('All speakers found:', all_spks)
