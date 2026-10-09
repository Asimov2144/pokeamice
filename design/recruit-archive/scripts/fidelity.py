"""Fidelity of every GAME FREAK recruit post: each Japanese `original` of the post's parallel_items
(parsed as YAML, so block scalars count) is looked for verbatim (normalised) in the archived page text.

Page text: text/<slug>/*.txt (versions.py, best-matching version) for the /recruit/<slug>/ pages,
raw-old/<stem>.html (audit_old.py) for the older .html pages.
Usage: python fidelity.py <repo>      -> fidelity.json + a table
"""
import glob, html as H, json, re, subprocess, sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = Path(sys.argv[1])
sys.path.insert(0, str(HERE))
from match_posts import SLUG_OF_POST  # noqa: E402

OLD = [
    "2013-11-01-interview-gamefreak-recruit-3d-graphics-to-fk", "2013-11-01-interview-gamefreak-recruit-programmer-tt-mi",
    "2015-08-01-interview-gamefreak-gear-tembo-turner", "2015-09-01-interview-gamefreak-rnd-launch-taya-mi",
    "2015-10-01-interview-gamefreak-recruit-designers", "2015-10-01-interview-gamefreak-recruit-planners",
    "2015-10-01-interview-gamefreak-recruit-programmers", "2017-03-01-interview-gamefreak-gear-gigawrecker",
    "2017-06-01-interview-gamefreak-rnd-ta-taya-kk", "2017-09-01-interview-gamefreak-recruit-cross-industry",
]


def norm(s):
    return re.sub(r"[\s　「」『』（）()、。，．・！？!?：:“”\"'…―ー〜~®]+", "", s or "")


def html_text(h):
    h = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "", h)
    return H.unescape(re.sub(r"<[^>]+>", "\n", h))


def originals(stem):
    t = subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:_posts/{stem}.md"], capture_output=True).stdout.decode("utf-8", "replace")
    fm = yaml.safe_load(t.split("\n---", 1)[0].lstrip("-\n"))
    out = []
    for it in fm.get("parallel_items") or []:
        if it.get("type") != "image" and isinstance(it.get("original"), str):
            o = it["original"].replace("\\n", "\n")
            # the post may glue paragraphs together: check each piece on its own
            for piece in re.split(r"\n\s*\n", o):
                if len(norm(piece)) >= 12:
                    out.append(piece.strip())
    return out


rows = {}
for stem in OLD + list(SLUG_OF_POST):
    if stem in SLUG_OF_POST:
        files = sorted(glob.glob(str(HERE / "text" / SLUG_OF_POST[stem] / "*.txt")))
        texts = {Path(f).stem: norm(Path(f).read_text("utf-8")) for f in files}
    else:
        p = HERE / "raw-old" / f"{stem}.html"
        texts = {"cited": norm(html_text(p.read_text("utf-8")))} if p.exists() else {}
    origs = originals(stem)
    if not texts:
        rows[stem] = {"n": len(origs), "note": "no page text"}
        print(f"{stem:<62} n={len(origs):>3}  (no page text yet)")
        continue
    best = max(texts, key=lambda k: sum(norm(o) in texts[k] for o in origs))
    hit = [o for o in origs if norm(o) in texts[best]]
    miss = [o for o in origs if norm(o) not in texts[best]]
    rows[stem] = {"version": best, "n": len(origs), "exact": len(hit), "missing": [m[:140] for m in miss]}
    print(f"{stem:<62} n={len(origs):>3} exact={len(hit):>3} ({len(hit) / max(1, len(origs)):.0%})  vs {best}")
(HERE / "fidelity.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), "utf-8")
