import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 10):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irej/vol1/{fn}"
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            # Title
            m_title = re.search(rb'<title>(.*?)</title>', data, re.I)
            t = m_title.group(1).decode('shift_jis', errors='replace') if m_title else "None"
            print(f"[OK] {fn}: {len(data)} bytes, Title: {t}")
    except Exception as e:
        print(f"[END/FAIL] {fn}: {e}")
        break
