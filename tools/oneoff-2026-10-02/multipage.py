"""multipage.py <post> <url>... — like audit_source_fidelity, but the source is all the given pages together
(posts that ran over several pages and only cite page 1). Uses the audit tool's fetch cache. Read-only."""
import sys
from pathlib import Path

DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
sys.path.insert(0, "P:/WEBSITE/pokeamice-main (1)/pokeamice-main/tools")
import audit_source_fidelity as A  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
post, urls = sys.argv[1], sys.argv[2:]
d, _ = A.front_matter(str(DOCS / post))
src = ""
for u in urls:
    t, how = A.fetch(u)
    print(f"  {how:<12} {len(t):>6}  {u}")
    src += "\n" + t
S = A.grams(A.norm(src))
checked = found = 0
misses = []
for i, x in enumerate(A.segments(d)):
    if not isinstance(x, dict):
        continue
    o = A.norm(x.get("original"))
    if len(o) < 12:
        continue
    g = A.grams(o)
    cov = len(g & S) / max(1, len(g))
    checked += 1
    if cov >= 0.55:
        found += 1
    else:
        misses.append((i, round(cov, 2), (x.get("original") or "")[:70].replace("\n", "/")))
print(f"{post[7:70]}: {found}/{checked} found")
for m in misses[:12]:
    print("   miss", *m)
if len(misses) > 12:
    print(f"   … {len(misses) - 12} more")
