import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

for pid, u in [
    ('PKMN-0086', 'https://www.famitsu.com/news/201208/05019240.html'),
    ('PKMN-0072', 'https://www.famitsu.com/news/201311/16043307.html')
]:
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw
    paras = re.findall(r'<p[^>]*>(.*?)</p>', body, re.DOTALL | re.I)
    clean_paras = []
    for p in paras:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', p))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Twitter', 'Facebook', 'ファミ通.com', '関連記事', '(C)20', '※', '株式会社']):
            clean_paras.append(c)
            
    raw_turns = []
    current_spk = "Fami通 记者"
    for p in clean_paras:
        if "増田氏" in p or "増田さん" in p:
            spk = "增田 顺一"
        elif "海野氏" in p or "海野さん" in p:
            spk = "海野 隆雄"
        elif "景山氏" in p or "景山さん" in p:
            spk = "景山 将太"
        elif p.startswith("▼質問") or "質問" in p:
            spk = "活动现场粉丝提问"
        else:
            spk = current_spk
        raw_turns.append({"speaker": spk, "text": p})
        current_spk = spk
        
    merged = []
    for t in raw_turns:
        if merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 400:
            merged[-1]["text"] += "\n" + t["text"]
        else:
            merged.append(dict(t))
            
    print(f"{pid}: raw turns {len(raw_turns)} -> merged turns {len(merged)}")
    for i, m in enumerate(merged[:4]):
        print(f"  [{m['speaker']}] {m['text'][:80]}...")
