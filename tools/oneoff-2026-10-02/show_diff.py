"""show_diff.py <cache dir name> [stem-substring…] — each finding as the changed spans only (current → fix), for fast reading."""
import difflib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
C = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export/data") / sys.argv[1]
want = sys.argv[2:]
for f in sorted(C.glob("*.json")):
    if want and not any(w in f.stem for w in want):
        continue
    b = json.loads(f.read_text(encoding="utf-8"))
    if not b["issues"]:
        continue
    print(f"\n## {f.stem[11:70]} ({len(b['issues'])})")
    for x in b["issues"]:
        a, z = x["current"], x["fix"]
        sm = difflib.SequenceMatcher(None, a, z)
        parts = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                ctx = a[max(0, i1 - 6):i1]
                parts.append(f"…{ctx}[{a[i1:i2]}→{z[j1:j2]}]")
        ch = " ".join(parts)
        if len(ch) > 260:
            ch = ch[:260] + "…"
        print(f"[{x['i']}] {x['kind']}: {x['why'][:90]}\n     {ch}")
