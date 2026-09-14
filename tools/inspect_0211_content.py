import urllib.request
import re
import html

base = "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/"
for page in ["01/01_04/index.html", "01/01_05/index.html"]:
    u = base + page
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("shift_jis", errors="replace")
            # strip script & styles & wayback
            raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL)
            raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
            raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL)
            
            body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
            body = body_m.group(1) if body_m else raw
            body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
            body = re.sub(r"</?(p|tr|td|div|h\d)[^>]*>", "\n", body, flags=re.I)
            body = re.sub(r"<[^>]+>", "", body)
            lines = [html.unescape(l).strip() for l in body.split("\n") if html.unescape(l).strip()]
            
            print(f"\n==================== {page} (Lines: {len(lines)}) ====================")
            for l in lines[:30]:
                if not l.startswith("★") and "N.O.M" not in l:
                    print("  |", l)
    except Exception as e:
        print(f"Error {page}: {e}")
