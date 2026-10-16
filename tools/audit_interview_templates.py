"""Read-only coverage audit for the editorial reader's content-form templates.

Keep resolve_template in step with _includes/interview-template.html. The audit
counts published posts only by default; --all includes unpublished material.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRONT = re.compile(r"\A\ufeff?---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
TEMPLATES = ("conversation", "roundtable", "longform", "profile", "annotated", "narrative", "technical", "scan")
COMMENTATORS = {"Dr. Lava", "Dr Lava", "Dr.Lava", "编者注", "编者按", "编者", "译者注", "作者解说", "Editor", "Editorial"}
CROWD = {"众人", "全员", "一同", "全体", "众人（笑）", "Everyone", "All"}


def features(page):
    items = page.get("parallel_items") or page.get("translation_segments") or page.get("segments") or []
    commentators = COMMENTATORS | set(page.get("commentary_speakers") or [])
    guests = []
    questions = headings = answers = commentary = chars = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        role, speaker = item.get("role"), item.get("speaker")
        is_commentary = role == "commentary" or item.get("voice") == "commentary" or speaker in commentators
        commentary += int(is_commentary)
        questions += int(role == "question")
        headings += int(item.get("type") in ("heading", "header"))
        chars += len(str(item.get("translation") or ""))
        if role == "answer" and not is_commentary:
            answers += 1
            if speaker and speaker not in CROWD and speaker not in guests:
                guests.append(speaker)
    scan = bool(page.get("translation_segments") and (page.get("source_pages") or page.get("scan_pages") or page.get("archive_type") == "scan_translation"))
    source = page.get("source") if isinstance(page.get("source"), dict) else {}
    technical = page.get("source_kind") in ("technical_report", "lecture_report") or source.get("source_type") in ("technical_report", "lecture_report") or page.get("article_kind") == "technical_feature"
    return dict(items=len(items), questions=questions, headings=headings, answers=answers,
                guests=guests, commentary=commentary, chars=chars, scan=scan, technical=technical)


def resolve_template(page, f=None):
    f = f or features(page)
    # Structural readers cannot be replaced by a prose template accidentally.
    if f["scan"]:
        return "scan"
    if f["technical"]:
        return "technical"
    explicit = page.get("interview_template")
    if explicit in TEMPLATES and explicit not in ("technical", "scan"):
        return explicit
    if page.get("archive_type") == "interview_excerpt" or f["commentary"]:
        return "annotated"
    if len(f["guests"]) >= 2:
        return "roundtable"
    if not f["questions"]:
        return "profile" if f["answers"] else "narrative"
    if page.get("source_kind") == "corporate_interview" or "-recruit-" in str(page.get("slug", "")):
        return "profile"
    if f["questions"] >= 12 or f["chars"] >= 6000:
        return "longform"
    return "conversation"


def audit(include_unpublished=False):
    rows, errors, legacy_candidates = [], [], []
    for path in sorted((ROOT / "_posts").rglob("*.md")):
        match = FRONT.match(path.read_text(encoding="utf-8-sig"))
        if not match:
            errors.append({"file": path.name, "error": "missing front matter"})
            continue
        try:
            page = yaml.load(match[1], Loader=LOADER) or {}
        except yaml.YAMLError as error:
            errors.append({"file": path.name, "error": str(error)})
            continue
        if not include_unpublished and page.get("published") is False:
            continue
        page.setdefault("slug", path.stem[11:])
        layout = page.get("layout", "single")
        if layout not in ("interview-editorial", "parallel-translation"):
            if layout not in ("gamefreak-director", "gamefreak-legacy-blog") and (
                "interview" in path.name or "采访" in str(page.get("categories")) or
                "访谈" in str(page.get("categories")) or page.get("archive_type") in ("interview_translation", "interview_excerpt")
            ):
                legacy_candidates.append({"file": path.name, "layout": layout, "title": page.get("title")})
            continue
        f = features(page)
        rows.append(dict(file=path.name, title=page.get("title"), layout=layout,
                         template=resolve_template(page, f), explicit=page.get("interview_template"), **f))
    return {
        "scope": "all" if include_unpublished else "published",
        "posts": len(rows),
        "layouts": dict(Counter(r["layout"] for r in rows)),
        "templates": dict(Counter(r["template"] for r in rows)),
        "empty_segment_posts": [r["file"] for r in rows if not r["items"]],
        "invalid_overrides": [r["file"] for r in rows if r["explicit"] and r["explicit"] not in TEMPLATES],
        "commentary_posts": sum(bool(r["commentary"]) for r in rows),
        "legacy_candidates": legacy_candidates,
        "errors": errors,
        "rows": rows,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Include unpublished posts")
    parser.add_argument("--details", action="store_true", help="Include every post's routing features")
    args = parser.parse_args()
    result = audit(args.all)
    if not args.details:
        result["examples"] = {
            key: [{"file": r["file"], "title": r["title"], "guests": r["guests"], "questions": r["questions"]}
                  for r in result["rows"] if r["template"] == key][:3]
            for key in TEMPLATES
        }
        del result["rows"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
