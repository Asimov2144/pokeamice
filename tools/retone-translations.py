#!/usr/bin/env python3
"""Rewrite existing interview translations into natural spoken Chinese, without changing what they say.

The first translations (DeepSeek, faithful and plain) often read as translationese: 「进行了……」
「对于……来说」, literal word order, stiff corporate phrasing, where the speaker is chatting. This
asks DeepSeek again, showing it the original and the current translation side by side, to say the
same thing the way a person would say it in Chinese - and nothing more: no added information,
evaluation or flourish, nothing dropped, names / terms / numbers as they are. Rows that already
read naturally come back unchanged.

The output is checked twice before anything is kept: tools/review-translations.py (Qwen) reads the
new rows against the originals, and every rewritten row it flags (for anything: meaning, a name or
number, a term, punctuation) goes back to its current translation (--revert <stem>… after the review, read
from data/cache_review/<stem>.json).

    python tools/retone-translations.py --only <stem> [more stems]       # rewrite, write the posts
    python tools/retone-translations.py --only <stem> --dry-run          # print old / new pairs
    python tools/retone-translations.py --revert <stem> [more stems]     # undo the rows Qwen flagged

Only the `translation` scalars of the touched rows change in the file (located with yaml.compose,
replaced in place as one-line double-quoted strings); everything else stays byte for byte.
Cache: data/cache_retone/<stem>.json (old translation, new translation, per row index).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_retone"
REVIEW = ROOT / "data" / "cache_review"          # tools/review-translations.py, one file per post
REV = 1
BATCH = 12

_spec = importlib.util.spec_from_file_location("import_nom", ROOT / "tools" / "import-nom.py")
_nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nom)
deepseek, load_glossary, glossary_hits = _nom.deepseek, _nom.load_glossary, _nom.glossary_hits

SYSTEM = (
    "你是宝可梦开发史料的译者，任务是把已有的中文译文改成自然的中文口语，让访谈读起来像真人在聊天，而意思一点不变。\n"
    "规则：\n"
    "1. 信息量与原文完全一致：不加原文没有的信息、评价、形容、比喻、夸张（如“享誉全球”“现象级”“走进了大家的生活”），不删任何信息，不合并或拆掉原文的意思。\n"
    "2. 去掉翻译腔和公文腔：“进行了……”“对于……来说”“……的方面”“作为……”这类照搬日文语序的说法，换成中文里自然的说法；句子太长可以断开。\n"
    "3. 口吻跟着说话的人走：受访者聊天时用平常说话的口气；保留（笑）（苦笑）等标记；编者的提问保持提问的口气；"
    "没有说话人的叙述段只去翻译腔，不改成口语。\n"
    "4. 不要网文腔、不要堆成语、不要加感叹号或语气词（原文有的保留）。\n"
    "5. 人名、作品名、公司与部门名、术语、数字、日期一律照现译不动；术语表里的译法必须保留。\n"
    "6. 现译已经自然的，原样返回，不要为改而改。\n"
    "只输出合法 JSON。"
)


def front_span(text: str):
    m = re.match(r"﻿?---\r?\n(.*?)\r?\n---", text, re.S)
    return m.start(1), m.end(1)


def rows_of(fm: dict):
    key = "parallel_items" if fm.get("parallel_items") else "translation_segments"
    out = []
    for i, r in enumerate(fm.get(key) or []):
        if not isinstance(r, dict) or r.get("type") in ("image", "heading"):
            continue
        o, t = str(r.get("original") or "").strip(), str(r.get("translation") or "").strip()
        if o and t and len(o) > 3:
            out.append({"i": i, "speaker": str(r.get("speaker") or ""), "original": o, "translation": t})
    return key, out


def post_path(stem: str) -> Path:
    p = ROOT / "_posts" / f"{stem}.md"
    if not p.exists():
        raise SystemExit(f"no such post: {stem}")
    return p


def ask(title: str, lang: str, gloss: str, batch: list) -> dict:
    payload = [{"i": r["i"], "speaker": r["speaker"], "original": r["original"], "translation": r["translation"]} for r in batch]
    prompt = (f"文章《{title}》（原文为{lang}）。下面每条给出原文和现在的中文译文，按规则改写 translation，保留编号 i。\n"
              f"术语表命中：\n{gloss}\n\n"
              '输出格式：{"items":[{"i":编号,"translation":"改写后的译文"}]}\n\n'
              + json.dumps(payload, ensure_ascii=False))
    for attempt in range(3):
        raw = deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
        try:
            return {int(x["i"]): str(x.get("translation") or "").strip() for x in json.loads(raw).get("items", []) if "i" in x}
        except (ValueError, TypeError) as exc:
            print(f"    bad JSON (attempt {attempt + 1}): {exc}", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError("retone batch failed three times")


def scalar_spans(text: str, key: str, wanted: set) -> dict:
    """index -> (start, end) of the translation scalar of rows `wanted`, offsets in the whole file."""
    fs, fe = front_span(text)
    node = yaml.compose(text[fs:fe])
    seq = next(v for k, v in node.value if k.value == key)
    spans = {}
    for idx, item in enumerate(seq.value):
        if idx not in wanted:
            continue
        val = next(v for k, v in item.value if k.value == "translation")
        spans[idx] = (fs + val.start_mark.index, fs + val.end_mark.index, val.style)
    return spans


def write_rows(path: Path, key: str, new: dict) -> None:
    """new: row index -> translation. Replaces only those scalars; re-parses to prove nothing else moved."""
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    before = yaml.safe_load(text[slice(*front_span(text))])
    spans = scalar_spans(text, key, set(new))
    for idx in sorted(spans, key=lambda k: -spans[k][0]):
        s, e, style = spans[idx]
        chunk = text[s:e]
        #  a block scalar's span runs on to the next key: keep the line break and indentation it ends with
        tail = chunk[len(chunk.rstrip()):] if style in ("|", ">") else ""
        text = text[:s] + json.dumps(new[idx], ensure_ascii=False) + tail + text[e:]
    after = yaml.safe_load(text[slice(*front_span(text))])
    for idx, t in new.items():
        assert after[key][idx]["translation"] == t, (path.name, idx)
        before[key][idx]["translation"] = t
    assert after == before, f"{path.name}: something other than the translations changed"
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def retone(stem: str, glossary, dry: bool) -> tuple[int, int]:
    path = post_path(stem)
    text = path.read_text(encoding="utf-8")
    fm = yaml.safe_load(text[slice(*front_span(text))])
    key, rows = rows_of(fm)
    title = fm.get("display_title") or fm.get("title") or stem
    lang = {"ja": "日文", "en": "英文"}.get(str(fm.get("original_lang") or fm.get("lang") or "ja"), "日文")
    gloss = "\n".join(f"- {s} → {t}" for s, t in glossary_hits("\n".join(r["original"] for r in rows), glossary)) or "（无）"
    digest = hashlib.sha1((json.dumps(rows, ensure_ascii=False) + f"|{REV}").encode("utf-8")).hexdigest()[:16]
    cache = CACHE / f"{stem}.json"
    got = None
    if cache.exists():
        blob = json.loads(cache.read_text(encoding="utf-8"))
        if blob.get("key") == digest:
            got = {int(k): v["new"] for k, v in blob["rows"].items()}
    if got is None:
        got = {}
        batches = [rows[k:k + BATCH] for k in range(0, len(rows), BATCH)]
        with ThreadPoolExecutor(4) as ex:
            for part in ex.map(lambda b: ask(title, lang, gloss, b), batches):
                got.update(part)
        CACHE.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"key": digest, "rows": {str(r["i"]): {"old": r["translation"], "new": got.get(r["i"], "")}
                                                             for r in rows}}, ensure_ascii=False, indent=1), encoding="utf-8")
    changed = {r["i"]: got[r["i"]] for r in rows if got.get(r["i"]) and got[r["i"]] != r["translation"]}
    if dry:
        for r in rows:
            if r["i"] in changed:
                print(f"[{r['i']}] {r['translation']}\n  → {changed[r['i']]}")
    elif changed:
        write_rows(path, key, changed)
    return len(changed), len(rows)


def revert(stem: str) -> int:
    """Put back the pre-retone translation of every rewritten row the Qwen review flagged."""
    blob = json.loads((CACHE / f"{stem}.json").read_text(encoding="utf-8"))
    review = json.loads((REVIEW / f"{stem}.json").read_text(encoding="utf-8"))
    #  any flag on a rewritten row - meaning, a name or number, a term, punctuation - means the rewrite
    #  is not clean: the row goes back to the translation that was already reviewed
    flagged = {int(x["i"]) for x in review.get("issues", [])}
    path = post_path(stem)
    text = path.read_text(encoding="utf-8")
    fm = yaml.safe_load(text[slice(*front_span(text))])
    key = "parallel_items" if fm.get("parallel_items") else "translation_segments"
    back = {i: blob["rows"][str(i)]["old"] for i in flagged
            if str(i) in blob["rows"] and blob["rows"][str(i)]["new"] == fm[key][i].get("translation")
            and blob["rows"][str(i)]["old"] != blob["rows"][str(i)]["new"]}
    if back:
        write_rows(path, key, back)
    return len(back)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--revert", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.revert:
        for stem in args.revert:
            print(f"{stem}: {revert(stem)} rows put back")
        return 0
    glossary = load_glossary()
    for stem in args.only:
        n, total = retone(stem, glossary, args.dry_run)
        print(f"{stem}: {n} / {total} rows rewritten", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
