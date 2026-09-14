import urllib.request, re, html, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
base_url = 'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/'

name_map = {
    '岩田': '岩田 聪',
    '石原': '石原 恒和',
    '増田': '增田 顺一',
    '石原・増田': '石原 恒和・增田 顺一',
    '増田・石原': '增田 顺一・石原 恒和',
    '一同': '众人'
}

for i in range(1, 5):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = base_url + fn
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    
    # Title
    subttls = re.findall(r'<h3[^>]*class=["\']interview__ttl["\'][^>]*>(.*?)</h3>', raw, re.I | re.DOTALL)
    ttl = re.sub(r'<[^>]+>', '', subttls[0]).strip() if subttls else f"Chapter {i}"
    
    # Dialogue boxes
    boxes = re.findall(r'<div class=["\']interview__name["\']><p>(.*?)</p></div>\s*<div class=["\']interview__text["\']><p>(.*?)</p></div>', raw, re.DOTALL | re.I)
    
    # Notes
    notes_raw = re.findall(r'<dl><dt>(※\d+)</dt><dd>(.*?)</dd></dl>', raw, re.DOTALL | re.I)
    notes_dict = {dt.strip(): re.sub(r'<[^>]+>', '', dd).strip() for dt, dd in notes_raw}
    
    print(f"Chapter {i}: {ttl} | {len(boxes)} turns | Notes: {list(notes_dict.keys())}")
    
    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)
        
        # Look for notes referenced in body (e.g. ※1, ※2)
        ref_notes = re.findall(r'※\d+', body)
        attached_notes = [f"{rn}: {notes_dict[rn]}" for rn in ref_notes if rn in notes_dict]
        
        b_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body, flags=re.I))
        b_clean = re.sub(r'<sup[^>]*>.*?</sup>', '', b_clean, flags=re.I)
        b_clean = re.sub(r'<br\s*/?>', '\n', b_clean, flags=re.I)
        b_clean = re.sub(r'<[^>]+>', '', b_clean).strip()
        
        dialogues.append({
            "speaker": spk_norm,
            "text": b_clean,
            "notes": " | ".join(attached_notes) if attached_notes else ""
        })
        
    print(f"  First turn: [{dialogues[0]['speaker']}] {dialogues[0]['text'][:60]}...")
    print(f"  Last turn:  [{dialogues[-1]['speaker']}] {dialogues[-1]['text'][:60]}...")
