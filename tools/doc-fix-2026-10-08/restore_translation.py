"""Restore the translation of paragraph-level notes that the note pass emptied.

For each item whose translation is now '' and which has a note:
  - translation := the translation git HEAD has for that item (same original, checked)
  - note        := HEAD's note if HEAD had one (pre-existing popover), otherwise removed
                   (the note was only a copy of the translation).
Only those lines are edited; the rest of the front matter is verified unchanged.
"""
import sys, subprocess, collections
sys.path.insert(0, r"C:/Users/2144j/AppData/Local/Temp/claude/P--WEBSITE-pokeamice/7afd9ba7-f41b-4a1f-8271-385fc41af425/scratchpad")
from common import POSTS, ROOT, read_post, write_post, split_fm, load_fm, L
from fixer import yq, item_spans, find_key, apply_edits, para_breaks
import yaml

DRY = "--dry" in sys.argv
stats = collections.Counter(); failures = []; head_cache = {}

def head_fm(name):
    if name not in head_cache:
        out = subprocess.run(["git", "show", f"HEAD:_posts/{name}"], cwd=ROOT, capture_output=True)
        head_cache[name] = out.stdout.decode("utf-8") if out.returncode == 0 else None
    txt = head_cache[name]
    if txt is None:
        return None
    fm, _, _ = split_fm(txt.lstrip("\ufeff"))
    return yaml.load(fm, Loader=L) or {}

for p in sorted(POSTS.glob("*.md")):
    name = p.name
    text, eol = read_post(p)
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    text = text.lstrip("\ufeff")
    fm, body, _ = split_fm(text)
    if fm is None:
        continue
    d0 = load_fm(fm)
    if not d0:
        continue
    targets = [i for i, it in enumerate(d0.get("parallel_items") or [])
               if isinstance(it, dict) and it.get("note") and str(it.get("translation", "x")).strip() == ""]
    if not targets:
        continue
    hd = head_fm(name)
    if hd is None or not isinstance(hd, dict):
        failures.append((name, "not in HEAD")); stats["skipped"] += len(targets); continue
    hitems = hd.get("parallel_items") or []
    lines = fm.split("\n")
    spans = item_spans(lines)
    edits, exp = [], {}
    try:
        for i in targets:
            hi = hitems[i] if i < len(hitems) and isinstance(hitems[i], dict) else None
            if hi is None or str(hi.get("original", "")) != str(d0["parallel_items"][i].get("original", "")):
                failures.append((name, f"item {i}: original differs from HEAD")); continue
            tr = para_breaks(str(hi.get("translation", "")))
            if not tr.strip():
                failures.append((name, f"item {i}: HEAD translation empty")); continue
            s, e, K = spans[i]
            kidx, kend, prefix = find_key(lines, s, e, K, "translation")
            edits.append((kidx, kend, [prefix + "translation: " + yq(tr)]))
            if "note" in hi:
                nidx, nend, nprefix = find_key(lines, s, e, K, "note")
                edits.append((nidx, nend, [nprefix + "note: " + yq(str(hi["note"]))]))
                exp[i] = {"translation": tr, "note": str(hi["note"])}
                stats["restored_with_head_note"] += 1
            else:
                nidx, nend, _ = find_key(lines, s, e, K, "note")
                edits.append((nidx, nend, []))
                exp[i] = {"translation": tr, "_drop_note": True}
                stats["restored_note_dropped"] += 1
        if not exp:
            continue
        new_lines = apply_edits(list(lines), edits)
        new_fm = "\n".join(new_lines)
        d1 = yaml.load(new_fm, Loader=L) or {}
        # verify: only the targeted items changed, and only in translation / note
        for k in set(d0) | set(d1):
            if k == "parallel_items":
                continue
            if d0.get(k) != d1.get(k):
                raise RuntimeError(f"top-level {k} changed")
        p0, p1 = d0["parallel_items"], d1["parallel_items"]
        if len(p0) != len(p1):
            raise RuntimeError("item count changed")
        for i, (a, b) in enumerate(zip(p0, p1)):
            if not isinstance(a, dict):
                continue
            if i not in exp:
                if a != b:
                    raise RuntimeError(f"item {i} changed unexpectedly")
                continue
            want = dict(a)
            if exp[i].get("_drop_note"):
                want.pop("note", None)
            else:
                want["note"] = exp[i]["note"]
            want["translation"] = exp[i]["translation"]
            if b != want:
                raise RuntimeError(f"item {i} differs from intended value")
        out = bom + "---\n" + new_fm + "\n---\n" + body
        stats["files"] += 1
        if not DRY:
            write_post(p, out, eol)
    except Exception as ex:
        failures.append((name, str(ex)[:160]))

print("STATS", dict(stats))
print("FAILURES", len(failures))
for f in failures[:20]:
    print("  ", f)
