"""Peek at one Wayback capture of each URL: title, text size, first lines. Usage: python peek.py url ..."""
import html as H, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw-peek"; RAW.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 pokeamice-docs research (archive reconstruction)"}


def get(u):
    for i in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
            for enc in ("utf-8", "shift_jis", "euc_jp", "cp932"):
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    pass
            return b.decode("utf-8", "replace")
        except Exception:
            time.sleep(8 * (i + 1))
    return ""


for url in sys.argv[1:]:
    cdx = get(f"https://web.archive.org/cdx/search/cdx?url={url}&fl=timestamp,statuscode&filter=statuscode:200&limit=-3")
    ts = [l.split()[0] for l in cdx.splitlines() if l[:1].isdigit()]
    if not ts:
        print(f"## {url}: no 200 capture"); continue
    t = ts[-1]
    h = get(f"https://web.archive.org/web/{t}id_/http://{url}")
    name = re.sub(r"[^a-z0-9]+", "-", url.lower()).strip("-")
    (RAW / f"{name}-{t}.html").write_text(h, "utf-8")
    title = re.search(r"(?is)<title>(.*?)</title>", h)
    body = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", "", h)
    body = re.sub(r"<[^>]+>", "\n", body)
    lines = [re.sub(r"\s+", " ", H.unescape(l)).strip() for l in body.splitlines()]
    lines = [l for l in lines if len(l) > 1]
    txt = sum(len(l) for l in lines)
    print(f"## {url} @{t} title={title.group(1).strip()[:60] if title else ''} chars={txt}")
    long = [l for l in lines if len(l) > 30][:6]
    for l in long:
        print("   ", l[:150])
    time.sleep(2)
