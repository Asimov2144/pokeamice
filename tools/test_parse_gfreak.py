import urllib.request
import re
import html
import time
from pathlib import Path

CACHE_DIR = Path("data/cache_nom")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_with_cache_and_retry(url: str, filename: str) -> str:
    cache_file = CACHE_DIR / filename
    if cache_file.exists() and cache_file.stat().st_size > 500:
        return cache_file.read_text(encoding="shift_jis", errors="replace")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Ensure https
    url_https = url.replace("http://", "https://")

    for attempt in range(5):
        try:
            req = urllib.request.Request(url_https, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r:
                raw_bytes = r.read()
                cache_file.write_bytes(raw_bytes)
                print(f"  [FETCHED & CACHED] {filename} ({len(raw_bytes)} bytes)")
                return raw_bytes.decode("shift_jis", errors="replace")
        except Exception as e:
            print(f"  [RETRY {attempt+1}] {url_https} failed: {e}")
            time.sleep(3 * (attempt + 1))

    raise RuntimeError(f"Failed to fetch {url} after 5 attempts")


def parse_gfreak_page(page_num: int):
    url = f"https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page0{page_num}.html"
    raw = fetch_with_cache_and_retry(url, f"nom_0007_gfreak_page0{page_num}.html")

    # Strip wayback toolbar & scripts
    raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

    # Title
    m_title = re.search(r"<title>(.*?)</title>", raw, re.I)
    title = m_title.group(1).strip() if m_title else f"Page {page_num}"

    # Extract images
    imgs = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>', raw, re.I)
    valid_imgs = [img for img in imgs if not "archive.org" in img and not "icon" in img and not "spacer" in img and not "back" in img]

    # Body
    body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
    body = body_m.group(1) if body_m else raw

    # Convert linebreaks and table cells to text
    body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
    body = re.sub(r"</?p[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"</?tr[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"</?td[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", "", body)

    lines = [html.unescape(l).strip() for l in body.split("\n")]
    lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

    dialogues = []
    current_speaker = ""
    current_text = []

    for l in lines:
        # Match speaker like '杉森>>', '増田>>', '西野>>', '森本>>', '渡辺>>'
        m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
        if m:
            if current_text:
                dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            current_speaker = m.group(1).strip()
            rest = m.group(3).strip()
            if rest:
                current_text.append(rest)
        else:
            if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                if not current_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                    if current_text:
                        dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})
                        current_text = []
                    current_speaker = "N.O.M 采访者"
                    current_text.append(l)
                    continue
            current_text.append(l)

    if current_text:
        dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})

    return title, dialogues, valid_imgs

if __name__ == "__main__":
    for p in range(1, 7):
        t, d, imgs = parse_gfreak_page(p)
        print(f"\n--- Page {p}: {t} ---")
        print(f"Dialogues: {len(d)}, Images: {imgs}")
        speakers = set(x['speaker'] for x in d)
        print(f"Speakers: {speakers}")
        for item in d[:2]:
            print(f"  [{item['speaker']}] {item['text'][:60]}...")
        time.sleep(1.5)
