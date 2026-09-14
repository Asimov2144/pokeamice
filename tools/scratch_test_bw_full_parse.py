import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0'}

def get_bw_chapter(i):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irbj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    
    # Try utf-8 first (works for index3), then shift_jis
    try:
        decoded = raw.decode('utf-8')
        if "通信" not in decoded and i == 3:
            raise ValueError()
    except:
        decoded = raw.decode('shift_jis', errors='replace')
        
    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', decoded, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {i}"
    
    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', decoded, re.DOTALL | re.I)
    
    dialogues = []
    name_map = {
        "岩田": "岩田 聪",
        "石原": "石原 恒和",
        "増田": "增田 顺一",
        "杉森": "杉森 建",
        "一同": "众人"
    }
    
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)
        body_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body))
        body_clean = re.sub(r'<BR\s*/?>', '\n', body_clean, flags=re.I)
        body_clean = re.sub(r'<[^>]+>', '', body_clean).strip()
        dialogues.append({"speaker": spk_norm, "text": body_clean})
        
    return title, dialogues

for c in range(1, 6):
    title, dlg = get_bw_chapter(c)
    print(f"Chapter {c}: {title} | {len(dlg)} turns")
    print(f"  First: [{dlg[0]['speaker']}] {dlg[0]['text'][:50]}...")
    print(f"  Last:  [{dlg[-1]['speaker']}] {dlg[-1]['text'][:50]}...")
