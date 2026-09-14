import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0'}

def get_b2w2_chapter(i):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irej/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()
    try:
        decoded = raw.decode("utf-8")
        if "ポケモン" not in decoded:
            raise ValueError()
    except:
        decoded = raw.decode("shift_jis", errors="replace")

    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', decoded, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {i}"

    # Footnotes mapping
    notes_map = {}
    note_boxes = re.findall(r'<DIV CLASS="notes-box">\s*<DIV CLASS="notes-num"><P>(※\d+)</P></DIV>\s*<DIV CLASS="notes-text"><P>(.*?)</P></DIV>', decoded, re.DOTALL | re.I)
    for num, ntext in note_boxes:
        clean_nt = html.unescape(re.sub(r'<[^>]+>', '', ntext)).strip()
        notes_map[num] = clean_nt

    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', decoded, re.DOTALL | re.I)
    name_map = {
        "岩田": "岩田 聪",
        "石原": "石原 恒和",
        "増田": "增田 顺一",
        "海野": "海野 隆雄",
        "一同": "众人"
    }

    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)

        m_notes = re.findall(r'※\d+', body)
        ref_notes = [f"{n}：{notes_map[n]}" for n in m_notes if n in notes_map]

        body_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body))
        body_clean = re.sub(r'<BR\s*/?>', '\n', body_clean, flags=re.I)
        body_clean = re.sub(r'<[^>]+>', '', body_clean).strip()

        dialogues.append({
            "speaker": spk_norm,
            "text": body_clean,
            "raw_notes": "；".join(ref_notes)
        })

    return title, dialogues

for c in range(1, 7):
    title, dlg = get_b2w2_chapter(c)
    print(f"Chapter {c}: {title} | {len(dlg)} turns")
    print(f"  First turn: [{dlg[0]['speaker']}] {dlg[0]['text'][:50]}...")
    print(f"  Last turn:  [{dlg[-1]['speaker']}] {dlg[-1]['text'][:50]}...")
