import urllib.request
import re

urls = [
    "http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan1/page01.html",
    "http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan2/page01.html",
    "http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/kawaguti/page01.html",
]

for u in urls:
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("shift_jis", errors="replace")
            m = re.search(r"<title>(.*?)</title>", raw, re.I)
            title = m.group(1).strip() if m else "No title"
            print(f"URL: {u.split('/')[-2]}/{u.split('/')[-1]} -> Title: {title}")
    except Exception as e:
        print(f"URL {u}: {e}")
