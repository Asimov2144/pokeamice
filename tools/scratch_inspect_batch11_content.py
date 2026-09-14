import urllib.request, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== INSPECTING PKMN-0043 (GI HGSS) ===")
u1 = "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx"
raw1 = urllib.request.urlopen(urllib.request.Request(u1, headers=headers)).read().decode('utf-8')
# Find article body
m_body1 = re.search(r'<div class=["\']field-body["\'][^>]*>(.*?)</div>\s*<div class=["\']field-tags["\']', raw1, re.DOTALL | re.I)
if not m_body1:
    m_body1 = re.search(r'<div class=["\']content["\'][^>]*>(.*?)</div>', raw1, re.DOTALL | re.I)
text1 = m_body1.group(1) if m_body1 else raw1
# Print first 5 paragraphs
paras1 = re.findall(r'<p>(.*?)</p>', text1, re.DOTALL | re.I)
print(f"Paras count: {len(paras1)}")
for p in paras1[:6]:
    clean = re.sub(r'<[^>]+>', '', p).strip()
    if clean:
        print("  P:", clean[:100], "...")

print("\n=== INSPECTING PKMN-0056 (Dengeki B2W2) ===")
u2 = "https://dengekionline.com/elem/000/000/518/518926/"
raw2 = urllib.request.urlopen(urllib.request.Request(u2, headers=headers)).read().decode('utf-8')
paras2 = re.findall(r'<p[^>]*>(.*?)</p>', raw2, re.DOTALL | re.I)
print(f"Paras count: {len(paras2)}")
for p in paras2[:8]:
    clean = re.sub(r'<[^>]+>', '', p).strip()
    if clean:
        print("  P:", clean[:100], "...")
# Check images in dengeki
imgs2 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw2, re.I)
print("Dengeki images:", [img for img in imgs2 if 'elem' in img])

print("\n=== INSPECTING PKMN-0826 (GI Monster Design) ===")
u3 = "https://www.gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx"
raw3 = urllib.request.urlopen(urllib.request.Request(u3, headers=headers)).read().decode('utf-8')
paras3 = re.findall(r'<p>(.*?)</p>', raw3, re.DOTALL | re.I)
print(f"Paras count: {len(paras3)}")
for p in paras3[:6]:
    clean = re.sub(r'<[^>]+>', '', p).strip()
    if clean:
        print("  P:", clean[:100], "...")
imgs3 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw3, re.I)
print("GI 2017 images:", [img for img in imgs3 if 'inline' in img or 'feature' in img or 'files' in img or 'jpg' in img or 'png' in img])
