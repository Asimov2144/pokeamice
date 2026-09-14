import urllib.request, urllib.parse, re, sys
sys.stdout.reconfigure(encoding='utf-8')
u = 'http://127.0.0.1:4000/' + urllib.parse.quote('访谈翻译/翻译/访谈整理') + '/interview-iwata-asks-xy-chapter-1-global-simultaneous-release/'
html = urllib.request.urlopen(u).read().decode('utf-8')

classes = set(re.findall(r'class=["\']([^"\']+)["\']', html))
print('Relevant classes:', [c for c in classes if any(k in c.lower() for k in ['speaker', 'dialogue', 'item', 'parallel', 'translation', 'row', 'bubble'])])

speakers = re.findall(r'<strong[^>]*class=["\']speaker[^"\']*["\'][^>]*>(.*?)</strong>', html)
if not speakers:
    speakers = re.findall(r'<div class=["\']speaker["\']>(.*?)</div>', html)
if not speakers:
    speakers = re.findall(r'(岩田 聪|石原 恒和|增田 顺一)', html)
print('Speakers found:', len(speakers), speakers[:8])
