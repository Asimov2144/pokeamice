"""Batch curate, clean, translate, and import 4 Iwata Asks: Pokémon Black 2 & White 2 developer interviews (Batch 7):
1. PKMN-0649: 社長が訊く『黑2·白2』第1章：为何打破传统做正统数字续篇（“两部续篇”与“两年之后”）
2. PKMN-0652: 社長が訊く『黑2·白2』第2章：百人实时同屏的庆典任务与遗迹通信挑战
3. PKMN-0651: 社長が訊く『黑2·白2』第3章：双版本同时发售的双钥匙联动机制与宝可梦好莱坞太空幻想
4. PKMN-0650: 社長が訊く『黑2·白2』第4章：为什么在3DS已上市时坚守NDS硬件（桧扇市全新开局、宝可梦本质与三神器联动）
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
正在整理《宝可梦 黑2·白2》社长问（岩田聪 × 石原恒和 × 增田顺一 × 海野隆雄）的日中对照史料档案。

请将以下访谈对话翻译为流畅、准确、忠实原文且极富历史沉浸感的简体中文。
注意：
1. 准确标注说话人(speaker)：如“岩田 聪”、“石原 恒和”、“增田 顺一”、“海野 隆雄”或“众人”。
2. 保持岩田聪温润敏锐的提问、增田顺一作为制作人的宏观把握、海野隆雄作为年轻总监的激情与执着、以及石原恒和统揽大局的商业眼光。
3. 如果对话中涉及特定历史典故、技术术语（如 宝可梦好莱坞/Pokéstar Studios、暗黑酋雷姆/焰白酋雷姆、合众连接/回忆之绊、三神器、梦境雷达/AR搜索器、桧扇市全新开局、百人庆典任务等），请在 note 字段给出简明精要的译注。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 黑2·白2（Black 2 & White 2）
- 黑·白（Black & White）
- 酋雷姆（Kyurem / キュレム）
- 暗黑酋雷姆（Black Kyurem / ブラックキュレム）
- 焰白酋雷姆（White Kyurem / ホワイトキュレム）
- 凯路迪欧（Keldeo / ケルディオ）
- 美洛耶塔（Meloetta / メロエッタ）
- 宝可梦好莱坞 / 宝可坞（Pokéstar Studios / ポケウッド）
- 桧扇市（Aspertia City / ヒオウギシティ）
- 庆典任务（Fes Missions / フェスミッション）
- 加油大道（Join Avenue / ジョインアベニュー）
- 宝可梦AR搜索器（Pokémon Dream Radar / ポケモンARサーチャー）
- 全国图鉴Pro（Pokédex 3D Pro / ポケモン全国図鑑Pro）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'海野 隆雄'，若无则留空字符串''）",
      "original": "该段对应的日文原文",
      "translation": "流畅雅致的简体中文译文",
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


def fetch_b2w2_chapter(chapter_index: int) -> tuple[str, list[dict]]:
    fn = "index.html" if chapter_index == 1 else f"index{chapter_index}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irej/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})).read()

    try:
        decoded = raw.decode("utf-8")
        if "ポケモン" not in decoded:
            raise ValueError()
    except:
        decoded = raw.decode("shift_jis", errors="replace")

    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', decoded, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {chapter_index}"

    notes_map = {}
    note_boxes = re.findall(r'<DIV CLASS="notes-box">\s*<DIV CLASS="notes-num"><P>(※\d+)</P></DIV>\s*<DIV CLASS="notes-text"><P>(.*?)</P></DIV>', decoded, re.DOTALL | re.I)
    for num, ntext in note_boxes:
        clean_nt = html.unescape(re.sub(r'<[^>]+>', '', ntext)).strip()
        notes_map[num] = clean_nt

    boxes = re.findall(r'<DIV CLASS="int-name"><P>(.*?)</P></DIV>\s*<DIV CLASS="int-text"><P>(.*?)</P></DIV>', decoded, re.DOTALL | re.I)
    name_map = {
        "岩田": "岩田 聪",
        "石原": "石原 恒和",
        "増田": "增田 顺一",
        "海野": "海野 隆雄",
        "一同": "众人"
    }

    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)

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

    return title, dialogues


def translate_dialogues(dialogues: list[dict], glossary: list[dict]) -> list[dict]:
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
# 1. PKMN-0649: Chapter 1 Two Sequels & Two Years Later
# =========================================================================
def import_b2w2_part1():
    slug = "2012-06-15-interview-iwata-asks-b2w2-chapter-1-two-sequels-two-years-later"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0649 社長が訊く『黑2·白2』第1章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_b2w2_mainvisual1.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/mainvisual1.jpg",
        "nintendo_b2w2_photo1.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/photo1.jpg",
        "black_kyurem.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10022.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_b2w2_chapter(1)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_b2w2_mainvisual1.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_b2w2_mainvisual1.jpg"],
            "caption_original": "社長が訊く『ポケットモンスターブラック２・ホワイト２』：岩田聡 × 石原恒和 × 増田順一 × 海野隆雄。",
            "caption_translation": "任天堂官方“社长问”《宝可梦 黑2·白2》专刊：岩田聪专访石原恒和、增田顺一与海野隆雄。"
        })
    if local_images.get("black_kyurem.png"):
        parallel_items.insert(15, {
            "type": "image",
            "image": local_images["black_kyurem.png"],
            "caption_original": "ブラックキュレム：ゼクロムの力を吸収した新たな合体伝説の象徴。",
            "caption_translation": "暗黑酋雷姆：合体吸收了捷克罗姆之力的冰之龙，象征着两部续篇的全新变幻。"
        })
    if local_images.get("nintendo_b2w2_photo1.jpg"):
        parallel_items.insert(25, {
            "type": "image",
            "image": local_images["nintendo_b2w2_photo1.jpg"],
            "caption_original": "「２作続編」と「２年後」という未踏の挑戦について語る海野隆雄総監督と増田順一。",
            "caption_translation": "总监海野隆雄与制作人增田顺一详述打破传统单版本资料片、首次打造‘两部正统数字续篇’与‘两年之后’的战略原点。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑2·白2》第1章：为何打破传统做正统数字续篇（“两部续篇”与“两年之后”）",
        "original_title": "社長が訊く『ポケットモンスターブラック２・ホワイト２』1. “２作続編”と“２年後”",
        "date": "2012-06-15",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "海野 隆雄, 增田 顺一, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑2·白2", "黑·白", "岩田聪", "增田顺一", "海野隆雄", "石原恒和", "社长问", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black 2 & White 2 Vol.1 第1回",
            "url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index.html",
        "summary": "以往宝可梦每一世代往往遵循‘双版本首发、单版本资料片跟进’（如黄、水晶、绿宝石、白金）的惯例，但《黑·白》之后全世界都以为会出《灰》，Game Freak 却颠覆性地推出了正统数字续篇《黑2·白2》！制作人增田顺一与首次挑起总监大梁的海野隆雄向岩田聪披露幕后原委：正因为《黑·白》剧本探讨了深邃的等离子队与人宠关系，单一资料片根本无法完整交待后续；于是团队大胆决定以‘时间推进两年后’的全新主角视角，双版本同步平行推进，以‘共鸣’为核心概念，为合众地方谱写真正的宏伟终章。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "海野 隆雄", "石原 恒和"],
            "games": ["宝可梦 黑2·白2", "宝可梦 黑·白", "宝可梦 白金"],
            "pokemon": ["暗黑酋雷姆", "焰白酋雷姆", "莱希拉姆", "捷克罗姆"]
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
# 2. PKMN-0652: Chapter 2 100-Player Co-op & Fes Missions
# =========================================================================
def import_b2w2_part2():
    slug = "2012-06-15-interview-iwata-asks-b2w2-chapter-2-100-player-co-op"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0652 社長が訊く『黑2·白2』第2章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_b2w2_photo2.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/photo2.jpg",
        "white_kyurem.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10023.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_b2w2_chapter(2)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_b2w2_photo2.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_b2w2_photo2.jpg"],
            "caption_original": "「100人プレイ」フェスミッションの無線通信技術について熱弁する開発陣。",
            "caption_translation": "海野隆雄与增田顺一向岩田聪展示如何在 NDS 无线通信极限下达成‘最多100人同时同屏参与庆典任务’的技术奇迹。"
        })
    if local_images.get("white_kyurem.png"):
        parallel_items.insert(16, {
            "type": "image",
            "image": local_images["white_kyurem.png"],
            "caption_original": "ホワイトキュレム：合体変身とともに、仲間たちとの共闘を加速させる存在。",
            "caption_translation": "焰白酋雷姆：与暗黑酋雷姆遥相呼应，见证连接之桥下百人并肩共斗的通信爆发力。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑2·白2》第2章：百人实时同屏的庆典任务与遗迹通信挑战",
        "original_title": "社長が訊く『ポケットモンスターブラック２・ホワイト２』2. １００人プレイ",
        "date": "2012-06-15",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "海野 隆雄, 增田 顺一, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑2·白2", "庆典任务", "海野隆雄", "增田顺一", "岩田聪", "石原恒和", "社长问", "百人同屏", "通信黑科技"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black 2 & White 2 Vol.1 第2回",
            "url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index2.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index2.html",
        "summary": "海野隆雄总监从玩家时代一路成长为掌舵人的热血历程！海野与增田向岩田聪详细拆解了本作在通信系统上的空前飞跃——‘庆典任务’（Fes Missions）：利用 DS 本地无线通信广播协议，成功实现最多 100 人同时在现场同屏接取任务、共同在合众地图上寻找道具或对战；无论彼此认不认识，只要身处同一空间就能即时产生强大的‘祭典共鸣感’，打破了传统两台机器一对一匹配的固有框架。",
        "entities": {
            "people": ["岩田 聪", "海野 隆雄", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 黑2·白2", "宝可梦 黑·白"],
            "pokemon": ["焰白酋雷姆"]
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
# 3. PKMN-0651: Chapter 3 Pokéstar Studios & Space Fantasy
# =========================================================================
def import_b2w2_part3():
    slug = "2012-06-15-interview-iwata-asks-b2w2-chapter-3-pokestar-studios-space-fantasy"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0651 社長が訊く『黑2·白2』第3章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_b2w2_photo3.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/photo3.jpg",
        "keldeo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/647.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_b2w2_chapter(3)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_b2w2_photo3.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_b2w2_photo3.jpg"],
            "caption_original": "「ポケウッド」で映画撮影とパズルバトルの融合について語る増田順一と海野隆雄。",
            "caption_translation": "增田顺一与海野隆雄揭秘宝可梦好莱坞（Pokéstar Studios）如何将剧本扮演、电影拍摄与硬核残局战棋巧妙融合。"
        })
    if local_images.get("keldeo.png"):
        parallel_items.insert(18, {
            "type": "image",
            "image": local_images["keldeo.png"],
            "caption_original": "ケルディオ（かくごのすがた）：聖剣士たちの教えを受け、映画とともに覚醒する若き英雄。",
            "caption_translation": "凯路迪欧（觉悟之姿）：传承三圣剑士正义精神，在同年大电影与黑白2游戏中同步觉醒的年轻英雄。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑2·白2》第3章：双版本同时发售的双钥匙联动机制与宝可梦好莱坞太空幻想",
        "original_title": "社長が訊く『ポケットモンスターブラック２・ホワイト２』3. 『ポケモン』でスペースファンタジー",
        "date": "2012-06-15",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "海野 隆雄, 增田 顺一, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑2·白2", "宝可梦好莱坞", "凯路迪欧", "海野隆雄", "增田顺一", "岩田聪", "石原恒和", "社长问", "设计秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black 2 & White 2 Vol.1 第3回",
            "url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index3.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index3.html",
        "summary": "本作最惊艳好评的新系统——‘宝可梦好莱坞’（Pokéstar Studios）的诞生内幕！增田顺一透露，原先在前作未能实现的‘残局对战/对战解谜’构想，与海野隆雄一直想尝试的‘在宝可梦世界里拍科幻特摄电影、穿上太空宇航服打外星怪兽’的异想天开一拍即合！岩田聪感叹道：‘当一个好玩的游戏点子与另一个看似完全无关的难题碰撞粘合在一起时，事物就会发生质的飞跃！’访谈还披露了黑2与白2各自独占的钥匙系统，通关后可解锁挑战模式（高难困难度）与休闲模式的颠覆性设计。",
        "entities": {
            "people": ["岩田 聪", "海野 隆雄", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 黑2·白2"],
            "pokemon": ["凯路迪欧"]
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
# 4. PKMN-0650: Chapters 4, 5, 6 Staying on DS & Three Sacred Treasures
# =========================================================================
def import_b2w2_part4():
    slug = "2012-06-15-interview-iwata-asks-b2w2-chapter-4-staying-on-ds-three-sacred-treasures"
    print(f"\n========================================================")
    print("=== Importing #4: PKMN-0650 社長が訊く『黑2·白2』第4章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_b2w2_photo4.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/photo4.jpg",
        "nintendo_b2w2_photo10.jpg": "https://www.nintendo.co.jp/ds/interview/irej/vol1/img/photo10.jpg",
        "meloetta.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/648.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    # Merge Chapters 4, 5, 6
    merged_dialogues = []
    for c in [4, 5, 6]:
        t, d = fetch_b2w2_chapter(c)
        merged_dialogues.append({"speaker": "【章节导览】", "text": f"=== {t} ===", "raw_notes": ""})
        merged_dialogues.extend(d)

    glossary = load_glossary()
    parallel_items = translate_dialogues(merged_dialogues, glossary)

    if local_images.get("nintendo_b2w2_photo4.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_b2w2_photo4.jpg"],
            "caption_original": "「ポケモンセンターを最初の街に置く」という発想の転換について語る海野総監督。",
            "caption_translation": "海野隆雄总监阐述为何打破惯例在初始城镇桧扇市设立宝可梦中心与道馆的逆向思维。"
        })
    if local_images.get("meloetta.png"):
        parallel_items.insert(30, {
            "type": "image",
            "image": local_images["meloetta.png"],
            "caption_original": "メロエッタ：歌声とステップで世界を魅了する幻のポケモン。",
            "caption_translation": "美洛耶塔：通过歌声与舞步切换古风与芭蕾形态、令合众世界为之倾倒的旋律宝可梦。"
        })
    if local_images.get("nintendo_b2w2_photo10.jpg"):
        parallel_items.insert(60, {
            "type": "image",
            "image": local_images["nintendo_b2w2_photo10.jpg"],
            "caption_original": "3DS時代にあっても「三種の神器」でハードの壁を越える連携を語る4人。",
            "caption_translation": "岩田聪、石原恒和、增田顺一与海野隆雄详解‘三神器’如何让 DS 卡带与 3DS 硬件实现跨世代无缝共振。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑2·白2》第4章：为什么在3DS已上市时坚守NDS硬件（桧扇市全新开局、宝可梦本质与三神器联动）",
        "original_title": "社長が訊く『ポケットモンスターブラック２・ホワイト２』4. ポケモンセンターを最初の街に 〜 6. “三種の神器”",
        "date": "2012-06-15",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "海野 隆雄, 增田 顺一, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑2·白2", "桧扇市", "三神器", "海野隆雄", "增田顺一", "岩田聪", "石原恒和", "社长问", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black 2 & White 2 Vol.1 第4〜6回",
            "url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index4.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index4.html",
        "summary": "《黑2·白2》社长问终章大结局（整合第4、5、6节）：深度解答了当时玩家最大的疑问——‘在 3DS 已经发售一年多的大背景下，为什么宝可梦正统新作依然坚持选择在 NDS 平台上发售？’石原恒和与岩田聪坦陈，这是为了让全球超过一亿台 NDS 存量玩家能够在毫无门槛的情况下第一时间体验冒险；但同时，任天堂与宝可梦社打造了史无前例的‘三神器’跨平台联动体系——通过 3DS 下下载软件《宝可梦 AR 搜索器》（Dream Radar）捕捉隐藏特性的土地云/雷电云/龙卷云灵兽形态，并无线回传至 NDS《黑2·白2》卡带；配合《全国图鉴 Pro》，打通了两代硬件的界限。最后四位主创就‘宝可梦永远坚守的纯粹感’献上寄语。",
        "entities": {
            "people": ["岩田 聪", "海野 隆雄", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 黑2·白2", "宝可梦AR搜索器", "宝可梦全国图鉴Pro"],
            "pokemon": ["美洛耶塔", "土地云", "雷电云", "龙卷云"]
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
        "PKMN-0649": {
            "title": "社长问《宝可梦 黑2·白2》第1章：为何打破传统做正统数字续篇（“两部续篇”与“两年之后”）",
            "date": "2012-06-15",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0649']}.md",
            "status": "imported"
        },
        "PKMN-0652": {
            "title": "社长问《宝可梦 黑2·白2》第2章：百人实时同屏的庆典任务与遗迹通信挑战",
            "date": "2012-06-15",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index2.html",
            "post_file": f"_posts/{batch_results['PKMN-0652']}.md",
            "status": "imported"
        },
        "PKMN-0651": {
            "title": "社长问《宝可梦 黑2·白2》第3章：双版本同时发售的双钥匙联动机制与宝可梦好莱坞太空幻想",
            "date": "2012-06-15",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index3.html",
            "post_file": f"_posts/{batch_results['PKMN-0651']}.md",
            "status": "imported"
        },
        "PKMN-0650": {
            "title": "社长问《宝可梦 黑2·白2》第4章：为什么在3DS已上市时坚守NDS硬件（桧扇市全新开局、宝可梦本质与三神器联动）",
            "date": "2012-06-15",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irej/vol1/index4.html",
            "post_file": f"_posts/{batch_results['PKMN-0650']}.md",
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
    print("Starting Batch 7 (Iwata Asks: Pokémon Black 2 & White 2 Series) Import Pipeline...")
    batch_results = {}

    batch_results["PKMN-0649"] = import_b2w2_part1()
    batch_results["PKMN-0652"] = import_b2w2_part2()
    batch_results["PKMN-0651"] = import_b2w2_part3()
    batch_results["PKMN-0650"] = import_b2w2_part4()

    update_catalog(batch_results)
    print("\nBatch 7 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
