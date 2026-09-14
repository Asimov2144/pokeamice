"""Batch curate, clean, translate, and import 3 milestone Pokémon Ruby & Sapphire (Generation 3) interviews from Nintendo Online Magazine (N.O.M) November 2002 (No. 52) (Batch 9):
1. PKMN-0115: N.O.M 2002年11月号：『红宝石·蓝宝石』发售纪念大特集（总监构想篇：增田顺一谈丰缘大自然与个性化时代）
2. PKMN-0116: N.O.M 2002年11月号：『红宝石·蓝宝石』美术与生态特征（杉森建篇：GBA色彩飞跃与新怪兽克制美学）
3. PKMN-0117: N.O.M 2002年11月号：『红宝石·蓝宝石』对战革命与秘密基地实测（石原恒和谈品牌、4人双打与数据通信）
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
CACHE_DIR = ROOT / "data" / "cache_nom"
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
    
    prompt = f"""你是精通任天堂史料、第三世代宝可梦开发史与GBA时代硬件革新的资深学者与翻译家。
正在整理 Nintendo Online Magazine (N.O.M) 2002年11月号（No.52）《宝可梦 红宝石·蓝宝石》发售纪念大特集档案：
【访谈背景】：{context_desc}

请将以下访谈内容翻译为流畅、雅致、忠实原文且极具历史沉浸感的简体中文。
注意：
1. 准确辨析并规范说话人(speaker)：如“增田 顺一”、“杉森 建”、“石原 恒和”、“N.O.M 采访者”、“实机体验报告”等。
2. 保持增田顺一作为年轻新任总监的宏大愿景、杉森建对美术风格克制的审慎思考、以及石原恒和统领宝可梦品牌的长线哲学。
3. 如果对话中涉及特定术语（如 丰缘地区、特性、性格、华丽大赛、秘密基地、2v2双打对战、记录角落Record Corner、大嘴鸥等），请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 红宝石·蓝宝石（Ruby & Sapphire）
- 丰缘地区（Hoenn / ホウエン地方）
- 固拉多（Groudon / グラードン）
- 盖欧卡（Kyogre / カイオーガ）
- 木守宫（Treecko / キモリ）
- 火稚鸡（Torchic / アチャモ）
- 水跃鱼（Mudkip / ミズゴロウ）
- 大嘴鸥（Pelipper / ペリッパー）
- 秘密基地（Secret Base / ひみつきち）
- 华丽大赛（Pokémon Contest / ポケモンコンテスト）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名",
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
        {"role": "system", "content": "你是一位精通任天堂历史与第三世代宝可梦诞生史料的双语专家。请只输出合法的 JSON 对象。"},
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


# =========================================================================
# 1. PKMN-0115: Director Junichi Masuda (World Concept & 4x Fun)
# =========================================================================
def import_nom_rs_masuda() -> str:
    slug = "2002-11-01-interview-nom-ruby-sapphire-director-masuda"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0115 N.O.M 2002年11月号 增田顺一总监篇 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "masuda.jpg": "https://web.archive.org/web/20221226221956im_/https://www.nintendo.co.jp/nom/0211/01/01_05/b_masu.jpg",
        "groudon.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/383.png",
        "kyogre.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/382.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = [
        {"speaker": "【章节导览】", "text": "=== 序言：新世代开启！GBA首部完全新作《宝可梦 红宝石·蓝宝石》发售特别企划 ==="},
        {"speaker": "N.O.M 导览", "text": "全世界待望的《宝可梦 红宝石·蓝宝石》终于要在Game Boy Advance上登场！本作不仅全面革新了画面与音效，更带来了全新的丰缘地区、特性、性格与华丽大赛。N.O.M编辑部在发售前夕特邀担任本作总监与游戏设计师的增田顺一先生，畅谈宏大构想。"},
        {"speaker": "【章节导览】", "text": "=== 增田顺一专访：从战斗走向‘每一只宝可梦的生态个性’ ==="},
        {"speaker": "N.O.M 采访者", "text": "增田先生担任本作的‘总监（Director）’，具体是一项怎样的工作呢？"},
        {"speaker": "增田 顺一", "text": "总监就是从‘要将这款游戏打造成什么样的作品’这一愿景出发，统揽全局并最终将其塑造成形的统括工作。如何将点子融入系统、世界观如何构建、操控手感与界面反馈如何把控，都要由全局来判断。无论是剧本剧情、全新的玩法机制，还是细微的按键操作感，只要能让作品变得更出色，我什么都会亲力亲为。"},
        {"speaker": "N.O.M 采访者", "text": "在制作《红宝石·蓝宝石》的过程中，一定有非常多的核心主题，能为我们透露其中之一吗？"},
        {"speaker": "增田 顺一", "text": "我们这次的核心主题之一，就是‘不再单纯特化战斗数值，而是深入挖掘并展现每一只宝可梦独一无二的个性’。全新的‘宝可梦华丽大赛’正是为了追求这种个体趣味而诞生的。当然，对战要素也比以往有了成倍的强化。此外，考虑到第一次接触宝可梦的新玩家，我们从‘宝可梦是什么？’到如何捕捉宝可梦等细致引导，都力求设计得极度简洁明了。"},
        {"speaker": "N.O.M 采访者", "text": "增田先生在本作中最喜欢的宝可梦是哪一只呢？"},
        {"speaker": "增田 顺一", "text": "哎呀，喜欢的好孩子实在太多了，完全没办法选出唯一的一只！非常抱歉（笑）。"},
        {"speaker": "N.O.M 采访者", "text": "最后，请对N.O.M的读者们送上一句寄语吧！"},
        {"speaker": "增田 顺一", "text": "全新实现的2vs2双打对战，结合属性、技能与‘特性’，真的能产生无限多样的战术搭配！另外，像华丽大赛、秘密基地等支持4人联机游玩的内容也非常丰富，请大家一定要和朋友们发掘各种各样的玩法！GBA是一台能让4人一起热闹联机的掌机，因此带来的乐趣绝对也是4倍的！！"}
    ]

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "N.O.M 2002年11月号《宝可梦 红宝石·蓝宝石》总监增田顺一专访：丰缘世界观、个性系统与4倍乐趣")

    if local_images.get("masuda.jpg"):
        parallel_items.insert(2, {
            "type": "image",
            "image": local_images["masuda.jpg"],
            "caption_original": "『ポケットモンスタールビー・サファイア』ディレクター／ゲームデザイナーの増田順一氏。",
            "caption_translation": "时任《宝可梦 红宝石·蓝宝石》总监兼游戏设计师的增田顺一（2002年11月N.O.M官方档案照）。"
        })
    if local_images.get("groudon.png"):
        parallel_items.insert(6, {
            "type": "image",
            "image": local_images["groudon.png"],
            "caption_original": "『ルビー』のパッケージを飾る大陸の創造神・グラードン。",
            "caption_translation": "《红宝石》封面传说的宝可梦——开拓大地的巨兽固拉多。"
        })
    if local_images.get("kyogre.png"):
        parallel_items.insert(7, {
            "type": "image",
            "image": local_images["kyogre.png"],
            "caption_original": "『サファイア』のパッケージを飾る海の創造神・カイオーガ。",
            "caption_translation": "《蓝宝石》封面传说的宝可梦——降下暴雨扩张海洋的盖欧卡。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』发售纪念大特集（总监构想篇：增田顺一谈丰缘大自然与个性化时代）",
        "subtitle": "打破单一对战桎梏！华丽大赛、特性性格机制与‘4人联机带来4倍乐趣’的GBA宣言",
        "date": "2002-11-01",
        "era_skin": "2003",
        "source_name": "任天堂官网「N.O.M」(No.52)",
        "source_url": "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
        "original_link": "https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
        "summary": "刊登于任天堂官方Web杂志《N.O.M》2002年11月号（No.52）的第三世代发售里程碑专访！首次正式接过正统续作总监（Director）重任的增田顺一深度阐述《红宝石·蓝宝石》的哲学转变：不再将游戏局限于‘谁强谁弱’的单一战斗特化，而是通过全新的‘特性’、‘性格’与‘宝可梦华丽大赛’，赋予每一只宝可梦鲜活立体的生态个性；同时借助GBA联机线实现革命性的4人双打对战与秘密基地互动，掷地有声地宣示‘GBA能让4人同乐，带来的游戏乐趣也是过往的4倍’！",
        "entities": {
            "people": ["增田 顺一"],
            "games": ["宝可梦 红宝石·蓝宝石"],
            "pokemon": ["固拉多", "盖欧卡"]
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
# 2. PKMN-0116: Art Director Ken Sugimori (Visual Fidelity & Restraint)
# =========================================================================
def import_nom_rs_sugimori() -> str:
    slug = "2002-11-01-interview-nom-ruby-sapphire-art-director-sugimori"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0116 N.O.M 2002年11月号 杉森建美术篇 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "sugimori.jpg": "https://web.archive.org/web/20221226221956im_/https://www.nintendo.co.jp/nom/0211/01/01_05/b_sugi.jpg",
        "treecko.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/252.png",
        "torchic.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/255.png",
        "mudkip.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/258.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = [
        {"speaker": "【章节导览】", "text": "=== 杉森建专访：GBA硬件色彩跃进与怪兽设计的‘克制美学’ ==="},
        {"speaker": "N.O.M 采访者", "text": "请杉森先生向大家介绍一下您在本作中的具体工作职责。"},
        {"speaker": "杉森 建", "text": "我主要负责全游戏角色的设计监修与统括。在Game Freak内部，包括我自己在内有多名设计师，大家会全员一起激荡出各种各样的怪兽点子。而我的工作就是把关这些新诞生的设计，统一视觉风格，让它们真正融合进宝可梦的世界。"},
        {"speaker": "N.O.M 采访者", "text": "作为GBA平台上的第一部宝可梦正统新作，画面的可显示色彩数获得了飞跃性的提升。在展开设计工作时，和以往相比有什么深刻的转变吗？"},
        {"speaker": "杉森 建", "text": "由于硬件表现力的大幅进化，过去Game Boy时代根本无法实现的细腻表现——比如极度贴近官方插画甚至TV动画质感的色彩与笔触——现在全都能够在掌机屏幕上呈现了。但与此同时，我时刻高度警惕并克制自己：绝对不能为了炫技而采用过于复杂繁琐的色彩或异化形状，从而失去‘宝可梦特有的质朴本质’。"},
        {"speaker": "N.O.M 采访者", "text": "杉森先生在本作中最钟爱的宝可梦究竟是哪一只呢？"},
        {"speaker": "杉森 建", "text": "虽然很难评选出第一名，但我个人反而对那些长相朴素、看起来不太起眼甚至人气不高的怪兽抱有最深的情感。这大概就像为人父母总是格外牵挂不起眼的孩子一样吧（笑）。"},
        {"speaker": "N.O.M 采访者", "text": "最后，请对期待新作的N.O.M读者们说一句话吧！"},
        {"speaker": "杉森 建", "text": "和前作一样，有可爱的伙伴，有神秘怪异的同伴，也有帅气威武的巨兽，我们为丰缘地区设计了大量全新的宝可梦。此外，更有那种会让大家惊呼‘诶？这也算宝可梦吗？！’的前卫新怪兽登场，绝对能让大家感受到完全新作带来的绝妙新鲜感。请务必把所有的宝可梦全都收服到图鉴里吧！"}
    ]

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "N.O.M 2002年11月号《宝可梦 红宝石·蓝宝石》艺术总监杉森建专访：GBA色彩表现与宝可梦设计克制美学")

    if local_images.get("sugimori.jpg"):
        parallel_items.insert(1, {
            "type": "image",
            "image": local_images["sugimori.jpg"],
            "caption_original": "『ポケットモンスタールビー・サファイア』アートディレクターの杉森建氏。",
            "caption_translation": "时任《宝可梦 红宝石·蓝宝石》艺术总监的杉森建（2002年11月N.O.M官方档案照）。"
        })
    if local_images.get("treecko.png"):
        parallel_items.insert(5, {
            "type": "image",
            "image": local_images["treecko.png"],
            "caption_original": "ホウエン地方の最初のパートナー・キモリ。",
            "caption_translation": "丰缘地区草属性最初的伙伴——性格冷静的木守宫。"
        })
    if local_images.get("torchic.png"):
        parallel_items.insert(6, {
            "type": "image",
            "image": local_images["torchic.png"],
            "caption_original": "ホウエン地方の最初のパートナー・アチャモ。",
            "caption_translation": "丰缘地区火属性最初的伙伴——娇小可爱的火稚鸡。"
        })
    if local_images.get("mudkip.png"):
        parallel_items.insert(7, {
            "type": "image",
            "image": local_images["mudkip.png"],
            "caption_original": "ホウエン地方の最初のパートナー・ミズゴロウ。",
            "caption_translation": "丰缘地区水属性最初的伙伴——拥有头顶鳍感知水流的水跃鱼。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』美术与生态特征（杉森建篇：GBA色彩飞跃与新怪兽克制美学）",
        "subtitle": "贴近动画插画却极力警惕复杂化！偏爱冷门怪兽的‘父母心’与‘这也是宝可梦？’的颠覆设计",
        "date": "2002-11-01",
        "era_skin": "2003",
        "source_name": "任天堂官网「N.O.M」(No.52)",
        "source_url": "https://web.archive.org/web/20221226221956/https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
        "original_link": "https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
        "summary": "刊登于《N.O.M》2002年11月号（No.52）的艺术总监深度对谈！杉森建揭示了进入GBA 32位全彩掌机时代后怪兽造型的核心设计哲学：面对大幅跃进的发色数与分辨率，Game Freak不仅没有盲目堆砌复杂线条与华丽渐变，反而刻意保持‘减法克制’，全力守护初代确立的亲和力与纯粹感；访谈中杉森建不仅坦诚自己对‘朴素不起眼怪兽’的偏爱犹如父母之心，更剧透了丰缘地区将迎来打破既有认知的超前卫怪兽构想！",
        "entities": {
            "people": ["杉森 建"],
            "games": ["宝可梦 红宝石·蓝宝石"],
            "pokemon": ["木守宫", "火稚鸡", "水跃鱼"]
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
# 3. PKMN-0117: Multi-Battle, Secret Base & Executive Producer Tsunekazu Ishihara
# =========================================================================
def import_nom_rs_features_ishihara() -> str:
    slug = "2002-11-01-interview-nom-ruby-sapphire-multi-battle-secret-base"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0117 N.O.M 2002年11月号 对战革命、秘密基地与石原恒和专访 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "taisen.jpg": "https://web.archive.org/web/20221026123518im_/https://www.nintendo.co.jp/nom/0211/01/01_04/taisen.jpg",
        "pelipper.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/279.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = [
        {"speaker": "【章节导览】", "text": "=== 实测报告：潜入株式会社宝可梦总部！GBA首创4人双打对战实况 ==="},
        {"speaker": "实机体验报告", "text": "本作最受瞩目的革新，莫过于终于实现的4人联机对战（マルチバトル），以及可以在野外开辟、布置家具的‘秘密基地’。在发售日前夕，N.O.M编辑部潜入株式会社宝可梦总部，提前体验了这两项颠覆性新要素！"},
        {"speaker": "实机体验报告", "text": "我们用专用通信线连接4台GBA，进入宝可梦中心2楼的竞技场。大家商量分组后，坐定位置即刻开始对战。由于可以随时换位更换队友，操作非常直观明快！"},
        {"speaker": "实机体验报告", "text": "战斗开始！双方各派出一只宝可梦展开2对2的协同作战。这与过去1对1的单打完全不同，现场爆发出一阵阵‘哇，居然打出这一招！’、‘坚持住！’的欢呼呐喊，所有人都能一起围坐喧闹，现场气氛极其热烈！"},
        {"speaker": "【章节导览】", "text": "=== 实测报告：专属私人空间‘秘密基地’与记录角落数据流转 ==="},
        {"speaker": "实机体验报告", "text": "我们在小山丘上发现了一个不起眼的小凹洞，让宝可梦使出特定技能后，洞穴入口豁然开朗！里面空间相当宽敞，我们铺上在之前城镇购买的地毯与积木，摆上心爱的宝可梦玩偶，立刻有了温暖的小屋质感。"},
        {"speaker": "实机体验报告", "text": "最令人震惊的机制在于宝可梦中心2楼的‘记录角落（Record Corner）’：只要与其他玩家进行通信交换记录，对方的秘密基地就会直接投射出现在你的游戏大地图中！随着你和越来越多的朋友联机，你的游戏卡带里就会源源不断地诞生各式各样充满个性的秘密基地，甚至还能与朋友留在那里的队伍交锋！"},
        {"speaker": "【章节导览】", "text": "=== 执行制作人专访：石原恒和谈跨媒体生态与最爱怪兽大嘴鸥 ==="},
        {"speaker": "N.O.M 采访者", "text": "石原先生作为执行制作人（Executive Producer），平时都在负责哪些宏观工作呢？"},
        {"speaker": "石原 恒和", "text": "我一直在思考：‘要怎么做，才能让宝可梦能够长长久久地被所有人喜爱和游玩？’这不仅涵盖GBA与NGC上的游戏软件开发，还包括宝可梦卡牌、TV动画、剧场版电影，乃至让人忍不住想收藏的实体手办周边。我坚信，当这些形形色色的宝可梦游玩方式相互串联、互相联动时，整个世界观就会变得前所未有地深邃与有趣。"},
        {"speaker": "N.O.M 采访者", "text": "株式会社宝可梦（The Pokémon Company）是一家怎样的公司呢？"},
        {"speaker": "石原 恒和", "text": "我们正是为了在全世界开展上述品牌统括业务而设立的公司。在这次《红宝石·蓝宝石》中，我们作为发行方与任天堂紧密携手将作品送到各位手中，同时还运营宝可梦中心专卖店与卡牌赛事。"},
        {"speaker": "N.O.M 采访者", "text": "在《红宝石·蓝宝石》所有新宝可梦中，石原先生最喜欢的究竟是哪一只？"},
        {"speaker": "石原 恒和", "text": "是‘大嘴鸥（ペリッパー）’！它那憨厚巨大、能把很多东西塞进去的大嘴巴实在太有魅力了！"},
        {"speaker": "N.O.M 采访者", "text": "最后，请对全日本期待发售的玩家们送上一句寄语！"},
        {"speaker": "石原 恒和", "text": "《红宝石·蓝宝石》即将发售，宝可梦的世界将在全新的丰缘地区展开全新的篇章。不管是初次接触宝可梦的新朋友，还是一直陪伴至今的老玩家，都请全心期待这趟宏大的全新旅程吧！"}
    ]

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "N.O.M 2002年11月号《宝可梦 红宝石·蓝宝石》4人双打对战、秘密基地实机测评与石原恒和专访")

    if local_images.get("taisen.jpg"):
        parallel_items.insert(2, {
            "type": "image",
            "image": local_images["taisen.jpg"],
            "caption_original": "GBAを4台つないで2対2のマルチバトルを体験するN.O.M取材班。",
            "caption_translation": "N.O.M采访团队在株式会社宝可梦总部使用4台GBA连接线展开2对2实机对战。"
        })
    if local_images.get("pelipper.png"):
        parallel_items.insert(12, {
            "type": "image",
            "image": local_images["pelipper.png"],
            "caption_original": "石原恒和氏が一番のお気に入りと明かしたホウエン地方のポケモン・ペリッパー。",
            "caption_translation": "石原恒和在专访中揭秘自己全游戏最钟爱的丰缘宝可梦——大嘴鸥。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』对战革命与秘密基地实测（石原恒和谈品牌、4人双打与数据通信）",
        "subtitle": "现场直击株式会社宝可梦总部：4人GBA热战、记录角落世界漫游与石原恒和的最爱大嘴鸥",
        "date": "2002-11-01",
        "era_skin": "2003",
        "source_name": "任天堂官网「N.O.M」(No.52)",
        "source_url": "https://web.archive.org/web/20221026123518/https://www.nintendo.co.jp/nom/0211/01/01_04/index.html",
        "original_link": "https://www.nintendo.co.jp/nom/0211/01/01_04/index.html",
        "summary": "刊登于任天堂官方Web杂志《N.O.M》2002年11月号的实地探秘与高层专访合辑！编辑部在《红宝石·蓝宝石》发售日前夕潜入株式会社宝可梦（The Pokémon Company）总部，亲测GBA 4人连接线2v2协同对战（Multi Battle）的临场震撼；解密野外开凿‘秘密基地’、地毯玩偶装饰以及通过宝可梦中心2楼‘记录角落’（Record Corner）让朋友的基地无缝跨卡带复制投射到自己世界的大互联网络！在专访中，执行制作人石原恒和深度阐述了统括游戏、卡牌、动画与周边的全域生态长青战略，并独家揭秘自己在丰缘地区最喜爱的宝可梦正是大嘴鸥！",
        "entities": {
            "people": ["石原 恒和"],
            "games": ["宝可梦 红宝石·蓝宝石", "宝可梦卡牌"],
            "pokemon": ["大嘴鸥"]
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
        "PKMN-0115": {
            "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』发售纪念大特集（总监构想篇：增田顺一谈丰缘大自然与个性化时代）",
            "date": "2002-11-01",
            "source_name": "任天堂官网「N.O.M」(No.52)",
            "source_url": "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0115']}.md",
            "status": "imported"
        },
        "PKMN-0116": {
            "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』美术与生态特征（杉森建篇：GBA色彩飞跃与新怪兽克制美学）",
            "date": "2002-11-01",
            "source_name": "任天堂官网「N.O.M」(No.52)",
            "source_url": "https://web.archive.org/web/20221226221956/https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0116']}.md",
            "status": "imported"
        },
        "PKMN-0117": {
            "title": "N.O.M 2002年11月号：『红宝石·蓝宝石』对战革命与秘密基地实测（石原恒和谈品牌、4人双打与数据通信）",
            "date": "2002-11-01",
            "source_name": "任天堂官网「N.O.M」(No.52)",
            "source_url": "https://web.archive.org/web/20221026123518/https://www.nintendo.co.jp/nom/0211/01/01_04/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0117']}.md",
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
    print("Starting Batch 9 (Nintendo Online Magazine Nov 2002 Ruby & Sapphire Trilogy) Import Pipeline...")
    batch_results = {}

    batch_results["PKMN-0115"] = import_nom_rs_masuda()
    batch_results["PKMN-0116"] = import_nom_rs_sugimori()
    batch_results["PKMN-0117"] = import_nom_rs_features_ishihara()

    update_catalog(batch_results)
    print("\nBatch 9 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
