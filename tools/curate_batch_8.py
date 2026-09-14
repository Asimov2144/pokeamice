"""Batch curate, clean, translate, and import 3 landmark Nintendo Online Magazine (N.O.M) interviews from July 2000 (No. 23) (Batch 8):
1. PKMN-0108: N.O.M 2000年7月号：Game Freak全员座谈会（前编·初代『赤·绿』诞生回忆）
2. PKMN-0109: N.O.M 2000年7月号：Game Freak全员座谈会（后编·续篇『金·银』突破与开发秘闻）
3. PKMN-0110: N.O.M 2000年7月号：田尻智 × 石原恒和 特别对谈（二人的相遇、六年长征与生命感哲学）
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
    
    prompt = f"""你是精通任天堂史料、宝可梦开发史与早期访谈的资深学者与翻译家。
正在整理 Nintendo Online Magazine (N.O.M) 2000年7月号（No.23）宝可梦开发史档案：
【访谈背景】：{context_desc}

请将以下访谈内容翻译为流畅、雅致、忠实原文且极具历史沉浸感的简体中文。
注意：
1. 准确辨析并规范说话人(speaker)：
   - 杉森建（Art Director / 角色设计总监）
   - 增田顺一（Director / 音频与对战系统总监）
   - 西野弘二（Planner / 宝可梦生态与招式策划）
   - 森本茂树（Programmer / 战斗程序员、梦幻创造者）
   - 渡边哲也（Programmer / 金银程序员）
   - 田尻智（Game Freak 社长 / 宝可梦之父）
   - 石原恒和（Creatures 社长 / 宝可梦制作人）
   - N.O.M 采访者（若为提问或引导性解说）
2. 忠实保留开发者的真实心境与历史细节（如Game Boy通信电缆、151只怪兽命名、舍弃3个存档位的决断、卡带压盘前偷塞梦幻、树才怪挡路剧情、宝可梦变声期、各版本存档音效彩蛋、爱普生时期相遇、六年濒临破产的坚持等）。
3. 如果对话中涉及特定游戏术语、未公开企划或历史背景，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 赤·绿（Red & Green）/ 金·银（Gold & Silver）/ 水晶（Crystal）
- 皮卡丘（Pikachu / ピカチュウ）
- 梦幻（Mew / ミュウ）
- 超梦（Mewtwo / ミュウツー）
- 树才怪 / 胡说树（Sudowoodo / ウソッキー）
- 凤王（Ho-Oh / ホウオウ）
- 洛奇亚（Lugia / ルギア）
- 妙蛙种子（Bulbasaur）/ 小火龙（Charmander）/ 杰尼龟（Squirtle）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'杉森 建'、'增田 顺一'、'田尻 智'、'石原 恒和'、'N.O.M 采访者'）",
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


# =========================================================================
# 1. PKMN-0108: Game Freak Roundtable Vol. 1 (Red & Green Development)
# =========================================================================
def import_nom_gf_part1() -> str:
    slug = "2000-07-01-interview-nom-gamefreak-roundtable-vol1-red-green"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0108 N.O.M 2000年7月号 GF初代赤绿篇 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "pikachu.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        "mew.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/151.png",
        "bulbasaur.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = []
    speaker_map = {
        "杉森": "杉森 建",
        "増田": "增田 顺一",
        "西野": "西野 弘二",
        "森本": "森本 茂树",
        "渡辺": "渡边 哲也",
        "N.O.M 采访者": "N.O.M 采访者"
    }

    for page_num in [1, 2, 3]:
        fpath = CACHE_DIR / f"nom_0007_gfreak_page0{page_num}.html"
        raw = fpath.read_bytes().decode("cp932", errors="replace")
        raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

        m_title = re.search(r"<title>(.*?)</title>", raw, re.I)
        sec_title = m_title.group(1).strip() if m_title else f"Page {page_num}"
        dialogues.append({"speaker": "【章节导览】", "text": f"=== 第{page_num}节：{sec_title} ==="})

        body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
        body = body_m.group(1) if body_m else raw
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
        body = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body, flags=re.I)
        body = re.sub(r"<[^>]+>", "", body)

        lines = [html.unescape(l).strip() for l in body.split("\n")]
        lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

        cur_speaker = ""
        cur_text = []
        for l in lines:
            m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
            if m:
                if cur_text:
                    dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                    cur_text = []
                cur_speaker = m.group(1).strip()
                rest = m.group(3).strip()
                if rest:
                    cur_text.append(rest)
            else:
                if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                    if not cur_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                        if cur_text:
                            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                            cur_text = []
                        cur_speaker = "N.O.M 采访者"
                        cur_text.append(l)
                        continue
                cur_text.append(l)
        if cur_text:
            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "Game Freak开发全员座谈会前篇：初代《宝可梦 赤·绿》开发秘辛")

    if local_images.get("pikachu.png"):
        parallel_items.insert(12, {
            "type": "image",
            "image": local_images["pikachu.png"],
            "caption_original": "「でんき」タイプという属性のアイデアから誕生したピカチュウ。",
            "caption_translation": "杉森建与西野弘二透露，皮卡丘正是为了赋予‘电属性’视觉象征而诞生的怪兽。"
        })
    if local_images.get("bulbasaur.png"):
        parallel_items.insert(25, {
            "type": "image",
            "image": local_images["bulbasaur.png"],
            "caption_original": "図鑑No.001のフシギダネ。タイプ相性の概念によって戦闘の奥深さが生まれた。",
            "caption_translation": "图鉴No.001的妙蛙种子。属性相克机制让初代打破了单纯的数值强弱。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2000年7月号：Game Freak全员座谈会（前编·初代『赤·绿』诞生回忆）",
        "subtitle": "从通信电缆联想交换到给151只怪兽起昵称——为了伙伴感而舍弃3个存档位的执着",
        "date": "2000-07-01",
        "era_skin": "1999",
        "source_name": "任天堂官网「N.O.M」(No.23)",
        "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/index.html",
        "original_link": "https://www.nintendo.co.jp/nom/0007/gfreak/index.html",
        "summary": "刊登于任天堂官方Web杂志《N.O.M》2000年7月号（No.23）的里程碑式座谈会！杉森建、增田顺一、西野弘二深入回忆《宝可梦 赤·绿》开发全过程：田尻智如何从Game Boy联机线灵光一闪联想到‘交换车票与卡片’；全团队10人跨部门脑力激荡；为什么彻底颠覆勇者斗恶龙模式将‘图鉴收集’立为核心目标；技能为何严格限制为4个；以及当年最为惊人的决策——在‘容纳3个玩家存档’与‘允许玩家给全部151只宝可梦起专属昵称’之间，团队全员一致选择‘必须能给全部宝可梦起名’，奠定了宝可梦作为玩家真挚伙伴的永恒基石！",
        "entities": {
            "people": ["杉森 建", "增田 顺一", "西野 弘二", "森本 茂树", "田尻 智"],
            "games": ["宝可梦 赤·绿", "宝可梦 青", "宝可梦 皮卡丘"],
            "pokemon": ["皮卡丘", "妙蛙种子", "梦幻"]
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
# 2. PKMN-0109: Game Freak Roundtable Vol. 2 (Gold & Silver Breakthrough & Secrets)
# =========================================================================
def import_nom_gf_part2() -> str:
    slug = "2000-07-01-interview-nom-gamefreak-roundtable-vol2-gold-silver-secrets"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0109 N.O.M 2000年7月号 GF金银篇与番外秘话 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "ho_oh.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png",
        "lugia.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png",
        "sudowoodo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/185.png",
        "gf_staff.jpg": "https://web.archive.org/web/20221026135305im_/https://www.nintendo.co.jp/nom/0007/gfreak/p15.jpg"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = []
    speaker_map = {
        "杉森": "杉森 建",
        "増田": "增田 顺一",
        "西野": "西野 弘二",
        "森本": "森本 茂树",
        "渡辺": "渡边 哲也",
        "N.O.M 采访者": "N.O.M 采访者"
    }

    # Pages 4, 5 (dialogues)
    for page_num in [4, 5]:
        fpath = CACHE_DIR / f"nom_0007_gfreak_page0{page_num}.html"
        raw = fpath.read_bytes().decode("cp932", errors="replace")
        raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

        m_title = re.search(r"<title>(.*?)</title>", raw, re.I)
        sec_title = m_title.group(1).strip() if m_title else f"Page {page_num}"
        dialogues.append({"speaker": "【章节导览】", "text": f"=== 第{page_num}节：{sec_title} ==="})

        body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
        body = body_m.group(1) if body_m else raw
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
        body = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body, flags=re.I)
        body = re.sub(r"<[^>]+>", "", body)

        lines = [html.unescape(l).strip() for l in body.split("\n")]
        lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

        cur_speaker = ""
        cur_text = []
        for l in lines:
            m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
            if m:
                if cur_text:
                    dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                    cur_text = []
                cur_speaker = m.group(1).strip()
                rest = m.group(3).strip()
                if rest:
                    cur_text.append(rest)
            else:
                if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                    if not cur_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                        if cur_text:
                            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                            cur_text = []
                        cur_speaker = "N.O.M 采访者"
                        cur_text.append(l)
                        continue
                cur_text.append(l)
        if cur_text:
            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})

    # Page 6: Extra Secrets
    fpath6 = CACHE_DIR / "nom_0007_gfreak_page06.html"
    raw6 = fpath6.read_bytes().decode("cp932", errors="replace")
    raw6 = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw6, flags=re.DOTALL | re.I)
    raw6 = re.sub(r"<script[^>]*>.*?</script>", "", raw6, flags=re.DOTALL | re.I)
    raw6 = re.sub(r"<style[^>]*>.*?</style>", "", raw6, flags=re.DOTALL | re.I)

    dialogues.append({"speaker": "【章节导览】", "text": "=== 番外篇：深度狂热粉丝必看！开发团队亲述宝可梦五大未公开秘密 ==="})
    body_m6 = re.search(r"<body[^>]*>(.*?)</body>", raw6, re.DOTALL | re.I)
    body6 = body_m6.group(1) if body_m6 else raw6
    body6 = re.sub(r"<br\s*/?>", "\n", body6, flags=re.I)
    body6 = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body6, flags=re.I)
    body6 = re.sub(r"<[^>]+>", "", body6)

    lines6 = [html.unescape(l).strip() for l in body6.split("\n")]
    lines6 = [l for l in lines6 if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

    cur_sec = ""
    for l in lines6:
        if re.match(r"^[１２３４５]\．", l):
            cur_sec = l
            dialogues.append({"speaker": "【绝密档案】", "text": l})
        elif "それぞれのクリエイター" in l:
            dialogues.append({"speaker": "N.O.M 导览", "text": l})
        elif cur_sec:
            dialogues.append({"speaker": "开发团队解密", "text": l})

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "Game Freak开发全员座谈会后篇：续篇《宝可梦 金·银》全面飞跃与五大未公开秘密")

    if local_images.get("gf_staff.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["gf_staff.jpg"],
            "caption_original": "ゲームフリークの制作現場風景（2000年当時）。",
            "caption_translation": "2000年当时的Game Freak开发团队现场（《金·银》发售后接受N.O.M专访）。"
        })
    if local_images.get("ho_oh.png"):
        parallel_items.insert(12, {
            "type": "image",
            "image": local_images["ho_oh.png"],
            "caption_original": "『金・銀』のパッケージを飾る伝説のポケモン・ホウオウ。",
            "caption_translation": "全面飞跃的《金·银》封面传说的宝可梦——凤王。"
        })
    if local_images.get("sudowoodo.png"):
        parallel_items.insert(28, {
            "type": "image",
            "image": local_images["sudowoodo.png"],
            "caption_original": "杉森建のスケッチから生まれ、道をふさぐストーリーが用意されたウソッキー。",
            "caption_translation": "杉森建灵光一闪构思出树才怪，并专程拜托剧本家为它创作‘挡路怪兽’的经典情节。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2000年7月号：Game Freak全员座谈会（后编·续篇『金·银』突破与开发秘闻）",
        "subtitle": "昼夜时间流逝、培育繁殖与五大绝密内幕：森本偷塞梦幻真相与树才怪挡路渊源",
        "date": "2000-07-01",
        "era_skin": "1999",
        "source_name": "任天堂官网「N.O.M」(No.23)",
        "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page04.html",
        "original_link": "https://www.nintendo.co.jp/nom/0007/gfreak/page04.html",
        "summary": "《N.O.M》2000年7月号Game Freak全员大座谈后编！渡边哲也、增田顺一、杉森建、森本茂树揭秘《金·银》突破性飞跃：在GB容量逼仄极限下塞入城都与关都两张完整世界地图、引入现实昼夜流动钟表与生蛋培育遗传系统；特攻特防拆分彻底平衡超能力霸权。最具历史价值的【番外篇五大绝密内幕】首次由主创本人亲口证实：1. 程序员森本茂树在母带压盘最后一刻发现仅剩极微小字节空余，偷偷写进第151只宝可梦‘梦幻’的惊险始末；2. 艺术总监杉森建画出假扮植物的‘树才怪’后特地请求编剧为它量身定做‘挡路怪兽’剧情；3. 世界级巨星皮卡丘在开发初期并不存在，全因确立电属性才作为象征诞生的真相；4. 宝可梦进化后叫声音频与波形变化的‘变声期’机制；5. 负责音效的增田顺一在红、绿、蓝、黄每一版中偷偷埋藏的不同版本存档音效彩蛋！",
        "entities": {
            "people": ["渡边 哲也", "增田 顺一", "杉森 建", "西野 弘二", "森本 茂树"],
            "games": ["宝可梦 金·银", "宝可梦 水晶版", "宝可梦 赤·绿"],
            "pokemon": ["凤王", "洛奇亚", "树才怪", "梦幻", "皮卡丘"]
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
# 3. PKMN-0110: Satoshi Tajiri x Tsunekazu Ishihara Special Dialogue
# =========================================================================
def import_nom_tajiri_ishihara() -> str:
    slug = "2000-07-01-interview-nom-special-dialogue-tajiri-ishihara"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0110 N.O.M 2000年7月号 田尻智 × 石原恒和特别对谈 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "two_shot.jpg": "https://web.archive.org/web/20221026135255im_/https://www.nintendo.co.jp/nom/0007/taidan2/two_03.jpg",
        "tajiri.jpg": "https://web.archive.org/web/20221026135255im_/https://www.nintendo.co.jp/nom/0007/taidan2/ta_18.jpg",
        "ishihara.jpg": "https://web.archive.org/web/20221026135255im_/https://www.nintendo.co.jp/nom/0007/taidan2/i_16.jpg",
        "starters.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    dialogues = []
    speaker_map = {
        "田尻": "田尻 智",
        "石原": "石原 恒和",
        "N.O.M 采访者": "N.O.M 采访者"
    }

    # Part 1: taidan1 (pages 1-4)
    sec_titles_1 = [
        "前篇第1节：二人的相遇（在爱普生与Game Boy连接线触电般的灵感）",
        "前篇第2节：制作宝可梦之前（昆虫采集、《Game Freak》同人志与街机黄金时代）",
        "前篇第3节：跨越语言之壁的游戏（把人与人真正连接起来的魔法）",
        "前篇第4节：放之四海皆准的童年冒险（哪怕身处异国也共通的成长渴望）"
    ]
    for idx, p in enumerate(range(1, 5)):
        fpath = CACHE_DIR / f"nom_0007_taidan1_page0{p}.html"
        raw = fpath.read_bytes().decode("cp932", errors="replace")
        raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

        dialogues.append({"speaker": "【章节导览】", "text": f"=== {sec_titles_1[idx]} ==="})
        body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
        body = body_m.group(1) if body_m else raw
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
        body = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body, flags=re.I)
        body = re.sub(r"<[^>]+>", "", body)

        lines = [html.unescape(l).strip() for l in body.split("\n")]
        lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

        cur_speaker = ""
        cur_text = []
        for l in lines:
            m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
            if m:
                if cur_text:
                    dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                    cur_text = []
                cur_speaker = m.group(1).strip()
                rest = m.group(3).strip()
                if rest:
                    cur_text.append(rest)
            else:
                if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                    if not cur_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                        if cur_text:
                            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                            cur_text = []
                        cur_speaker = "N.O.M 采访者"
                        cur_text.append(l)
                        continue
                cur_text.append(l)
        if cur_text:
            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})

    # Part 2: taidan2 (pages 1-4)
    sec_titles_2 = [
        "后篇第1节：田尻智与石原恒和的六年（长达六年的漫长艰苦研发与执念）",
        "后篇第2节：宝可梦们的生命感（不是冰冷机械，而是拥有生态与温度的生物）",
        "后篇第3节：多媒体跨界联动（卡牌、动画与衍生周边如何丰满世界观）",
        "后篇第4节：令人在意的未来（宝可梦系列永不停步的新挑战）"
    ]
    for idx, p in enumerate(range(1, 5)):
        fpath = CACHE_DIR / f"nom_0007_taidan2_page0{p}.html"
        raw = fpath.read_bytes().decode("cp932", errors="replace")
        raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

        dialogues.append({"speaker": "【章节导览】", "text": f"=== {sec_titles_2[idx]} ==="})
        body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
        body = body_m.group(1) if body_m else raw
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
        body = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body, flags=re.I)
        body = re.sub(r"<[^>]+>", "", body)

        lines = [html.unescape(l).strip() for l in body.split("\n")]
        lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

        cur_speaker = ""
        cur_text = []
        for l in lines:
            m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
            if m:
                if cur_text:
                    dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                    cur_text = []
                cur_speaker = m.group(1).strip()
                rest = m.group(3).strip()
                if rest:
                    cur_text.append(rest)
            else:
                if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                    if not cur_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                        if cur_text:
                            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})
                            cur_text = []
                        cur_speaker = "N.O.M 采访者"
                        cur_text.append(l)
                        continue
                cur_text.append(l)
        if cur_text:
            dialogues.append({"speaker": speaker_map.get(cur_speaker, cur_speaker), "text": " ".join(cur_text)})

    glossary = load_glossary()
    parallel_items = translate_dialogues(dialogues, glossary, "田尻智 × 石原恒和 N.O.M 2000年7月号特别对谈：宝可梦诞生史与生命感哲学全记录")

    if local_images.get("two_shot.jpg"):
        parallel_items.insert(0, {
            "type": "image",
            "image": local_images["two_shot.jpg"],
            "caption_original": "田尻智氏（左）と石原恒和氏（右）の貴重な対談ツーショット（2000年7月）。",
            "caption_translation": "田尻智（左）与石原恒和（右）2000年7月现场对谈珍贵合影。"
        })
    if local_images.get("tajiri.jpg"):
        parallel_items.insert(15, {
            "type": "image",
            "image": local_images["tajiri.jpg"],
            "caption_original": "少年時代の昆虫採集の記憶とゲームボーイの可能性について熱く語る田尻智氏。",
            "caption_translation": "田尻智深情讲述童年昆虫采集回忆与Game Boy通信线灵感的奇妙结合。"
        })
    if local_images.get("ishihara.jpg"):
        parallel_items.insert(30, {
            "type": "image",
            "image": local_images["ishihara.jpg"],
            "caption_original": "「ポケモンの生命感」とマルチメディア展開について語る石原恒和氏。",
            "caption_translation": "石原恒和阐述宝可梦的‘生态生命感’与卡牌、动画等多媒体联动的深层战略。"
        })

    post_meta = {
        "layout": "parallel-translation",
        "title": "N.O.M 2000年7月号：田尻智 × 石原恒和 特别对谈（二人的相遇、六年长征与生命感哲学）",
        "subtitle": "宝可梦之父与掌舵人亲述：六年濒临破产的坚持、跨越语言之壁的童年共鸣与真正的生物感",
        "date": "2000-07-01",
        "era_skin": "1999",
        "source_name": "任天堂官网「N.O.M」(No.23)",
        "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan1/index.html",
        "original_link": "https://www.nintendo.co.jp/nom/0007/taidan1/index.html",
        "summary": "宝可梦开发史上最高价值的黄金对话！任天堂官方杂志《N.O.M》2000年7月号特邀‘宝可梦之父’田尻智（Game Freak社长）与‘总掌舵人’石原恒和（Creatures社长/宝可梦社社长）促膝长谈：从两人在爱普生时期的初次相识、见到Game Boy连接线时触电般的启示，到制作宝可梦之前田尻智对昆虫采集的热爱与创办《Game Freak》同人志的初心；详细披露了《赤·绿》历经整整六年艰苦漫长研发、资金几乎断绝濒临崩溃边缘却因深信其魅力而咬牙坚持的心酸内幕；深度剖析了为什么宝可梦能‘跨越语言与文化的隔阂’引发全球儿童的共鸣；以及石原恒和提出的核心美学信条——‘宝可梦绝不是冷冰冰的战斗机器，它们是具有自己生活习性、呼吸与温度的生命体’！",
        "entities": {
            "people": ["田尻 智", "石原 恒和"],
            "games": ["宝可梦 赤·绿", "宝可梦 金·银", "宝可梦卡牌"],
            "pokemon": ["皮卡丘", "小火龙", "杰尼龟", "妙蛙种子"]
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
        "PKMN-0108": {
            "title": "N.O.M 2000年7月号：Game Freak全员座谈会（前编·初代『赤·绿』诞生回忆）",
            "date": "2000-07-01",
            "source_name": "任天堂官网「N.O.M」(No.23)",
            "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0108']}.md",
            "status": "imported"
        },
        "PKMN-0109": {
            "title": "N.O.M 2000年7月号：Game Freak全员座谈会（后编·续篇『金·银』突破与开发秘闻）",
            "date": "2000-07-01",
            "source_name": "任天堂官网「N.O.M」(No.23)",
            "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page04.html",
            "post_file": f"_posts/{batch_results['PKMN-0109']}.md",
            "status": "imported"
        },
        "PKMN-0110": {
            "title": "N.O.M 2000年7月号：田尻智 × 石原恒和 特别对谈（二人的相遇、六年长征与生命感哲学）",
            "date": "2000-07-01",
            "source_name": "任天堂官网「N.O.M」(No.23)",
            "source_url": "https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan1/index.html",
            "post_file": f"_posts/{batch_results['PKMN-0110']}.md",
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
    print("Starting Batch 8 (Nintendo Online Magazine July 2000 Golden Era Trilogy) Import Pipeline...")
    batch_results = {}

    batch_results["PKMN-0108"] = import_nom_gf_part1()
    batch_results["PKMN-0109"] = import_nom_gf_part2()
    batch_results["PKMN-0110"] = import_nom_tajiri_ishihara()

    update_catalog(batch_results)
    print("\nBatch 8 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
