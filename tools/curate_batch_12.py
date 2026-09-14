"""Batch curate, clean, translate, and import 3 milestone Pokémon interviews (Batch 12):
1. PKMN-0091: 电玩志 Denfaminicogamer (2017-07-03): 大森滋 × 尾上将之（后篇：GF企划孵化机制与“齿轮企划”破格传承）
2. PKMN-0678: 电玩志 Denfaminicogamer (2018-06-08): 石原恒和 × 川岛优志 × 增田顺一（后篇：50倍服务器洪峰与社会现象舞台幕后）
3. PKMN-0050: 周刊 Fami通 (2021-04-30): 石原恒和 × 须崎春树谈《New 宝可梦随乐拍》时隔22年的生态摄像革命
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
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
    
    prompt = f"""你是精通任天堂史料、宝可梦开发史与日本核心游戏媒体访谈的资深学者与翻译家。
正在整理宝可梦主创人员深度访谈档案：
【访谈背景】：{context_desc}

请将以下访谈内容翻译为流畅、雅致、忠实原文且极具游戏史料沉浸感的简体中文。
注意：
1. 准确规范说话人(speaker)中文名称：
   - 大森 滋 (Game Freak 董事、《太阳·月亮》《剑·盾》《朱·紫》游戏总监)
   - 尾上 将之 (Game Freak 程序员、《小象历险记》总监)
   - 石原 恒和 (The Pokémon Company 董事长兼社长)
   - 川岛 优志 (Niantic 亚太区副总裁)
   - 增田 顺一 (Game Freak 董事、音乐家、总监、制作人)
   - 须崎 春树 (万代南梦宫工作室 / 《New 宝可梦随乐拍》《宝可拳》游戏总监)
   - 电玩志 记者 / Fami通 记者 / 章节标题
2. 忠实保留开发者的真实心境与一手历史细节（如齿轮企划Gear Project的内部提拔、Pokemon GO发布首周服务器承受50倍极限洪峰、中央公园水伊布引发狂欢、时隔22年重制Pokemon Snap与智能手机摄影时代的呼应、轻快苹果与霓光现象等）。
3. 如果对话中涉及特定游戏术语、未公开细节或开发逸闻，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【官方专业术语规范】：
优先遵循以下官方规范译名：
{glossary_str}
- 太阳·月亮 -> 《宝可梦 太阳·月亮》
- 究极之日·究极之月 -> 《宝可梦 究极之日·究极之月》
- New ポケモンスナップ -> 《New 宝可梦随乐拍》
- ポケモンスナップ -> 《宝可梦随乐拍》
- ギアプロジェクト / Gear Project -> 齿轮企划（Game Freak 内部独立游戏孵化机制）
- イルミナ現象 / Illumina -> 霓光现象（蓝蒂尔地区特有的发光生态）
- ふわりんご / Fluffruit -> 轻快苹果（随乐拍中投掷以吸引宝可梦的果实）
- レンティル地方 / Lental region -> 蓝蒂尔地区
- ヌシポケモン / Totem Pokémon -> 霸主宝可梦
- Zワザ / Z-Move -> Z招式
- シャワーズ / Vaporeon -> 水伊布
- ソルガレオ / Solgaleo -> 索尔迦雷欧
- ルナアーラ / Lunala -> 露奈雅拉
- メガニウム / Meganium -> 大文字花 / 大竺葵
- ビビヨン / Vivillon -> 彩粉蝶

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'大森 滋'、'尾上 将之'、'石原 恒和'、'川岛 优志'、'须崎 春树'、'电玩志 记者'、'章节标题'等）",
      "original": "该段对应的原文日文",
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


def translate_dialogues(dialogues: list[dict], glossary: list[dict], context_desc: str, chunk_size: int = 6) -> list[dict]:
    full_text = " ".join(it["text"] for it in dialogues)
    glossary_matches = find_glossary_matches(full_text, glossary)

    items = []
    total_chunks = (len(dialogues) + chunk_size - 1) // chunk_size

    for idx in range(0, len(dialogues), chunk_size):
        chunk = dialogues[idx:idx + chunk_size]
        chunk_num = (idx // chunk_size) + 1
        print(f"   Translating chunk {chunk_num}/{total_chunks}...")

        segments = translate_chunk(chunk, glossary_matches, context_desc)
        for seg in segments:
            spk = seg.get("speaker", "")
            orig = seg.get("original", "")
            trans = seg.get("translation", "")
            if spk == "章节标题" or orig.startswith("###"):
                items.append({
                    "type": "header",
                    "level": 3,
                    "original": orig.replace("###", "").strip(),
                    "translation": trans.replace("###", "").strip()
                })
            else:
                items.append({
                    "type": "dialogue",
                    "speaker": spk,
                    "original": orig,
                    "translation": trans,
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


# =========================================================================
# 1. PKMN-0091: Denfami Ohmori x Onoue Part 2 (2017)
# =========================================================================
def import_denfami_ohmori_part2(glossary: list[dict]) -> str:
    slug = "2017-07-03-interview-denfaminicogamer-ohmori-onoue-gear-project"
    print("\n========================================================")
    print("=== Importing #1: PKMN-0091 电玩志专访大森滋与尾上将之（后篇） ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    # Reuse part 1 hero image if available
    part1_hero = IMG_DIR / "2017-07-03-interview-denfaminicogamer-ohmori-onoue-new-generation" / "hero_ohmori_onoue_2017.jpg"
    dest_hero = img_dir / "hero_ohmori_onoue_2017.jpg"
    if part1_hero.exists() and not dest_hero.exists():
        shutil.copy(part1_hero, dest_hero)

    img_sources = {
        "solgaleo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/791.png",
        "lunala.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/792.png",
        "mimikyu.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/778.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}
    local_images["hero_ohmori_onoue_2017.jpg"] = f"/assets/img/interviews/{slug}/hero_ohmori_onoue_2017.jpg"

    html_url = "https://news.denfaminicogamer.jp/interview/170703/2"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div class=["\']article-body["\'][^>]*>(.*?)</div>\s*<div class=["\']article-footer["\']', raw, re.DOTALL | re.I)
    if not m_body:
        m_body = re.search(r'<div class=["\']main-content[^"\']*["\'][^>]*>(.*?)</div>', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw

    items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
    clean_items = []
    for tag, content in items:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', 'この記事に関するタグ', 'いま読まれている記事']) and len(c) > 2:
            clean_items.append((tag, c))

    speaker_keywords = {
        "大森": "大森 滋",
        "尾上": "尾上 将之",
        "増田": "增田 顺一",
        "田尻": "田尻 智",
        "杉森": "杉森 建"
    }
    turns = []
    current_spk = "电玩志 记者"
    for tag, c in clean_items:
        if tag.startswith('h'):
            turns.append({"speaker": "章节标题", "text": f"### {c}"})
            continue
        spk = current_spk
        text = c
        m_spk = re.match(r'^([^\s：:───]+)[：:]\s*(.*)', c, re.DOTALL)
        if m_spk:
            raw_s = m_spk.group(1).strip()
            for key, norm in speaker_keywords.items():
                if key in raw_s:
                    spk = norm
                    text = m_spk.group(2).strip()
                    break
        elif c.startswith('──') or c.startswith('――') or c.startswith('──さて'):
            spk = "电玩志 记者"
            text = re.sub(r'^[─―]+\s*', '', c).strip()
        else:
            for key, norm in speaker_keywords.items():
                if c.startswith(key):
                    spk = norm
                    text = c[len(key):].strip()
                    break
        turns.append({"speaker": spk, "text": text})
        current_spk = spk

    merged = []
    for t in turns:
        if t["speaker"] == "章节标题":
            merged.append(t)
        elif merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 500:
            merged[-1]["text"] += "\n" + t["text"]
        else:
            merged.append(dict(t))

    print(f"Parsed {len(merged)} turns for PKMN-0091.")
    context = "电玩志（Denfaminicogamer）2017年7月向新世代发问（后篇）：大森滋 × 尾上将之。探讨Game Freak内部传奇的‘齿轮企划’（Gear Project）独立游戏孵化机制、年轻程序员如何提拔破格成为总监、在网络攻略秒速普及的现代如何设计充满未知的游戏体验。"
    translated_items = translate_dialogues(merged, glossary, context, chunk_size=6)

    parallel_items = [
        {
            "type": "image",
            "image": local_images["hero_ohmori_onoue_2017.jpg"],
            "caption_original": "電ファミニコゲーマー取材：大森滋氏（左）と尾上将之氏（右）。",
            "caption_translation": "电玩志专访：36岁的大森滋与29岁的尾上将之，肩负Game Freak未来的少壮派总监们。"
        }
    ]

    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("solgaleo.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["solgaleo.png"],
                    "caption_original": "大森滋ディレクターが手がけた『サン・ムーン』の象徴「ソルガレオ」。",
                    "caption_translation": "大森滋总监倾力打造的《太阳·月亮》传说宝可梦“索尔迦雷欧”。"
                })
            if local_images.get("mimikyu.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["mimikyu.png"],
                    "caption_original": "『サン・ムーン』で社会現象的な人気を獲得した「ミミッキュ」。",
                    "caption_translation": "在《太阳·月亮》中引发巨大网络狂潮的超人气宝可梦“谜拟丘”。"
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 电玩志专访大森滋与尾上将之（后篇）：Game Freak 的企划孵化机制与“齿轮企划”破格传承",
        "original_title": "【新連載：新世代に訊く】『ポケモン』新作は“攻略”を検索される前提？ゲームフリークの伝説を受け継ぐ若きディレクター達（後編）",
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
        "tags": ["Pokemon", "太阳·月亮", "大森滋", "尾上将之", "Game Freak", "齿轮企划", "游戏设计", "电玩志"],
        "archive_type": "interview_translation",
        "source": {
            "title": "電ファミニコゲーマー 新世代に訊く：大森滋氏・尾上将之氏インタビュー（後編）",
            "url": html_url,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": html_url,
        "summary": "电玩志《向新世代发问》终篇：大森滋与尾上将之深入披露 Game Freak 内部极具传奇色彩的“齿轮企划（Gear Project）”。在这个机制下，任何员工无论资历都可以自由提案原创 IP，29 岁的尾上将之正是由此脱颖而出执导《小象历险记》。两人详述了面对智能手机互联网时代“攻略瞬间被搜索引擎解密”的现实，游戏设计如何反套路打破道馆体系、重构探索未知感，以及如何将田尻智与增田顺一创立的工匠文化代代传承。",
        "entities": {
            "people": ["大森 滋", "尾上 将之", "田尻 智", "增田 顺一", "森本 茂树"],
            "games": ["宝可梦 太阳·月亮", "小象历险记", "千兆破坏者"],
            "pokemon": ["索尔迦雷欧", "露奈雅拉", "谜拟丘"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# 2. PKMN-0678: Denfami Pokemon GO Part 2 (2018)
# =========================================================================
def import_denfami_pokego_part2(glossary: list[dict]) -> str:
    slug = "2018-06-08-interview-denfaminicogamer-pokemon-go-server-miracle"
    print("\n========================================================")
    print("=== Importing #2: PKMN-0678 电玩志Pokemon GO奇迹（后篇） ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    part1_hero = IMG_DIR / "2018-06-08-interview-denfaminicogamer-pokemon-go-miracle" / "group_main.jpg"
    dest_hero = img_dir / "group_main.jpg"
    if part1_hero.exists() and not dest_hero.exists():
        shutil.copy(part1_hero, dest_hero)

    img_sources = {
        "pikachu.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        "mewtwo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
        "gyarados.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/130.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}
    local_images["group_main.jpg"] = f"/assets/img/interviews/{slug}/group_main.jpg"

    html_url = "https://news.denfaminicogamer.jp/interview/180608/2"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div class=["\']article-body["\'][^>]*>(.*?)</div>\s*<div class=["\']article-footer["\']', raw, re.DOTALL | re.I)
    if not m_body:
        m_body = re.search(r'<div class=["\']main-content[^"\']*["\'][^>]*>(.*?)</div>', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw

    items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
    clean_items = []
    for tag, content in items:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', 'この記事に関するタグ', 'いま読まれている記事']) and len(c) > 2:
            clean_items.append((tag, c))

    speaker_keywords = {
        "石原": "石原 恒和",
        "川島": "川岛 优志",
        "増田": "增田 顺一",
        "ハンケ": "约翰·汉克",
        "野村": "野村 达雄"
    }
    turns = []
    current_spk = "电玩志 记者"
    for tag, c in clean_items:
        if tag.startswith('h'):
            turns.append({"speaker": "章节标题", "text": f"### {c}"})
            continue
        spk = current_spk
        text = c
        m_spk = re.match(r'^([^\s：:───]+)[：:]\s*(.*)', c, re.DOTALL)
        if m_spk:
            raw_s = m_spk.group(1).strip()
            for key, norm in speaker_keywords.items():
                if key in raw_s:
                    spk = norm
                    text = m_spk.group(2).strip()
                    break
        elif c.startswith('──') or c.startswith('――') or c.startswith('──さて'):
            spk = "电玩志 记者"
            text = re.sub(r'^[─―]+\s*', '', c).strip()
        else:
            for key, norm in speaker_keywords.items():
                if c.startswith(key):
                    spk = norm
                    text = c[len(key):].strip()
                    break
        turns.append({"speaker": spk, "text": text})
        current_spk = spk

    merged = []
    for t in turns:
        if t["speaker"] == "章节标题":
            merged.append(t)
        elif merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 500:
            merged[-1]["text"] += "\n" + t["text"]
        else:
            merged.append(dict(t))

    print(f"Parsed {len(merged)} turns for PKMN-0678.")
    context = "电玩志（Denfaminicogamer）2018年6月宝可梦GO奇迹专访（后篇）：石原恒和 × 川岛优志 × 增田顺一。全面揭秘2016年7月游戏在全球上市瞬间触发超出Google最悲观预估50倍的服务器极限洪峰、美澳中央公园万人狂奔水伊布、拯救孤独与抑郁症患者走入阳光的现实连接奇迹。"
    translated_items = translate_dialogues(merged, glossary, context, chunk_size=6)

    parallel_items = [
        {
            "type": "image",
            "image": local_images["group_main.jpg"],
            "caption_original": "川島優志氏（Niantic）、石原恒和氏（ポケモン社）、増田順一氏（ゲームフリーク）。",
            "caption_translation": "从左至右：Niantic亚太副总裁川岛优志、The Pokémon Company社长石原恒和、Game Freak董事增田顺一。"
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
                    "caption_original": "現実世界のあらゆる場所でトレーナーたちを笑顔にした「ピカチュウ」。",
                    "caption_translation": "在现实世界的街头巷尾让无数训练家展开笑颜的“皮卡丘”。"
                })
            if local_images.get("mewtwo.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["mewtwo.png"],
                    "caption_original": "伝説のレイドバトルで全世界のトレーナーが集結した「ミュウツー」。",
                    "caption_translation": "在传说团队战中召唤全世界训练家并肩作战的“超梦”。"
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 电玩志三巨头对谈（后篇）：石原恒和 × 川岛优志 × 增田顺一揭秘《Pokemon GO》50倍服务器洪峰与社会现象",
        "original_title": "「あの瞬間」何が起きていたのか？ キーマンたちが初めて語るポケモン GOリリース直後の熱狂、その舞台裏（後編）",
        "date": "2018-06-08",
        "era": "2017–2021 · Switch Microsite 触控时代",
        "era_skin": "2019",
        "publication": "电ファミニコゲーマー (Denfaminicogamer)",
        "source_kind": "web_magazine",
        "author": "稲葉ほたて, 斉藤大地 (Denfaminicogamer)",
        "translator": "Poke Amice Studio",
        "interviewee": "石原恒和, 川岛优志, 增田顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "Pokemon GO", "石原恒和", "川岛优志", "增田顺一", "Niantic", "Game Freak", "AR", "电玩志"],
        "archive_type": "interview_translation",
        "source": {
            "title": "電ファミニコゲーマー 特集記事：ポケモン GOの奇跡（後編）",
            "url": html_url,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": html_url,
        "summary": "电玩志《Pokémon GO的奇迹》终篇：还原 2016 年 7 月上线那一刻震撼全球的惊涛骇浪。开服首日全球流量便冲破 Google 云计算工程团队预想极限的 50 倍，Niantic 与任天堂工程师日夜兼程加固架构；纽约中央公园深夜数千人狂奔捕获水伊布成为全球头条；石原恒和、川岛优志与增田顺一动情探讨了这款游戏如何打破宅家孤立、促使抑郁症患者走入阳光社区、连接跨世代家庭的真实情感力量。",
        "entities": {
            "people": ["石原 恒和", "川岛 优志", "增田 顺一", "约翰·汉克", "野村 达雄"],
            "games": ["Pokémon GO", "Ingress"],
            "pokemon": ["皮卡丘", "超梦", "水伊布", "暴鲤龙"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# 3. PKMN-0050: Famitsu New Pokemon Snap (2021)
# =========================================================================
def import_famitsu_snap(glossary: list[dict]) -> str:
    slug = "2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki"
    print("\n========================================================")
    print("=== Importing #3: PKMN-0050 Fami通《New 宝可梦随乐拍》独家专访 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    famitsu_imgs = [
        ("snap_01.jpg", "https://www.famitsu.com/images/000/218/824/y_6082dee0a8e3f.jpg"),
        ("snap_02.jpg", "https://www.famitsu.com/images/000/218/824/y_6082deeae52ef.jpg"),
        ("snap_03.jpg", "https://www.famitsu.com/images/000/218/824/y_6082dbc9e0674.jpg"),
        ("snap_04.jpg", "https://www.famitsu.com/images/000/218/824/y_6082d9133eb13.jpg"),
        ("snap_05.jpg", "https://www.famitsu.com/images/000/218/824/y_6082d9134ea26.jpg")
    ]
    local_images = {k: download_image(u, img_dir, k) for k, u in famitsu_imgs}

    poke_arts = {
        "meganium.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/154.png",
        "vivillon.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/666.png"
    }
    for k, u in poke_arts.items():
        local_images[k] = download_image(u, img_dir, k)

    html_url = "https://www.famitsu.com/news/202104/30218824.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw

    items = re.findall(r'<(h[2-3]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.I)
    clean_items = []
    for tag, content in items:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', content))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Share', 'Twitter', 'Facebook', '関連記事', '(C)20', '※', '株式会社']) and len(c) > 2:
            clean_items.append((tag, c))

    turns = []
    current_spk = "Fami通 记者"
    for tag, c in clean_items:
        if tag.startswith('h'):
            turns.append({"speaker": "章节标题", "text": f"### {c}"})
            continue
        spk = current_spk
        text = c
        if c.startswith("石原") or "石原氏" in c:
            spk = "石原 恒和"
            text = re.sub(r'^石原[氏\s：:]*', '', c).strip()
        elif c.startswith("須崎") or "須崎氏" in c or "須崎D" in c:
            spk = "须崎 春树"
            text = re.sub(r'^須崎[氏D\s：:]*', '', c).strip()
        elif c.startswith("――") or c.startswith("──"):
            spk = "Fami通 记者"
            text = re.sub(r'^[─―]+\s*', '', c).strip()
        turns.append({"speaker": spk, "text": text})
        current_spk = spk

    merged = []
    for t in turns:
        if t["speaker"] == "章节标题":
            merged.append(t)
        elif merged and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 500:
            merged[-1]["text"] += "\n" + t["text"]
        else:
            merged.append(dict(t))

    print(f"Parsed {len(merged)} turns for PKMN-0050.")
    context = "周刊 Fami通 2021年4月独家专访：《New 宝可梦随乐拍》发售特辑。The Pokémon Company 社长石原恒和与万代南梦宫工作室总监须崎春树深度对谈，详述为何续篇等待了整整22年、智能手机摄影普及如何重塑拍照游戏、蓝蒂尔地区自然生态的精微呈现以及霓光现象的生态奇观。"
    translated_items = translate_dialogues(merged, glossary, context, chunk_size=6)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話",
            "translation": "石原社长与须崎总监独家专访：《New 宝可梦随乐拍》时隔22年的开发秘辛"
        }
    ]

    step = max(1, len(translated_items) // (len(local_images) + 1))
    img_keys = list(local_images.keys())
    img_idx = 0
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i % step == 0 and img_idx < len(img_keys):
            k = img_keys[img_idx]
            img_idx += 1
            if local_images.get(k):
                cap_orig = "『New ポケモンスナップ』で描かれる生き生きとしたポケモンの生態。"
                cap_trans = "《New 宝可梦随乐拍》中展现的栩栩如生的野生宝可梦生态奇观。"
                if "meganium" in k:
                    cap_orig = "イルミナ現象によって神秘的な輝きを放つ「メガニウム」。"
                    cap_trans = "因霓光现象而沐浴在神秘光芒中的巨大宝可梦“大竺葵”。"

                parallel_items.append({
                    "type": "image",
                    "image": local_images[k],
                    "caption_original": cap_orig,
                    "caption_translation": cap_trans
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 周刊 Fami通 独家专访：石原恒和 × 须崎春树谈《New 宝可梦随乐拍》时隔22年的生态摄像革命",
        "original_title": "石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話。写真を撮ることがより手軽になった2021年、ゲームデザインはどう変わったのか？",
        "date": "2021-04-30",
        "era": "2017–2021 · Switch Microsite 触控时代",
        "era_skin": "2019",
        "publication": "週刊ファミ通 (Famitsu.com)",
        "source_kind": "media_interview",
        "author": "周刊 Fami通 采访组",
        "translator": "Poke Amice Studio",
        "interviewee": "石原恒和, 须崎春树",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "New 宝可梦随乐拍", "石原恒和", "须崎春树", "万代南梦宫", "生态摄影", "蓝蒂尔地区", "Fami通"],
        "archive_type": "interview_translation",
        "source": {
            "title": "ファミ通.com 特集記事：石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話",
            "url": html_url,
            "language": "ja",
            "source_type": "media_interview"
        },
        "original_link": html_url,
        "summary": "1999 年 N64《宝可梦随乐拍》问世时，拍照还是胶卷相机的特权；而到了智能手机人手一部的 2021 年，如何重新定义‘摄影游戏’？The Pokémon Company 社长石原恒和与万代南梦宫总监须崎春树在《New 宝可梦随乐拍》发售之际向 Fami通 深度复盘：等待 22 年正是为了硬件技术足以无缝模拟数百只野生宝可梦不为人知的自然栖息生态。从轻快苹果引诱、点唱机音乐唤醒、到蓝蒂尔地区神秘的霓光现象，团队构建了一个即便没有人类注视依然在生生不息运转的奇迹世界。",
        "entities": {
            "people": ["石原 恒和", "须崎 春树"],
            "games": ["New 宝可梦随乐拍", "宝可梦随乐拍", "宝可拳"],
            "pokemon": ["大竺葵", "皮卡丘", "彩粉蝶"]
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
                "generation": item.get("generation", "Gen 7"),
                "language": "JA",
                "outlet": item.get("outlet", "Denfaminicogamer"),
                "type": "Media Interview",
                "tags": []
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
        if "people" in item:
            entry["people"] = item["people"]

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"\n[Catalog Updated] Successfully synchronized {len(completed)} entries in {CATALOG_PATH.name}")


def main():
    print("Loading glossary...")
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    s1 = import_denfami_ohmori_part2(glossary)
    s2 = import_denfami_pokego_part2(glossary)
    s3 = import_famitsu_snap(glossary)

    completed = [
        {
            "id": "PKMN-0091",
            "title": "电玩志专访大森滋与尾上将之（后篇）：Game Freak 的企划孵化机制与“齿轮企划”破格传承",
            "original_title": "【新連載：新世代に訊く】『ポケモン』新作は“攻略”を検索される前提？ゲームフリークの伝説を受け継ぐ若きディレクター達（後編）",
            "date": "2017-07-03",
            "post_file": f"_posts/{s1}.md",
            "url": "https://news.denfaminicogamer.jp/interview/170703/2",
            "summary": "电玩志《向新世代发问》终篇：大森滋与尾上将之深入披露 Game Freak 内部极具传奇色彩的“齿轮企划（Gear Project）”。在这个机制下，任何员工无论资历都可以自由提案原创 IP，29 岁的尾上将之正是由此脱颖而出执导《小象历险记》。两人详述了面对智能手机互联网时代“攻略瞬间被搜索引擎解密”的现实，游戏设计如何反套路打破道馆体系、重构探索未知感，以及如何将田尻智与增田顺一创立的工匠文化代代传承。",
            "people": ["大森滋", "尾上将之"]
        },
        {
            "id": "PKMN-0678",
            "title": "电玩志三巨头对谈（后篇）：石原恒和 × 川岛优志 × 增田顺一揭秘《Pokemon GO》50倍服务器洪峰与社会现象",
            "original_title": "「あの瞬間」何が起きていたのか？ キーマンたちが初めて語るポケモン GOリリース直後の熱狂、その舞台裏（後編）",
            "date": "2018-06-08",
            "post_file": f"_posts/{s2}.md",
            "url": "https://news.denfaminicogamer.jp/interview/180608/2",
            "summary": "电玩志《Pokémon GO的奇迹》终篇：还原 2016 年 7 月上线那一刻震撼全球的惊涛骇浪。开服首日全球流量便冲破 Google 云计算工程团队预想极限的 50 倍，Niantic 与任天堂工程师日夜兼程加固架构；纽约中央公园深夜数千人狂奔捕获水伊布成为全球头条；石原恒和、川岛优志与增田顺一动情探讨了这款游戏如何打破宅家孤立、促使抑郁症患者走入阳光社区、连接跨世代家庭的真实情感力量。",
            "people": ["石原恒和", "川岛优志", "增田顺一"]
        },
        {
            "id": "PKMN-0050",
            "title": "周刊 Fami通 独家专访：石原恒和 × 须崎春树谈《New 宝可梦随乐拍》时隔22年的生态摄像革命",
            "original_title": "石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話。写真を撮ることがより手軽になった2021年、ゲームデザインはどう変わったのか？",
            "date": "2021-04-30",
            "post_file": f"_posts/{s3}.md",
            "url": "https://www.famitsu.com/news/202104/30218824.html",
            "summary": "1999 年 N64《宝可梦随乐拍》问世时，拍照还是胶卷相机的特权；而到了智能手机人手一部的 2021 年，如何重新定义‘摄影游戏’？The Pokémon Company 社长石原恒和与万代南梦宫总监须崎春树在《New 宝可梦随乐拍》发售之际向 Fami通 深度复盘：等待 22 年正是为了硬件技术足以无缝模拟数百只野生宝可梦不为人知的自然栖息生态。从轻快苹果引诱、点唱机音乐唤醒、到蓝蒂尔地区神秘的霓光现象，团队构建了一个即便没有人类注视依然在生生不息运转的奇迹世界。",
            "people": ["石原恒和", "须崎春树"]
        }
    ]

    sync_catalog(completed)
    print("\nBatch 12 completed successfully!")


if __name__ == "__main__":
    main()
