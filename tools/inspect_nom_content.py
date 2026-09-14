import urllib.request
import re

url = "http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page01.html"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    html_raw = r.read().decode("shift_jis", errors="replace")

# Print first 2000 characters of body
body_m = re.search(r"<body[^>]*>(.*?)</body>", html_raw, re.IGNORECASE | re.DOTALL)
if body_m:
    body = body_m.group(1)
    # Strip scripts / styles
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.DOTALL | re.I)
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.DOTALL | re.I)
    # Strip archive toolbar
    body = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", body, flags=re.DOTALL | re.I)
    
    # Strip tags
    text = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
    text = re.sub(r"</?p[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    print(f"Total lines: {len(lines)}")
    for line in lines[:35]:
        print("  |", line)
