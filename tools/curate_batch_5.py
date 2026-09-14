"""Batch curate, clean, translate, and import 4 Iwata Asks: HGSS developer interviews (Batch 5):
1. PKMN-0636: 社長が訊く『心金·魂银』第1章：从赤绿到金银的十年传承与最终电车奇迹 (Chapter 1)
2. PKMN-0638: 社長が訊く『心金·魂银』第2章：石原恒和与“便携玩具之王”的衍生哲学 (Chapter 2)
3. PKMN-0637: 社長が訊く『心金·魂银』第3章：岩田聪亲述当年为金银写压缩算法救场与一周移植宝可梦竞技场 (Chapter 3)
4. PKMN-0639: 社長が訊く『心金·魂银』第4章：Pokéwalker软硬件开发、全493只宝可梦跟随与十周年致玩家 (Chapters 4, 5, 6)
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import yaml

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path("p:/WEBSITE/pokeamice-main (1)/pokeamice-main")
POSTS_DIR = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
CATALOG_PATH = ROOT / "data" / "pokemon_1000_interviews.json"
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
    
    prompt = f"""你是精通任天堂史料、宝可梦开发史与岩田聪“社长问（社長が訊く）”系列的资深学者与翻译家。
正在整理《宝可梦 心金·魂银》社长问（岩田聪 × 石原恒和 × 森本茂树）的日中对照史料档案。

请将以下访谈对话翻译为流畅、准确、忠实原文且富有历史代入感的简体中文。
注意：
1. 准确识别并标注说话人(speaker)：如“岩田 聪”、“石原 恒和”、“森本 茂树”、“石原 & 森本”或“众人”。
2. 保持岩田聪温和、睿智、风趣而敏锐的提问风采，以及石原恒和与森本茂树充满敬意与激情的回答语气。
3. 如果对话中涉及特定历史典故、技术术语（如金银数据压缩、汇编代码、N64移植、生活节拍器、计步器、梦幻、全国图鉴493跟随等），请在 note 字段给出简明译注。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 心金·魂银（HeartGold & SoulSilver）
- 金·银（Gold & Silver）
- 赤·绿（Red & Green）
- 宝可计步器 / Pokéwalker（ポケウォーカー）
- 口袋皮卡丘（ポケットピカチュウ）
- 梦幻（Mew / ミュウ）
- 凤王（Ho-Oh / ホウオウ）
- 洛奇亚（Lugia / ルギア）
- 宝可梦竞技场（Pokémon Stadium / ポケモンスタジアム）
- HAL 研究所（HAL Laboratory）
- 宝可梦公司（The Pokémon Company）
- Creatures（株式会社クリーチャーズ）
- Game Freak（株式会社ゲームフリーク）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'岩田 聪'，若无则留空字符串''）",
      "original": "该段对应的日文原文",
      "translation": "流畅典雅的简体中文译文",
      "note": "对原文背景、技术细节或历史事件的简要译注（若无则留空字符串''）"
    }}
  ]
}}

待翻译原文段落列表：
{json.dumps(chunk, ensure_ascii=False, indent=2)}
"""

    messages = [
        {"role": "system", "content": "你是一位精通任天堂社长问系列与宝可梦开发史的双语史料专家。请只输出合法的 JSON 对象。"},
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
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 800:
                dest_path.write_bytes(data)
                print(f"      [Image Saved] {filename} ({len(data)} bytes)")
                return f"/assets/img/interviews/{dest_dir.name}/{filename}"
    except Exception as e:
        print(f"      [Image Download Failed] {img_url}: {e}")
    return None


def clean_post(post_path: Path):
    clean_tool = ROOT / "tools" / "clean_interview_noise.py"
    if clean_tool.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("clean_interview_noise", clean_tool)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clean_post(post_path)
        print("Completed zero-noise verification via clean_interview_noise.")


def fetch_chapter_dialogues(chapter_index: int) -> tuple[str, list[dict], dict[str, str]]:
    fn = "index.html" if chapter_index == 1 else f"index{chapter_index}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/ipkj/vol1/{fn}"
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=15).read().decode('shift_jis', errors='replace')

    # Title
    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', raw, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {chapter_index}"

    # Footnotes mapping
    notes_map = {}
    note_boxes = re.findall(r'<DIV CLASS="notes-box">\s*<DIV CLASS="notes-num"><P>(※\d+)</P></DIV>\s*<DIV CLASS="notes-text"><P>(.*?)</P></DIV>', raw, re.DOTALL | re.I)
    for num, ntext in note_boxes:
        clean_nt = html.unescape(re.sub(r'<[^>]+>', '', ntext)).strip()
        notes_map[num] = clean_nt

    # Dialogues
    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', raw, re.DOTALL | re.I)
    name_map = {
        "岩田": "岩田 聪",
        "石原": "石原 恒和",
        "森本": "森本 茂树",
        "石原・森本": "石原 & 森本",
        "一同": "众人"
    }

    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)

        # Check footnotes referenced in this turn
        m_notes = re.findall(r'※\d+', body)
        ref_notes = [f"{n}：{notes_map[n]}" for n in m_notes if n in notes_map]

        body_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body))
        body_clean = re.sub(r'<BR\s*/?>', '\n', body_clean, flags=re.I)
        body_clean = re.sub(r'<[^>]+>', '', body_clean).strip()

        dialogues.append({
            "speaker": spk_norm,
            "text": body_clean,
            "raw_notes": "；".join(ref_notes)
        })

    return title, dialogues, notes_map


def run_translation_and_build_items(dialogues: list[dict], glossary: list[dict]) -> list[dict]:
    full_text = " ".join(it["text"] for it in dialogues)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items = []
    chunk_size = 6
    for i in range(0, len(dialogues), chunk_size):
        chunk = dialogues[i:i+chunk_size]
        print(f"   Translating chunk {i//chunk_size + 1}/{(len(dialogues)-1)//chunk_size + 1}...")
        segments = translate_chunk(chunk, glossary_matches)
        for idx_c, seg in enumerate(segments):
            orig_meta = chunk[idx_c] if idx_c < len(chunk) else {}
            existing_note = seg.get("note", "").strip()
            raw_note = orig_meta.get("raw_notes", "").strip()
            final_note = f"{existing_note}（任天堂官方注：{raw_note}）" if (existing_note and raw_note) else (existing_note or (f"任天堂官方注：{raw_note}" if raw_note else ""))

            items.append({
                "speaker": seg.get("speaker", ""),
                "original": seg.get("original", ""),
                "translation": seg.get("translation", ""),
                "note": final_note
            })
        time.sleep(1)
    return items


# =========================================================================
# 1. PKMN-0636: Chapter 1 Red/Green Launch & Mew
# =========================================================================
def import_hgss_part1():
    slug = "2009-09-04-interview-iwata-asks-hgss-chapter-1-red-green-mew"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0636 社長が訊く『心金·魂银』第1章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_photo01.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo01.jpg",
        "nintendo_mainvisual1.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/mainvisual1.jpg",
        "mew.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/151.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    title_jap, raw_items, notes_map = fetch_chapter_dialogues(1)
    glossary = load_glossary()
    parallel_items = run_translation_and_build_items(raw_items, glossary)

    # Insert images
    if local_images.get("nintendo_mainvisual1.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_mainvisual1.jpg"],
            "caption_original": "社長が訊く『ポケットモンスター ハートゴールド・ソウルシルバー』：岩田聡 × 石原恒和 × 森本茂樹。",
            "caption_translation": "任天堂官方访谈“社长问”《宝可梦 心金·魂银》专刊：岩田聪社长亲自主持对谈石原恒和与森本茂树。"
        })
    if local_images.get("mew.png"):
        parallel_items.insert(20, {
            "type": "image",
            "image": local_images["mew.png"],
            "caption_original": "幻のポケモン「ミュウ」：デバッグ完了後の空き領域に、森本茂樹氏の“イタズラ心”で密かに書き込まれた奇跡の存在。",
            "caption_translation": "幻之宝可梦“梦幻”：在全部调试结束后仅剩的 300 字节空闲数据区中，由森本茂树怀着恶作剧般的执念偷偷写入代码的传奇奇迹。"
        })
    if local_images.get("nintendo_photo01.jpg"):
        parallel_items.insert(35, {
            "type": "image",
            "image": local_images["nintendo_photo01.jpg"],
            "caption_original": "「最終電車に間に合った」と振り返る岩田聡と、石原恒和・森本茂樹。",
            "caption_translation": "岩田聪与石原恒和、森本茂树共同回顾当年赤绿赶上 Game Boy‘末班车’的不可思议历程。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 心金·魂银》第1章：岩田聪 × 石原恒和 × 森本茂树——赶上末班车的赤绿与偷塞“梦幻”的真相",
        "original_title": "社長が訊く『ポケットモンスター ハートゴールド・ソウルシルバー』1. 最終電車に間に合った『ポケモン』",
        "date": "2009-09-04",
        "era": "2006–2009 · NDS / 触控探索时代",
        "era_skin": "2007",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 森本 茂树",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "心金·魂银", "赤·绿", "岩田聪", "石原恒和", "森本茂树", "社长问", "任天堂", "梦幻", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Vol.1 第1回",
            "url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html",
        "summary": "任天堂传奇社长岩田聪亲自主持对谈宝可梦社长石原恒和与《心金·魂银》总监森本茂树。三人全景重温了宝可梦创生期的传奇篇章：1996 年《红·绿》赶在 Game Boy 硬件生命末期‘末班车’惊险首发；在零电视宣传下凭借小学生口碑传播掀起全球狂潮的十年奇迹；森本茂树首次向岩田聪完整承认——在极其漫长严苛的联机测试与调试全部通过后，利用卡带仅剩的 300 字节空闲区域，背着所有人偷偷将第 151 号宝可梦‘梦幻’写入 ROM 中，并由此引爆《快乐龙》杂志 20 个抽选名额收到 7.8 万封明信片的轰动历史。",
        "entities": {
            "people": ["岩田 聪", "石原 恒和", "森本 茂树", "田尻 智"],
            "games": ["宝可梦 心金·魂银", "宝可梦 红·绿", "宝可梦 金·银"],
            "pokemon": ["梦幻", "皮卡丘"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)
    return slug


# =========================================================================
# 2. PKMN-0638: Chapter 2 Handheld Toy King & Creatures
# =========================================================================
def import_hgss_part2():
    slug = "2009-09-04-interview-iwata-asks-hgss-chapter-2-portable-toy-king"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0638 社長が訊く『心金·魂银』第2章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_photo02.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo02.jpg",
        "nintendo_sub_photo01.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/sub_photo01.jpg",
        "pikachu.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    title_jap, raw_items, notes_map = fetch_chapter_dialogues(2)
    glossary = load_glossary()
    parallel_items = run_translation_and_build_items(raw_items, glossary)

    if local_images.get("nintendo_sub_photo01.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_sub_photo01.jpg"],
            "caption_original": "『ポケットピカチュウ』：石原恒和氏がプロデュースした携帯型液晶歩数計玩具。",
            "caption_translation": "《口袋皮卡丘》：由石原恒和亲自担当制作人的便携式液晶步数计玩具，开启了宝可梦陪伴玩家现实步行的先河。"
        })
    if local_images.get("nintendo_photo02.jpg"):
        parallel_items.insert(15, {
            "type": "image",
            "image": local_images["nintendo_photo02.jpg"],
            "caption_original": "「携帯玩具王」石原恒和氏のモノづくり哲学について語り合う岩田聡と森本茂樹。",
            "caption_translation": "岩田聪与森本茂树风趣探讨石原恒和作为‘便携玩具之王’对实体外设与卡牌生态的执着追求。"
        })
    if local_images.get("pikachu.png"):
        parallel_items.insert(28, {
            "type": "image",
            "image": local_images["pikachu.png"],
            "caption_original": "ピカチュウ：ゲームの枠を超えて世界中の子どもたちの日常に浸透した象徴。",
            "caption_translation": "皮卡丘：突破卡带界限，通过集换式卡牌、动画与计步器玩具全方位融入全球大众日常生活的文化符号。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 心金·魂银》第2章：岩田聪 × 石原恒和——“便携玩具之王”与跳出卡带的宝可梦生态",
        "original_title": "社長が訊く『ポケットモンスター ハートゴールド・ソウルシルバー』2. “携帯玩具王”",
        "date": "2009-09-04",
        "era": "2006–2009 · NDS / 触控探索时代",
        "era_skin": "2007",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 森本 茂树",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "心金·魂银", "口袋皮卡丘", "石原恒和", "岩田聪", "森本茂树", "社长问", "宝可梦卡牌", "Creatures"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Vol.1 第2回",
            "url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index2.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index2.html",
        "summary": "岩田聪与石原恒和、森本茂树共同剖析宝可梦如何从一款掌机卡带进化为横跨全媒介的全球生态。石原恒和揭示了创立 Creatures、开发宝可梦官方集换式卡牌（PTCG）、以及在动画化前夜制作独立计步器玩具《口袋皮卡丘》（Pocket Pikachu）的敏锐洞察。岩田聪将其戏称为‘便携玩具之王’，阐明正是跳出屏幕、将宝可梦赋予真实世界交互实感的理念，才让品牌在续作诞生前的三年真空期中生命力非但没有枯竭，反而越发鼎盛。",
        "entities": {
            "people": ["岩田 聪", "石原 恒和", "森本 茂树"],
            "games": ["宝可梦 心金·魂银", "口袋皮卡丘", "宝可梦集换式卡牌游戏"],
            "pokemon": ["皮卡丘"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)
    return slug


# =========================================================================
# 3. PKMN-0637: Chapter 3 Iwata Compression & Stadium in a Week
# =========================================================================
def import_hgss_part3():
    slug = "2009-09-04-interview-iwata-asks-hgss-chapter-3-iwata-compression-stadium"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0637 社長が訊く『心金·魂银』第3章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_photo03.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo03.jpg",
        "ho_oh.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png",
        "lugia.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    title_jap, raw_items, notes_map = fetch_chapter_dialogues(3)
    glossary = load_glossary()
    parallel_items = run_translation_and_build_items(raw_items, glossary)

    if local_images.get("nintendo_photo03.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_photo03.jpg"],
            "caption_original": "「社長にしておくにはもったいない」と語られる岩田聡のプログラミング伝説。",
            "caption_translation": "石原恒和与森本茂树感叹‘光当个社长实在太暴殄天物了’——岩田聪当年挽救《金·银》的编程奇迹。"
        })
    if local_images.get("ho_oh.png"):
        parallel_items.insert(16, {
            "type": "image",
            "image": local_images["ho_oh.png"],
            "caption_original": "ホウオウ：ジョウト地方の伝承を背負い、カントー地方をも内包した『金・銀』の象徴。",
            "caption_translation": "凤王：承载城都地方千年传说，并在岩田聪的极限压缩助力下包容下整个关都地方的伟大图腾。"
        })
    if local_images.get("lugia.png"):
        parallel_items.insert(32, {
            "type": "image",
            "image": local_images["lugia.png"],
            "caption_original": "ルギア：N64『ポケモンスタジアム』でも躍動した、海と嵐を司る伝説の守護神。",
            "caption_translation": "洛奇亚：由首里城与深海灵感孕育，亦在 N64《宝可梦竞技场》全 3D 舞台上震撼登场的银色守护神。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 心金·魂银》第3章：岩田聪亲述当年为《金·银》写压缩代码救场与一周移植宝可梦竞技场",
        "original_title": "社長が訊く『ポケットモンスター ハートゴールド・ソウルシルバー』3. 社長にしておくにはもったいない",
        "date": "2009-09-04",
        "era": "2006–2009 · NDS / 触控探索时代",
        "era_skin": "2007",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 森本 茂树",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "心金·魂银", "金·银", "岩田聪", "石原恒和", "森本茂树", "社长问", "宝可梦竞技场", "汇编语言", "编程传奇"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Vol.1 第3回",
            "url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index3.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index3.html",
        "summary": "游戏工业史上最负盛名的程序员传奇与管理奇迹在此被当事人完整解密！当年《宝可梦 金·银》由于技术极限与人手不足面临严重难产，时任 HAL 研究所社长的岩田聪亲自挂帅，亲手编写了一套极其精妙的高性能数据压缩工具，不仅成功将庞大的城都地方塞进卡带，甚至腾出了海量空间，让初代整个关都地区（Kanto）以‘通关后隐藏大地图’的奇迹形式重现！紧接着，为了让海外玩家与 N64 玩家体验 3D 对战，在没有任何 Game Freak 规格说明书的情况下，岩田聪仅凭森本茂树注释晦涩的汇编源代码，仅用一周时间就在 N64 上从底层完整复现了初代宝可梦的对战逻辑引擎，森本茂树与石原恒和当场赞叹：‘这个人只当个社长实在太浪费了！’",
        "entities": {
            "people": ["岩田 聪", "石原 恒和", "森本 茂树"],
            "games": ["宝可梦 金·银", "宝可梦竞技场", "宝可梦 心金·魂银", "宝可梦 红·绿"],
            "pokemon": ["凤王", "洛奇亚"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)
    return slug


# =========================================================================
# 4. PKMN-0639: Chapters 4, 5, 6 Pokéwalker & 493 Following
# =========================================================================
def import_hgss_part4():
    slug = "2009-09-04-interview-iwata-asks-hgss-chapter-4-pokewalker-493-following"
    print(f"\n========================================================")
    print("=== Importing #4: PKMN-0639 社長が訊く『心金·魂银』第4章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_photo04.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo04.jpg",
        "nintendo_sub_photo04.jpg": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/sub_photo04.jpg",
        "ho_oh.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    # Merge Chapters 4, 5, 6
    merged_dialogues = []
    for c in [4, 5, 6]:
        t, d, _ = fetch_chapter_dialogues(c)
        merged_dialogues.append({"speaker": "【章节导览】", "text": f"=== {t} ===", "raw_notes": ""})
        merged_dialogues.extend(d)

    glossary = load_glossary()
    parallel_items = run_translation_and_build_items(merged_dialogues, glossary)

    if local_images.get("nintendo_sub_photo04.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_sub_photo04.jpg"],
            "caption_original": "ポケウォーカー（Pokéwalker）：赤外線通信を内蔵し、ゲームから好きなポケモンを連れ出せる超高精度歩数計。",
            "caption_translation": "宝可计步器（Pokéwalker）：内置红外线无线通信，可将游戏中喜爱的任何宝可梦随时带往现实漫步的超高精度外设。"
        })
    if local_images.get("nintendo_photo04.jpg"):
        parallel_items.insert(30, {
            "type": "image",
            "image": local_images["nintendo_photo04.jpg"],
            "caption_original": "「かがくのちからって すげえ」と笑い合う岩田聡、石原恒和、森本茂樹。",
            "caption_translation": "三人感叹真新镇肥宅经典名句‘科学的力量真伟大啊’，并回顾任天堂员工每天别在腰间步行测试计步器精度的趣事。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 心金·魂银》第4章：Pokéwalker软硬件开发、全493只宝可梦跟随与十周年致玩家",
        "original_title": "社長が訊く『ポケットモンスター ハートゴールド・ソウルシルバー』4. 「かがくのちからって すげえ」〜 6. 昔といまのポケモンプレイヤーに",
        "date": "2009-09-04",
        "era": "2006–2009 · NDS / 触控探索时代",
        "era_skin": "2007",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 森本 茂树",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "心金·魂银", "Pokéwalker", "岩田聪", "石原恒和", "森本茂树", "社长问", "宝可梦跟随", "十周年", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Vol.1 第4〜6回",
            "url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index4.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index4.html",
        "summary": "《心金·魂银》社长问大结局篇章（整合第4、5、6节）：从真新镇名台词‘科学的力量真伟大啊！’切入，详述作为随卡带附赠外设的 Pokéwalker 开发历程——采用任天堂硬件技术精工打造的防作弊高精度计步器、红外线双向无线通信、以及任天堂社员全员佩戴步行的严格验证；森本茂树揭秘为了让玩家随时产生‘心心相印’的伙伴感，不惜工本为当时全国图鉴全部 493 只宝可梦（包括闪光形态与特殊形态）全部手绘大地图跟随行走图并设计丰富情绪反应的‘极其贪婪的豪华规格’；最后，三人向十年前玩过金银已为人父母、以及初次接触宝可梦的新生代玩家送上深情寄语。",
        "entities": {
            "people": ["岩田 聪", "石原 恒和", "森本 茂树"],
            "games": ["宝可梦 心金·魂银", "宝可梦 金·银", "生活节拍器DS"],
            "pokemon": ["凤王", "洛奇亚", "皮卡丘"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)
    return slug


def update_catalog(batch_results: dict[str, str]):
    if not CATALOG_PATH.exists():
        return
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta_updates = {
        "PKMN-0636": {
            "title": "社长问《宝可梦 心金·魂银》第1章：岩田聪 × 石原恒和 × 森本茂树——赶上末班车的赤绿与偷塞“梦幻”的真相",
            "date": "2009-09-04",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0636']}.md",
            "status": "imported"
        },
        "PKMN-0638": {
            "title": "社长问《宝可梦 心金·魂银》第2章：岩田聪 × 石原恒和——“便携玩具之王”与跳出卡带的宝可梦生态",
            "date": "2009-09-04",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index2.html",
            "post_file": f"_posts/{batch_results['PKMN-0638']}.md",
            "status": "imported"
        },
        "PKMN-0637": {
            "title": "社长问《宝可梦 心金·魂银》第3章：岩田聪亲述当年为《金·银》写压缩代码救场与一周移植宝可梦竞技场",
            "date": "2009-09-04",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index3.html",
            "post_file": f"_posts/{batch_results['PKMN-0637']}.md",
            "status": "imported"
        },
        "PKMN-0639": {
            "title": "社长问《宝可梦 心金·魂银》第4章：Pokéwalker软硬件开发、全493只宝可梦跟随与十周年致玩家",
            "date": "2009-09-04",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index4.html",
            "post_file": f"_posts/{batch_results['PKMN-0639']}.md",
            "status": "imported"
        }
    }

    updated_count = 0
    for item in data:
        cid = item.get("id")
        if cid in meta_updates:
            up = meta_updates[cid]
            item.update(up)
            updated_count += 1

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[CATALOG UPDATED] Successfully updated {updated_count} records in {CATALOG_PATH.name}!")


def main():
    print("Starting Batch 5 (Iwata Asks: HGSS Series) Import Pipeline...")
    batch_results = {}
    
    slug_0636 = import_hgss_part1()
    batch_results["PKMN-0636"] = slug_0636

    slug_0638 = import_hgss_part2()
    batch_results["PKMN-0638"] = slug_0638

    slug_0637 = import_hgss_part3()
    batch_results["PKMN-0637"] = slug_0637

    slug_0639 = import_hgss_part4()
    batch_results["PKMN-0639"] = slug_0639

    update_catalog(batch_results)
    print("\nBatch 5 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
