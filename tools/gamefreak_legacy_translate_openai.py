"""Translate the archived Game Freak art and staff blogs with OpenAI.

The source layer is never modified.  Translations are written into each
blog's normal ``translations/zh-CN`` layer so the existing legacy-blog
publisher can expose the Chinese, Japanese and (when available) English
views.  The prompt deliberately changes with the blog: Sugimori's posts are
creator/design notes, while Staff posts are workplace and development diary
entries.
"""

from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path
from typing import Any

import yaml

from gamefreak_translate_deepseek import (
    DEFAULT_GLOSSARY_CANDIDATES,
    clean_card_text,
    clean_translation,
    glossary_checks,
    glossary_context,
    glossary_matches,
    load_glossary,
    utc_now,
    validate_translation,
)
from gamefreak_translate_openai import call_openai
from gamefreak_staff_names import (
    DEFAULT_POLICY as DEFAULT_STAFF_NAMES,
    applicable_names,
    load_policy as load_staff_names,
    name_context,
    normalize_body as normalize_staff_body,
    normalize_card_text as normalize_staff_card_text,
)


ROOT = Path(__file__).resolve().parents[1]

BLOGS: dict[str, dict[str, Any]] = {
    "art": {
        "slug": "gamefreak-art",
        "label": "杉森建博客",
        "author": "杉森建",
        "series": "杉森建的绘画日和",
        "content_dir": ROOT / "archive" / "gamefreak-art" / "content",
        "translation_dir": ROOT / "archive" / "gamefreak-art" / "translations" / "zh-CN",
        "title_style": "【设定资料】+年代+作品/角色/设计主题",
        "scene": (
            "这是画师杉森建记录角色设定稿、电影或游戏相关美术设计的创作者博客。"
            "重点是准确呈现画面说明、设计取舍、人物印象和创作者的轻松口吻；"
            "不要把设计随笔改写成百科、新闻稿或营销文案。"
        ),
    },
    "staff": {
        "slug": "gamefreak-staff",
        "label": "GAME FREAK Staff 博客",
        "author": "GAME FREAK 员工",
        "series": "晴时偶有阴",
        "content_dir": ROOT / "archive" / "gamefreak-staff" / "content",
        "translation_dir": ROOT / "archive" / "gamefreak-staff" / "translations" / "zh-CN",
        "title_style": "【工作日志】+年代+网站/开发/活动/日常主题",
        "scene": (
            "这是 GAME FREAK 员工轮流记录网站制作、游戏开发现场、活动和公司日常的旧博客。"
            "要区分工作人员的自述、现场记录和技术说明，保留亲切自然的工作日志口吻；"
            "不要把日记改写成统一的官方公告，也不要替作者补充背景。"
        ),
    },
}


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text.strip()
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid front matter: {path}")
    return yaml.safe_load(parts[1]) or {}, parts[2].strip()


def write_markdown(path: Path, metadata: dict[str, Any], body: str) -> None:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def source_articles(blog_name: str) -> list[tuple[int, Path, dict[str, Any], str]]:
    blog = BLOGS[blog_name]
    result: list[tuple[int, Path, dict[str, Any], str]] = []
    for path in sorted(blog["content_dir"].glob("*/ja.md")):
        metadata, body = read_markdown(path)
        number = int(metadata.get("post_id") or path.parent.name)
        result.append((number, path, metadata, body))
    return sorted(result, key=lambda item: item[0])


def existing_translation(path: Path) -> bool:
    if not path.exists():
        return False
    metadata, body = read_markdown(path)
    status = str(metadata.get("translation_status") or "")
    return bool(body.strip()) and status not in {"", "missing"} and "中文翻译待完成" not in body


def build_prompt(
    blog_name: str,
    number: int,
    source_metadata: dict[str, Any],
    body: str,
    glossary: str,
    staff_names: str = "",
) -> str:
    blog = BLOGS[blog_name]
    return f"""你是资深日中翻译与宝可梦史料编辑，正在整理 GAME FREAK 的「{blog['series']}」历史博客。

{blog['scene']}

请把下面第 {number} 篇日文正文翻译成自然、准确、亲切的简体中文，供中文宝可梦玩家阅读和人工校对。
译文要像原作者在当时写博客：保留随笔感、现场感、兴奋、自嘲或轻松的语气，但不要擅自卖萌、网络化、补写背景或添加原文没有的信息。

必须遵守：
1. 只翻译当前正文，不补写背景，不删去句子，不总结；正文开头不要重复日文标题、日期、署名或导语。
2. 严格保留原文的段落数量、空行、换行节奏和内容顺序。原文用 `<br>` 分开的短句，中文也必须用 `<br>` 保持分行；不得把多段文字挤成一段。
3. 正文中的 Markdown 链接、URL、HTML 标签，以及 `{{% legacy_image ... %}}`、`{{% spacer %}}` 等标记必须逐字原样保留，位置不能移动；不要翻译 URL、标记属性或图片 id。
4. 杉森建文章要保留“设计说明/画面注释/创作者随笔”的层次；Staff 文章要保留不同员工的自述、工作现场与技术细节，不要统一改成新闻稿。
5. 专有名词必须优先采用下方译名库中的目标译名，并在本篇保持一致。括号内的分类、来源或备注只用于理解，不要把括号说明写入正文；除非括号本身就是原文的一部分。
6. 日文拟声、结尾语和口头招呼按上下文译成自然中文；例如「チャオ」统一译为“下回再见”并可搭配自然的语气词（咯、啦、呀、喽等），不要一篇内忽译音译、忽译“再见”。
7. 不要在中文正文中附上整段日文；日文原文会由网页的“阅读语言”切换单独展示。
8. 另生成一个用于搜索结果和外部卡片的中文标题与摘要。标题应根据本篇真正主题自然拟写，参考风格：{blog['title_style']}；标题约 10—20 字，摘要约 30—60 字。标题和摘要不得含日文假名，不要只写“第{number}回”或复述占位说明。
9. 只输出严格 JSON：{{"translation_markdown":"翻译后的 Markdown 正文","translation_title":"可检索中文标题","translation_summary":"30—60字中文摘要"}}。不要输出 front matter、解释或代码围栏。
{staff_names}

文章元数据：
- 日期：{source_metadata.get('date') or ''}
- 原文标题：{source_metadata.get('title') or ''}
- 原文系列：{source_metadata.get('series', {}).get('name_ja') if isinstance(source_metadata.get('series'), dict) else ''}

本篇命中的译名库（原词 → 统一中文译名）：
{glossary}

日文原文：
{body}
""".strip()


def make_metadata(
    blog_name: str,
    number: int,
    source: dict[str, Any],
    model: str,
    warnings: list[str],
    glossary_path: Path,
    matches: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    title: str,
    summary: str,
    name_annotations: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    metadata = {
        "article_id": source.get("article_id") or f"{BLOGS[blog_name]['slug']}-{number}",
        "post_id": number,
        "lang": "zh-CN",
        "source_language": "ja",
        "translation_status": "openai-machine-translated",
        "translator": f"OpenAI {model}",
        "provider": "openai",
        "reviewer": None,
        "translated_at": utc_now(),
        "source_date": source.get("date"),
        "translation_warnings": warnings,
        "translation_title": title,
        "translation_summary": summary,
        "glossary_source": glossary_path.name,
        "glossary_match_count": len(matches),
        "glossary_missing_targets": [check["target"] for check in checks if check["status"] == "missing-target"],
        "glossary_checks": checks,
    }
    if name_annotations:
        metadata["staff_name_policy"] = "kana-first; first occurrence annotated"
        metadata["staff_name_annotations"] = name_annotations
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate Game Freak art/staff archives with OpenAI.")
    parser.add_argument("--blog", choices=["art", "staff", "both"], default="both")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=int, nargs="*")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--glossary", default=os.getenv("GAMEFREAK_GLOSSARY_PATH", ""))
    parser.add_argument("--staff-names", type=Path, default=DEFAULT_STAFF_NAMES)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        raise SystemExit("Missing OPENAI_API_KEY. Set it in PowerShell before running.")
    glossary_path = Path(args.glossary).expanduser() if args.glossary else next(
        (path for path in DEFAULT_GLOSSARY_CANDIDATES if path.exists()), None
    )
    if glossary_path is None or not glossary_path.exists():
        raise SystemExit("Glossary Master JSON was not found. Pass --glossary path/to/glossary-master.json.")
    glossary = load_glossary(glossary_path)
    staff_name_entries = load_staff_names(args.staff_names)
    print(f"Glossary: {glossary_path} ({len(glossary)} usable entries)")

    names = ["art", "staff"] if args.blog == "both" else [args.blog]
    for blog_name in names:
        selected = [
            item for item in source_articles(blog_name)
            if item[0] >= args.start and (not args.end or item[0] <= args.end)
            and (not args.only or item[0] in set(args.only))
        ]
        if args.limit > 0:
            selected = selected[: args.limit]
        output_dir = BLOGS[blog_name]["translation_dir"]
        print(f"{blog_name}: selected {len(selected)} article(s); output={output_dir}")
        for index, (number, _path, source_metadata, source_body) in enumerate(selected, start=1):
            output = output_dir / f"{number}.md"
            if args.reuse_existing and existing_translation(output):
                print(f"Reuse {blog_name} [{index}/{len(selected)}] {number}")
                continue
            matches = glossary_matches(source_body, glossary)
            if args.dry_run:
                print(f"Would translate {blog_name} [{index}/{len(selected)}] {number} (glossary matches: {len(matches)})")
                continue
            print(f"OpenAI {blog_name} [{index}/{len(selected)}] {number}")
            article_names = applicable_names(source_body, staff_name_entries, number) if blog_name == "staff" else []
            staff_name_prompt = ""
            if article_names:
                staff_name_prompt = "\n10. Staff 人物昵称必须遵守以下本篇人物表：\n" + name_context(article_names)
            result = call_openai(
                build_prompt(
                    blog_name,
                    number,
                    source_metadata,
                    source_body,
                    glossary_context(matches),
                    staff_name_prompt,
                ),
                args.api_key,
                args.base_url,
                args.model,
                args.temperature,
                args.retries,
            )
            translation = clean_translation(result["translation_markdown"])
            fallback_title = f"【{('设定资料' if blog_name == 'art' else '工作日志')}】{str(source_metadata.get('date', ''))[:4]}年第{number}篇"
            title = clean_card_text(result.get("translation_title"), 8, 30) or fallback_title
            summary = clean_card_text(result.get("translation_summary"), 30, 60)
            if not summary:
                summary = re.sub(r"[*_`#]", "", next((p.strip() for p in re.split(r"\n\s*\n", translation) if p.strip()), ""))
                summary = re.sub(r"\s+", " ", summary).strip()[:60]
            name_annotations: list[dict[str, str]] = []
            if blog_name == "staff":
                translation, name_annotations = normalize_staff_body(
                    source_body,
                    translation,
                    staff_name_entries,
                    number,
                )
                title = normalize_staff_card_text(title, article_names)
                summary = normalize_staff_card_text(summary, article_names)
            warnings = validate_translation(source_body, translation)
            checks = glossary_checks(matches, translation)
            missing = [check["target"] for check in checks if check["status"] == "missing-target"]
            if missing:
                warnings.append("missing_glossary_targets: " + ", ".join(missing[:12]))
            if warnings:
                print(f"  warning: {', '.join(warnings)}")
            write_markdown(
                output,
                make_metadata(
                    blog_name,
                    number,
                    source_metadata,
                    args.model,
                    warnings,
                    glossary_path,
                    matches,
                    checks,
                    title,
                    summary,
                    name_annotations,
                ),
                translation,
            )
            time.sleep(max(args.delay, 0))


if __name__ == "__main__":
    main()
