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
    print(pid, 'clean paras:', len(clean_paras))
    # Check average length of paragraphs
    lengths = [len(p) for p in clean_paras]
    print(' ', f"min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)//len(lengths)}")
