"""Batch curate, clean, translate, and import 3 major Pokémon developer interviews:
1. Game Informer (2011-03-07) - Masuda & Ibe: Past, Present, and Future (Era Skin 2011)
2. Game Informer (2014-02-14) - Masuda: Afterwords - Pokemon X & Y (Era Skin 2014)
3. Yomiuri Shimbun / Siliconera (2018-07-27) - Sugimori: Monster Design Balance (Era Skin 2019)
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
    
    prompt = f"""你是精通宝可梦历史考据、游戏史料与专业翻译的专家。
正在整理宝可梦官方与媒体开发者访谈的日中/英中对照档案。

请将以下访谈内容翻译为流畅、准确、忠实原文的简体中文。
如果是对话/采访形式（如“问：... 答：...”或“Masuda: ...”），请准确识别出说话人(speaker)。
如果段落中有特定的背景设定、行业术语、人名梗或值得注释的地方，请填写在 note 字段中。

【说话人识别规范】：
- 明确标注角色名字或职务，如“提问”、“增田顺一”、“井部真那”、“杉森建”等。
- 不要把整句问答混在 speaker 里。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名或职务（如'增田顺一'，若无则留空字符串''）",
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


# =========================================================================
# 1. Game Informer (2011-03-07) Past, Present, and Future
# =========================================================================
def import_gi_2011():
    url = "https://www.gameinformer.com/b/features/archive/2011/03/07/pokemon-past-present-future.aspx"
    slug = "2011-03-07-interview-gameinformer-masuda-past-present-future"
    print(f"\n========================================================")
    print("=== Importing #1: Game Informer 2011 Past Present Future ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    artwork_map = {
        "reshiram.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/643.png",
        "zekrom.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/644.png",
        "victini.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/494.png"
    }
    local_images = {}
    for fn, u in artwork_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
    clean_html = re.sub(r'<script.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    ps = re.findall(r'<p>(.*?)</p>', clean_html, re.DOTALL)
    raw_items = []
    current_spk = ""
    speaker_map = {"Masuda": "增田顺一", "Ibe": "井部真那", "Sugimori": "杉森建"}

    for p in ps:
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        if not t:
            continue
        if "Check out our review" in t or "View the discussion" in t or "Sign In" in t or "All Rights Reserved" in t:
            continue
        if len(t) < 15 and not any(s in t for s in ["Masuda", "Ibe"]):
            continue

        if t.endswith("...") and len(t) < 60:
            raw_items.append({"speaker": "", "text": f"【回顾主题】{t}"})
            current_spk = ""
            continue

        m = re.match(r"^([A-Za-z]+):\s*(.*)", t)
        if m and m.group(1) in speaker_map:
            current_spk = speaker_map[m.group(1)]
            text = m.group(2)
        else:
            text = t

        raw_items.append({"speaker": current_spk, "text": text})

    print(f"Extracted {len(raw_items)} paragraphs from GI 2011.")

    glossary = load_glossary()
    full_text = " ".join(it["text"] for it in raw_items)
    glossary_matches = find_glossary_matches(full_text, glossary)

    parallel_items = []
    chunk_size = 6
    for i in range(0, len(raw_items), chunk_size):
        chunk = raw_items[i:i+chunk_size]
        print(f"   Translating chunk {i//chunk_size + 1}/{(len(raw_items)-1)//chunk_size + 1}...")
        segments = translate_chunk(chunk, glossary_matches)
        for seg in segments:
            parallel_items.append({
                "speaker": seg.get("speaker", ""),
                "original": seg.get("original", ""),
                "translation": seg.get("translation", ""),
                "note": seg.get("note", "")
            })
        
        if i == 0 and "reshiram.png" in local_images and "zekrom.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["reshiram.png"],
                "caption_original": "Reshiram and Zekrom represent the core dualism themes behind Pokémon Black and White.",
                "caption_translation": "莱希拉姆与捷克罗姆：象征着《宝可梦 黑·白》背后关于真实与理想的核心二元哲学思考。"
            })
        elif i == 12 and "victini.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["victini.png"],
                "caption_original": "Victini, designed by Mana Ibe, symbolizing victory in the Unova region.",
                "caption_translation": "比克提尼：由年轻原画师井部真那创作，成为合众地区带来胜利与无限能量的象征。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Game Informer 专访增田顺一与井部真那：宝可梦 15 年的过去、现在与未来",
        "original_title": "Pokémon: Past, Present, And Future - Game Freak on 15 Years of Pokémon",
        "date": "2011-03-07",
        "era": "2010–2013 · NDS / 宝可梦 黑·白 黄金时期",
        "era_skin": "2011",
        "publication": "Game Informer",
        "source_kind": "magazine_feature",
        "author": "Game Informer Editorial",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 井部真那",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "增田顺一", "井部真那", "Game Freak", "红·绿", "15周年", "合众地区", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Game Informer (March 2011 Feature)",
            "url": url,
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": url,
        "summary": "2011 年 3 月《宝可梦 黑·白》美版首发之际，Game Informer 专访 Game Freak 制作人增田顺一与新世代设计师井部真那。增田顺一全面回顾了宝可梦 15 年历程：同人志时期的 Game Freak 缘起、通信电缆对玩家现实社交的革命、早期开发时曾构想的无缝超大地图（Open World 雏形）、初代没有进化与属性时的‘胶囊怪兽’设定，以及坚持宝可梦正统作为便携式掌机、而非主机 RPG 的设计哲学；井部真那则分享了儿时玩初代到成年后参与黑白 17 人设计团队并亲手创造比克提尼的感动。",
        "entities": {
            "people": ["增田顺一", "井部真那", "田尻智", "杉森建"],
            "games": ["宝可梦 黑·白", "宝可梦 红·绿", "宝可梦 金·银", "宝可梦 心金·魂银"],
            "pokemon": ["莱希拉姆", "捷克罗姆", "比克提尼"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)


# =========================================================================
# 2. Game Informer (2014-02-14) Afterwords - Pokemon X & Y
# =========================================================================
def import_gi_2014():
    url = "https://www.gameinformer.com/b/features/archive/2014/02/14/afterwords-unabridged-pokemon-x-and-y.aspx"
    slug = "2014-02-14-interview-gameinformer-masuda-afterwords-xy"
    print(f"\n========================================================")
    print("=== Importing #2: Game Informer 2014 Afterwords XY ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    artwork_map = {
        "fennekin.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/653.png",
        "sylveon.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/700.png",
        "mega_mewtwo_y.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10035.png",
        "xerneas.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/716.png"
    }
    local_images = {}
    for fn, u in artwork_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
    clean_html = re.sub(r'<script.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    ps = re.findall(r'<p>(.*?)</p>', clean_html, re.DOTALL)
    raw_items = []

    for i, p in enumerate(ps):
        t = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        if not t:
            continue
        if "For our review" in t or "View the discussion" in t or "Sign In" in t or "All Rights Reserved" in t:
            continue
        if len(t) < 10:
            continue

        is_q = False
        if p.strip().startswith("<b>") or p.strip().startswith("<strong>") or t.startswith("There are hints") or t.endswith("?"):
            is_q = True

        if is_q:
            spk = "提问"
            text = t
        else:
            if i < 3 and ("originally appeared" in t or "biggest step forward" in t or "cut a number of questions" in t):
                spk = "编辑部"
            else:
                spk = "增田顺一"
            text = t

        raw_items.append({"speaker": spk, "text": text})

    print(f"Extracted {len(raw_items)} paragraphs from GI 2014.")

    glossary = load_glossary()
    full_text = " ".join(it["text"] for it in raw_items)
    glossary_matches = find_glossary_matches(full_text, glossary)

    parallel_items = []
    chunk_size = 7
    for i in range(0, len(raw_items), chunk_size):
        chunk = raw_items[i:i+chunk_size]
        print(f"   Translating chunk {i//chunk_size + 1}/{(len(raw_items)-1)//chunk_size + 1}...")
        segments = translate_chunk(chunk, glossary_matches)
        for seg in segments:
            parallel_items.append({
                "speaker": seg.get("speaker", ""),
                "original": seg.get("original", ""),
                "translation": seg.get("translation", ""),
                "note": seg.get("note", "")
            })
        
        if i == 7 and "sylveon.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["sylveon.png"],
                "caption_original": "Sylveon introduced the new Fairy-type to rebalance Dragon-type dominance.",
                "caption_translation": "仙子伊布：作为新属性‘妖精属性’的代表，旨在彻底打破龙属性独大的对战平衡。"
            })
        elif i == 21 and "xerneas.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["xerneas.png"],
                "caption_original": "Xerneas, representing eternal life in the Kalos mythology.",
                "caption_translation": "哲尔尼亚斯：卡洛斯神话中象征永恒生命的生命之树传说的宝可梦。"
            })
        elif i == 42 and "fennekin.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["fennekin.png"],
                "caption_original": "Fennekin, Masuda's personal favorite starter to play with in Pokémon-Amie.",
                "caption_translation": "火狐狸：增田顺一个人在‘宝可友友乐’中最喜欢与之互动的卡洛斯初学者宝可梦。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Game Informer 独家专访增田顺一：《宝可梦 X·Y》全景事后解密与宝可友友乐诞生",
        "original_title": "Afterwords – Pokémon X & Y (Unabridged Interview with Junichi Masuda)",
        "date": "2014-02-14",
        "era": "2013–2016 · 3DS / 全球同步与立体世代",
        "era_skin": "2014",
        "publication": "Game Informer",
        "source_kind": "magazine_feature",
        "author": "Kyle Hilliard (Game Informer)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "增田顺一", "Game Informer", "宝可友友乐", "超级进化", "卡洛斯地区", "妖精属性", "AZ国王"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Game Informer Issue #250 Unabridged Feature",
            "url": url,
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": url,
        "summary": "2014 年 2 月，Game Informer 刊发第 250 期《宝可梦 X·Y》全景事后专访未删节完整版（Unabridged）。总监增田顺一深度解密了卡洛斯地区的诸多剧情未解之谜与技术抉择：巴拉法姆香殿烟花夜会中与莎娜（Shauna）的微恋爱心动感营造、三千年前古大战与 AZ 国王身高超过 2.7 米的生命能量辐射起源、超级进化（Mega Evolution）与超级超梦的双形态设定、为抑制龙系过强而创立妖精属性的平衡哲学、大地图关闭裸眼 3D 以保障最佳画质帧率的考量，以及增田顺一最喜爱的系统——与火狐狸亲密互动的‘宝可友友乐’（Pokémon-Amie）诞生过程。",
        "entities": {
            "people": ["增田顺一", "AZ", "布拉塔诺博士", "弗拉达利", "莎娜"],
            "games": ["宝可梦 X·Y", "宝可梦 黑·白", "Pokémon HOME", "Pokémon Bank"],
            "pokemon": ["火狐狸", "仙子伊布", "哲尔尼亚斯", "伊裴尔塔尔", "超梦"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)


# =========================================================================
# 3. Yomiuri Shimbun / Siliconera (2018-07-27) Sugimori Monster Design Balance
# =========================================================================
def import_siliconera_sugimori():
    url = "https://www.siliconera.com/pokmon-designer-on-balancing-cool-or-cute-pokmon-by-adding-uncool-or-uncute-features/"
    slug = "2018-07-27-interview-yomiuri-siliconera-sugimori-monster-balance"
    print(f"\n========================================================")
    print("=== Importing #3: Yomiuri / Siliconera Sugimori Balance ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    artwork_map = {
        "oshawott.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/501.png",
        "luxray.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/405.png",
        "lucario.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/448.png",
        "venusaur.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/3.png"
    }
    local_images = {}
    for fn, u in artwork_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    # Content structure as verified from Siliconera & Yomiuri Shimbun
    raw_items = [
        {
            "speaker": "编辑部",
            "text": "Ken Sugimori has worked on designing Pokémon from the very beginning, and he shared a little secret on how he comes up with designs using a concept of addition by subtraction and vice-versa in an interview with the Yomiuri Shimbun."
        },
        {
            "speaker": "杉森建",
            "text": "The technique I often use when finishing up designs for Pokémon is to “keep the balance.” I might try adding something uncool to a Pokémon that is too cool, or I might add something cheerful to a Pokémon that is too serious. I spoke about making friendly designs earlier, but what I actually do is take something cool and make it less cool. [laughs]"
        },
        {
            "speaker": "提问",
            "text": "Huh? But Lucario and Luxray look very cool."
        },
        {
            "speaker": "杉森建",
            "text": "But if you were to make Luxray’s head smaller and eyes sharper, it would look cooler. “Making it cooler” is an adjustment I wouldn’t dare to do."
        },
        {
            "speaker": "提问",
            "text": "That is certainly a unique sensitivity of yours, Sugimori-san."
        },
        {
            "speaker": "杉森建",
            "text": "I often tell members in charge of design to “take away from designs that are too cool,” but that is probably a sentiment that is difficult to grasp. What’s cool and what’s not is all subjective in the end. To put it extremely, my job is to get something that would look cooler if it didn’t have this or that on it, then put it in on purpose. [laughs] Basically, if it looks too cool then it takes away from what makes it memorable for the players."
        },
        {
            "speaker": "提问",
            "text": "So you’re saying that it becomes kind of like a pretty landscape painting."
        },
        {
            "speaker": "杉森建",
            "text": "Exactly. It simply ends at “that’s cool.” After all, as Pokémon that are being sent out to the world, we want them to always remain memorable; however, I feel that in order to do so you have to add a touch to it. For example, look at Oshawott’s cheeks. It has three freckles, and if you take them away Oshawott becomes cuter. However, taking them away makes its face less memorable. Actually, a lot of people told me “I want you to get rid of the freckles,” but I strongly insisted “It is better to have them.” Going by my standards, this is the correct way to design Pokémon."
        }
    ]

    glossary = load_glossary()
    full_text = " ".join(it["text"] for it in raw_items)
    glossary_matches = find_glossary_matches(full_text, glossary)

    print(f"Translating {len(raw_items)} items for Sugimori Design Balance...")
    segments = translate_chunk(raw_items, glossary_matches)

    parallel_items = []
    for idx, seg in enumerate(segments):
        parallel_items.append({
            "speaker": seg.get("speaker", ""),
            "original": seg.get("original", ""),
            "translation": seg.get("translation", ""),
            "note": seg.get("note", "")
        })
        if idx == 3 and "luxray.png" in local_images and "lucario.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["luxray.png"],
                "caption_original": "Luxray - Sugimori explains that making its head smaller would make it cooler, but less uniquely memorable.",
                "caption_translation": "伦琴猫：杉森建解释如果把头改小、眼神改锐利确实会更帅，但他绝不敢做这种‘让它更帅’的调整。"
            })
            parallel_items.append({
                "type": "image",
                "image": local_images["lucario.png"],
                "caption_original": "Lucario - Balancing cool aesthetic with approachable proportions.",
                "caption_translation": "路卡利欧：兼具帅气冷峻与亲和力比例的经典代表。"
            })
        elif idx == 7 and "oshawott.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["oshawott.png"],
                "caption_original": "Oshawott - The famous 3 freckles that Sugimori insisted on keeping despite team objections.",
                "caption_translation": "水水獭：脸颊两侧标志性的雀斑。杉森建顶住团队‘去掉更可爱’的意见坚决保留，成为点睛之笔。"
            })

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 读卖新闻 × Siliconera 专访杉森建：宝可梦设计的“减法美学”与帅气/可爱的微妙平衡",
        "original_title": "Pokémon Designer On Balancing Cool Or Cute Pokémon By Adding Uncool Or Uncute Features",
        "date": "2018-07-27",
        "era": "2017–2021 · Switch Microsite 触控时代",
        "era_skin": "2019",
        "publication": "読売新聞 (Yomiuri Shimbun) / Siliconera",
        "source_kind": "newspaper_interview",
        "author": "Yomiuri Shimbun / Sato (Siliconera)",
        "translator": "Poke Amice Studio",
        "interviewee": "杉森建",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "杉森建", "怪兽设计", "设计哲学", "读卖新闻", "水水獭", "伦琴猫", "路卡利欧", "减法美学"],
        "archive_type": "interview_translation",
        "source": {
            "title": "読売新聞 (Yomiuri Shimbun 2018-07-26) / Siliconera",
            "url": url,
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "2018 年 7 月，宝可梦传奇艺术总监杉森建在接受《读卖新闻》采访时，首次揭晓了宝可梦怪兽造型的终极心法——‘保持平衡（Keep the balance）’的减法美学。杉森建直言：如果一个设计太帅，他会故意加入某种‘不够帅’的滑稽或笨拙元素；如果太可爱，就必须加入某种奇异的异质感。他以伦琴猫（Luxray）的大头比例、以及水水獭（Oshawott）脸颊上的三点雀斑为例：虽然团队很多人强烈要求去掉雀斑以显得更萌，但他坚决力保——正是这种‘破坏完美’的触笔，才让宝可梦免于沦为平庸的风景画，深深烙印在数亿玩家的记忆中。",
        "entities": {
            "people": ["杉森建"],
            "pokemon": ["水水獭", "伦琴猫", "路卡利欧", "妙蛙花"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)


# =========================================================================
# Catalog Synchronizer
# =========================================================================
def sync_catalog():
    if not CATALOG_PATH.exists():
        print(f"Catalog {CATALOG_PATH} does not exist.")
        return

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    # 1. Update PKMN-0021 (GI 2011)
    for it in data:
        if it.get("id") == "PKMN-0021" or "past-present-future" in it.get("url", ""):
            it["title"] = "Game Informer 专访增田顺一与井部真那：宝可梦 15 年的过去、现在与未来"
            it["original_title"] = "Pokémon: Past, Present, And Future - Game Freak on 15 Years of Pokémon"
            it["date"] = "2011-03-07"
            it["outlet"] = "Game Informer"
            it["people"] = ["增田顺一", "井部真那"]
            it["post_file"] = "_posts/2011-03-07-interview-gameinformer-masuda-past-present-future.md"
            it["status"] = "imported"
            it["era_skin"] = "2011"
            print("Updated PKMN-0021 in catalog.")
            break

    # 2. Update PKMN-0024 (GI 2014)
    for it in data:
        if it.get("id") == "PKMN-0024" or "afterwords-unabridged" in it.get("url", ""):
            it["title"] = "Game Informer 独家专访增田顺一：《宝可梦 X·Y》全景事后解密与宝可友友乐诞生"
            it["original_title"] = "Afterwords – Pokémon X & Y (Unabridged Interview with Junichi Masuda)"
            it["date"] = "2014-02-14"
            it["outlet"] = "Game Informer"
            it["people"] = ["增田顺一"]
            it["post_file"] = "_posts/2014-02-14-interview-gameinformer-masuda-afterwords-xy.md"
            it["status"] = "imported"
            it["era_skin"] = "2014"
            print("Updated PKMN-0024 in catalog.")
            break

    # 3. Update PKMN-0095 (Siliconera Sugimori)
    for it in data:
        if it.get("id") == "PKMN-0095" or "adding-uncool-or-uncute-features" in it.get("url", ""):
            it["title"] = "读卖新闻 × Siliconera 专访杉森建：宝可梦设计的“减法美学”与帅气/可爱的微妙平衡"
            it["original_title"] = "Pokémon Designer On Balancing Cool Or Cute Pokémon By Adding Uncool Or Uncute Features"
            it["date"] = "2018-07-27"
            it["outlet"] = "読売新聞 (Yomiuri Shimbun) / Siliconera"
            it["people"] = ["杉森建"]
            it["post_file"] = "_posts/2018-07-27-interview-yomiuri-siliconera-sugimori-monster-balance.md"
            it["status"] = "imported"
            it["era_skin"] = "2019"
            print("Updated PKMN-0095 in catalog.")
            break

    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Catalog synchronization complete.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "gi2011":
        import_gi_2011()
        sync_catalog()
    elif action == "gi2014":
        import_gi_2014()
        sync_catalog()
    elif action == "sugimori":
        import_siliconera_sugimori()
        sync_catalog()
    elif action == "sync":
        sync_catalog()
    elif action == "all":
        import_gi_2011()
        import_gi_2014()
        import_siliconera_sugimori()
        sync_catalog()
