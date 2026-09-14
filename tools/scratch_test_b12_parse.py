import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def inspect_denfami(url, name):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8')
    # Denfami article content is in <div class="article-content"> or inside <main>
    # Denfami format: <p><strong>Speaker:</strong> text</p> or <p><strong>Speaker</strong><br>text</p>
    m_body = re.search(r'<div class=["\']article-body["\'][^>]*>(.*?)</div>\s*<div class=["\']article-footer["\']', raw, re.DOTALL | re.I)
    if not m_body:
        m_body = re.search(r'<div class=["\']main-content[^"\']*["\'][^>]*>(.*?)</div>', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw
    
    # Extract headings (h2/h3) and paragraphs
    items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
    clean_items = []
    for tag, content in items:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', 'この記事に関するタグ', 'いま読まれている記事']):
            clean_items.append((tag, c))
            
    print(f"\n=== {name} ({url}) ===")
    print(f"Extracted {len(clean_items)} elements:")
    for tag, c in clean_items[:6]:
        print(f"  <{tag}> {c[:70]}...")
    return clean_items

inspect_denfami("https://news.denfaminicogamer.jp/interview/170703/2", "PKMN-0091 Ohmori x Onoue Part 2")
inspect_denfami("https://news.denfaminicogamer.jp/interview/180608/2", "PKMN-0678 Pokemon GO Part 2")
