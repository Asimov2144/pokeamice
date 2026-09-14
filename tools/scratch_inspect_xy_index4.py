import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

u = 'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index4.html'
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')

subttls = re.findall(r'<h3[^>]*class=["\']interview__ttl["\'][^>]*>(.*?)</h3>', raw, re.I | re.DOTALL)
print('Subttls in index4:', [re.sub(r'<[^>]+>', '', st).strip() for st in subttls])
boxes = re.findall(r'<div class=["\']interview__name["\']><p>(.*?)</p></div>\s*<div class=["\']interview__text["\']><p>(.*?)</p></div>', raw, re.DOTALL | re.I)
print('Turns in index4:', len(boxes))
if boxes:
    print('First turn:', boxes[0][0], re.sub(r'<[^>]+>', '', boxes[0][1])[:80])
    print('Last turn:', boxes[-1][0], re.sub(r'<[^>]+>', '', boxes[-1][1])[:80])

imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw, re.I)
print('Imgs in index4:', [img for img in imgs if any(k in img for k in ['movie', 'thumb', 'main', 'photo'])])
notes = re.findall(r'<div class=["\']interview__note["\']>(.*?)</div>', raw, re.DOTALL | re.I)
print('Notes count in index4:', len(notes))
for n in notes:
    print('  Note:', re.sub(r'<[^>]+>', '', n).strip().replace('\n', ' '))
