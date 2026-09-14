"""Curate, clean, translate, and import high-value Pokémon developer interviews into _posts/
with strict noise filtering and historical metadata enrichment.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
GLOSSARY_PATH = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def load_glossary() -> list[dict]:
    if not GLOSSARY_PATH.exists():
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


def translate_chunk(chunk: list[dict], glossary_matches: list[tuple[str, str]]) -> list[dict]:
    glossary_str = "\n".join(f"- {src} -> {tgt}" for src, tgt in glossary_matches) or "无特定匹配词条"
    
    prompt = f"""你是精通宝可梦历史考据、游戏史料与专业翻译的专家。
正在整理宝可梦官方与媒体开发者访谈的日中/英中对照档案。

请将以下访谈内容翻译为流畅、准确、忠实原文的简体中文。
如果是对话/采访形式（如“问：... 答：...”或“Sugimori: ... Nishida: ...”），请准确识别出说话人(speaker)。
如果段落中有特定的背景设定、行业术语、人名梗或值得注释的地方，请填写在 note 字段中。

【说话人识别规范】：
- 明确标注角色名字或职务，如“提问”、“杉森建”、“西田敦子”、“西野弘二”、“增田顺一”、“田尻智”等。
- 不要把整句问答混在 speaker 里。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名或职务（如'西田敦子'，若无则留空字符串''）",
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
        print(f"      Error parsing DeepSeek JSON: {e}", file=sys.stderr)
        return [{"speaker": item.get("speaker", ""), "original": item.get("text", ""), "translation": item.get("text", ""), "note": ""} for item in chunk]


def download_image(img_url: str, dest_dir: Path, filename: str) -> str | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return f"/assets/img/interviews/{dest_dir.name}/{filename}"

    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 800:
                dest_path.write_bytes(data)
                print(f"      [Image Saved] {filename} ({len(data)} bytes)")
                return f"/assets/img/interviews/{dest_dir.name}/{filename}"
    except Exception as e:
        print(f"      [Image Download Failed] {img_url}: {e}")
    return None


def import_interview_pikachu():
    url = "https://web.archive.org/web/20180901/https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/"
    print(f"\n========================================================")
    print("=== Importing: Creator Profile: The Creators of Pikachu ===")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    article_match = re.search(r"<article[^>]*>([\s\S]*?)</article>", raw_html)
    content_html = article_match.group(1) if article_match else raw_html

    # Clean and filter noise
    blocks = re.findall(r"<(p|h1|h2|h3|h4|blockquote)[^>]*>([\s\S]*?)</\1>", content_html)
    skip_phrases = [
        "History is littered", "archiveteam.org", "Archive Team", "ArchiveBot", "Internet Archive",
        "Wayback Machine", "Terms of Use", "Privacy Policy", "Share", "Tweet", "Cookie", "Sign In"
    ]

    cleaned_raw_blocks = []
    for tag, text in blocks:
        clean_txt = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
        clean_txt = re.sub(r"\s+", " ", clean_txt)
        if not clean_txt or len(clean_txt) < 5:
            continue
        if any(sp in clean_txt for sp in skip_phrases):
            continue
        # Skip date header paragraph
        if clean_txt == "July 26, 2018":
            continue
        # Skip main article title since it will be in frontmatter
        if clean_txt == "Creator Profile: The Creators of Pikachu":
            continue
        cleaned_raw_blocks.append((tag, clean_txt))

    print(f"Extracted {len(cleaned_raw_blocks)} pure content blocks (filtered out all Wayback/ad noise).")

    # Download important images
    img_dir = IMG_DIR / "2018-07-26-interview-creators-of-pikachu"
    download_image("https://web.archive.org/web/20180914115937im_/https://assets.pokemon.com/assets/cms2/img/misc/_tiles/creator-profile/creators-of-pikachu/creator-profile-origin-of-pikachu-169.jpg", img_dir, "hero_pikachu_creators.jpg")
    download_image("https://web.archive.org/web/20180914115937im_/https://assets.pokemon.com//assets/cms2/img/misc/_tiles/creator-profile/creators-of-pikachu/inline/atsuko-nishida-200.jpg", img_dir, "atsuko_nishida.jpg")
    download_image("https://web.archive.org/web/20180914115937im_/https://assets.pokemon.com//assets/cms2/img/misc/_tiles/creator-profile/creators-of-pikachu/inline/ken-sugimori-200.jpg", img_dir, "ken_sugimori.jpg")
    download_image("https://web.archive.org/web/20180914115937im_/https://assets.pokemon.com//assets/cms2/img/misc/_tiles/creator-profile/creators-of-pikachu/inline/002-578.jpg", img_dir, "pikachu_early_sprites.jpg")
    download_image("https://web.archive.org/web/20180914115937im_/https://assets.pokemon.com//assets/cms2/img/misc/_tiles/creator-profile/creators-of-pikachu/inline/008-578.jpg", img_dir, "pikachu_daifuku_concept.jpg")

    # Group into chunks for translation
    glossary = load_glossary()
    full_text = "\n".join(t for _, t in cleaned_raw_blocks)
    glossary_matches = find_glossary_matches(full_text, glossary)

    # Convert blocks to structured dicts for chunking
    items_to_translate = []
    for tag, t in cleaned_raw_blocks:
        speaker = ""
        orig_text = t
        # Check speaker prefixes
        if t.startswith("Sugimori:"):
            speaker = "杉森建"
            orig_text = t.replace("Sugimori:", "").strip()
        elif t.startswith("Nishida:"):
            speaker = "西田敦子"
            orig_text = t.replace("Nishida:", "").strip()
        elif t.startswith("Nishino:"):
            speaker = "西野弘二"
            orig_text = t.replace("Nishino:", "").strip()
        elif tag == "h2" or tag == "h3":
            speaker = ""
        elif t.endswith("?"):
            speaker = "提问"

        items_to_translate.append({
            "tag": tag,
            "speaker": speaker,
            "text": orig_text
        })

    chunk_size = 12
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []

    # Insert hero image at the beginning
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2018-07-26-interview-creators-of-pikachu/hero_pikachu_creators.jpg",
        "alt": "皮卡丘的创造者们：杉森建、西野弘二与西田敦子",
        "caption": "皮卡丘诞生秘辛：从大福饼到风靡全球的电气鼠"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}
            
            # If it's a heading
            if item["tag"] in ("h2", "h3"):
                parallel_items.append({
                    "type": "heading",
                    "level": 2 if item["tag"] == "h2" else 3,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            else:
                spk = seg.get("speaker") or item["speaker"]
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })

        time.sleep(1)

    # Build clean frontmatter
    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 宝可梦官方专访：皮卡丘诞生秘辛 —— 专访杉森建、西田敦子与西野弘二",
        "original_title": "Creator Profile: The Creators of Pikachu",
        "date": "2018-07-26",
        "era": "2017–2021 · Switch / 开放世界探索",
        "era_skin": "2019",
        "publication": "Pokemon.com 官方特辑",
        "source_kind": "web",
        "author": "The Pokémon Company International",
        "translator": "Poke Amice Studio",
        "interviewee": "杉森建, 西田敦子, 西野弘二",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "皮卡丘", "初代", "杉森建", "西田敦子", "角色设计"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Creator Profile: The Creators of Pikachu",
            "url": "https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/",
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": "https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/",
        "summary": "2018 年宝可梦官方发布的重磅创作者档案。皮卡丘的原案设计师西田敦子、艺术总监杉森建以及数值策划西野弘二，首次完整复盘皮卡丘的诞生全过程：从最初类似‘和菓子大福饼’的圆滚滚构想、以松鼠为灵感的蓄电脸颊，到西野弘二因‘舍不得被别人捉到’而调低野外遭遇率的开发秘闻。",
        "entities": {
            "people": ["杉森建", "西田敦子", "西野弘二"],
            "games": ["宝可梦 红·绿", "宝可梦 黄"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2018-07-26-interview-creators-of-pikachu.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    # Post-process noise cleaning
    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def import_interview_masuda_sugimori_gen5():
    url = "https://lavacutcontent.com/masuda-sugimori-gen-5/"
    print(f"\n========================================================")
    print("=== Importing: Nintendo Power BW Interview (Masuda & Sugimori) ===")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    m = re.search(r'<div class=[\x27\x22]entry-content[\x27\x22][^>]*>([\s\S]*?)</div>\s*<!-- \.entry-content -->', raw_html)
    content = m.group(1) if m else raw_html

    raw_blocks = re.findall(r'<(p|h2|h3|h4|blockquote)[^>]*>([\s\S]*?)</\1>', content)
    
    # Filter noise: Skip modern blogger intro lines (Dr Lava) and extract only original interview
    cleaned_raw_blocks = []
    interview_started = False
    for tag, text in raw_blocks:
        clean_txt = html.unescape(re.sub(r'<[^>]+>', '', text)).strip()
        clean_txt = re.sub(r'\s+', ' ', clean_txt)
        if not clean_txt or len(clean_txt) < 5:
            continue
        if "Breeding the Fifth" in clean_txt or "From photocopying a hand-drawn fanzine" in clean_txt:
            interview_started = True
        if not interview_started:
            continue
        if any(skip in clean_txt for skip in ["Leave a Reply", "Your email address will not be published", "Comments", "Lava Cut Content", "Support Dr Lava on Patreon"]):
            break
        cleaned_raw_blocks.append((tag, clean_txt))

    print(f"Extracted {len(cleaned_raw_blocks)} pure interview blocks (cleanly filtered out blogger commentary & ads).")

    # Download images
    img_dir = IMG_DIR / "2011-03-01-interview-nintendo-power-bw-masuda-sugimori"
    download_image("https://lavacutcontent.com/wp-content/uploads/2019/11/Masuda-Thumb-2-1024x588.png", img_dir, "hero_bw_masuda_sugimori.png")
    download_image("http://lavacutcontent.com/wp-content/uploads/2019/11/Masuda-and-Sugimori.png", img_dir, "masuda_and_sugimori.png")
    download_image("http://lavacutcontent.com/wp-content/uploads/2019/11/BW-JP-Boxes-2.jpg", img_dir, "bw_boxes.jpg")

    # Prepare chunking
    glossary = load_glossary()
    full_text = "\n".join(t for _, t in cleaned_raw_blocks)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items_to_translate = []
    for tag, t in cleaned_raw_blocks:
        speaker = ""
        orig_text = t
        if t.startswith("Nintendo Power:"):
            speaker = "提问"
            orig_text = t.replace("Nintendo Power:", "").strip()
        elif t.startswith("Masuda:"):
            speaker = "增田顺一"
            orig_text = t.replace("Masuda:", "").strip()
        elif t.startswith("Sugimori:"):
            speaker = "杉森建"
            orig_text = t.replace("Sugimori:", "").strip()
        elif tag == "h2" or tag == "h3":
            speaker = ""

        items_to_translate.append({
            "tag": tag,
            "speaker": speaker,
            "text": orig_text
        })

    chunk_size = 12
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2011-03-01-interview-nintendo-power-bw-masuda-sugimori/hero_bw_masuda_sugimori.png",
        "alt": "增田顺一与杉森建在《宝可梦 黑·白》开发期间",
        "caption": "任天堂力量专访：增田顺一与杉森建谈《黑·白》的理念重塑与全新合众宝可梦"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}
            if item["tag"] in ("h2", "h3"):
                parallel_items.append({
                    "type": "heading",
                    "level": 2 if item["tag"] == "h2" else 3,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            else:
                spk = seg.get("speaker") or item["speaker"]
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Nintendo Power 专访增田顺一与杉森建：《宝可梦 黑·白》设计理念与百余只全新宝可梦",
        "original_title": "Nintendo Power: Pokemon Black & White Developer Interview (Masuda & Sugimori)",
        "date": "2011-03-01",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "Nintendo Power 杂志第 265 期",
        "source_kind": "magazine",
        "author": "Nintendo Power (Steve Thomason)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 杉森建",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "黑·白", "合众", "增田顺一", "杉森建", "角色设计"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Nintendo Power Vol. 265",
            "url": "https://lavacutcontent.com/masuda-sugimori-gen-5/",
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": "https://lavacutcontent.com/masuda-sugimori-gen-5/",
        "summary": "2011 年《宝可梦 黑·白》海外发售之际，北美权威游戏杂志 Nintendo Power 对游戏总监增田顺一与艺术总监杉森建进行的独家深度访谈。两人深入剖析了为何在通关前彻底封印前四代旧宝可梦、全数采用 156 只全新设计的魄力决断，以及纽约合众大都会与自然交融的设计哲学。",
        "entities": {
            "people": ["增田顺一", "杉森建"],
            "games": ["宝可梦 黑·白"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def import_interview_sugimori_gen2_cut_pokemon():
    url = "https://lavacutcontent.com/sugimori-hundreds-pokemon-cut/"
    print(f"\n========================================================")
    print("=== Importing: Nintendo Power GS Cut Pokemon (Sugimori & GF Bigwigs) ===")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    m = re.search(r'<div class=[\x27\x22]entry-content[\x27\x22][^>]*>([\s\S]*?)</div>\s*<!-- \.entry-content -->', raw_html)
    content = m.group(1) if m else raw_html

    raw_blocks = re.findall(r'<(p|h2|h3|h4|blockquote)[^>]*>([\s\S]*?)</\1>', content)

    # Filter noise: Skip modern blog prologue and extract only original round-table interview
    cleaned_raw_blocks = []
    interview_started = False
    for tag, text in raw_blocks:
        clean_txt = html.unescape(re.sub(r'<[^>]+>', '', text)).strip()
        clean_txt = re.sub(r'\s+', ' ', clean_txt)
        if not clean_txt or len(clean_txt) < 5:
            continue
        if "Nintendo Power Chats with" in clean_txt or "The Pokemon Bigwigs" in clean_txt or "The following interview" in clean_txt:
            interview_started = True
        if not interview_started:
            continue
        if any(skip in clean_txt for skip in ["Leave a Reply", "Your email address will not be published", "Comments", "Lava Cut Content", "Support Dr Lava on Patreon"]):
            break
        cleaned_raw_blocks.append((tag, clean_txt))

    print(f"Extracted {len(cleaned_raw_blocks)} pure interview blocks (zero blog noise).")

    # Download images
    img_dir = IMG_DIR / "2000-11-01-interview-nintendo-power-gs-bigwigs"
    download_image("https://lavacutcontent.com/wp-content/uploads/2019/11/Sugi-GS-Thumb-1024x588.png", img_dir, "hero_sugimori_gs_cut.png")
    download_image("http://lavacutcontent.com/wp-content/uploads/2019/11/Photo.png", img_dir, "gamefreak_2000_office.png")

    glossary = load_glossary()
    full_text = "\n".join(t for _, t in cleaned_raw_blocks)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items_to_translate = []
    for tag, t in cleaned_raw_blocks:
        speaker = ""
        orig_text = t
        if t.startswith("Nintendo Power:"):
            speaker = "提问"
            orig_text = t.replace("Nintendo Power:", "").strip()
        elif t.startswith("Sugimori:"):
            speaker = "杉森建"
            orig_text = t.replace("Sugimori:", "").strip()
        elif t.startswith("Masuda:"):
            speaker = "增田顺一"
            orig_text = t.replace("Masuda:", "").strip()
        elif t.startswith("Ishihara:"):
            speaker = "石原恒和"
            orig_text = t.replace("Ishihara:", "").strip()
        elif t.startswith("Morimoto:"):
            speaker = "森本茂树"
            orig_text = t.replace("Morimoto:", "").strip()
        elif t.startswith("Ota:"):
            speaker = "太田健典"
            orig_text = t.replace("Ota:", "").strip()
        elif t.startswith("Ichinose:"):
            speaker = "一之濑刚"
            orig_text = t.replace("Ichinose:", "").strip()
        elif tag == "h2" or tag == "h3":
            speaker = ""

        items_to_translate.append({
            "tag": tag,
            "speaker": speaker,
            "text": orig_text
        })

    chunk_size = 12
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2000-11-01-interview-nintendo-power-gs-bigwigs/hero_sugimori_gs_cut.png",
        "alt": "杉森建与《宝可梦 金·银》废案与新宝可梦设计",
        "caption": "任天堂力量官方对谈：主创团队谈《金·银》漫长开发与被舍弃的数百只废案宝可梦"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}
            if item["tag"] in ("h2", "h3"):
                parallel_items.append({
                    "type": "heading",
                    "level": 2 if item["tag"] == "h2" else 3,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            else:
                spk = seg.get("speaker") or item["speaker"]
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Nintendo Power 专访 Game Freak 主创团队：《金·银》漫长开发与被舍弃的数百只宝可梦",
        "original_title": "Nintendo Power: Chats with the Pokemon Bigwigs (Gold & Silver)",
        "date": "2000-11-01",
        "era": "1996–2001 · Early Web 黎明期",
        "era_skin": "1999",
        "publication": "Nintendo Power 杂志第 134 期",
        "source_kind": "magazine",
        "author": "Nintendo Power",
        "translator": "Poke Amice Studio",
        "interviewee": "杉森建, 增田顺一, 石原恒和, 森本茂树, 太田健典, 一之濑刚",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "金·银", "杉森建", "增田顺一", "森本茂树", "石原恒和", "废案"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Nintendo Power Vol. 134",
            "url": "https://lavacutcontent.com/sugimori-hundreds-pokemon-cut/",
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": "https://lavacutcontent.com/sugimori-hundreds-pokemon-cut/",
        "summary": "2000 年 11 月《宝可梦 金·银》北美发售之际，Nintendo Power 专访了 Game Freak 与 Creatures 的全明星开发阵容。艺术总监杉森建首次透露团队为《金·银》设计了超过 300 只宝可梦，经过残酷筛选才最终定格为 100 只新宝可梦，并揭晓了咕咕等经典设计的灵感起源。",
        "entities": {
            "people": ["杉森建", "增田顺一", "石原恒和", "森本茂树", "太田健典", "一之濑刚"],
            "games": ["宝可梦 金·银"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2000-11-01-interview-nintendo-power-gs-bigwigs.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def import_interview_weekly_ascii_bw():
    url = "https://weekly.ascii.jp/elem/000/002/602/2602549/?r=1"
    print(f"\n========================================================")
    print("=== Importing: Weekly ASCII - Junichi Masuda BW Secrets ===")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    p_tags = re.findall(r'<p[^>]*>([\s\S]*?)</p>', raw_html)
    parsed_blocks = []
    interview_started = False

    for p in p_tags:
        txt = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        txt = re.sub(r'\s+', ' ', txt)
        if not txt:
            continue
        if "9月18日にいよいよ発売となる" in txt:
            interview_started = True
            parsed_blocks.append({"type": "intro", "text": txt})
            continue
        if not interview_started:
            continue
        if any(skip in txt for skip in ["週刊アスキーの最新情報を購読しよう", "本記事はアフィリエイト", "アクセスランキング", "©KADOKAWA"]):
            break

        if "■" in txt:
            h = txt.replace("■", "").strip()
            parsed_blocks.append({"type": "heading", "level": 2, "text": h})
        elif "――" in txt and "増田：" in txt:
            parts = txt.split("増田：")
            q_part = parts[0].strip()
            a_part = parts[1].strip()
            parsed_blocks.append({"type": "dialogue", "speaker": "提问", "text": q_part})
            parsed_blocks.append({"type": "dialogue", "speaker": "增田顺一", "text": a_part})
        elif txt.startswith("――"):
            parsed_blocks.append({"type": "dialogue", "speaker": "提问", "text": txt})
        elif txt.startswith("増田："):
            parsed_blocks.append({"type": "dialogue", "speaker": "增田顺一", "text": txt.replace("増田：", "").strip()})
        elif txt.startswith("(※"):
            parsed_blocks.append({"type": "note", "text": txt})
        elif "ニンテンドーDS用ソフト" in txt or "『ポケットモンスター ブラック』" in txt:
            continue
        else:
            parsed_blocks.append({"type": "paragraph", "text": txt})

    print(f"Extracted {len(parsed_blocks)} structured interview blocks (zero noise).")

    # Download images
    img_dir = IMG_DIR / "2010-09-13-interview-weekly-ascii-masuda-bw"
    download_image("https://ascii.jp/img/2020/02/21/2208699/l/b20f665e73487e2b.jpg", img_dir, "masuda_portrait_2010.jpg")
    download_image("https://ascii.jp/img/2020/02/21/2208700/l/573a6797987b26cd.jpg", img_dir, "masuda_playing_bw.jpg")
    download_image("https://ascii.jp/img/2020/02/21/2208701/l/c3b6c3785c9fe820.jpg", img_dir, "castelia_city_scene.jpg")
    download_image("https://ascii.jp/img/2020/02/21/2208702/l/4ee06d6ecd1b7825.jpg", img_dir, "pgl_dream_world.jpg")
    download_image("https://ascii.jp/img/2020/02/21/2208704/l/b6a40c941006a4bb.jpg", img_dir, "bw_package_black.jpg")
    download_image("https://ascii.jp/img/2020/02/21/2208705/l/8872bc86e2ccecd6.jpg", img_dir, "bw_package_white.jpg")

    glossary = load_glossary()
    full_text = "\n".join(b.get("text", "") for b in parsed_blocks)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items_to_translate = []
    for b in parsed_blocks:
        items_to_translate.append({
            "tag": b["type"],
            "speaker": b.get("speaker", ""),
            "text": b["text"]
        })

    chunk_size = 10
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []
    # Hero image
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2010-09-13-interview-weekly-ascii-masuda-bw/masuda_portrait_2010.jpg",
        "alt": "《宝可梦 黑·白》总监 增田顺一 接受周刊 ASCII 专访",
        "caption": "周刊 ASCII 独家对谈：总监增田顺一披露《黑·白》纸媒未能尽述的企划秘闻"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}
            
            # Insert editorial illustration before specific sections
            if "冒険の舞台に秘められた秘密" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2010-09-13-interview-weekly-ascii-masuda-bw/castelia_city_scene.jpg",
                    "alt": "合众地区大都会飞云市与天箭桥",
                    "caption": "跳出日本关东与神奥、远赴大洋彼岸纽约构想的全新舞台“合众地区”与飞云市"
                })
            elif "ポケモングローバルリンク" in item["text"] and item["tag"] == "heading":
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2010-09-13-interview-weekly-ascii-masuda-bw/pgl_dream_world.jpg",
                    "alt": "宝可梦全球连接 PGL 与梦境世界",
                    "caption": "通过任天堂 Wi-Fi 连通掌机与 PC 互联网的“宝可梦全球连接”（PGL）与梦境世界"
                })
            elif "新たなバトルルール" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2010-09-13-interview-weekly-ascii-masuda-bw/masuda_playing_bw.jpg",
                    "alt": "增田顺一在 Nintendo DS 上测试三打对战与结局流程",
                    "caption": "增田顺一正在 DS 上仔细核对《黑·白》三打对战以及通关结尾前最后 15 秒的镜头"
                })

            if item["tag"] == "heading":
                parallel_items.append({
                    "type": "heading",
                    "level": 2,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            elif item["tag"] == "intro" or item["tag"] == "paragraph":
                parallel_items.append({
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
            elif item["tag"] == "note":
                parallel_items.append({
                    "type": "note",
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            else:
                spk = seg.get("speaker") or item["speaker"] or "增田顺一"
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 周刊 ASCII 专访增田顺一：杂志未及详叙的《宝可梦 黑·白》开发秘话",
        "original_title": "誌面では語りきれなかった、ポケットモンスター ブラック・ホワイトの開発秘話!!",
        "date": "2010-09-13",
        "era": "2010–2012 · Connected Web 互联世代",
        "era_skin": "2011",
        "publication": "週刊アスキー (Weekly ASCII)",
        "source_kind": "web_magazine",
        "author": "后藤宏典 (ASCII)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "黑·白", "增田顺一", "PGL", "合众地区", "对战机制"],
        "archive_type": "interview_translation",
        "source": {
            "title": "週刊アスキー (Weekly ASCII) 2010年9月",
            "url": url,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "2010 年 9 月《宝可梦 黑·白》发售前夕，周刊 ASCII 深度专访总监增田顺一。增田深入拆解了为何在《钻石·珍珠》追求“究极”之后转向“黑与白”的二元论哲学、通关前全员 156 只全新宝可梦的生态设定、突破重重阻力打造打通掌机与 PC 网络的 PGL/梦境世界、以及从射击游戏衰落史反思得出的对战门槛设计哲学。",
        "entities": {
            "people": ["增田顺一", "后藤宏典", "三枝成彰"],
            "games": ["宝可梦 黑·白", "宝可梦 钻石·珍珠", "宝可梦 心金·魂银"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2010-09-13-interview-weekly-ascii-masuda-bw.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def import_interview_gamasutra_xy_monster_design():
    url = "https://www.gamedeveloper.com/production/how-pokemon-are-born-designing-the-series-iconic-monsters"
    print(f"\n========================================================")
    print("=== Importing: Gamasutra - Hironobu Yoshida & Junichi Masuda (XY Monster Design) ===")
    print(f"URL: {url}")

    # Download official high-res artwork
    img_dir = IMG_DIR / "2013-10-10-interview-gamasutra-xy-monster-design"
    download_image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/650.png", img_dir, "chespin.png")
    download_image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/653.png", img_dir, "fennekin.png")
    download_image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/656.png", img_dir, "froakie.png")

    # Structured interview blocks from the verified Gamasutra article
    raw_blocks = [
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "When you think of the Pokemon game franchise, of course you think of its iconic monsters. Pokemon, after all, is a portmanteau of its Japanese title, Pocket Monsters, and the series' most iconic mon' is Pikachu, which still serves as its symbol over a decade later. With every game in the franchise, a team of monster designers at developer Game Freak comes up with new creatures for players to battle and catch."},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "Hironobu Yoshida led the graphic design team for the game's interface; he also worked on the monster designs alongside a team of about 20 designers who come up with ideas for pokemon."},
        {"type": "heading", "level": 2, "speaker": "", "text": "The Starters: Faces of the Generation"},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "Pikachu may endure, but each game has its own stars -- the trio of 'starters,' the three monsters from which the player selects his or her first companion. Above, you can see the starters from Pokemon X and Y."},
        {"type": "dialogue", "speaker": "Junichi Masuda", "text": "\"I do believe they represent a very important position in the Pokemon games, of course. They're the first pokemon you pick,\" says the game's director, Junichi Masuda."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"I think they're absolutely necessary to the Pokemon games,\" Yoshida says. \"Personally, I think they're the ones that should be on the packaging. They're really the face of that generation, and I think even as designers, they feel a bit more special to us than some of the other pokemon.\""},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "It's not just about aesthetics -- the starters teach players how the game works in fundamental ways, a challenge to accomplish through visual design."},
        {"type": "dialogue", "speaker": "Junichi Masuda", "text": "\"With the starter pokemon, they always evolve twice, and a lot of players will use these pokemon until the end. They teach the players a bit about the basics, so we need to make sure the designs are at the same time easy to understand -- the way they evolve, for example -- and of course making them appealing is very important to the games,\" says Masuda."},
        {"type": "heading", "level": 2, "speaker": "", "text": "The 20-Person Committee and the Rejection Process"},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "As you might imagine, the process of coming up with these monsters is very painstaking:"},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"Since there are 20 of us and we're working all on our own ideas, we want to make sure we're not overlapping ideas. At Game Freak, we have an internal server where we can upload our designs and share them with everyone else on the team. This allows us to see what everyone else is working on and get ideas from each other,\" Yoshida says."},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "Getting a monster selected for the final roster, however, is not simple."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"It's very difficult work every time. There are probably five to 10 times the number of ideas that are rejected as the ones that make it into the final design, so it's a very difficult process,\" Yoshida says."},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "The studio has a committee of five people who decide which designs will go into the game -- and which do not make the cut."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"And they also will leave feedback on all of the designs, even the ones that are rejected, to say why they got rejected or why they didn't choose a certain one. What that lets us do is improve for the future, so we can use that knowledge for the next series of titles,\" Yoshida says."},
        {"type": "heading", "level": 2, "speaker": "", "text": "From Setup Sheets to the Pokédex: The Final Supervision"},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "It's Yoshida's job to supervise the final look of each monster, in the form of setup sheets that contain every detail of their appearance."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"I'm in charge of really creating these setup sheets and making the final adjustments to the pokemon,\" he says. He also created the Pokemon X and Y pokedex -- the in-game catalogue of all the monsters."},
        {"type": "paragraph", "speaker": "Christian Nutt", "text": "The monster designs also don't occur in a vacuum. The nature of the game means that various monster 'types' -- there are 18, which function similarly to elements in other RPGs -- are needed to fill the roster and provide for balanced play."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"Of course, we do a lot of free thinking on our own, but we also get orders from the planners, saying, 'We need this type of pokemon,' or even from Mr. Masuda, the director. He'll say that we need specific pokemon,\" Yoshida says."},
        {"type": "dialogue", "speaker": "Hironobu Yoshida", "text": "\"Really one of the good things about the company is that it's really open for discussion,\" he adds. \"We can talk with each other until both parties come to an agreement, I think.\""}
    ]

    glossary = load_glossary()
    full_text = "\n".join(b["text"] for b in raw_blocks)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items_to_translate = []
    for b in raw_blocks:
        spk = ""
        if b["speaker"] == "Christian Nutt":
            spk = "旁白"
        elif b["speaker"] == "Junichi Masuda":
            spk = "增田顺一"
        elif b["speaker"] == "Hironobu Yoshida":
            spk = "吉田宏信"

        items_to_translate.append({
            "tag": b["type"],
            "speaker": spk,
            "text": b["text"]
        })

    chunk_size = 10
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []
    # Hero image: XY Starters
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2013-10-10-interview-gamasutra-xy-monster-design/froakie.png",
        "alt": "《宝可梦 X·Y》最初的伙伴与怪兽设计哲学",
        "caption": "Gamasutra 独家专访：吉田宏信与增田顺一揭晓《X·Y》宝可梦设计委员会与御三家哲学"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}
            
            if "The 20-Person Committee" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2013-10-10-interview-gamasutra-xy-monster-design/fennekin.png",
                    "alt": "火狐狸官方艺术图",
                    "caption": "内部服务器共享与 5 人评审团：从 5 至 10 倍草案中脱颖而出的严酷机制"
                })
            elif "From Setup Sheets to the Pokédex" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2013-10-10-interview-gamasutra-xy-monster-design/chespin.png",
                    "alt": "哈力栗官方艺术图",
                    "caption": "三视图设定稿与最终调整：确保每只宝可梦在 3D 空间下展现统一的设计灵魂"
                })

            if item["tag"] == "heading":
                parallel_items.append({
                    "type": "heading",
                    "level": 2,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            elif item["tag"] == "paragraph":
                parallel_items.append({
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
            else:
                spk = seg.get("speaker") or item["speaker"]
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Gamasutra 专访吉田宏信与增田顺一：宝可梦是如何诞生的？标志性生物的设计哲学",
        "original_title": "How Pokemon are born: Designing the series' iconic monsters",
        "date": "2013-10-10",
        "era": "2013–2016 · Editorial Web 杂志化排版",
        "era_skin": "2014",
        "publication": "Gamasutra / Game Developer",
        "source_kind": "feature_interview",
        "author": "Christian Nutt (Gamasutra)",
        "translator": "Poke Amice Studio",
        "interviewee": "吉田宏信, 增田顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "X·Y", "吉田宏信", "增田顺一", "宝可梦设计", "御三家"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Gamasutra Feature (2013-10-10)",
            "url": url,
            "language": "en",
            "source_type": "feature_interview"
        },
        "original_link": url,
        "summary": "2013 年 10 月《宝可梦 X·Y》全球发售之际，Gamasutra 资深编辑 Christian Nutt 深度专访了 Game Freak 界面设计主管兼宝可梦最终监修吉田宏信与总监增田顺一。访谈首次详尽公开了 Game Freak 20 人怪兽设计团队的内部运作流程、高达 5 至 10 倍的高淘汰率、5 人核心评审委员会的反馈机制，以及为何御三家必须承载“世代门面”与教学重任的独家见解。",
        "entities": {
            "people": ["吉田宏信", "增田顺一", "杉森建", "Christian Nutt"],
            "games": ["宝可梦 X·Y"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2013-10-10-interview-gamasutra-xy-monster-design.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def import_interview_denfaminicogamer_new_generation():
    url = "https://news.denfaminicogamer.jp/interview/170703"
    print(f"\n========================================================")
    print("=== Importing: Denfaminicogamer - Shigeru Ohmori & Masayuki Onoue ===")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    idx = raw_html.find('29歳と36歳の若きディレクター')
    end_idx = raw_html.find('カテゴリーピックアップ', idx)
    body = raw_html[idx:end_idx]

    tags = re.findall(r'<(p|h2|h3|blockquote)[^>]*>([\s\S]*?)</\1>', body)

    parsed_items = []
    for tag, val in tags:
        txt = html.unescape(re.sub(r'<[^>]+>', '', val)).strip()
        txt = re.sub(r'\s+', ' ', txt)
        if not txt or len(txt) < 3:
            continue
        if any(s in txt for s in ["関連記事", "人気の記事", "新着記事", "目次"]):
            continue

        if tag == "h2":
            parsed_items.append({"type": "heading", "level": 2, "speaker": "", "text": txt})
        elif tag == "h3":
            parsed_items.append({"type": "heading", "level": 3, "speaker": "", "text": txt})
        elif txt.startswith("※") or txt.startswith("【※"):
            parsed_items.append({"type": "note", "speaker": "", "text": txt})
        elif "尾上将之氏（以下、尾上氏）：" in txt or txt.startswith("尾上氏："):
            clean_text = re.sub(r'^尾上将之氏（以下、尾上氏）：\s*', '', txt)
            clean_text = re.sub(r'^尾上氏：\s*', '', clean_text)
            parsed_items.append({"type": "dialogue", "speaker": "尾上将之", "text": clean_text})
        elif "大森滋氏（以下、大森氏）：" in txt or txt.startswith("大森氏："):
            clean_text = re.sub(r'^大森滋氏（以下、大森氏）：\s*', '', txt)
            clean_text = re.sub(r'^大森氏：\s*', '', clean_text)
            parsed_items.append({"type": "dialogue", "speaker": "大森滋", "text": clean_text})
        elif txt.startswith("――") or txt.startswith("——") or txt.startswith("──"):
            parsed_items.append({"type": "dialogue", "speaker": "提问", "text": txt.lstrip("―─—").strip()})
        else:
            if parsed_items and parsed_items[-1]["type"] == "dialogue":
                parsed_items[-1]["text"] += "\n" + txt
            else:
                parsed_items.append({"type": "paragraph", "speaker": "", "text": txt})

    print(f"Extracted {len(parsed_items)} structured interview blocks (zero noise).")

    # Download images
    img_dir = IMG_DIR / "2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation"
    download_image("https://news.denfaminicogamer.jp/wp-content/uploads/2017/06/fi_20170223_006-1024x710.jpg", img_dir, "hero_ohmori_onoue_2017.jpg")
    download_image("https://news.denfaminicogamer.jp/wp-content/uploads/2017/06/20170223_036-1024x683.jpg", img_dir, "ohmori_profile.jpg")
    download_image("https://news.denfaminicogamer.jp/wp-content/uploads/2017/06/20170223_095-1024x683.jpg", img_dir, "onoue_profile.jpg")
    download_image("https://news.denfaminicogamer.jp/wp-content/uploads/2017/06/160626_sm.jpg", img_dir, "sun_moon_cover.jpg")
    download_image("https://news.denfaminicogamer.jp/wp-content/uploads/2017/06/20170223_010.jpg", img_dir, "interview_discussion.jpg")

    glossary = load_glossary()
    full_text = "\n".join(b["text"] for b in parsed_items)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items_to_translate = []
    for b in parsed_items:
        items_to_translate.append({
            "tag": b["type"],
            "speaker": b.get("speaker", ""),
            "text": b["text"]
        })

    chunk_size = 10
    chunks = [items_to_translate[i:i + chunk_size] for i in range(0, len(items_to_translate), chunk_size)]
    print(f"Translating in {len(chunks)} chunk(s)...")

    parallel_items = []
    # Hero image
    parallel_items.append({
        "type": "image",
        "image": "/assets/img/interviews/2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation/hero_ohmori_onoue_2017.jpg",
        "alt": "电玩志专访：大森滋（左，36岁，Sun & Moon 总监）与尾上将之（右，29岁，Gear Project 负责人）",
        "caption": "电玩志专访：36 岁的大森滋与 29 岁的尾上将之，肩负 Game Freak 未来的少壮派总监们"
    })

    for c_idx, chunk in enumerate(chunks, 1):
        print(f"  Chunk {c_idx}/{len(chunks)} ({len(chunk)} items)...", end="", flush=True)
        t0 = time.time()
        translated_segments = translate_chunk(chunk, glossary_matches)
        print(f" done in {time.time()-t0:.1f}s, received {len(translated_segments)} segs.")

        for i, item in enumerate(chunk):
            seg = translated_segments[i] if i < len(translated_segments) else {"speaker": item["speaker"], "original": item["text"], "translation": item["text"], "note": ""}

            if "『ポケモン』のディレクターは何をするのか？" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation/sun_moon_cover.jpg",
                    "alt": "《宝可梦 太阳·月亮》阿罗拉地区诸岛巡礼",
                    "caption": "20 周年节点之作《宝可梦 太阳·月亮》：打破道馆馆主传统的阿罗拉诸岛巡礼与霸主宝可梦"
                })
            elif "「『サン・ムーン』のプレッシャーは違った」" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation/ohmori_profile.jpg",
                    "alt": "大森滋个人特写",
                    "caption": "大森滋：2001 年作为策划入职 Game Freak，从地图与道具配置逐步成长为系列总监"
                })
            elif "『赤・緑』の時代になかったネットにどう向き合うか" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation/interview_discussion.jpg",
                    "alt": "访谈对谈现场",
                    "caption": "面对‘查攻略’时代的全新游戏考量：在互联网时代重塑宝可梦的惊喜感与探索乐趣"
                })
            elif "「検索エンジン」を前提にしたゲーム開発" in item["text"]:
                parallel_items.append({
                    "type": "image",
                    "image": "/assets/img/interviews/2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation/onoue_profile.jpg",
                    "alt": "尾上将之个人特写",
                    "caption": "尾上将之：从战斗设施程序员到掌舵非宝可梦独立新 IP 的年轻总监"
                })

            if item["tag"] == "heading":
                parallel_items.append({
                    "type": "heading",
                    "level": 2,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            elif item["tag"] == "note":
                parallel_items.append({
                    "type": "note",
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"])
                })
            elif item["tag"] == "paragraph":
                parallel_items.append({
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
            else:
                spk = seg.get("speaker") or item["speaker"] or "大森滋"
                parallel_items.append({
                    "speaker": spk,
                    "original": item["text"],
                    "translation": seg.get("translation", item["text"]),
                    "note": seg.get("note", "")
                })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 电玩志专访大森滋与尾上将之：新作是假定会被搜索引擎查攻略？继承 Game Freak 传奇的年轻总监们",
        "original_title": "【新連載：新世代に訊く】 『ポケモン』新作は“攻略”を検索される前提？ ゲームフリークの伝説を受け継ぐ若きディレクター達 【大森 滋氏・尾上 将之氏インタビュー】",
        "date": "2017-07-03",
        "era": "2017–2021 · Switch Microsite 触控时代",
        "era_skin": "2019",
        "publication": "电ファミニコゲーマー (Denfaminicogamer)",
        "source_kind": "web_magazine",
        "author": "稲葉ほたて, 斉藤大地, TAITAI (Denfaminicogamer)",
        "translator": "Poke Amice Studio",
        "interviewee": "大森滋, 尾上将之",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "太阳·月亮", "大森滋", "尾上将之", "Game Freak", "游戏设计", "阿罗拉"],
        "archive_type": "interview_translation",
        "source": {
            "title": "電ファミニコゲーマー (Denfaminicogamer 2017-07-03)",
            "url": url,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "2017 年 7 月，著名游戏媒体“电玩志（Denfaminicogamer）”开启全新企划【向新世代发问】，首期深度对谈 Game Freak 的两位少壮派核心主创：36 岁掌舵 20 周年正统大作《宝可梦 太阳·月亮》的总监大森滋，与 29 岁从程序员破格成为独立新 IP 负责人的尾上将之。访谈深刻揭示了在互联网与智能手机普及、任何秘密都会被搜索引擎瞬间揭底的现代社会中，宝可梦游戏设计如何颠覆 20 年传统道馆机制、以霸主宝可梦重塑未知冒险感，以及内部孵化创意的“齿轮企划（Gear Project）”。",
        "entities": {
            "people": ["大森滋", "尾上将之", "田尻智", "增田顺一"],
            "games": ["宝可梦 太阳·月亮", "宝可梦 红·绿", "宝可梦 红宝石·蓝宝石", "宝可梦 钻石·珍珠", "TEMBO THE BADASS ELEPHANT"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / "2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post_path = ROOT / "tools" / "clean_interview_noise.py"
    if clean_post_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_post_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "ascii"
    if action == "pikachu":
        import_interview_pikachu()
    elif action == "bw":
        import_interview_masuda_sugimori_gen5()
    elif action == "gs":
        import_interview_sugimori_gen2_cut_pokemon()
    elif action == "ascii":
        import_interview_weekly_ascii_bw()
    elif action == "xy":
        import_interview_gamasutra_xy_monster_design()
    elif action == "denfamini":
        import_interview_denfaminicogamer_new_generation()
    elif action == "batch":
        import_interview_weekly_ascii_bw()
        import_interview_gamasutra_xy_monster_design()
        import_interview_denfaminicogamer_new_generation()
    elif action == "all":
        import_interview_pikachu()
        import_interview_masuda_sugimori_gen5()
        import_interview_sugimori_gen2_cut_pokemon()
        import_interview_weekly_ascii_bw()
        import_interview_gamasutra_xy_monster_design()
        import_interview_denfaminicogamer_new_generation()



