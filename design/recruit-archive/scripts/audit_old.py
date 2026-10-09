"""Fidelity of the older recruit posts (2013-2019): are the post's Japanese `original:` paragraphs
really on the archived page the post cites?

For each post: take its original_link / original_url (a Wayback address, or a live address that is
looked up in Wayback near the post's date), fetch the raw capture (id_), normalise both sides and count
paragraphs found verbatim, plus the best fuzzy ratio of the ones that are not.
Usage: python audit_old.py <repo> stem ...
"""
import difflib, html as H, json, re, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw-old"; RAW.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 pokeamice-docs research (archive reconstruction)"}
REPO = Path(sys.argv[1])


def norm(s):
    return re.sub(r"[\s　「」『』（）()、。，．・！？!?：:“”\"'…―ー〜~]+", "", s)


def get(u):
    for i in range(5):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
            for enc in ("utf-8", "shift_jis", "cp932", "euc_jp"):
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    pass
            return b.decode("utf-8", "replace")
        except Exception:
            time.sleep(10 * (i + 1))
    return ""


def page_text(h):
    h = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "", h)
    h = re.sub(r"<[^>]+>", "\n", h)
    return H.unescape(h)


out = {}
for stem in sys.argv[2:]:
    t = subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:_posts/{stem}.md"], capture_output=True).stdout.decode("utf-8", "replace")
    m = re.search(r"^(?:original_link|original_url):\s*(\S+)", t, re.M)
    url = m.group(1) if m else ""
    w = re.match(r"https?://web\.archive\.org/web/(\d+)[a-z_]*/(.+)", url)
    if w:
        ts, target = w.group(1), w.group(2)
    else:
        target, ts = url, re.match(r"(\d{4})-(\d\d)-(\d\d)", stem).group(0).replace("-", "")
    cache = RAW / (stem + ".html")
    if cache.exists():
        h = cache.read_text("utf-8")
    else:
        h = get(f"https://web.archive.org/web/{ts}id_/{target}")
        cache.write_text(h, "utf-8")
        time.sleep(3)
    body = norm(page_text(h))
    origs = [o.strip().strip('"').strip("'") for o in re.findall(r"^\s+original: (.+)$", t, re.M) if not o.strip().startswith("/assets")]
    origs = [o for o in origs if len(norm(o)) >= 12]
    exact = [o for o in origs if norm(o) in body]
    miss = [o for o in origs if norm(o) not in body]
    out[stem] = {"url": url, "fetched": f"{ts} {target}", "n": len(origs), "exact": len(exact), "missing": [x[:120] for x in miss]}
    print(f"{stem:<60} {len(exact)}/{len(origs)}  ({len(h)} bytes)", flush=True)
(HERE / "audit-old.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
