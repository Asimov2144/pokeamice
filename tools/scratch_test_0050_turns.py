import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

u = "https://www.famitsu.com/news/202104/30218824.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
body = m_body.group(1) if m_body else raw

items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
clean_items = []
for tag, content in items:
    c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
    c = re.sub(r'<[^>]+>', '', c).strip()
    if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', '関連記事', '(C)20', '※', '株式会社']) and len(c) > 2:
        clean_items.append((tag, c))

turns = []
current_spk = "Fami通 记者"
for tag, c in clean_items:
    if tag.startswith('h'):
        turns.append({"speaker": "章节标题", "text": f"### {c}"})
        continue
    spk = current_spk
    text = c
    if c.startswith("石原") or "石原氏" in c:
        spk = "石原 恒和"
        text = re.sub(r'^石原[氏\s：:]*', '', c).strip()
    elif c.startswith("須崎") or "須崎氏" in c or "須崎D" in c:
        spk = "须崎 春树"
        text = re.sub(r'^須崎[氏D\s：:]*', '', c).strip()
    elif c.startswith("――") or c.startswith("──"):
        spk = "Fami通 记者"
        text = re.sub(r'^[─―]+\s*', '', c).strip()
    turns.append({"speaker": spk, "text": text})
    current_spk = spk

merged = []
for t in turns:
    if t["speaker"] == "章节标题":
        merged.append(t)
    elif merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 500:
        merged[-1]["text"] += "\n" + t["text"]
    else:
        merged.append(dict(t))

print(f"PKMN-0050: {len(merged)} merged turns:")
for t in merged[:4]:
    print(f"  [{t['speaker']}] {t['text'][:60]}...")
