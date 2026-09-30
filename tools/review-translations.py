"""A second model reads the translations against their originals and lists what is wrong.

The translations of the web interviews, the corporate topics and the magazine scans were made by
one model (DeepSeek) and checked mechanically (audit_source_fidelity.py: names and numbers;
audit_translation_padding.py: length; proof_scan-style regexes). None of those reads the sentence.
This asks another model - Qwen on DashScope, the one that transcribes the scans - to read each
row pair and report only what is certainly wrong: a mistranslation, something left out or added,
a name or number that does not match, a term against the site's glossary, a sentence that does not
parse. It does not judge style. The answers are a queue to read, not edits: nothing is written
into the posts.

    python tools/review-translations.py <list.txt>            # one post path per line
    python tools/review-translations.py --since ebc40fc8      # the posts added since a commit
    python tools/review-translations.py --only corporate-topic-01 [more stems]
    python tools/review-translations.py --report              # print the queue

Cache: data/cache_review/<post stem>.json (by a hash of the rows it was shown, so an edited post
is asked again). Report: design/translation-review-queue.json.
"""
import argparse
import collections
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_review"
QUEUE = ROOT / "design" / "translation-review-queue.json"
L = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

spec = importlib.util.spec_from_file_location("iss", ROOT / "tools" / "import-scan-set.py")
_iss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_iss)
URL, KEY, MODEL = _iss.VLM_URL, _iss.VLM_KEY, _iss.VLM_MODEL

REV = 1
BATCH_ROWS, BATCH_CHARS = 28, 5200

SYSTEM = (
    "你是日中、英中翻译的校对员，校对宝可梦开发史料的中文译文。逐条对照原文和译文，只报告确定有问题的条目，问题限于：\n"
    "1. mistranslation 误译：意思和原文不符、主客体或因果弄反、把一个词译成了别的词；\n"
    "2. omission 漏译：原文有的信息译文没有；\n"
    "3. addition 多译：译文里有原文没有的信息、评价或修饰；\n"
    "4. name_number 人名、作品名、机构名、数字、日期、单位与原文不符；\n"
    "5. term 术语：不符合本站译名（宝可梦、宝可梦中心、宝可梦巡护员、轮转对战、GAME FREAK、株式会社宝可梦、任天堂、Creatures），"
    "或同一个原词在译文里前后译成了不同的词。译文在前文给某个名称定义了简称或昵称（如“宝可梦井盖‘宝可盖’”）后文沿用，不算问题；\n"
    "6. fluency 不通顺：读不懂或有病句；\n"
    "7. punct 标点：中文句子里出现半角引号 \" 或 '，或引号、括号不成对。全角的“ ” ‘ ’ 和 「 」 都是正确的，不要报告；\n"
    "宝可梦的中文名一律用中国大陆官方译名（如伊布、穿山鼠、铁甲蛹、皮卡丘），不要改成台湾或香港译名。\n"
    "只报告有把握的问题：拿不准的、可以两种译法的、只是不够好听的，不要报告。\n"
    "不评价风格，不要求润色，不因为译文比原文更口语而报告；原文本身的错别字或识别错误不算译文问题。\n"
    "输出 JSON：{\"issues\":[{\"i\":条目编号,\"kind\":\"上面的英文类别\",\"fix\":\"改正后的完整译文\",\"why\":\"一句话说明具体错在哪\"}]}。"
    "没有问题就输出 {\"issues\":[]}。fix 必须是这一条译文改好后的全文，不要只写片段。"
)


def front(text):
    text = text.replace("\r\r\n", "\n").replace("\r\n", "\n")
    m = re.match(r"﻿?---\n(.*?)\n---", text, re.S)
    return yaml.load(m.group(1), Loader=L) if m else {}


def rows_of(fm):
    """(index in the file's row list, original, translation) for every row with text on both sides."""
    key = "parallel_items" if fm.get("parallel_items") else "translation_segments"
    out = []
    for i, r in enumerate(fm.get(key) or []):
        if not isinstance(r, dict) or r.get("type") == "image":
            continue
        o = str(r.get("original") or "").strip()
        t = str(r.get("translation") or "").strip()
        if not o and r.get("type") == "heading":
            continue
        if o and t and len(o) > 3:
            out.append((i, o, t))
    return key, out


def batches(rows):
    cur, n = [], 0
    for r in rows:
        size = len(r[1]) + len(r[2])
        if cur and (len(cur) >= BATCH_ROWS or n + size > BATCH_CHARS):
            yield cur
            cur, n = [], 0
        cur.append(r)
        n += size
    if cur:
        yield cur


def ask(lang, title, batch):
    src = {"ja": "日文", "en": "英文"}.get(lang, "外文")
    lines = [f"《{title}》，原文为{src}。以下每条是「原文 / 译文」："]
    for i, o, t in batch:
        lines.append(f"[{i}] 原文：{o}\n    译文：{t}")
    body = {"model": MODEL, "enable_thinking": False, "temperature": 0.1, "max_tokens": 4000,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(lines)}]}
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                text = json.load(r)["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", text, re.S)
            return (json.loads(m.group(0) if m else text)).get("issues") or []
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            last = exc
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"review failed: {last}")


def review_post(rel, force=False):
    path = ROOT / rel
    fm = front(path.read_bytes().decode("utf-8-sig"))
    key, rows = rows_of(fm)
    sig = hashlib.sha1(json.dumps([REV, rows], ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    cache = CACHE / (path.stem + ".json")
    if cache.exists() and not force:
        blob = json.loads(cache.read_text(encoding="utf-8"))
        if blob.get("sig") == sig:
            return blob, True
    issues = []
    by_i = {i: (o, t) for i, o, t in rows}
    for batch in batches(rows):
        for it in ask(fm.get("original_lang") or "ja", str(fm.get("title") or path.stem), batch):
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
    blob = {"sig": sig, "post": rel, "rows": len(rows), "field": key, "model": MODEL, "issues": issues}
    CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(blob, ensure_ascii=False, indent=1), encoding="utf-8")
    return blob, False


def report():
    out = {}
    tot = collections.Counter()
    for f in sorted(CACHE.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        if b.get("issues"):
            out[b["post"]] = {"rows": b["rows"], "issues": b["issues"]}
            tot.update(x["kind"] for x in b["issues"])
    QUEUE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} posts with issues, {sum(tot.values())} issues: {dict(tot)} -> {QUEUE.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list", nargs="?")
    ap.add_argument("--since")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        return report()
    if a.list:
        files = [l.strip() for l in open(a.list, encoding="utf-8") if l.strip()]
    elif a.since:
        out = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--name-only", "--diff-filter=A", "-z", a.since, "HEAD", "--", "_posts"],
                             cwd=ROOT, capture_output=True).stdout.decode("utf-8")
        files = [f for f in out.split("\0") if f.endswith(".md")]
    else:
        files = ["_posts/" + p.name for p in sorted((ROOT / "_posts").glob("*.md")) if any(s in p.name for s in (a.only or []))]
    if not KEY:
        raise SystemExit("no DashScope key (DASHSCOPE_API_KEY / VLM_OCR_API_KEY)")
    print(f"{len(files)} posts", flush=True)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(review_post, f, a.force): f for f in files}
        for fut in as_completed(futs):
            f = futs[fut]
            try:
                blob, cached = fut.result()
                print(f"  {'cached' if cached else 'asked '} {Path(f).name[:60]}: {len(blob['issues'])} issues / {blob['rows']} rows", flush=True)
            except Exception as exc:  # noqa: BLE001 - one bad post must not stop the run
                print(f"  FAIL {Path(f).name[:60]}: {exc}", file=sys.stderr, flush=True)
    report()


if __name__ == "__main__":
    main()
