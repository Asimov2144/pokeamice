#!/usr/bin/env python3
"""每次部署时把给 App 的数据（assets/data/app/）重导一遍：导出前补齐、导出后检查并定版本号。

在 .github/workflows/jekyll.yml 里按这个顺序跑：

    python tools/app-data-release.py fill-concepts          # 1. 导出前：补上图鉴条目缺的概念标注
    python tools/export-docs-archive.py --commit <sha>       # 2. 导出（写进源目录，Jekyll 原样拷进 _site）
    python tools/export-document-entities.py --commit <sha>
    bundle exec jekyll build
    python tools/app-data-release.py check --site _site --commit <sha>   # 3. 检查 + 定版本号

fill-concepts
    概念是规则标注（build-post-lore.py --concepts，不花钱）。图鉴条目记录要是在别处重建时丢了
    facets.concepts，这里当场补上再导出，并在 Actions 里留一条警告——补的结果只在这次部署里，
    要落进仓库得在本地跑同一条命令再提交。

check
    ① 检查：拿这次导出的 manifest 计数和线上那份比（线上拉不到就和仓库里提交的那份比），
       篇数、段数、人物、图鉴条目、概念行等明显变少就报错退出，部署停下，线上保持原样。
       有意撤帖 / 删数据时，在推送的最后一个提交说明里写 [app-data allow-shrink]，
       或手动运行工作流时勾上 allow_shrink。schema_version 变了会让旧版 App 读不了，
       另要 [app-data allow-schema]。
    ② 版本号：App 按 manifest.docs_commit 缓存所有数据，版本号一变就整份重拉。所以先算这次导出
       的内容指纹（除 manifest 外的所有文件 + 今日一句句库；两张 document 表去掉版本与时间）
       写进 manifest.content_hash：和线上那份相同 = 数据没变，沿用线上的 docs_commit 和
       generated_at，App 什么都不用重拉；不同才盖成这次提交的短 sha。
       两张 document 表头上的 docs_commit / generated_at 跟 manifest 对齐。
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LORE = ROOT / "data" / "post_lore"
EVIDENCE = ROOT / "design" / "concepts-evidence.json"
LIVE = "https://docs.pokeamice.com/assets/data/app/manifest.json"
DATA = Path("assets") / "data" / "app"
QUOTES = Path("assets") / "js" / "quotes.json"          # App 也按 docs_commit 缓存这一份（docsApi.quotes）
DOC_TABLES = ("document-entities.json", "document-concepts.json")
ALLOW_SHRINK = "[app-data allow-shrink]"
ALLOW_SCHEMA = "[app-data allow-schema]"

#  计数路径 → (允许少几个, 允许少几成)：少得比两者都多才算「明显变少」
TOLERANCE = {
    "posts": (3, 0),
    "by_kind.*": (3, 0),
    "segments": (0, 0.02),
    "people": (3, 0.01),
    "people_with_credits": (3, 0.01),
    "speakers": (3, 0.02),
    "works": (2, 0.02),
    "credits_games": (1, 0),
    "credits_indexed": (1, 0),
    "atlas": (1, 0),
    "staff_rows": (0, 0.02),
    "relations": (1, 0),
    "glossary": (0, 0.05),
    "topics": (1, 0),
    "search_bytes": (0, 0.05),
    "posts_bytes": (0, 0.05),
    "lore.posts": (3, 0),
    "lore.dex": (0, 0.05),
    "lore.observations": (0, 0.03),
    "lore.relations": (0, 0.03),
    "lore.concepts": (2, 0),
    "lore.concept_rows": (0, 0.03),
}
SUMMARY_KEYS = ("posts", "segments", "people", "speakers", "works", "staff_rows", "lore.posts", "lore.observations",
                "lore.concept_rows", "search_bytes", "posts_bytes")

IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


def say(level: str, msg: str) -> None:
    """Actions 里写成注解（显示在运行页顶上），本地照常打印"""
    if IN_ACTIONS:
        print(f"::{level} title=App 数据::{msg}")
    else:
        print(f"[{level}] {msg}")


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))      # 和两个导出器一字不差


def write(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(dumps(obj), encoding="utf-8")
    os.replace(tmp, path)


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except Exception:
        return ""


# ---------------------------------------------------------------- fill-concepts

FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---", re.S)


def published(stem: str) -> bool:
    f = ROOT / "_posts" / f"{stem}.md"
    if not stem or not f.exists():
        return False
    m = FRONT.match(f.read_text(encoding="utf-8", errors="replace"))
    return not (m and re.search(r"(?m)^published:\s*false\s*$", m.group(1)))


def fill_concepts() -> int:
    missing = []
    for f in sorted(LORE.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if "concepts" not in (rec.get("facets") or {}) and published(rec.get("stem") or ""):
            missing.append(rec.get("id") or f.stem)
    if not missing:
        print("图鉴条目的概念标注齐全")
        return 0
    keep = EVIDENCE.read_bytes() if EVIDENCE.exists() else None     # --only 会把证据文件写成局部统计
    try:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build-post-lore.py"), "--concepts", "--only", *missing],
                       cwd=ROOT, check=True)
    finally:
        if keep is not None:
            EVIDENCE.write_bytes(keep)
    say("warning", f"{len(missing)} 篇的图鉴条目缺概念标注，这次部署已当场补上（{'、'.join(missing[:6])}"
                   f"{' 等' if len(missing) > 6 else ''}）。要落进仓库：本地跑 "
                   f"python tools/build-post-lore.py --concepts --only <这些 id> 再提交。")
    return 0


# ---------------------------------------------------------------- check

def content_hash(site: Path) -> str:
    h = hashlib.sha256()
    base = site / DATA
    files = sorted(p for p in base.rglob("*") if p.is_file() and p.name != "manifest.json" and not p.name.endswith(".tmp"))
    for p in files:
        rel = p.relative_to(base).as_posix()
        blob = p.read_bytes()
        if rel in DOC_TABLES:
            obj = json.loads(blob)
            obj.pop("docs_commit", None)
            obj.pop("generated_at", None)
            blob = dumps(obj).encode("utf-8")
        h.update(rel.encode("utf-8") + b"\0" + blob + b"\0")
    quotes = site / QUOTES
    if quotes.exists():
        h.update(b"../../js/quotes.json\0" + quotes.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def baseline(url: str) -> tuple[dict | None, str]:
    """线上那份 manifest；拉不到就退回仓库里提交的那份（它没有 content_hash，版本号一定会换）。
    --live 给本地文件路径时直接读它（本地演练用）"""
    if not url.startswith(("http://", "https://")):
        return json.loads(Path(url).read_text(encoding="utf-8")), "线上"
    last: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(f"{url}?t={int(time.time())}", headers={"User-Agent": "pokeamice-docs-deploy"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8")), "线上"
        except Exception as exc:                                    # noqa: BLE001 - 网络不通也要能部署
            last = exc
            time.sleep(2 * (attempt + 1))
    say("warning", f"拉不到线上 manifest（{last}），改和仓库里提交的那份比")
    text = git("show", f"HEAD:{DATA.as_posix()}/manifest.json")
    return (json.loads(text) if text.strip() else None), "仓库"


def flat(counts: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in (counts or {}).items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flat(v, key + "."))
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            out[key] = v
    return out


def tolerance(key: str):
    if key in TOLERANCE:
        return TOLERANCE[key]
    head = key.rsplit(".", 1)[0] + ".*"
    return TOLERANCE.get(head)


def shrinkage(old: dict, new: dict) -> list[str]:
    o, n = flat(old), flat(new)
    bad = []
    for key, was in sorted(o.items()):
        tol = tolerance(key)
        if tol is None:
            continue
        now = n.get(key, 0)
        allowed = max(tol[0], tol[1] * was)
        if was - now > allowed:
            bad.append(f"{key} {was:,} → {now:,}（少了 {was - now:,}，允许 {allowed:,.0f}）")
    return bad


def integrity(site: Path, manifest: dict) -> list[str]:
    base = site / DATA
    bad = []
    index = json.loads((base / "index.json").read_text(encoding="utf-8"))["items"]
    ids = [it["id"] for it in index]
    if len(ids) != len(set(ids)):
        bad.append(f"index.json 有重复 id：{len(ids) - len(set(ids))} 个")
    lost = [i for i in ids if not (base / "posts" / f"{i}.json").exists()]
    if lost:
        bad.append(f"index.json 里 {len(lost)} 篇没有 posts/<id>.json（{'、'.join(lost[:5])}）")
    if (manifest.get("counts") or {}).get("posts") != len(ids):
        bad.append(f"manifest 的 posts 计数 {manifest.get('counts', {}).get('posts')} 和 index.json 的 {len(ids)} 篇对不上")
    for name in DOC_TABLES:
        if not (base / name).exists():
            bad.append(f"缺 {name}")
    return bad


def check(args) -> int:
    site = Path(args.site)
    path = site / DATA / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    message = git("log", "-1", "--format=%B")
    allow_shrink = args.allow_shrink or ALLOW_SHRINK in message or os.environ.get("APP_DATA_ALLOW_SHRINK", "").lower() in ("1", "true")
    allow_schema = ALLOW_SCHEMA in message

    old, where = baseline(args.live)
    errors = integrity(site, manifest)
    if old:
        if old.get("schema_version") != manifest.get("schema_version"):
            msg = f"schema_version {old.get('schema_version')} → {manifest.get('schema_version')}：旧版 App 会读不了"
            if allow_schema:
                say("warning", msg + f"（提交说明写了 {ALLOW_SCHEMA}，放行）")
            else:
                errors.append(msg + f"。确定要换，在提交说明里写 {ALLOW_SCHEMA}")
        shrunk = shrinkage(old.get("counts") or {}, manifest.get("counts") or {})
        if shrunk:
            if allow_shrink:
                for s in shrunk:
                    say("warning", f"比{where}少了：{s}（已放行）")
            else:
                errors += [f"比{where}明显变少：{s}" for s in shrunk]
                errors.append(f"有意撤帖 / 删数据的话，在推送的最后一个提交说明里写 {ALLOW_SHRINK}，"
                              f"或手动运行工作流时勾上 allow_shrink")

    digest = content_hash(site)
    same = bool(old) and where == "线上" and old.get("content_hash") == digest
    stamped = {}
    for k, v in manifest.items():
        if k == "content_hash":
            continue
        if k == "docs_commit":
            v = old["docs_commit"] if same else (args.commit or v)
        elif k == "generated_at" and same:
            v = old.get("generated_at") or v
        stamped[k] = v
        if k == "docs_commit":
            stamped["content_hash"] = digest

    rows = [f"| {k} | {flat(old.get('counts') or {}).get(k, '–') if old else '–'} | {flat(manifest.get('counts') or {}).get(k, '–')} |"
            for k in SUMMARY_KEYS]
    verdict = (f"数据没变，沿用{where}的版本 `{stamped['docs_commit']}`" if same
               else f"数据有变，新版本 `{stamped['docs_commit']}`（内容指纹 `{digest}`）")
    report = "\n".join([f"### App 数据（assets/data/app）", "", verdict, "",
                        f"| 计数 | {where} | 这次 |", "|---|---:|---:|", *rows, ""]
                       + ([f"**没通过：**", ""] + [f"- {e}" for e in errors] if errors else []))
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with io.open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    if errors:
        for e in errors:
            say("error", e)
        return 1

    write(path, stamped)
    for name in DOC_TABLES:
        p = site / DATA / name
        obj = json.loads(p.read_text(encoding="utf-8"))
        obj["docs_commit"], obj["generated_at"] = stamped["docs_commit"], stamped["generated_at"]
        write(p, obj)
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fill-concepts")
    c = sub.add_parser("check")
    c.add_argument("--site", default="_site")
    c.add_argument("--commit", default="", help="这次提交的短 sha；数据有变时盖进 docs_commit")
    c.add_argument("--live", default=LIVE)
    c.add_argument("--allow-shrink", action="store_true")
    args = ap.parse_args()
    return fill_concepts() if args.cmd == "fill-concepts" else check(args)


if __name__ == "__main__":
    raise SystemExit(main())
