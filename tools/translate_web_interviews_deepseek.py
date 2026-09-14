"""Translate raw web interviews using DeepSeek API and generate parallel-translation posts with images.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "archive" / "web-interviews" / "raw"
OUTPUT_DIR = ROOT / "_posts"
ASSETS_IMG_DIR = ROOT / "assets" / "img" / "interviews"
GLOSSARY_PATH = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def load_glossary() -> list[dict]:
    if not GLOSSARY_PATH.exists():
        print(f"Warning: glossary not found at {GLOSSARY_PATH}")
        return []
    try:
        data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
        entries = []
        for item in data.get("entries", []):
            target = item.get("target")
            terms = item.get("terms") or []
            if target and terms:
                entries.append({"target": target, "terms": terms})
        return entries
    except Exception as e:
        print(f"Error loading glossary: {e}")
        return []


def find_glossary_matches(text: str, glossary: list[dict]) -> list[tuple[str, str]]:
    matches = []
    text_lower = text.lower()
    for entry in glossary:
        target = entry["target"]
        for term in entry["terms"]:
            term_clean = term.strip()
            if len(term_clean) < 2:
                continue
            if re.match(r"^[A-Za-z0-9\s\.\-]+$", term_clean):
                if len(term_clean) <= 2:
                    continue
                pattern = r"\b" + re.escape(term_clean.lower()) + r"\b"
                if re.search(pattern, text_lower):
                    matches.append((term_clean, target))
                    break
            else:
                if term_clean.lower() in text_lower:
                    matches.append((term_clean, target))
                    break
    seen = set()
    unique = []
    for term, target in sorted(matches, key=lambda x: -len(x[0])):
        if term not in seen:
            seen.add(term)
            unique.append((term, target))
    return unique[:80]


def call_deepseek(messages: list[dict], max_tokens: int = 4096, temperature: float = 0.3) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"DeepSeek call attempt {attempt+1} failed: {exc}", file=sys.stderr)
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("Unreachable")


def download_image(img_url: str, dest_dir: Path, fallback_name: str) -> str | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(img_url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if not ext or ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        ext = ".jpg"
    
    filename = f"{fallback_name}{ext}"
    dest_path = dest_dir / filename
    
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return f"/assets/img/interviews/{dest_dir.name}/{filename}"
        
    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 200: # skip empty 1x1 tracking gifs
                dest_path.write_bytes(data)
                print(f"      [Image Saved] {dest_path.name} ({len(data)} bytes)")
                return f"/assets/img/interviews/{dest_dir.name}/{filename}"
    except Exception as e:
        print(f"      [Image Download Failed] {img_url}: {e}", file=sys.stderr)
    return None


def clean_source_paragraphs(paragraphs: list[str], interview_id: str) -> list[str]:
    cleaned = []
    
    end_markers_exact = {
        "記事をシェアする", "関連記事", "コメント", "コメント ※", "メールアドレスが公開されることはありません",
        "スポンサーリンク", "Twitter Facebook はてブ LINE", "Comments", "Leave a Reply",
        "Your email address will not be published", "Next Story", "Recommended Posts",
        "Most Popular »", "IGN Logo Recommends", "More from Game Informer", "Legacy Comments",
        "Related Content", "Popular Discussions", "Site Map", "About Us"
    }

    skip_exact = {
        "Home", "TIME Magazine", "Photos", "Videos", "Specials", "Topics", "Subscribe",
        "Mobile Apps", "Newsletters", "RSS", "@TIME", "NewsFeed", "U.S.", "Politics",
        "World", "Business", "Money", "Tech", "Health", "Science", "Entertainment",
        "Opinion", "SEARCH TIME.COM", "Full Archive", "Covers", "Current Issue",
        "Archive", "Print", "Email", "Reprints", "share", "LinkedIn", "StumbleUpon",
        "Reddit", "Digg", "Del.i.cious", "Tweet", "Back Button", "COUNTER",
        "Next", "Previous", "Top", "Menu", "success", "fail", "DS", "ホーム",
        "Focus Reset", "0 comments", "SUBSCRIBE", "Search:", "Type: - Any - Product Preview Review",
        "Items per page: 10 20 50 100", "Sort by: Most Relevant Oldest first Newest first",
        "Follow Us", "Twitter", "Facebook", "Instagram", "Twitch", "YouTube", "Tiktok",
        "Share", "Close", "Post Tweet Email", "Copy Link", "Feature", "Facebook Post",
        "Twitter Tweet", "Email Email", "Comment Comment", "Latest activity", "Register",
        "Install the app", "Install", "How to install the app on iOS", "Games",
        "You are using an out of date browser. It  may not display this or other websites correctly.",
        "You should upgrade or use an alternative browser ."
    }

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean or len(p_clean) < 2:
            continue
            
        # Check end marker
        if p_clean in end_markers_exact or any(p_clean.startswith(marker) for marker in ["© 20", "© 19", "Legacy Comments"]):
            break
            
        if p_clean in skip_exact:
            continue
        if p_clean.startswith("Follow along with the video") or p_clean.startswith("Note: This feature may not be"):
            continue
        if p_clean.startswith("Home ›") or p_clean.startswith("Updated :") or p_clean.startswith("https://gameinformer.com"):
            continue
        if "Skip to main content" in p_clean:
            continue
        if any(s in p_clean for s in ["captures", "Wayback Machine", "COLLECTED BY", "Alexa Crawl", "Internet Archive", "Crawl FS", "Focused crawls are"]):
            continue
        if p_clean.startswith("var ") or p_clean.startswith("function("):
            continue
            
        cleaned.append(p_clean)
        
    return cleaned


def translate_interview_chunk(
    chunk: list[str],
    interview_meta: dict,
    glossary_matches: list[tuple[str, str]]
) -> list[dict]:
    glossary_str = "\n".join(f"- {src} -> {tgt}" for src, tgt in glossary_matches) or "无特定匹配词条"
    
    prompt = f"""你是精通宝可梦历史考据、游戏史料与专业翻译的专家。
正在整理宝可梦官方与媒体开发者访谈的日中/英中对照档案。

请把以下访谈内容翻译为流畅、准确、忠实原文的简体中文。
如果是对话/采访形式（如“问：... 答：...”或“TIME: ... Tajiri: ...”），请识别出说话人(speaker)。
如果段落中有特定的背景设定、行业术语、人名梗或值得注释的地方，请填写在 note 字段中。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}

【输出格式要求】：
请输出严格的 JSON 对象，格式为：
{{
  "segments": [
    {{
      "speaker": "说话人名字或职务（如'TIME'、'田尻智'、'增田顺一'、'问'、'答'等，若非对话段落则留空字符串''）",
      "original": "该段对应的原文",
      "translation": "流畅自然的简体中文译文",
      "note": "对原文背景、专有名词或特定事件的译注（若无则留空字符串''）"
    }}
  ]
}}

待翻译原文段落列表：
{json.dumps(chunk, ensure_ascii=False, indent=2)}
"""

    messages = [
        {"role": "system", "content": "你是一位专业的宝可梦游戏历史考据与开发者访谈双语翻译专家。请只输出合法的 JSON 对象。"},
        {"role": "user", "content": prompt}
    ]

    raw_json = call_deepseek(messages)
    try:
        parsed = json.loads(raw_json)
        return parsed.get("segments", [])
    except Exception as e:
        print(f"Error parsing DeepSeek JSON: {e}\nRaw was: {raw_json[:300]}...", file=sys.stderr)
        return [{"speaker": "", "original": p, "translation": p, "note": ""} for p in chunk]


def build_bilingual_post(interview: dict, segments: list[dict], extra_images: list[dict] = None) -> str:
    front_matter = {
        "layout": "parallel-translation",
        "title": f"[访谈翻译] {interview['title']}",
        "date": interview["date"],
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", interview.get("lang", "ja").upper()] + interview.get("interviewees", []),
        "archive_type": "interview_translation",
        "source": {
            "title": interview.get("title_original") or interview["title"],
            "url": interview["url"],
            "language": interview.get("lang", "ja"),
            "source_type": "web_interview"
        },
        "workflow": {
            "scan": "not_applicable",
            "preprocess": "done",
            "ocr": "not_applicable",
            "translation": "done",
            "proofreading": "pending",
            "published": "done"
        },
        "entities": {
            "people": interview.get("interviewees", []),
            "works": ["宝可梦"],
            "organizations": ["Game Freak", "Nintendo"]
        },
        "parallel_items": []
    }

    # Insert header image if available
    if extra_images:
        for img in extra_images:
            if img.get("position") == "top":
                front_matter["parallel_items"].append({
                    "type": "image",
                    "image": img["path"],
                    "caption": img.get("caption", "访谈配图")
                })

    for seg in segments:
        orig = seg.get("original", "").strip()
        trans = seg.get("translation", "").strip()
        if not orig and not trans:
            continue
        
        item = {
            "type": "paragraph",
            "original": orig,
            "translation": trans
        }
        if seg.get("speaker"):
            item["speaker"] = seg["speaker"]
        if seg.get("note"):
            item["note"] = seg["note"]
        front_matter["parallel_items"].append(item)

    # Insert trailing image if available
    if extra_images:
        for img in extra_images:
            if img.get("position") == "bottom":
                front_matter["parallel_items"].append({
                    "type": "image",
                    "image": img["path"],
                    "caption": img.get("caption", "相关图解")
                })

    yaml_str = yaml.dump(front_matter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{yaml_str}---\n"


# Specific known article images
INTERVIEW_IMAGES = {
    "2011-02-21-pokemon-memo-bw-bridge-interview": [
        {
            "url": "https://pokemon-memo.com/image/news/2011/02/21/black-white-bridge.gif",
            "filename": "black-white-bridge",
            "caption": "《宝可梦 黑·白》合众地方五座桥梁与地理示意图",
            "position": "bottom"
        }
    ],
    "1997-10-16-gamefreak-classic-interview": [
        {
            "url": "https://web.archive.org/web/19971016220436im_/http://www.gamefreak.co.jp/POKEMON/INTER/PI_TA01.JPG",
            "filename": "satoshi-tajiri-1997",
            "caption": "Game Freak 早期官网采访中的社长田尻智肖像",
            "position": "top"
        }
    ]
}


def process_interview(raw_file: Path, glossary: list[dict]) -> Path | None:
    data = json.loads(raw_file.read_text(encoding="utf-8"))
    print(f"\n========================================================")
    print(f"Processing: {data['title']} ({data['date']})")
    print(f"Source URL: {data['url']}")
    
    raw_paragraphs = []
    if "sections" in data and isinstance(data["sections"], list):
        for sec in data["sections"]:
            raw_paragraphs.append(f"### {sec['title']}")
            raw_paragraphs.extend(sec.get("paragraphs", []))
    else:
        raw_paragraphs = data.get("paragraphs", [])

    cleaned_paragraphs = clean_source_paragraphs(raw_paragraphs, data["id"])
    print(f"Cleaned paragraphs: {len(cleaned_paragraphs)}")
    if not cleaned_paragraphs:
        print("Warning: no paragraphs left after cleaning!")
        return None

    # Handle images
    images_to_insert = []
    if data["id"] in INTERVIEW_IMAGES:
        dest_dir = ASSETS_IMG_DIR / data["id"]
        for img_info in INTERVIEW_IMAGES[data["id"]]:
            saved_rel_path = download_image(img_info["url"], dest_dir, img_info["filename"])
            if saved_rel_path:
                images_to_insert.append({
                    "path": saved_rel_path,
                    "caption": img_info.get("caption", ""),
                    "position": img_info.get("position", "top")
                })

    full_text = "\n".join(cleaned_paragraphs)
    glossary_matches = find_glossary_matches(full_text, glossary)
    print(f"Matched {len(glossary_matches)} glossary terms.")

    chunk_size = 15
    chunks = [cleaned_paragraphs[i:i + chunk_size] for i in range(0, len(cleaned_paragraphs), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    all_segments = []
    for idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {idx}/{len(chunks)} ({len(chunk)} paragraphs)...", end="", flush=True)
        t0 = time.time()
        segs = translate_interview_chunk(chunk, data, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, got {len(segs)} segments.")
        all_segments.extend(segs)
        time.sleep(1)

    post_content = build_bilingual_post(data, all_segments, images_to_insert)
    
    slug = data["id"].replace("-interview", "").replace("-classic", "")
    post_filename = f"{data['date']}-interview-{slug}.md"
    post_path = OUTPUT_DIR / post_filename
    post_path.write_text(post_content, encoding="utf-8")
    print(f"-> Successfully written post to: {post_path.relative_to(ROOT)}")
    return post_path


def main():
    parser = argparse.ArgumentParser(description="Translate web interviews using DeepSeek")
    parser.add_argument("--id", help="Specific interview id to translate")
    parser.add_argument("--limit", type=int, default=10, help="Maximum interviews to translate")
    args = parser.parse_args()

    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    raw_files = sorted(RAW_DIR.glob("*.json"))
    if args.id:
        raw_files = [f for f in raw_files if args.id in f.stem]

    target_files = raw_files[:args.limit]
    print(f"Selected {len(target_files)} raw interview file(s) to process.")

    results = []
    for f in target_files:
        try:
            res = process_interview(f, glossary)
            if res:
                results.append(res)
        except Exception as exc:
            print(f"Failed to process {f.name}: {exc}", file=sys.stderr)

    print(f"\nAll done! Successfully generated {len(results)} bilingual interview posts.")


if __name__ == "__main__":
    main()
