"""(Qwen copy) review-translations.py with DeepSeek's reasoning model in place of Qwen (DashScope answers 403 AccessDenied.Unpurchased
since 09-30). Same system prompt, same row batches, same issue format; a separate cache (data/cache_review_ds/, not
committed) so the tracked Qwen cache and design/translation-review-queue.json stay as they are.

    python review_ds.py <list.txt>     → data/cache_review_ds/<stem>.json, prints a count per post
"""
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
spec = importlib.util.spec_from_file_location("rt", DOCS / "tools" / "review-translations.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
R.CACHE = DOCS / "data" / "cache_review_qwen"





def review_post(rel):
    """R.review_post with the post's batches asked side by side (same cache, same result shape)."""
    import hashlib
    path = R.ROOT / rel
    fm = R.front(path.read_bytes().decode("utf-8-sig"))
    key, rows = R.rows_of(fm)
    sig = hashlib.sha1(json.dumps([R.REV, rows], ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    cache = R.CACHE / (path.stem + ".json")
    if cache.exists():
        blob = json.loads(cache.read_text(encoding="utf-8"))
        if blob.get("sig") == sig:
            return blob, True
    by_i = {i: (o, t) for i, o, t in rows}
    lang, title = fm.get("original_lang") or "ja", str(fm.get("title") or path.stem)
    with ThreadPoolExecutor(max_workers=6) as ex:
        answers = list(ex.map(lambda b: R.ask(lang, title, b), list(R.batches(rows))))
    issues = []
    for found in answers:
        for it in found:
            try:
                i = int(it.get("i"))
            except (TypeError, ValueError):
                continue
            if i not in by_i or not str(it.get("fix") or "").strip():
                continue
            o, t = by_i[i]
            if str(it["fix"]).strip() == t:
                continue
            issues.append({"i": i, "kind": it.get("kind"), "why": str(it.get("why") or "")[:160], "original": o[:300],
                           "current": t, "fix": str(it["fix"]).strip()})
    blob = {"sig": sig, "post": rel, "rows": len(rows), "field": key, "model": R.MODEL, "issues": issues}
    R.CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(blob, ensure_ascii=False, indent=1), encoding="utf-8")
    return blob, False


files = list(dict.fromkeys(l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()))
if "--reverse" in sys.argv:
    files.reverse()
print(len(files), "posts", flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(review_post, f): f for f in files}
    for fut in as_completed(futs):
        f = futs[fut]
        try:
            blob, cached = fut.result()
            print(f"  {'cached' if cached else 'asked '} {Path(f).name[:64]}: {len(blob['issues'])} issues / {blob['rows']} rows", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {Path(f).name[:64]}: {exc}", flush=True)
