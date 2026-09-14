import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for i in range(1, 7):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/ipkj/vol1/{fn}"
    req = urllib.request.Request(u, headers=headers)
    raw = urllib.request.urlopen(req).read().decode('shift_jis', errors='replace')
    
    # Title or heading
    m_t = re.search(r'<title>(.*?)</title>', raw, re.I)
    t = m_t.group(1).strip() if m_t else "No Title"
    
    # Find h3, h4 or main question
    headings = re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', raw, re.I)
    clean_h = [html.unescape(re.sub(r'<[^>]+>', '', h)).strip() for h in headings]
    
    print(f"\n--- Chapter {i} ({fn}) ---")
    print(f"Title: {t}")
    print(f"Headings: {clean_h[:3]}")
