"""Build the data file used by the public GAME FREAK Staff Blog report."""

from __future__ import annotations

import argparse
import re
import statistics
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from gamefreak_staff_names import applicable_names, load_policy, read_markdown


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "archive" / "gamefreak-staff" / "manifest" / "articles.yml"
DEFAULT_CONTENT = ROOT / "archive" / "gamefreak-staff" / "content"
DEFAULT_TRANSLATIONS = ROOT / "archive" / "gamefreak-staff" / "translations" / "zh-CN"
DEFAULT_OUTPUT = ROOT / "_data" / "gamefreak_staff_analysis.yml"

THEMES = [
    {
        "id": "pokemon",
        "label": "宝可梦与作品",
        "description": "宝可梦作品、对战、卡牌、角色和开发访谈。",
        "keywords": ["ポケモン", "ポケットモンスター", "ブラック・ホワイト", "ハートゴールド", "ソウルシルバー"],
    },
    {
        "id": "development",
        "label": "开发与制作",
        "description": "企划、程序、美术、声音、设计与制作现场。",
        "keywords": ["開発", "プログラム", "プログラマー", "グラフィック", "デザイン", "サウンド", "企画"],
    },
    {
        "id": "recruitment",
        "label": "招聘与职业",
        "description": "应届招聘、说明会、面试、求职与新人经验。",
        "keywords": ["採用", "就職", "新卒", "会社説明会", "面接", "入社"],
    },
    {
        "id": "company",
        "label": "公司与集体活动",
        "description": "办公室、公司制度、员工活动、比赛与聚会。",
        "keywords": ["社内", "会社", "オフィス", "イベント", "パーティ", "大会", "引越し"],
    },
    {
        "id": "daily-life",
        "label": "日常、兴趣与旅行",
        "description": "假期、旅行、饮食、运动、宠物和个人兴趣。",
        "keywords": ["旅行", "夏休み", "冬休み", "休日", "料理", "食べ", "スポーツ", "ペット", "趣味"],
    },
]

ROLES = [
    ("企划", ["プランナー", "企画"]),
    ("程序", ["プログラマー", "プログラム"]),
    ("美术与图形", ["グラフィック", "デザイナー", "デザイン"]),
    ("网站", ["Web担当", "Web制作", "ウェブ", "サイト担当"]),
    ("声音", ["サウンド", "音楽"]),
    ("招聘", ["採用担当", "採用"]),
]

STRUCTURAL_RE = re.compile(r"\{%.*?%\}|\{\{.*?\}\}|<[^>]+>|\[[^]]+\]\([^)]+\)", re.DOTALL)
IMAGE_RE = re.compile(r"\{%\s*legacy_image\b")
LINK_RE = re.compile(r"\[[^]]+\]\([^)]+\)")


def percent(value: int, total: int) -> float:
    return round(value * 100 / total, 1) if total else 0.0


def article_url(article_id: int) -> str:
    return f"/gamefreak-staff/entry-{article_id}/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Staff Blog analysis data for Jekyll.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--content", type=Path, default=DEFAULT_CONTENT)
    parser.add_argument("--translations", type=Path, default=DEFAULT_TRANSLATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8")) or {}
    articles = manifest.get("articles") or []
    if not articles:
        raise SystemExit("Staff Blog manifest contains no articles.")

    entries = load_policy()
    records: list[dict[str, Any]] = []
    person_articles: dict[str, list[dict[str, Any]]] = {}
    source_tags: Counter[str] = Counter()
    year_counts: Counter[int] = Counter()
    theme_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    dates: list[date] = []
    translated = 0
    image_count = 0
    image_articles = 0
    link_count = 0
    link_articles = 0

    for article in articles:
        article_id = int(article["id"])
        article_date = date.fromisoformat(str(article["date"]))
        source_path = args.content / str(article_id) / "ja.md"
        _metadata, body = read_markdown(source_path)
        translation_path = args.translations / f"{article_id}.md"
        translation_metadata: dict[str, Any] = {}
        translation_body = ""
        if translation_path.exists():
            translation_metadata, translation_body = read_markdown(translation_path)
        has_translation = bool(translation_body.strip()) and str(
            translation_metadata.get("translation_status") or ""
        ) not in {"", "missing"}
        title_zh = str(translation_metadata.get("translation_title") or "").strip()
        visible = STRUCTURAL_RE.sub("", body)
        compact = re.sub(r"\s+", "", visible)
        searchable = f"{article.get('title', '')}\n{visible}"
        images = len(IMAGE_RE.findall(body))
        links = len(LINK_RE.findall(body))

        dates.append(article_date)
        year_counts[article_date.year] += 1
        source_tags.update(str(tag) for tag in article.get("tags") or [])
        image_count += images
        image_articles += int(images > 0)
        link_count += links
        link_articles += int(links > 0)
        translated += int(has_translation)

        matched_themes: list[str] = []
        for theme in THEMES:
            if any(keyword in searchable for keyword in theme["keywords"]):
                theme_counts[theme["id"]] += 1
                matched_themes.append(theme["id"])
        for label, keywords in ROLES:
            if any(keyword in searchable for keyword in keywords):
                role_counts[label] += 1

        for entry in applicable_names(body, entries, article_id):
            person_articles.setdefault(entry["source"], []).append(
                {
                    "id": article_id,
                    "date": article_date.isoformat(),
                    "title": article.get("title") or "",
                    "title_zh": title_zh,
                    "url": article_url(article_id),
                    "target": entry["target"],
                }
            )

        records.append(
            {
                "id": article_id,
                "date": article_date.isoformat(),
                "year": article_date.year,
                "title": article.get("title") or "",
                "title_zh": title_zh,
                "url": article_url(article_id),
                "characters": len(compact),
                "images": images,
                "links": links,
                "themes": matched_themes,
            }
        )

    records.sort(key=lambda item: item["date"])
    dates.sort()
    gaps = [(later - earlier).days for earlier, later in zip(dates, dates[1:])]
    character_counts = [record["characters"] for record in records]
    longest = sorted(records, key=lambda item: item["characters"], reverse=True)[:5]
    most_visual = sorted(records, key=lambda item: (item["images"], item["characters"]), reverse=True)[:5]
    max_gap = max(gaps)
    max_gap_index = gaps.index(max_gap)
    total = len(records)

    people = []
    for source, appearances in person_articles.items():
        appearances.sort(key=lambda item: item["date"])
        people.append(
            {
                "source": source,
                "target": appearances[0]["target"],
                "article_count": len(appearances),
                "share": percent(len(appearances), total),
                "first": appearances[0],
                "last": appearances[-1],
            }
        )
    people.sort(key=lambda item: (-item["article_count"], item["source"]))

    data = {
        "schema_version": 1,
        "source_manifest_generated_at": manifest.get("generated_at"),
        "method": {
            "article_authority": "archive/gamefreak-staff/manifest/articles.yml",
            "text_layer": "archive/gamefreak-staff/content/*/ja.md",
            "translation_layer": "archive/gamefreak-staff/translations/zh-CN/*.md",
            "people_policy": "archive/gamefreak-staff/staff-names.yml",
            "note": "主题和职位为日文标题及正文的关键词命中，类别彼此重叠；人物统计表示正文提及，不等同于署名作者。",
        },
        "overview": {
            "articles": total,
            "first_date": dates[0].isoformat(),
            "last_date": dates[-1].isoformat(),
            "calendar_days": (dates[-1] - dates[0]).days + 1,
            "years": len(year_counts),
            "translations": translated,
            "translation_rate": percent(translated, total),
            "source_characters": sum(character_counts),
            "average_characters": round(statistics.mean(character_counts)),
            "median_characters": round(statistics.median(character_counts)),
            "images": image_count,
            "image_articles": image_articles,
            "image_article_rate": percent(image_articles, total),
            "links": link_count,
            "link_articles": link_articles,
            "link_article_rate": percent(link_articles, total),
            "named_people": len(people),
        },
        "cadence": {
            "median_gap_days": round(statistics.median(gaps), 1),
            "average_gap_days": round(statistics.mean(gaps), 1),
            "within_10_days": sum(gap <= 10 for gap in gaps),
            "within_10_days_rate": percent(sum(gap <= 10 for gap in gaps), len(gaps)),
            "longest_gap_days": max_gap,
            "longest_gap_from": dates[max_gap_index].isoformat(),
            "longest_gap_to": dates[max_gap_index + 1].isoformat(),
        },
        "years": [
            {
                "year": year,
                "count": count,
                "share": percent(count, total),
                "relative": percent(count, max(year_counts.values())),
            }
            for year, count in sorted(year_counts.items())
        ],
        "themes": [
            {
                "id": theme["id"],
                "label": theme["label"],
                "description": theme["description"],
                "count": theme_counts[theme["id"]],
                "share": percent(theme_counts[theme["id"]], total),
                "keywords": theme["keywords"],
            }
            for theme in THEMES
        ],
        "roles": [
            {"label": label, "count": role_counts[label], "share": percent(role_counts[label], total)}
            for label, _keywords in ROLES
        ],
        "source_tags": [
            {"label": label, "count": count, "share": percent(count, total)}
            for label, count in source_tags.most_common()
        ],
        "people": people,
        "longest_articles": longest,
        "most_visual_articles": most_visual,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )
    print(
        f"staff analysis: {total} articles; {translated} translations; "
        f"{len(people)} named people; {image_count} images"
    )


if __name__ == "__main__":
    main()
