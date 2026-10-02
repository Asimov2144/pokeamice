"""Apply the review findings I accepted (decisions.json: {stem: {"accept": [row…], "custom": {row: text}, "all": true}})
with tools/rowedit.py, so only the edited lines change. A finding is applied only if the row's translation is still the
one the reviewer saw."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
sys.path.insert(0, str(DOCS / "tools"))
from rowedit import Post  # noqa: E402

HERE = Path(__file__).parent
dec = json.loads((HERE / (sys.argv[2] if len(sys.argv) > 2 else "decisions.json")).read_text(encoding="utf-8"))
total = 0
for stem, d in dec.items():
    blob = json.loads((DOCS / "data" / (sys.argv[1] if len(sys.argv) > 1 else "cache_review_ds") / f"{stem}.json").read_text(encoding="utf-8"))
    by_i = {}
    for x in blob["issues"]:
        by_i.setdefault(x["i"], x)          # first finding per row
    rows = set(by_i) if d.get("all") else set(d.get("accept", []))
    rows -= set(d.get("reject", []))
    p = Post(str(DOCS / "_posts" / f"{stem}.md"))
    n = 0
    for i in sorted(rows | {int(k) for k in d.get("custom", {})}):
        new = d.get("custom", {}).get(str(i)) or by_i[i]["fix"]
        cur = p.rows[i].get("translation")
        if i in by_i and str(cur or "").strip() != by_i[i]["current"]:
            print(f"   skip {stem[:40]} [{i}]: translation changed since the review")
            continue
        if i in by_i and str(i) not in d.get("custom", {}) and len(new) < 0.75 * len(cur or "") and len(cur or "") > 40:
            print(f"   CHECK {stem[:40]} [{i}]: fix much shorter than the current text ({len(new)} < {len(cur)})")
            continue
        p.set(i, "translation", new)
        n += 1
    p.save()
    total += n
    print(f"{stem[:70]}: {n} rows")
print("total", total)
