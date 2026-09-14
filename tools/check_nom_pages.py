import urllib.request
import re

for p in range(1, 7):
    url = f"http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page0{p}.html"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html_raw = r.read().decode("shift_jis", errors="replace")
            m = re.search(r"<title>(.*?)</title>", html_raw, re.I)
            title = m.group(1).strip() if m else "No title"
            print(f"Page {p}: {title}")
    except Exception as e:
        print(f"Page {p}: Error {e}")
