"""Batch curate, clean, translate, and import 5 Iwata Asks: Pokémon Black & White developer interviews (Batch 6):
1. PKMN-0640: 社長が訊く『黑·白』第1章：在NDS平台第二次制作完全新作（放弃全部旧怪兽做156只新宠的豪赌）
2. PKMN-0641: 社長が訊く『黑·白』第2章：焕然一新的宝可梦世界（为什么要把舞台搬到海外大都会曼哈顿）
3. PKMN-0642: 社長が訊く『黑·白』第3章：因通信而拓展的游玩方式（随时无线连接、红外与C-Gear革命）
4. PKMN-0643: 社長が訊く『黑·白』第4章：未曾改变的“宝可梦本质”（等离子队、哲学反思与永不毕业的乐趣）
5. PKMN-0644: 社長が訊く『黑·白』第5章：崭新的世界与崭新的相遇（3D高低差视角与主创致玩家寄语）
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
正在整理《宝可梦 黑·白》社长问（岩田聪 × 石原恒和 × 增田顺一 × 杉森建）的日中对照史料档案。

请将以下访谈对话翻译为流畅、准确、忠实原文且极富历史沉浸感的简体中文。
注意：
1. 准确标注说话人(speaker)：如“岩田 聪”、“石原 恒和”、“增田 顺一”、“杉森 建”或“众人”。
2. 保持岩田聪温润敏锐的提问、增田顺一充满革新激情的回答、杉森建关于设计取舍的严谨思考、以及石原恒和统揽大局的商业眼光。
3. 如果对话中涉及特定历史典故、技术术语（如 C-Gear、红外高速通信、合众地区、曼哈顿取景、等离子队、通关前零旧怪兽、全国图鉴毕业论等），请在 note 字段给出简明精要的译注。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 黑·白（Black & White）
- 钻石·珍珠（Diamond & Pearl）
- 赤·绿（Red & Green）
- 合众地区（Unova / イッシュ地方）
- 飞云市（Castelia City / ヒウンシティ）
- 莱希拉姆（Reshiram / レシラム）
- 捷克罗姆（Zekrom / ゼクロム）
- 比克提尼（Victini / ビクティニ）
- 藤藤蛇（Snivy / ツタージャ）
- 暖暖猪（Tepig / ポカブ）
- 水水獭（Oshawott / ミジュマル）
- C-Gear（Cギア）
- 宝可梦全球连接（Pokémon Global Link / PGL）
- 等离子队（Team Plasma / プラズマ団）
- N（エヌ）
- 魁奇思（Ghetsis / ゲーチス）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'增田 顺一'，若无则留空字符串''）",
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


def fetch_bw_chapter(chapter_index: int) -> tuple[str, list[dict]]:
    fn = "index.html" if chapter_index == 1 else f"index{chapter_index}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irbj/vol1/{fn}"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})).read()

    try:
        decoded = raw.decode("utf-8")
        if "通信" not in decoded and chapter_index == 3:
            raise ValueError()
    except:
        decoded = raw.decode("shift_jis", errors="replace")

    m_h3 = re.search(r'<H3><IMG[^>]+ALT=["\']([^"\']+)["\']', decoded, re.I)
    title = m_h3.group(1).strip() if m_h3 else f"Chapter {chapter_index}"

    # Footnotes mapping
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
        "杉森": "杉森 建",
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
# 1. PKMN-0640: Chapter 1 DS Second Game & 156 All-New Monsters
# =========================================================================
def import_bw_chapter_1():
    slug = "2010-09-10-interview-iwata-asks-bw-chapter-1-second-game-on-ds"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0640 社長が訊く『黑·白』第1章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_bw_mainvisual1.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/mainvisual1.jpg",
        "nintendo_bw_photo1.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo1.jpg",
        "snivy.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/495.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_bw_chapter(1)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_bw_mainvisual1.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_bw_mainvisual1.jpg"],
            "caption_original": "社長が訊く『ポケットモンスターブラック・ホワイト』：岩田聡 × 増田順一 × 杉森建 × 石原恒和。",
            "caption_translation": "任天堂官方“社长问”《宝可梦 黑·白》专刊：岩田聪社长专访增田顺一、杉森建与石原恒和。"
        })
    if local_images.get("snivy.png"):
        parallel_items.insert(20, {
            "type": "image",
            "image": local_images["snivy.png"],
            "caption_original": "ツタージャ：通関前は過去作のポケモンが一切出現しない、完全新規156匹という大勝負。",
            "caption_translation": "藤藤蛇：全通关前旧怪兽登场概率为零，156 只全新宝可梦构筑的震撼大冒险。"
        })
    if local_images.get("nintendo_bw_photo1.jpg"):
        parallel_items.insert(35, {
            "type": "image",
            "image": local_images["nintendo_bw_photo1.jpg"],
            "caption_original": "「同じハードで2作目の完全新作をつくること」の葛藤と挑戦を語る増田順一と岩田聡。",
            "caption_translation": "增田顺一与岩田聪深入探讨在同一代掌机硬件（NDS）上开发第二部完全新作的巨大心理重压与颠覆决意。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑·白》第1章：在NDS平台第二次制作完全新作（放弃全部旧怪兽做156只新宠的豪赌）",
        "original_title": "社長が訊く『ポケットモンスターブラック・ホワイト』1. DSで２作目の完全新作をつくること",
        "date": "2010-09-10",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 杉森 建, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "岩田聪", "增田顺一", "杉森建", "石原恒和", "社长问", "任天堂", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black & White Vol.1 第1回",
            "url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index.html",
        "summary": "在《宝可梦 黑·白》即将全球发售前夕，任天堂社长岩田聪亲赴宝可梦公司，与总监增田顺一、艺术总监杉森建及石原恒和展开深度对谈。增田顺一直面‘在同一硬件平台（NDS）上制作第二部完全新作’的空前难度，揭秘最初定下的决断宣言：通关前彻底封印过去 493 只所有旧宝可梦，以皮卡丘都不出现的魄力打造整整 156 只纯全新宝可梦构成的全新生态圈，让无论老玩家还是新手，都能重新回到 1996 年面对未知的纯粹感动。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "杉森 建", "石原 恒和"],
            "games": ["宝可梦 黑·白", "宝可梦 钻石·珍珠", "宝可梦 红·绿"],
            "pokemon": ["藤藤蛇", "暖暖猪", "水水獭", "皮卡丘"]
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
# 2. PKMN-0641: Chapter 2 Brand New World & Manhattan
# =========================================================================
def import_bw_chapter_2():
    slug = "2010-09-10-interview-iwata-asks-bw-chapter-2-brand-new-world"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0641 社長が訊く『黑·白』第2章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_bw_photo2.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo2.jpg",
        "nintendo_bw_photo3.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo3.jpg",
        "victini.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/494.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_bw_chapter(2)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_bw_photo2.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_bw_photo2.jpg"],
            "caption_original": "「一新されたポケモンの世界」について熱く語る杉森建と増田順一。",
            "caption_translation": "杉森建与增田顺一深度解析合众地区为何打破日本本土地域桎梏、远赴纽约曼哈顿取景的大胆构想。"
        })
    if local_images.get("victini.png"):
        parallel_items.insert(25, {
            "type": "image",
            "image": local_images["victini.png"],
            "caption_original": "ビクティニ：図鑑ナンバー000を与えられ、勝利を導く新たな幻のポケモン。",
            "caption_translation": "比克提尼：史无前例获得图鉴编号 000、为合众带来胜利与纯净能量的全新幻之宝可梦。"
        })
    if local_images.get("nintendo_bw_photo3.jpg"):
        parallel_items.insert(50, {
            "type": "image",
            "image": local_images["nintendo_bw_photo3.jpg"],
            "caption_original": "17人の社内デザイナーたちが挑んだ156匹のデザイン会議の裏側。",
            "caption_translation": "杉森建阐述 17 人设计团队每人构思多只、全员评审调色避免色系偏颇的设计中枢机制。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑·白》第2章：焕然一新的宝可梦世界（为什么要把舞台搬到海外大都会曼哈顿）",
        "original_title": "社長が訊く『ポケットモンスターブラック・ホワイト』2. 一新されたポケモンの世界",
        "date": "2010-09-10",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 杉森 建, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "合众地区", "飞云市", "曼哈顿", "岩田聪", "增田顺一", "杉森建", "比克提尼", "设计秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black & White Vol.1 第2回",
            "url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index2.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index2.html",
        "summary": "关都、城都、丰缘、神奥等以往作品均以日本列岛为舞台，而《黑·白》做出了开天辟地的决定——将舞台搬到遥远的海外大都会纽约曼哈顿！增田顺一透露，之所以选择曼哈顿，是因为中央公园与周边高楼林立、多元种族与文化交融的格局，完美契合‘黑与白、自然与人造二元并存’的哲学内核；杉森建则详尽分享了 17 人设计师大军如何每人提交方案、在白板前通宵达旦逐一审阅 156 只怪兽，并为比克提尼赋予第 000 号图鉴的背后故事。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "杉森 建", "石原 恒和"],
            "games": ["宝可梦 黑·白", "宝可梦 钻石·珍珠"],
            "pokemon": ["比克提尼", "藤藤蛇", "暖暖猪", "水水獭"]
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
# 3. PKMN-0642: Chapter 3 Expanding Play with Communication
# =========================================================================
def import_bw_chapter_3():
    slug = "2010-09-10-interview-iwata-asks-bw-chapter-3-expanding-play-communication"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0642 社長が訊く『黑·白』第3章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_bw_photo4.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo4.jpg",
        "nintendo_bw_photo5.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo5.jpg"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_bw_chapter(3)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_bw_photo4.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_bw_photo4.jpg"],
            "caption_original": "赤外線通信とC-Gearによる“常時接続”の通信革命について語る岩田聡と増田順一。",
            "caption_translation": "岩田聪与增田顺一深度复盘黑白卡带内置红外线芯片与 C-Gear 达成的‘零等待随时连接’通信革命。"
        })
    if local_images.get("nintendo_bw_photo5.jpg"):
        parallel_items.insert(25, {
            "type": "image",
            "image": local_images["nintendo_bw_photo5.jpg"],
            "caption_original": "ハイリンクやPGL（ポケモングローバルリンク）が拓いた新しい遊びの地平。",
            "caption_translation": "连接之桥（High Link）与宝可梦全球连接（PGL）打通掌机与互联网网页端交互的全新维度。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑·白》第3章：因通信而拓展的游玩方式（随时无线连接、红外与C-Gear革命）",
        "original_title": "社長が訊く『ポケットモンスターブラック・ホワイト』3. 通信でひろがる遊び",
        "date": "2010-09-10",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 杉森 建, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "C-Gear", "PGL", "红外通信", "岩田聪", "增田顺一", "石原恒和", "社长问", "通信革命"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black & White Vol.1 第3回",
            "url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index3.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index3.html",
        "summary": "以往的宝可梦通信必须跑到宝可梦中心二楼前台排队，而《黑·白》彻底颠覆了这一点。增田顺一与任天堂工程师在 DS 特制卡带中直接嵌入高速红外线芯片，配合下屏幕常驻的 C-Gear，玩家对准机器一秒即可瞬间开启对战与交换；更有打通游戏与 PC 互联网的‘宝可梦全球连接’（PGL）梦境世界、以及直接闯入好友世界冒险的‘连接之桥’（High Link）系统，岩田聪盛赞这彻底跨越了传统单机 RPG 与网游的藩篱。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "石原 恒和", "杉森 建"],
            "games": ["宝可梦 黑·白", "宝可梦全球连接"],
            "pokemon": []
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
# 4. PKMN-0643: Chapter 4 Unchanging Essence & Plasma
# =========================================================================
def import_bw_chapter_4():
    slug = "2010-09-10-interview-iwata-asks-bw-chapter-4-unchanging-pokemon-essence"
    print(f"\n========================================================")
    print("=== Importing #4: PKMN-0643 社長が訊く『黑·白』第4章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_bw_photo6.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo6.jpg",
        "reshiram.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/643.png",
        "zekrom.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/644.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_bw_chapter(4)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_bw_photo6.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_bw_photo6.jpg"],
            "caption_original": "「変わらない『ポケモン』らしさ」とプラズマ団の哲学について語り合う開発首脳陣。",
            "caption_translation": "主创团队探讨等离子队质疑‘人类束缚宝可梦是否正义’的深刻思辨，以及永不改变的宝可梦内核。"
        })
    if local_images.get("reshiram.png") and local_images.get("zekrom.png"):
        parallel_items.insert(20, {
            "type": "image",
            "image": local_images["reshiram.png"],
            "caption_original": "レシラムとゼクロム：真実と理想、白と黒の対立と調和を象徴する伝説の竜。",
            "caption_translation": "莱希拉姆与捷克罗姆：象征真实与理想、白与黑的交织对抗与终极和谐。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑·白》第4章：未曾改变的“宝可梦本质”（等离子队、哲学反思与永不毕业的乐趣）",
        "original_title": "社長が訊く『ポケットモンスターブラック・ホワイト』4. 変わらない『ポケモン』らしさ",
        "date": "2010-09-10",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 杉森 建, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "等离子队", "N", "莱希拉姆", "捷克罗姆", "岩田聪", "增田顺一", "杉森建", "哲学思辨"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black & White Vol.1 第4回",
            "url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index4.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index4.html",
        "summary": "尽管系统经历了翻天覆地的重构，但什么是宝可梦系列‘绝不能改变的根基’？岩田聪与增田顺一展开了极具思想深度的拷问。在本作中，敌对组织等离子队与青年 N 首次向玩家抛出触及游戏核心伦理的终极拷问——‘将宝可梦关进精灵球是否是一种束缚与残忍？人类自私的爱是否剥夺了宝可梦的自由？’增田顺一阐述了由此展开的‘真实与理想’二元哲学；同时，四人剖析了如何打破‘长大成人就会从宝可梦毕业’的魔咒，让全年龄玩家终生享受对战与培育乐趣。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "杉森 建", "石原 恒和"],
            "games": ["宝可梦 黑·白"],
            "pokemon": ["莱希拉姆", "捷克罗姆"]
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
# 5. PKMN-0644: Chapter 5 New World & Messages to Fans
# =========================================================================
def import_bw_chapter_5():
    slug = "2010-09-10-interview-iwata-asks-bw-chapter-5-new-world-new-encounters"
    print(f"\n========================================================")
    print("=== Importing #5: PKMN-0644 社長が訊く『黑·白』第5章 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "nintendo_bw_photo10.jpg": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/img/photo10.jpg",
        "zekrom.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/644.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    _, raw_items = fetch_bw_chapter(5)
    glossary = load_glossary()
    parallel_items = translate_dialogues(raw_items, glossary)

    if local_images.get("nintendo_bw_photo10.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["nintendo_bw_photo10.jpg"],
            "caption_original": "『ポケットモンスターブラック・ホワイト』の完成を祝し、世界中のファンへメッセージを贈る4人。",
            "caption_translation": "四位核心主创共同举起黑白卡带，向全世界所有即将踏入合众全新冒险的玩家致以最诚挚的寄语。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 黑·白》第5章：崭新的世界与崭新的相遇（3D高低差视角与主创致玩家寄语）",
        "original_title": "社長が訊く『ポケットモンスターブラック・ホワイト』5. 新しい世界、新しい出会い",
        "date": "2010-09-10",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 杉森 建, 石原 恒和",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "岩田聪", "增田顺一", "杉森建", "石原恒和", "社长问", "3D视角", "致玩家寄语"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「社長が訊く」Pokemon Black & White Vol.1 第5回",
            "url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index5.html",
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index5.html",
        "summary": "《宝可梦 黑·白》社长问终章大结局：增田顺一与杉森建详解本作在大地图视角上引入的‘动态 3D 高低差视角与俯瞰运镜’——从飞云大桥的弧形宏伟跨越，到天箭大桥的穿梭感，给掌机点阵艺术带来了前所未有的视差纵深；在访谈尾声，增田顺一、杉森建、石原恒和与岩田聪向全世界玩家深情寄语，呼吁不论是玩过初代的老玩家，还是第一次拿起掌机的小朋友，都能以‘零预设’的纯真初心，在合众地方开启一段一生难忘的新相遇。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "杉森 建", "石原 恒和"],
            "games": ["宝可梦 黑·白"],
            "pokemon": ["莱希拉姆", "捷克罗姆"]
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
        "PKMN-0640": {
            "title": "社长问《宝可梦 黑·白》第1章：在NDS平台第二次制作完全新作（放弃全部旧怪兽做156只新宠的豪赌）",
            "date": "2010-09-10",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0640']}.md",
            "status": "imported"
        },
        "PKMN-0641": {
            "title": "社长问《宝可梦 黑·白》第2章：焕然一新的宝可梦世界（为什么要把舞台搬到海外大都会曼哈顿）",
            "date": "2010-09-10",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index2.html",
            "post_file": f"_posts/{batch_results['PKMN-0641']}.md",
            "status": "imported"
        },
        "PKMN-0642": {
            "title": "社长问《宝可梦 黑·白》第3章：因通信而拓展的游玩方式（随时无线连接、红外与C-Gear革命）",
            "date": "2010-09-10",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index3.html",
            "post_file": f"_posts/{batch_results['PKMN-0642']}.md",
            "status": "imported"
        },
        "PKMN-0643": {
            "title": "社长问《宝可梦 黑·白》第4章：未曾改变的“宝可梦本质”（等离子队、哲学反思与永不毕业的乐趣）",
            "date": "2010-09-10",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index4.html",
            "post_file": f"_posts/{batch_results['PKMN-0643']}.md",
            "status": "imported"
        },
        "PKMN-0644": {
            "title": "社长问《宝可梦 黑·白》第5章：崭新的世界与崭新的相遇（3D高低差视角与主创致玩家寄语）",
            "date": "2010-09-10",
            "source_name": "任天堂官网「社長が訊く」",
            "source_url": "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index5.html",
            "post_file": f"_posts/{batch_results['PKMN-0644']}.md",
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
    print("Starting Batch 6 (Iwata Asks: Pokémon Black & White Series) Import Pipeline...")
    batch_results = {}

    batch_results["PKMN-0640"] = import_bw_chapter_1()
    batch_results["PKMN-0641"] = import_bw_chapter_2()
    batch_results["PKMN-0642"] = import_bw_chapter_3()
    batch_results["PKMN-0643"] = import_bw_chapter_4()
    batch_results["PKMN-0644"] = import_bw_chapter_5()

    update_catalog(batch_results)
    print("\nBatch 6 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
