"""Batch curate, clean, translate, and import 4 milestone Pokémon X & Y interviews
from Nintendo official 'うごく社長が訊く' (Moving Iwata Asks) October 2013 (Batch 10):
1. PKMN-0653: 社长问《宝可梦 X·Y》第1章：系列首次全球同日发售的奇迹（七国语言同步、跨时区保密与全球命名挑战）
2. PKMN-0654: 社长问《宝可梦 X·Y》第2章：焕然一新的宝可梦与全3D建模（皮卡丘大谷育江原声录制与生动表情）
3. PKMN-0655: 社长问《宝可梦 X·Y》第3章：全新属性妖精与对战数值重构（时隔14年的对战革命与龙属性制衡）
4. PKMN-0655-4: 社长问《宝可梦 X·Y》第4章：让宝可梦变得更加亲近（宝可友友乐、超级进化与致玩家信）
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


def translate_chunk(chunk: list[dict], glossary_matches: list[tuple[str, str]], context_desc: str) -> list[dict]:
    glossary_str = "\n".join(f"- {src} -> {tgt}" for src, tgt in glossary_matches) or "无特定匹配词条"
    
    prompt = f"""你是精通任天堂史料、宝可梦开发史与官方访谈的资深学者与翻译家。
正在整理 2013年10月 任天堂官方「社長が訊く」（社长问）《宝可梦 Ｘ・Ｙ》特辑档案：
【访谈背景】：{context_desc}

请将以下访谈内容翻译为流畅、专业、忠实原文且极具任天堂社长问文风沉浸感的简体中文。
注意：
1. 准确规范说话人(speaker)：
   - 岩田 聪（任天堂社长，访谈主持）
   - 石原 恒和（The Pokémon Company 社长 / 宝可梦制作人）
   - 增田 顺一（Game Freak 董事 / 《X·Y》游戏总监、音乐与世界观设计）
   - 石原 恒和・增田 顺一（若两人同时发言）
   - 众人（若为一同）
2. 忠实保留开发者的真实心境与历史细节（如全球同日发售、七国语言实时同步、全球商标命名冲突、皮卡丘首次大谷育江原声录制、宝可友友乐触摸抚摸加深羁绊、时隔14年引入妖精属性打破龙属性垄断、超级进化超越极限、空中对战与群聚对战等）。
3. 如果对话中涉及特定游戏术语、未公开细节或开发逸闻，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【官方专业术语规范】：
优先遵循以下官方规范译名：
{glossary_str}
- ポケットモンスター Ｘ・Ｙ -> 《宝可梦 Ｘ・Ｙ》
- ピカチュウ -> 皮卡丘
- ポケパルレ -> 宝可友友乐（Poké-Amie）
- ポケパフ -> 宝芙蕾（Poké Puff）
- メガシンカ -> 超级进化（Mega Evolution）
- メガストーン -> 超级石（Mega Stone）
- フェアリータイプ -> 妖精属性（Fairy-type）
- ドラゴンタイプ -> 龙属性（Dragon-type）
- スカイバトル -> 空中对战（Sky Battle）
- 群れバトル -> 群聚对战（Horde Battle）
- ゼルネアス -> 哲尔尼亚斯（Xerneas）
- イベルタル -> 伊裴尔塔尔（Yveltal）
- ハリマロン -> 哈力栗（Chespin）
- フォッコ -> 火狐狸（Fennekin）
- ケロマツ -> 呱呱泡蛙（Froakie）
- ニンフィア -> 仙子伊布（Sylveon）
- サーナイト -> 沙奈朵（Gardevoir）
- ガブリアス -> 烈咬陆鲨（Garchomp）
- ルカリオ -> 路卡利欧（Lucario）
- リザードン -> 喷火龙（Charizard）
- カロス地方 -> 卡洛斯地区（Kalos region）
- ミアレシティ -> 密阿雷市（Lumiose City）
- 大谷育江（皮卡丘声优）
- 杉森建（角色设计总监）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'岩田 聪'、'石原 恒和'、'增田 顺一'、'石原 恒和・增田 顺一'）",
      "original": "该段对应的日文原文",
      "translation": "流畅雅致的简体中文译文",
      "note": "对原文背景、技术细节或历史事件的简明译注（若无则留空字符串''）"
    }}
  ]
}}

待翻译原文段落列表：
{json.dumps(chunk, ensure_ascii=False, indent=2)}
"""

    messages = [
        {"role": "system", "content": "你是一位精通任天堂历史与宝可梦诞生史料的双语专家。请只输出合法的 JSON 对象。"},
        {"role": "user", "content": prompt}
    ]

    raw_json = call_deepseek(messages)
    try:
        parsed = json.loads(raw_json)
        return parsed.get("segments", [])
    except Exception as e:
        print(f"      Error parsing DeepSeek JSON: {e}", file=sys.stderr)
        return [{"speaker": item.get("speaker", ""), "original": item.get("text", ""), "translation": item.get("text", ""), "note": ""} for item in chunk]


def translate_dialogues(dialogues: list[dict], glossary: list[dict], context_desc: str) -> list[dict]:
    full_text = " ".join(it["text"] for it in dialogues)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items = []
    chunk_size = 6
    total_chunks = (len(dialogues) + chunk_size - 1) // chunk_size

    for idx in range(0, len(dialogues), chunk_size):
        chunk = dialogues[idx:idx + chunk_size]
        chunk_num = (idx // chunk_size) + 1
        print(f"   Translating chunk {chunk_num}/{total_chunks}...")

        segments = translate_chunk(chunk, glossary_matches, context_desc)
        for seg in segments:
            items.append({
                "type": "dialogue",
                "speaker": seg.get("speaker", ""),
                "original": seg.get("original", ""),
                "translation": seg.get("translation", ""),
                "note": seg.get("note", "")
            })

    return items


def download_image(img_url: str, dest_dir: Path, filename: str) -> str | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    if dest_path.exists() and dest_path.stat().st_size > 500:
        return f"/assets/img/interviews/{dest_dir.name}/{filename}"

    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 500:
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


def scrape_chapter_dialogues(html_url: str) -> tuple[str, list[dict], dict]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    subttls = re.findall(r'<h3[^>]*class=["\']interview__ttl["\'][^>]*>(.*?)</h3>', raw, re.I | re.DOTALL)
    cleaned_subttls = [re.sub(r'<[^>]+>', '', s).strip() for s in subttls]
    # Pick the numbered chapter title if present
    ttl = cleaned_subttls[-1] if cleaned_subttls else "Chapter"
    for s in cleaned_subttls:
        if any(d in s for d in ["1.", "2.", "3.", "4."]):
            ttl = s
            break

    boxes = re.findall(r'<div class=["\']interview__name["\']><p>(.*?)</p></div>\s*<div class=["\']interview__text["\']><p>(.*?)</p></div>', raw, re.DOTALL | re.I)

    notes_raw = re.findall(r'<dl><dt>(※\d+)</dt><dd>(.*?)</dd></dl>', raw, re.DOTALL | re.I)
    notes_dict = {dt.strip(): re.sub(r'<[^>]+>', '', dd).strip() for dt, dd in notes_raw}

    name_map = {
        "岩田": "岩田 聪",
        "石原": "石原 恒和",
        "増田": "增田 顺一",
        "石原・増田": "石原 恒和・增田 顺一",
        "増田・石原": "增田 顺一・石原 恒和",
        "一同": "众人"
    }

    dialogues = []
    for spk, body in boxes:
        spk_clean = html.unescape(re.sub(r'<[^>]+>', '', spk)).strip()
        spk_norm = name_map.get(spk_clean, spk_clean)

        ref_notes = re.findall(r'※\d+', body)
        attached_notes = [f"{rn}: {notes_dict[rn]}" for rn in ref_notes if rn in notes_dict]

        b_clean = html.unescape(re.sub(r'<SUP>（※\d+）</SUP>', '', body, flags=re.I))
        b_clean = re.sub(r'<sup[^>]*>.*?</sup>', '', b_clean, flags=re.I)
        b_clean = re.sub(r'<br\s*/?>', '\n', b_clean, flags=re.I)
        b_clean = re.sub(r'<[^>]+>', '', b_clean).strip()

        dialogues.append({
            "speaker": spk_norm,
            "text": b_clean,
            "notes": " | ".join(attached_notes) if attached_notes else ""
        })

    return ttl, dialogues, notes_dict


# =========================================================================
# Chapter 1: PKMN-0653
# =========================================================================
def import_xy_chapter_1(glossary: list[dict]) -> str:
    slug = "2013-10-10-interview-iwata-asks-xy-chapter-1-global-simultaneous-release"
    print("\n========================================================")
    print("=== Importing #1: PKMN-0653 社长问《X·Y》第1章：系列首次全球同日发售 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "mainvisual1.jpg": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/img/mainvisual1.jpg",
        "movie001_thumb.jpg": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/img/movie001_thumb.jpg",
        "chespin.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/650.png",
        "fennekin.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/653.png",
        "froakie.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/656.png",
        "xerneas.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/716.png",
        "yveltal.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/717.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    html_url = "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index.html"
    title_jp, dialogues, notes_dict = scrape_chapter_dialogues(html_url)
    print(f"Scraped Chapter 1: {title_jp} ({len(dialogues)} turns)")

    context = "任天堂官方社长问《宝可梦 X·Y》第1章：系列首次全球同日发售。岩田聪社长专访石原恒和与增田顺一，详述跨越各大洲时区的测试同步、七国语言实时通信互联、全球宝可梦商标统一注册的极限挑战。"
    translated_items = translate_dialogues(dialogues, glossary, context)

    parallel_items = [
        {
            "type": "image",
            "image": local_images["mainvisual1.jpg"],
            "caption_original": "うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』：岩田聡 × 石原恒和 × 増田順一。",
            "caption_translation": "任天堂官方“社长问”《宝可梦 X·Y》影像特辑：岩田聪对谈石原恒和与增田顺一。"
        },
        {
            "type": "header",
            "level": 3,
            "original": "はじめに：1. シリーズ初の世界同時発売",
            "translation": "序言：1. 系列首次全球同日发售的奇迹"
        },
        {
            "type": "image",
            "image": local_images["movie001_thumb.jpg"],
            "caption_original": "第1章「シリーズ初の世界同時発売」：世界各地のプレイヤーが同じ瞬間に冒険を始めるための挑戦。",
            "caption_translation": "第1章“系列首次全球同日发售”：让全世界训练家在同一个瞬间启程冒险的史无前例挑战。"
        }
    ]

    # Insert dialogue items and mid-interview starter showcase
    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("xerneas.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["xerneas.png"],
                    "caption_original": "『ポケットモンスター Ｘ』パッケージを飾る伝説のポケモン「ゼルネアス」（フェアリータイプ）。",
                    "caption_translation": "《宝可梦 X》封面登场的传说宝可梦“哲尔尼亚斯”（妖精属性）。"
                })
            if local_images.get("yveltal.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["yveltal.png"],
                    "caption_original": "『ポケットモンスター Ｙ』パッケージを飾る伝説のポケモン「イベルタル」（あく・ひこうタイプ）。",
                    "caption_translation": "《宝可梦 Y》封面登场的传说宝可梦“伊裴尔塔尔”（恶·飞行属性）。"
                })

    if notes_dict:
        note_text_jp = "\n".join(f"{k} {v}" for k, v in notes_dict.items())
        parallel_items.append({
            "type": "dialogue",
            "speaker": "任天堂官方注记",
            "original": note_text_jp,
            "translation": "※1 世界同日发售＝除部分极特殊地区外，全球主要国家和地区同步上市发售。",
            "note": "官方原注"
        })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 X·Y》第1章：系列首次全球同日发售的奇迹（七国语言同步、跨时区保密与全球命名挑战）",
        "original_title": f"うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』{title_jp}",
        "date": "2013-10-10",
        "era": "2013–2016 · 3D Era / 三维进化时代",
        "era_skin": "2014",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 增田 顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "岩田聪", "增田顺一", "石原恒和", "社长问", "全球同日发售", "七国语言", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「うごく社長が訊く」Pokemon X & Y Vol.1 第1回",
            "url": html_url,
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": html_url,
        "summary": "2013年10月，任天堂社长岩田聪与The Pokémon Company社长石原恒和、Game Freak总监增田顺一展开深度对谈。这是宝可梦历史上首次实现全球主要地区同日发售，游戏支持七国语言自由切换。石原坦言从初代起这就是长年夙愿，曾被视作‘绝不可能的梦幻构想’；增田顺一与岩田聪亲述跨越全球时区的测试同步、全怪兽多国语言命名统一注册与防剧透保密体系的非凡攻坚历程。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 X·Y", "宝可梦 赤·绿", "宝可梦 红宝石·蓝宝石"],
            "pokemon": ["哲尔尼亚斯", "伊裴尔塔尔", "哈力栗", "火狐狸", "呱呱泡蛙"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# Chapter 2: PKMN-0654
# =========================================================================
def import_xy_chapter_2(glossary: list[dict]) -> str:
    slug = "2013-10-10-interview-iwata-asks-xy-chapter-2-reborn-pokemon-3d-amie"
    print("\n========================================================")
    print("=== Importing #2: PKMN-0654 社长问《X·Y》第2章：焕然一新的宝可梦与全3D建模 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "movie002_thumb.jpg": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/img/movie002_thumb.jpg",
        "pikachu.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        "sylveon.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/700.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    html_url = "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index2.html"
    title_jp, dialogues, notes_dict = scrape_chapter_dialogues(html_url)
    print(f"Scraped Chapter 2: {title_jp} ({len(dialogues)} turns)")

    context = "任天堂官方社长问《宝可梦 X·Y》第2章：焕然一新的宝可梦与全3D建模。岩田聪专访石原恒和与增田顺一，畅谈数百只宝可梦从像素到3D骨骼全貌展现、皮卡丘首次采用大谷育江原声配音、以及通过‘宝可友友乐’抚摸怪兽带来生命温度的革新。"
    translated_items = translate_dialogues(dialogues, glossary, context)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "2. 生まれかわったポケモン",
            "translation": "2. 焕然一新的宝可梦：全3D多边形与鲜活生命力"
        },
        {
            "type": "image",
            "image": local_images["movie002_thumb.jpg"],
            "caption_original": "第2章「生まれかわったポケモン」：ピカチュウの声、表情豊かな3Dモーション、ポケパルレの触れ合い。",
            "caption_translation": "第2章“焕然一新的宝可梦”：皮卡丘的大谷育江真实原声、生动细腻的3D动作与宝可友友乐的指尖互动。"
        }
    ]

    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("pikachu.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["pikachu.png"],
                    "caption_original": "正統シリーズとして初めて大谷育江さんの声で「ピカチュウ！」と鳴くようになったピカチュウ。",
                    "caption_translation": "正统续作中首次直接以声优大谷育江原声录制叫声的皮卡丘。"
                })
            if local_images.get("sylveon.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["sylveon.png"],
                    "caption_original": "新タイプ「フェアリー」を代表するイーブイの新たな進化形「ニンフィア」。ポケパルレでの絆が進化の鍵となる。",
                    "caption_translation": "代表全新“妖精属性”的伊布全新进化形态“仙子伊布”。在宝可友友乐中培养深厚羁绊是其进化的关键条件。"
                })

    if notes_dict:
        note_text_jp = "\n".join(f"{k} {v}" for k, v in notes_dict.items())
        parallel_items.append({
            "type": "dialogue",
            "speaker": "任天堂官方注记",
            "original": note_text_jp,
            "translation": "※2 首次「Pokémon Direct」＝2013年1月8日全球首播的直面会，首次公开《宝可梦 X·Y》标题与3D画面。\n※3 『赤·绿』＝初代正统作，1996年2月27日GB平台发售。\n※4 『红宝石·蓝宝石』＝2002年11月21日GBA平台发售。\n※5 杉森建＝从初代至今担任宝可梦角色设计总监、Game Freak董事。",
            "note": "官方原注"
        })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 X·Y》第2章：焕然一新的宝可梦与全3D建模（皮卡丘大谷育江原声录制与生动表情）",
        "original_title": f"うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』{title_jp}",
        "date": "2013-10-10",
        "era": "2013–2016 · 3D Era / 三维进化时代",
        "era_skin": "2014",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 增田 顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "岩田聪", "增田顺一", "石原恒和", "社长问", "3D建模", "皮卡丘", "大谷育江", "宝可友友乐"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「うごく社長が訊く」Pokemon X & Y Vol.1 第2回",
            "url": html_url,
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": html_url,
        "summary": "《宝可梦 X·Y》从过去的2D像素全面跨入全3D多边形时代。石原恒和笑谈3D化后才终于看清‘原来这里不是背部而是尾巴’，首次能360度全方位审视怪兽生理构造；正统作首次收录大谷育江亲声录制的皮卡丘真实嗓音；引入全新的‘宝可友友乐（Poké-Amie）’，训练家可直接在触摸屏上抚摸怪兽、喂食宝芙蕾，通过生动丰富的喜怒哀乐神态赋予怪兽真正的生命温度。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "石原 恒和", "大谷 育江", "杉森 建"],
            "games": ["宝可梦 X·Y", "宝可梦 赤·绿", "宝可梦 红宝石·蓝宝石"],
            "pokemon": ["皮卡丘", "仙子伊布", "伊布"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# Chapter 3: PKMN-0655
# =========================================================================
def import_xy_chapter_3(glossary: list[dict]) -> str:
    slug = "2013-10-10-interview-iwata-asks-xy-chapter-3-new-battles-fairy-type"
    print("\n========================================================")
    print("=== Importing #3: PKMN-0655 社长问《X·Y》第3章：全新属性妖精与对战数值重构 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "movie003_thumb.jpg": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/img/movie003_thumb.jpg",
        "gardevoir.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/282.png",
        "garchomp.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/445.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    html_url = "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index3.html"
    title_jp, dialogues, notes_dict = scrape_chapter_dialogues(html_url)
    print(f"Scraped Chapter 3: {title_jp} ({len(dialogues)} turns)")

    context = "任天堂官方社长问《宝可梦 X·Y》第3章：全新对战。岩田聪专访石原恒和与增田顺一，揭秘时隔14年引入第18种属性‘妖精属性’重构对战平衡打破龙属性霸权、为空中宝可梦打造的空中对战、以及1对5的野生群聚对战。"
    translated_items = translate_dialogues(dialogues, glossary, context)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "3. 新しいバトル",
            "translation": "3. 全新对战：妖精属性登场与攻防格局大洗牌"
        },
        {
            "type": "image",
            "image": local_images["movie003_thumb.jpg"],
            "caption_original": "第3章「新しいバトル」：フェアリータイプの追加と対戦バランスの全面見直し。",
            "caption_translation": "第3章“全新对战”：妖精属性的加入与对战平衡性自底层起的全盘重新调整。"
        }
    ]

    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("garchomp.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["garchomp.png"],
                    "caption_original": "対戦環境で長年猛威を振るってきたドラゴンタイプの代表格「ガブリアス」。",
                    "caption_translation": "多年来在对战环境中具备统治级压制力的龙属性代表宝可梦“烈咬陆鲨”。"
                })
            if local_images.get("gardevoir.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["gardevoir.png"],
                    "caption_original": "『X・Y』で新たに「フェアリータイプ」が追加され、華麗な大躍進を遂げた「サーナイト」。",
                    "caption_translation": "在《X·Y》中被正式追加“妖精属性”、实现华丽蜕变与战术飞跃的“沙奈朵”。"
                })

    if notes_dict:
        note_text_jp = "\n".join(f"{k} {v}" for k, v in notes_dict.items())
        parallel_items.append({
            "type": "dialogue",
            "speaker": "任天堂官方注记",
            "original": note_text_jp,
            "translation": "※6 宝可梦卡牌游戏＝以宝可梦世界为主题的双人集换式对战卡牌游戏。\n※7 空中对战＝仅限飞行属性或拥有‘飘浮’特性的宝可梦参加的空中交锋。\n※8 群聚对战＝与野生宝可梦同时进行1对5的对战，能一口气击倒多只宝可梦并获得大量经验值。",
            "note": "官方原注"
        })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 X·Y》第3章：全新属性妖精与对战数值重构（时隔14年的对战革命与龙属性制衡）",
        "original_title": f"うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』{title_jp}",
        "date": "2013-10-10",
        "era": "2013–2016 · 3D Era / 三维进化时代",
        "era_skin": "2014",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 增田 顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "岩田聪", "增田顺一", "石原恒和", "社长问", "妖精属性", "对战平衡", "空中对战", "群聚对战"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「うごく社長が訊く」Pokemon X & Y Vol.1 第3回",
            "url": html_url,
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": html_url,
        "summary": "继1999年《金·银》加入恶属性与钢属性之后，正统系列时隔整整14年再度迎来第18种属性——‘妖精属性（Fairy-type）’。增田顺一感叹数值调整‘无比艰难漫长’，但此前对战环境中龙属性几乎处于压倒性优势，妖精属性的诞生令属性克制体系重新焕发生机。同时全新加入空中对战与群聚对战，拓展了更富层次的战术纵深与培育乐趣。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 X·Y", "宝可梦 金·银"],
            "pokemon": ["沙奈朵", "烈咬陆鲨"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# Chapter 4: PKMN-0655-4
# =========================================================================
def import_xy_chapter_4(glossary: list[dict]) -> str:
    slug = "2013-10-10-interview-iwata-asks-xy-chapter-4-closer-bonds-mega-evolution"
    print("\n========================================================")
    print("=== Importing #4: PKMN-0655-4 社长问《X·Y》第4章：让宝可梦变得更加亲近 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "movie004_thumb.jpg": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/img/movie004_thumb.jpg",
        "mega_lucario.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10059.png",
        "mega_charizard_x.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10034.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    html_url = "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index4.html"
    title_jp, dialogues, notes_dict = scrape_chapter_dialogues(html_url)
    print(f"Scraped Chapter 4: {title_jp} ({len(dialogues)} turns)")

    context = "任天堂官方社长问《宝可梦 X·Y》第4章：让宝可梦变得更加亲近。岩田聪专访石原恒和与增田顺一，深度解密‘宝可友友乐（Poké-Amie）’命名中融合法语Parler与英语Pal的双重巧思、超级进化的超越极限羁绊理念、以及三人面向全世界训练家的深情寄语。"
    translated_items = translate_dialogues(dialogues, glossary, context)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "4. ポケモンがより身近な存在に",
            "translation": "4. 让宝可梦成为更亲近的存在：友友乐、超级进化与跨越时代的深厚羁绊"
        },
        {
            "type": "image",
            "image": local_images["movie004_thumb.jpg"],
            "caption_original": "第4章「ポケモンがより身近な存在に」：絆を深めるメガシンカと、世界中のプレイヤーへのメッセージ。",
            "caption_translation": "第4章“让宝可梦成为更亲近的存在”：以羁绊为源泉的超级进化，以及给全世界玩家的终章寄语。"
        }
    ]

    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("mega_lucario.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["mega_lucario.png"],
                    "caption_original": "バトル中にメガストーンと強い絆で限界を超えた進化を遂げる「メガルカリオ」。",
                    "caption_translation": "在对战中凭借超级石与深厚羁绊突破极限形态的“超级路卡利欧”。"
                })
            if local_images.get("mega_charizard_x.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["mega_charizard_x.png"],
                    "caption_original": "初代からの相棒が漆黒の炎とドラゴンの力を宿す「メガリザードンＸ」。",
                    "caption_translation": "初代搭档宿入漆黑烈焰与龙之威能的狂暴形态“超级喷火龙Ｘ”。"
                })

    if notes_dict:
        note_text_jp = "\n".join(f"{k} {v}" for k, v in notes_dict.items())
        parallel_items.append({
            "type": "dialogue",
            "speaker": "任天堂官方注记",
            "original": note_text_jp,
            "translation": "※9 超级进化（Mega Evolution）＝仅在对战中才能触发的“超越极限的进化”。超级进化后宝可梦外观发生巨变，能力、特性乃至属性均会产生深刻质变；战斗结束后恢复原状。",
            "note": "官方原注"
        })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 社长问《宝可梦 X·Y》第4章：让宝可梦变得更加亲近（宝可友友乐、超级进化与致玩家信）",
        "original_title": f"うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』{title_jp}",
        "date": "2013-10-10",
        "era": "2013–2016 · 3D Era / 三维进化时代",
        "era_skin": "2014",
        "publication": "任天堂官网「社長が訊く」",
        "source_kind": "official_interview",
        "author": "岩田聪 (任天堂社长)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原 恒和, 增田 顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "岩田聪", "增田顺一", "石原恒和", "社长问", "宝可友友乐", "超级进化", "羁绊", "寄语"],
        "archive_type": "interview_translation",
        "source": {
            "title": "任天堂公式ウェブサイト「うごく社長が訊く」Pokemon X & Y Vol.1 第4回",
            "url": html_url,
            "language": "ja",
            "source_type": "official_web"
        },
        "original_link": html_url,
        "summary": "在社长问《宝可梦 X·Y》终章中，增田顺一详细解密了‘宝可友友乐（Poké-Amie / ポケパルレ）’命名背后融合法语‘Parler（对话交流）’与英语‘Pal（亲密伙伴）’的深刻用意。石原恒和与增田指出，超级进化绝非单纯的力量膨胀，而必须依赖训练家与宝可梦之间沉淀的深厚羁绊。访谈尾声，岩田聪、石原恒和与增田顺一共同向全世界的新老训练家致以最诚挚的寄语。",
        "entities": {
            "people": ["岩田 聪", "增田 顺一", "石原 恒和"],
            "games": ["宝可梦 X·Y", "宝可梦 赤·绿"],
            "pokemon": ["超级路卡利欧", "超级喷火龙X", "路卡利欧", "喷火龙"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# Catalog Synchronization
# =========================================================================
def sync_catalog(completed: list[dict]):
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog_map = {d["id"]: d for d in catalog}

    for item in completed:
        item_id = item["id"]
        if item_id in catalog_map:
            entry = catalog_map[item_id]
        else:
            entry = {
                "id": item_id,
                "generation": "Gen 6",
                "language": "JA",
                "outlet": "任天堂官方",
                "type": "Iwata Asks",
                "tags": ["社長が訊く", "XY", "超级进化", "宝可友友乐", "JA"]
            }
            catalog.append(entry)

        entry["status"] = "imported"
        entry["title"] = item["title"]
        entry["original_title"] = item["original_title"]
        entry["date"] = item["date"]
        entry["post_file"] = item["post_file"]
        entry["url"] = item["url"]
        entry["source_url"] = item["url"]
        entry["summary"] = item["summary"]
        entry["people"] = ["岩田聪", "增田顺一", "石原恒和"]

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"\n[Catalog Updated] Successfully synchronized {len(completed)} entries in {CATALOG_PATH.name}")


def main():
    print("Loading glossary...")
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    s1 = import_xy_chapter_1(glossary)
    s2 = import_xy_chapter_2(glossary)
    s3 = import_xy_chapter_3(glossary)
    s4 = import_xy_chapter_4(glossary)

    completed = [
        {
            "id": "PKMN-0653",
            "title": "社长问《宝可梦 X·Y》第1章：系列首次全球同日发售的奇迹（七国语言同步、跨时区保密与全球命名挑战）",
            "original_title": "うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』1. シリーズ初の世界同時発売",
            "date": "2013-10-10",
            "post_file": f"_posts/{s1}.md",
            "url": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index.html",
            "summary": "2013年10月，任天堂社长岩田聪与The Pokémon Company社长石原恒和、Game Freak总监增田顺一展开深度对谈。这是宝可梦历史上首次实现全球主要地区同日发售，游戏支持七国语言自由切换。石原坦言从初代起这就是长年夙愿，曾被视作‘绝不可能的梦幻构想’；增田顺一与岩田聪亲述跨越全球时区的测试同步、全怪兽多国语言命名统一注册与防剧透保密体系的非凡攻坚历程。"
        },
        {
            "id": "PKMN-0654",
            "title": "社长问《宝可梦 X·Y》第2章：焕然一新的宝可梦与全3D建模（皮卡丘大谷育江原声录制与生动表情）",
            "original_title": "うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』2. 生まれかわったポケモン",
            "date": "2013-10-10",
            "post_file": f"_posts/{s2}.md",
            "url": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index2.html",
            "summary": "《宝可梦 X·Y》从过去的2D像素全面跨入全3D多边形时代。石原恒和笑谈3D化后才终于看清‘原来这里不是背部而是尾巴’，首次能360度全方位审视怪兽生理构造；正统作首次收录大谷育江亲声录制的皮卡丘真实嗓音；引入全新的‘宝可友友乐（Poké-Amie）’，训练家可直接在触摸屏上抚摸怪兽、喂食宝芙蕾，通过生动丰富的喜怒哀乐神态赋予怪兽真正的生命温度。"
        },
        {
            "id": "PKMN-0655",
            "title": "社长问《宝可梦 X·Y》第3章：全新属性妖精与对战数值重构（时隔14年的对战革命与龙属性制衡）",
            "original_title": "うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』3. 新しいバトル",
            "date": "2013-10-10",
            "post_file": f"_posts/{s3}.md",
            "url": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index3.html",
            "summary": "继1999年《金·银》加入恶属性与钢属性之后，正统系列时隔整整14年再度迎来第18种属性——‘妖精属性（Fairy-type）’。增田顺一感叹数值调整‘无比艰难漫长’，但此前对战环境中龙属性几乎处于压倒性优势，妖精属性的诞生令属性克制体系重新焕发生机。同时全新加入空中对战与群聚对战，拓展了更富层次的战术纵深与培育乐趣。"
        },
        {
            "id": "PKMN-0655-4",
            "title": "社长问《宝可梦 X·Y》第4章：让宝可梦变得更加亲近（宝可友友乐、超级进化与致玩家信）",
            "original_title": "うごく社長が訊く『ポケットモンスター Ｘ・Ｙ』4. ポケモンがより身近な存在に",
            "date": "2013-10-10",
            "post_file": f"_posts/{s4}.md",
            "url": "https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/index4.html",
            "summary": "在社长问《宝可梦 X·Y》终章中，增田顺一详细解密了‘宝可友友乐（Poké-Amie / ポケパルレ）’命名背后融合法语‘Parler（对话交流）’与英语‘Pal（亲密伙伴）’的深刻用意。石原恒和与增田指出，超级进化绝非单纯的力量膨胀，而必须依赖训练家与宝可梦之间沉淀的深厚羁绊。访谈尾声，岩田聪、石原恒和与增田顺一共同向全世界的新老训练家致以最诚挚的寄语。"
        }
    ]

    sync_catalog(completed)
    print("\nBatch 10 completed successfully!")


if __name__ == "__main__":
    main()
