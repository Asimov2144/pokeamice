import urllib.request, re, html, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== 1. TEST PARSING PKMN-0043 (GI HGSS) ===")
u1 = "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx"
raw1 = urllib.request.urlopen(urllib.request.Request(u1, headers=headers)).read().decode('utf-8')
# Find the main article container
m_body = re.search(r'<div class=["\']field-body["\'][^>]*>(.*?)</div>\s*<div class=["\']field-tags["\']', raw1, re.DOTALL | re.I)
if not m_body:
    # fallback to between article title and footer
    start = raw1.find('field-body')
    end = raw1.find('field-tags')
    body_text1 = raw1[start:end] if start != -1 and end != -1 else raw1
else:
    body_text1 = m_body.group(1)

# Extract paragraphs or Q&A
qa_pairs1 = []
paras1 = re.findall(r'<p>(.*?)</p>', body_text1, re.DOTALL | re.I)
for p in paras1:
    clean = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
    if clean and not any(clean.startswith(x) for x in ['Share', 'Related Games', 'Review']):
        qa_pairs1.append(clean)

print(f"GI HGSS extracted {len(qa_pairs1)} paragraphs.")
for i, p in enumerate(qa_pairs1[:4]):
    print(f"  [{i}] {p[:80]}...")

print("\n=== 2. TEST PARSING PKMN-0086 (Famitsu B2W2 Event) ===")
u2 = "https://www.famitsu.com/news/201208/05019240.html"
raw2 = urllib.request.urlopen(urllib.request.Request(u2, headers=headers)).read().decode('utf-8')
# Famitsu article body
m_article2 = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw2, re.DOTALL | re.I)
if not m_article2:
    m_article2 = re.search(r'<div[^>]*id=["\']article-body["\'][^>]*>(.*?)</div>', raw2, re.DOTALL | re.I)
body2 = m_article2.group(1) if m_article2 else raw2

paras2 = re.findall(r'<p[^>]*>(.*?)</p>', body2, re.DOTALL | re.I)
clean_paras2 = []
for p in paras2:
    c = html.unescape(re.sub(r'<br\s*/?>', '\n', p))
    c = re.sub(r'<[^>]+>', '', c).strip()
    if c and not any(k in c for k in ['Twitter', 'Facebook', 'ファミ通.com']):
        clean_paras2.append(c)

print(f"Famitsu B2W2 extracted {len(clean_paras2)} paragraphs.")
for i, p in enumerate(clean_paras2[:4]):
    print(f"  [{i}] {p[:80]}...")

imgs2 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', body2, re.I)
print(f"Famitsu B2W2 images found: {len(imgs2)} =>", imgs2[:4])

print("\n=== 3. TEST PARSING PKMN-0072 (Famitsu XY Music) ===")
u3 = "https://www.famitsu.com/news/201311/16043307.html"
raw3 = urllib.request.urlopen(urllib.request.Request(u3, headers=headers)).read().decode('utf-8')
m_article3 = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw3, re.DOTALL | re.I)
if not m_article3:
    m_article3 = re.search(r'<div[^>]*id=["\']article-body["\'][^>]*>(.*?)</div>', raw3, re.DOTALL | re.I)
body3 = m_article3.group(1) if m_article3 else raw3

paras3 = re.findall(r'<p[^>]*>(.*?)</p>', body3, re.DOTALL | re.I)
clean_paras3 = []
for p in paras3:
    c = html.unescape(re.sub(r'<br\s*/?>', '\n', p))
    c = re.sub(r'<[^>]+>', '', c).strip()
    if c and not any(k in c for k in ['Twitter', 'Facebook', 'ファミ通.com']):
        clean_paras3.append(c)

print(f"Famitsu XY Music extracted {len(clean_paras3)} paragraphs.")
for i, p in enumerate(clean_paras3[:4]):
    print(f"  [{i}] {p[:80]}...")

imgs3 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', body3, re.I)
print(f"Famitsu XY Music images found: {len(imgs3)} =>", imgs3[:4])
