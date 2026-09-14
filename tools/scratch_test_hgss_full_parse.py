import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0'}

def get_chapter(i):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/ipkj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')
    
    # Title
    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', raw, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {i}"
    
    # Extract boxes
    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', raw, re.DOTALL | re.I)
    
    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        body_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body))
        body_clean = re.sub(r'<BR\s*/?>', '\n', body_clean, flags=re.I)
        body_clean = re.sub(r'<[^>]+>', '', body_clean).strip()
        dialogues.append({"speaker": spk_clean, "text": body_clean})
        
    return title, dialogues

for c in range(1, 7):
    title, dlg = get_chapter(c)
    print(f"Chapter {c}: {title} | {len(dlg)} dialogue turns")
    print(f"  First turn: [{dlg[0]['speaker']}] {dlg[0]['text'][:60]}...")
    print(f"  Last turn: [{dlg[-1]['speaker']}] {dlg[-1]['text'][:60]}...")
