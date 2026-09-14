import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 6):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irbj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')
    
    # Title
    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', raw, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {i}"
    
    # Dialogue boxes
    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', raw, re.DOTALL | re.I)
    speakers = set(re.sub(r'<[^>]+>', '', b[0]).strip() for b in boxes)
    
    print(f"\n--- Chapter {i} ({fn}) ---")
    print(f"Title: {title}")
    print(f"Turns: {len(boxes)}")
    print(f"Speakers: {speakers}")
    if boxes:
        spk0 = re.sub(r'<[^>]+>', '', boxes[0][0]).strip()
        txt0 = re.sub(r'<[^>]+>', '', boxes[0][1]).replace('\n', ' ').strip()
        print(f"  First turn: [{spk0}] {txt0[:70]}...")
