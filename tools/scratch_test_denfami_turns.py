import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def parse_denfami_dialogues(url, speaker_keywords):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8')
    m_body = re.search(r'<div class=["\']article-body["\'][^>]*>(.*?)</div>\s*<div class=["\']article-footer["\']', raw, re.DOTALL | re.I)
    if not m_body:
        m_body = re.search(r'<div class=["\']main-content[^"\']*["\'][^>]*>(.*?)</div>', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw
    
    items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
    clean_items = []
    for tag, content in items:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', 'この記事に関するタグ', 'いま読まれている記事']) and len(c) > 2:
            clean_items.append((tag, c))
            
    # Process into turns
    turns = []
    current_spk = "电玩志 记者"
    for tag, c in clean_items:
        if tag.startswith('h'):
            turns.append({"speaker": "章节标题", "text": f"### {c}"})
            continue
        # Check speaker at beginning
        spk = current_spk
        text = c
        # Patterns like: 大森氏：, 尾上：, ──, 石原氏：, 川島氏：, 増田氏：
        m_spk = re.match(r'^([^\s：:───]+)[：:]\s*(.*)', c, re.DOTALL)
        if m_spk:
            raw_s = m_spk.group(1).strip()
            for key, norm in speaker_keywords.items():
                if key in raw_s:
                    spk = norm
                    text = m_spk.group(2).strip()
                    break
        elif c.startswith('──') or c.startswith('――') or c.startswith('──さて'):
            spk = "电玩志 记者"
            text = re.sub(r'^[─―]+\s*', '', c).strip()
        else:
            # check if starts with speaker name like "増田　" or "石原　"
            for key, norm in speaker_keywords.items():
                if c.startswith(key):
                    spk = norm
                    text = c[len(key):].strip()
                    break
        turns.append({"speaker": spk, "text": text})
        current_spk = spk

    # Merge consecutive turns from same speaker
    merged = []
    for t in turns:
        if t["speaker"] == "章节标题":
            merged.append(t)
        elif merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 500:
            merged[-1]["text"] += "\n" + t["text"]
        else:
            merged.append(dict(t))
    return merged

# Test 0091
spks_0091 = {
    "大森": "大森 滋",
    "尾上": "尾上 将之",
    "増田": "增田 顺一",
    "田尻": "田尻 智",
    "杉森": "杉森 建"
}
turns_0091 = parse_denfami_dialogues("https://news.denfaminicogamer.jp/interview/170703/2", spks_0091)
print(f"PKMN-0091: {len(turns_0091)} merged turns:")
for t in turns_0091[:4]:
    print(f"  [{t['speaker']}] {t['text'][:60]}...")

# Test 0678
spks_0678 = {
    "石原": "石原 恒和",
    "川島": "川岛 优志",
    "増田": "增田 顺一",
    "ハンケ": "约翰·汉克",
    "野村": "野村 达雄"
}
turns_0678 = parse_denfami_dialogues("https://news.denfaminicogamer.jp/interview/180608/2", spks_0678)
print(f"\nPKMN-0678: {len(turns_0678)} merged turns:")
for t in turns_0678[:4]:
    print(f"  [{t['speaker']}] {t['text'][:60]}...")
