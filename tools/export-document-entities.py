#!/usr/bin/env python3
"""文章 ↔ 作品 / 宝可梦 / 地点 / 人：给服务器 `document_entities` 的那张表（worklist D-2）。

    python tools/export-document-entities.py                 # 写 assets/data/app/document-entities.json
                                                            #  + document-concepts.json（同一张表的另一半）
    python tools/export-document-entities.py --out <文件>

每篇文章的图鉴条目（tools/build-post-lore.py，data/post_lore/<id>.json）里已经有「这篇点名了什么、
在第几段」。这里把它摊平成规格 02 §6 的那几列：

    document_id · entity_id · role · start_offset · end_offset · confidence · reviewed

和规格的对照，三处要说清楚：

`start_offset` 是**段号**，不是字符偏移。docs 的正文按段存（导出给 App 的 `body.segments[].n`），
没有稳定的字符偏移；主键是 (document_id, entity_id, start_offset)，所以同一篇同一个实体在第几段
出现就是第几行。整篇级的（前言里写了、正文没点名）给 `-1`，`end_offset` 一律 null。

`entity_id` 只在 docs 认得出服务器那份 registry 的 id 时才填（计划 §3-3 的规范 ID）：

    pokemon   全国图鉴号补四位        pokemon:0025      registry 已有（1,025 + 58 形态）
    place     旅图地点 id             place:carrot_tower registry 已有（tour-places 714）
    person    docs 的人物 slug        person:masuda-junichi   registry 还没有 person，这就是它的 source_id
    document  docs 的文章 id          document:interview-…    同上

作品不填：服务器的 work registry 是你们作品库的 377 条，docs 这边只有站内作品名和制作名单的 slug
（3,161 条边里 1,057 条有 slug），对不上就不硬填——每行都带 `source`，crosswalk 一映就有了。
地点同理：只有 43 条边能落到某一处店址，另外 66 条说的是「这家店」（`place_entity`，按文章日期落店址）、
11 条是一片地方（`place_area`）、22 条是「关于宝可梦中心」这一类（`place_category`）、516 条是游戏里的地名
（`world: game`，不是现实地点）、1,198 条旅图上没有，只有名字。

`confidence` 由 `via` 映射（CONFIDENCE），`reviewed` 是这篇的条目有没有人工改过（记录里的 `edited`）。
`role`：人物是 speaker / mentioned，作品命中这篇的主体作品是 subject、其余 mentions，
地点里游戏与动画中的地方是 setting，其余一律 mentions，概念是 topic。

概念（`concept:<id>`）的 id 空间是 docs 的词表 data/lore_tables/concepts.yml：人写的一份，逐段按写法
命中（via: body / tag / title），不是模型推测。词表里人审过的那几条，这张表里的 `reviewed` 就是 1
——其余仍是 0。名字、归面与一句说明在 assets/data/app/concepts.json。
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
LORE = ROOT / "data" / "post_lore"
DEFAULT_OUT = ROOT / "assets" / "data" / "app" / "document-entities.json"
DEFAULT_CONCEPTS_OUT = ROOT / "assets" / "data" / "app" / "document-concepts.json"
SCHEMA = "document-entities/v1"

#  来源 → 置信度。规则扫出来的（正文、标签、标题、gazetteer、手写补充表）都是「确立」，
#  模型补的是推测——App 的证据闸也是按这条线分的（docsDex.loreLevel）。
CONFIDENCE = {
    "entities": 0.95,   # 前言里编者写的
    "body": 0.90,       # 正文里按写法表命中
    "gazetteer": 0.90,  # 旅图地点表命中
    "extra": 0.90,      # 手写的地名补充表
    "tag": 0.85,
    "title": 0.80,
    "llm": 0.50,        # 只有模型点出来的
}


def git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:                                                  # noqa: BLE001
        return ""


def load_lore() -> list:
    out = []
    for path in sorted(LORE.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if rec.get("id"):
            out.append(rec)
    return out


def primary_work_of(index: dict, post_id: str) -> str:
    row = index.get(post_id) or {}
    return ((row.get("primary_work") or {}).get("name") or "").strip()


def rows_for(rec: dict, primary: str) -> list:
    """一篇的所有边，已经按段摊平"""
    facets = rec.get("facets") or {}
    document = f"document:{rec['id']}"
    reviewed = 1 if rec.get("edited") else 0
    out = []

    def add(entity_id, source: dict, role: str, segs: list, via: str, extra: dict | None = None,
            reviewed_row: bool | None = None) -> None:
        spots = [n for n in (segs or []) if isinstance(n, int)] or [-1]
        for n in spots:
            row = {"document_id": document, "entity_id": entity_id, "role": role,
                   "start_offset": n, "end_offset": None,
                   "confidence": CONFIDENCE.get(via, 0.5),
                   "reviewed": 1 if reviewed_row else reviewed,
                   "via": via or "", "source": source}
            if extra:
                row.update(extra)
            out.append(row)

    for k in facets.get("pokemon") or []:
        ndex = k.get("ndex")
        if not isinstance(ndex, int) or ndex <= 0:
            continue
        canonical = f"pokemon:{ndex:04d}" if ndex < 10000 else f"pokemon:{ndex}"
        add(canonical, {"system": "docs", "type": "pokemon", "id": str(ndex), "name": k.get("name")},
            "mentions", k.get("seg"), k.get("via") or "body")

    for w in facets.get("works") or []:
        name = (w.get("name") or "").strip()
        if not name:
            continue
        #  服务器的 work registry 是作品库的 id，docs 对不上——entity_id 留空，让 crosswalk 映
        add(None, {"system": "docs", "type": "work", "id": w.get("slug") or name, "name": name,
                   "credits_slug": w.get("slug")},
            "subject" if name == primary else "mentions", w.get("seg"), w.get("via") or "entities")

    for p in facets.get("people") or []:
        name = (p.get("name") or "").strip()
        slug = (p.get("slug") or "").strip()
        if not name:
            continue
        add(f"person:{slug}" if slug else None,
            {"system": "docs", "type": "person", "id": slug or name, "name": name, "kind": p.get("kind")},
            "speaker" if p.get("role") == "speaker" else "mentioned", p.get("seg"), p.get("via") or "entities")

    for s in facets.get("places") or []:
        name = (s.get("name") or "").strip()
        if not name:
            continue
        extra = {k: s[k] for k in ("entity", "area", "category_link", "world", "scale", "what", "when") if s.get(k)}
        if "category_link" in extra:
            extra["place_category"] = extra.pop("category_link")
        if "entity" in extra:
            extra["place_entity"] = extra.pop("entity")
        if "area" in extra:
            extra["place_area"] = extra.pop("area")
        add(f"place:{s['id']}" if s.get("id") else None,
            {"system": "tour" if s.get("id") else "docs", "type": "place", "id": s.get("id") or name, "name": name},
            "setting" if s.get("world") == "game" else "mentions", s.get("seg"), s.get("via") or "gazetteer", extra)

    #  概念：人写的词表逐段命中（data/lore_tables/concepts.yml）。id 空间是 docs 的，
    #  规范 ID 就是 `concept:<id>`（dex-core 的 12 类之一）；词表里人审过的那几条 reviewed = 1
    for t in facets.get("concepts") or []:
        cid = (t.get("id") or "").strip()
        if not cid:
            continue
        add(f"concept:{cid}",
            {"system": "docs", "type": "concept", "id": cid, "name": t.get("name"),
             **({"facet": t["facet"]} if t.get("facet") else {}),
             **({"as": t["as"]} if t.get("as") else {})},
            "topic", t.get("seg"), t.get("via") or "body", reviewed_row=bool(t.get("reviewed")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--concepts-out", type=Path, default=DEFAULT_CONCEPTS_OUT)
    ap.add_argument("--commit", default="")
    args = ap.parse_args()

    index_path = ROOT / "assets" / "data" / "app" / "index.json"
    index = {}
    if index_path.exists():
        index = {row["id"]: row for row in json.loads(index_path.read_text(encoding="utf-8")).get("items", [])}

    rows = []
    for rec in load_lore():
        rows.extend(rows_for(rec, primary_work_of(index, rec["id"])))

    #  主键是 (document_id, entity_id, start_offset)：同一段里「GAME FREAK」与「三轩茶屋」
    #  都落到胡萝卜塔，那是同一行。留最可靠的那次，别的写法记在 also 里
    merged: dict = {}
    for row in rows:
        key = (row["document_id"], row["entity_id"] or f"{row['source']['type']}~{row['source']['id']}", row["start_offset"])
        had = merged.get(key)
        if had is None:
            merged[key] = row
            continue
        keep, drop = (had, row) if had["confidence"] >= row["confidence"] else (row, had)
        name = (drop.get("source") or {}).get("name")
        if name and name != (keep.get("source") or {}).get("name"):
            keep.setdefault("also", [])
            if name not in keep["also"]:
                keep["also"].append(name)
        merged[key] = keep
    rows = list(merged.values())

    #  同一张表，分两个文件写：实体那一半 App 在阅读器里要整份拉（手机上 5 MB 已经不轻），
    #  概念那一半只有服务器和以后的概念层要，别让它把阅读器的那一份撑大一倍
    parts = [("entities", args.out, [r for r in rows if r["source"]["type"] != "concept"]),
             ("concepts", args.concepts_out, [r for r in rows if r["source"]["type"] == "concept"])]
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    commit = args.commit or git_head()
    for part, path, part_rows in parts:
        other = next(p.name for kind, p, _ in parts if kind != part)
        payload = {
            "schema": SCHEMA,
            "spec": "scan-engineering-2026-09-24/02 §6 document_entities",
            "source_system": "docs",
            "part": part,
            "pair": other,
            "docs_commit": commit,
            "generated_at": stamp,
            "notes": {
                "start_offset": "段号（body.segments[].n）；整篇级的给 -1，没有字符偏移",
                "entity_id": "只在 docs 认得出服务器 registry 的 id 时才填；其余为 null，按 source 做 crosswalk",
                "part": f"document_entities 的一半，另一半在 {other}；服务器两份都收",
                "confidence": CONFIDENCE,
            },
            "counts": {
                "documents": len({r["document_id"] for r in part_rows}),
                "rows": len(part_rows),
                "by_type": dict(collections.Counter(r["source"]["type"] for r in part_rows)),
                "with_entity_id": dict(collections.Counter(r["source"]["type"] for r in part_rows if r["entity_id"])),
            },
            "rows": part_rows,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        tmp = path.with_suffix(path.suffix + ".tmp")
        for attempt in range(4):
            try:
                tmp.write_text(text, encoding="utf-8")
                os.replace(tmp, path)
                break
            except OSError:
                if attempt == 3:
                    raise
                time.sleep(0.4 * (attempt + 1))
        print(json.dumps({k: payload[k] for k in ("part", "docs_commit", "counts")}, ensure_ascii=False, indent=1))
        print(f"→ {path.name}  {len(text) // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
