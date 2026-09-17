"""Fill the translations a post's segments lack: every parallel_items / translation_segments
row that has an `original` but an empty `translation` goes to DeepSeek in batches (with the
project glossary, the rows around it as context, and the post's title), and the answer is
written into that row's own `translation: ""` line - nothing else in the file is touched,
so the diff is the translations and only the translations.

    python tools/fill-translations.py --list                 # what is missing, per post
    python tools/fill-translations.py --only ndream-2010     # posts whose file name contains this
    python tools/fill-translations.py                        # every post with a gap
"""
import glob
import io
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
_spec = importlib.util.spec_from_file_location("importnom", ROOT / "tools" / "import-nom.py")
nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nom)

SYSTEM = ("你是宝可梦开发史料的日中译者。这些是杂志扫描页上零散的标题、图注、表格项和短句，"
          "译文忠实、平实、简短，不加渲染、不加感叹号、不补充原文没有的内容；游戏名、宝可梦名、人名优先采用术语表和通行中文译名；"
          "纯数字、纯符号、纯英文缩写原样保留；只输出合法 JSON。")


def gaps(fm):
    """(index, row) of every text row whose translation is empty"""
    rows = fm.get("parallel_items") or fm.get("translation_segments") or []
    out = []
    for i, it in enumerate(rows):
        if not isinstance(it, dict) or it.get("type") in ("image", "header", "profile"):
            continue
        o, t = it.get("original"), it.get("translation")
        if isinstance(o, str) and o.strip() and not (isinstance(t, str) and t.strip()):
            out.append((i, it))
    return rows, out


def yaml_scalar(s):
    """a double-quoted YAML scalar for one line"""
    return json.dumps(s, ensure_ascii=False)


def write_back(path, text, rows, done):
    """the empty translation line right after each filled row's own original line; the rows
    are found in file order, so the n-th empty translation after the n-th matching original"""
    lines = text.split("\n")
    # every `original:` line's index, in order; the k-th text row with an original maps to the k-th such line
    orig_lines = [n for n, l in enumerate(lines) if re.match(r"^\s+original: ", l)]
    row_with_orig = [i for i, it in enumerate(rows) if isinstance(it, dict) and isinstance(it.get("original"), str)]
    if len(orig_lines) != len(row_with_orig):
        raise RuntimeError(f"{path.name}: {len(orig_lines)} original lines but {len(row_with_orig)} rows carry one - not a line-per-row file")
    at = dict(zip(row_with_orig, orig_lines))
    filled = 0
    for i, tr in done.items():
        n = at[i]
        # the translation line of this row: the next `translation:` before the next row starts
        j = n + 1
        while j < len(lines) and not re.match(r"^\s+- |^\S", lines[j]) and not re.match(r"^\s+translation:", lines[j]):
            j += 1
        indent = re.match(r"^(\s+)", lines[n]).group(1)
        if j < len(lines) and re.match(r"^\s+translation:\s*(\"\"|''|)\s*$", lines[j]):
            lines[j] = f"{indent}translation: {yaml_scalar(tr)}"
        else:
            lines.insert(n + 1, f"{indent}translation: {yaml_scalar(tr)}")
            # later line numbers shift by one
            for k in at:
                if at[k] > n:
                    at[k] += 1
        filled += 1
    return "\n".join(lines), filled


def translate(post_title, rows, missing, glossary):
    full = "\n".join(it["original"] for _, it in missing)
    hits = nom.glossary_hits(full, glossary)
    gloss = "\n".join(f"- {s} → {t}" for s, t in hits) or "（无）"
    system = SYSTEM + f"\n术语表：\n{gloss}"
    done = {}
    chunk = 25
    for start in range(0, len(missing), chunk):
        part = missing[start:start + chunk]
        payload = []
        for i, it in part:
            # a translated neighbour, for the wording of the same page
            near = ""
            for k in (i - 1, i + 1, i - 2, i + 2):
                if 0 <= k < len(rows) and isinstance(rows[k], dict) and isinstance(rows[k].get("translation"), str) and rows[k]["translation"].strip() and isinstance(rows[k].get("original"), str):
                    near = f"{rows[k]['original'][:60]} → {rows[k]['translation'][:60]}"
                    break
            payload.append({"i": i, "kind": it.get("type") or it.get("region_type") or "", "text": it["original"], "near": near})
        prompt = (f"这是《{post_title}》扫描页上的零散文字。逐条把 text 译成简体中文，保留编号 i；near 是同一页已译好的邻句，用它统一用词；"
                  f"标题照译成标题，图注照译成图注，排行榜条目保留名次和属性写法。\n\n"
                  f"输出格式：{{\"items\":[{{\"i\":编号,\"translation\":\"译文\"}}]}}\n\n待译：\n{json.dumps(payload, ensure_ascii=False)}")
        print(f"    translating {start + 1}-{start + len(part)} / {len(missing)} ...", flush=True)
        got = None
        for attempt in range(3):
            raw = nom.deepseek([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
            try:
                got = {int(r["i"]): str(r.get("translation", "")).strip() for r in json.loads(raw).get("items", []) if "i" in r}
                break
            except (ValueError, TypeError) as exc:
                print(f"    bad JSON from the model (attempt {attempt + 1}): {exc}", file=sys.stderr)
        if got is None:
            raise RuntimeError("a chunk failed three times")
        for i, it in part:
            if got.get(i):
                done[i] = got[i].replace("・", "·")      # the site writes 黑2·白2, not the Japanese dot
        time.sleep(1)
    return done


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    listing = "--list" in sys.argv
    glossary = None if listing else nom.load_glossary()
    total = 0
    for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        path = Path(f)
        if only and only not in path.name:
            continue
        text = io.open(path, encoding="utf-8", newline="").read()
        m = FRONT.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        rows, missing = gaps(fm)
        if not missing:
            continue
        print(f"== {path.name}: {len(missing)} of {len(rows)} rows without a translation")
        total += len(missing)
        if listing:
            continue
        nl = "\r\n" if "\r\n" in text[:2000] else "\n"
        body = text.replace("\r\n", "\n")
        done = translate(str(fm.get("title") or path.stem), rows, missing, glossary)
        new, filled = write_back(path, body, rows, done)
        # the result must parse and hold what was written
        fm2 = yaml.safe_load(FRONT.match(new).group(1))
        left = len(gaps(fm2)[1])
        io.open(path, "w", encoding="utf-8", newline="").write(new.replace("\n", nl) if nl == "\r\n" else new)
        print(f"   filled {filled}, {left} still empty")
    print(f"{total} segments" + (" listed" if listing else " handled"))


if __name__ == "__main__":
    main()
