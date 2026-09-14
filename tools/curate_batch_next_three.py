"""Batch curate, clean, translate, and import 3 major Pokémon developer interviews:
1. Pokemon Peer (2010-09-10) - Sugimori, Ohmura, Ibe, Tanoue (Era Skin 2011)
2. Denfaminicogamer (2018-06-08) - Ishihara x Kawashima x Masuda (Era Skin 2019)
3. Famitsu E3 2019 (2019-06-13) - Masuda & Ohmori (Era Skin 2019)
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
如果是对话/采访形式（如“问：... 答：...”或“Sugimori: ...”），请准确识别出说话人(speaker)。
如果段落中有特定的背景设定、行业术语、人名梗或值得注释的地方，请填写在 note 字段中。

【说话人识别规范】：
- 明确标注角色名字或职务，如“提问”、“杉森建”、“大村祐介”、“井部真那”、“田上怜子”、“石原恒和”、“川岛优志”、“增田顺一”、“大森滋”等。
- 不要把整句问答混在 speaker 里。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名或职务（如'杉森建'，若无则留空字符串''）",
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
# 1. Pokemon Peer (2010-09-10)
# =========================================================================
def import_pokemon_peer():
    url = "https://www.pokebeach.com/2010/09/pokemon-peer-interview-translations"
    slug = "2010-09-10-interview-pokemon-peer-sugimori-ohmori-designers"
    print(f"\n========================================================")
    print("=== Importing #1: Pokemon Peer 2010 Designers Interview ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    artwork_map = {
        "victini.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/494.png",
        "snivy.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/495.png",
        "tepig.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/498.png",
        "oshawott.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/501.png",
        "pidove.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/519.png",
        "sewaddle.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/540.png"
    }
    local_images = {}
    for fn, u in artwork_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")

    bqs = re.findall(r'<blockquote>(.*?)</blockquote>', raw_html, re.DOTALL)
    ps = re.findall(r'<p>(.*?)</p>', bqs[0], re.DOTALL)

    speaker_map = {
        "Sugimori": "杉森建",
        "Oumura": "大村祐介",
        "Oomura": "大村祐介",
        "Ibe": "井部真那",
        "Tagami": "田上怜子",
        "Everyone": "全员"
    }

    raw_items = []
    for i, p in enumerate(ps):
        clean = re.sub(r'<[^>]+>', '', p).strip()
        clean = html.unescape(clean)
        if not clean:
            continue
        
        speaker = ""
        text = clean
        if p.strip().startswith("<b>") or clean.startswith("Today we’re") or clean.startswith("Between the 4") or clean.startswith("This time all") or clean.startswith("Then, you started") or clean.startswith("Mr. Oumura was") or clean.startswith("You combined") or clean.startswith("In order to design") or clean.startswith("That’s interesting"):
            speaker = "提问"
        else:
            m = re.match(r"^([A-Za-z]+):\s*(.*)", clean)
            if m:
                spk_raw = m.group(1)
                speaker = speaker_map.get(spk_raw, spk_raw)
                text = m.group(2)
        
        raw_items.append({"speaker": speaker, "text": text})

    print(f"Extracted {len(raw_items)} paragraphs from Pokemon Peer.")

    glossary = load_glossary()
    full_text = " ".join(it["text"] for it in raw_items)
    glossary_matches = find_glossary_matches(full_text, glossary)
    print(f"Found {len(glossary_matches)} glossary matches.")

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
        
        # Insert illustrative artworks at relevant points
        if i == 0 and "victini.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["victini.png"],
                "caption_original": "Victini, designed by Mana Ibe with an 'apple rabbit' motif to represent victory.",
                "caption_translation": "比克提尼：由井部真那以‘苹果兔’为原型设计，寓意胜利与无限能量，全国图鉴编号特殊设定为 #000。"
            })
        elif i == 14 and "snivy.png" in local_images and "oshawott.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["snivy.png"],
                "caption_original": "Snivy, designed by Reiko Tanoue based on a vine snake with European noble aesthetic.",
                "caption_translation": "藤藤蛇：由田上怜子基于‘藤蔓蛇’构思，并融入艾尔米塔什博物馆等欧洲贵族艺术气质设计。"
            })
            parallel_items.append({
                "type": "image",
                "image": local_images["oshawott.png"],
                "caption_original": "Oshawott, designed by Yusuke Ohmura after observing live sea otters at an aquarium.",
                "caption_translation": "水水獭：由大村祐介在水族馆实地观察海獭后设计，腹部贝壳兼具日式扇贝与武士刀元素。"
            })
        elif i == 35 and "sewaddle.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["sewaddle.png"],
                "caption_original": "Sewaddle, designed by Reiko Tanoue inspired by tailoring insects.",
                "caption_translation": "虫宝包：田上怜子凭借对昆虫习性的热爱，以会缝合树叶的卷叶象鼻虫为原型设计。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Pokemon Peer 官方专访：杉森建、大村祐介、井部真那与田上怜子谈《黑·白》设计秘辛",
        "original_title": "『Pokemon Peer』開発者インタビュー：杉森建、大村祐介、井部真那、田上怜子",
        "date": "2010-09-10",
        "era": "2010–2013 · NDS / 宝可梦 黑·白 黄金时期",
        "era_skin": "2011",
        "publication": "Pokemon Peer (ポケモン ピア) / Pokebeach",
        "source_kind": "mook_interview",
        "author": "Pokemon Peer Editorial / Translated by Bangiras (Pokebeach)",
        "translator": "Poke Amice Studio",
        "interviewee": "杉森建, 大村祐介, 井部真那, 田上怜子",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑·白", "杉森建", "大村祐介", "井部真那", "田上怜子", "怪兽设计", "御三家", "比克提尼", "藤藤蛇", "水水獭"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Pokemon Peer Official Mook / Pokebeach Archive",
            "url": url,
            "language": "en",
            "source_type": "official_mook"
        },
        "original_link": url,
        "summary": "2010 年 9 月宝可梦官方特刊《Pokemon Peer》深度专访 Game Freak 设计核心团队：艺术总监杉森建、角色与御三家设计师大村祐介、比克提尼设计师井部真那、藤藤蛇与虫宝包设计师田上怜子。访谈首次公开了第五世代 17 人设计团队每人设计约 10 只宝可梦的工作机制、从零开始捕捉活体生物动作的动物园/水族馆采风经历、比克提尼苹果兔造型的诞生、藤藤蛇融合贵族审美与蛇类异质感的平衡，以及水水獭和风武士风格的演进历程。",
        "entities": {
            "people": ["杉森建", "大村祐介", "井部真那", "田上怜子", "增田顺一"],
            "games": ["宝可梦 黑·白", "宝可梦 白金", "宝可梦 心金·魂银"],
            "pokemon": ["比克提尼", "藤藤蛇", "暖暖猪", "水水獭", "豆豆鸽", "虫宝包"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)


# =========================================================================
# 2. Denfaminicogamer (2018-06-08) Pokemon GO Miracle
# =========================================================================
def import_denfamini_go():
    url1 = "https://news.denfaminicogamer.jp/interview/180608"
    url2 = "https://news.denfaminicogamer.jp/interview/180608/2"
    slug = "2018-06-08-interview-denfaminicogamer-pokemon-go-miracle"
    print(f"\n========================================================")
    print("=== Importing #2: Denfaminicogamer Pokemon GO Miracle ===")
    print(f"URLs: {url1} & {url2}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    photo_map = {
        "group_main.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2018/06/a61c07e691ce92529dba78488b6fa4501.jpg",
        "ishihara_1.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2018/05/DSC1553-600x400.jpg",
        "kawashima_1.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2018/05/DSC1438-600x400.jpg",
        "masuda_1.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2018/05/DSC1458-600x400.jpg",
        "roundtable.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2018/05/DSC1538-600x400.jpg"
    }
    local_images = {}
    for fn, u in photo_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def extract_page_items(url, part_label):
        req = urllib.request.Request(url, headers=headers)
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
        raw = re.sub(r'<script.*?</script>', '', raw, flags=re.DOTALL | re.IGNORECASE)
        raw = re.sub(r'<style.*?</style>', '', raw, flags=re.DOTALL | re.IGNORECASE)

        m = re.search(r'<div class="post-content[^"]*">(.*?)<div class="author-area', raw, re.DOTALL)
        if not m:
            m = re.search(r'<article[^>]*>(.*?)</article>', raw, re.DOTALL)
        body = m.group(1) if m else ""

        elements = re.findall(r'<(h[23]|p)[^>]*>(.*?)</\1>', body, re.DOTALL | re.IGNORECASE)
        items = []
        current_spk = ""
        for tag, content in elements:
            clean = html.unescape(re.sub(r'<[^>]+>', '', content)).strip()
            if not clean:
                continue
            if "pic.twitter.com" in clean or "クリック" in clean or clean in ["1", "2", "3"] or "この記事をシェア" in clean:
                continue
            if clean in ["石原恒和氏", "川島優志氏", "増田順一氏", "目次"]:
                continue

            if tag in ["h2", "h3"]:
                items.append({"type": "heading", "speaker": "", "text": f"【{part_label}】{clean}"})
                current_spk = ""
            else:
                if clean.startswith("──") or clean.startswith("――") or clean.startswith("―"):
                    current_spk = "提问"
                    text = re.sub(r"^[―─]+\s*", "", clean)
                elif "（以下、石原氏）：" in clean or "石原氏：" in clean:
                    current_spk = "石原恒和"
                    text = re.sub(r"^.*?石原氏[）\)]?：\s*", "", clean)
                elif "（以下、川島氏）：" in clean or "川島氏：" in clean:
                    current_spk = "川岛优志"
                    text = re.sub(r"^.*?川島氏[）\)]?：\s*", "", clean)
                elif "（以下、増田氏）：" in clean or "増田氏：" in clean:
                    current_spk = "增田顺一"
                    text = re.sub(r"^.*?増田氏[）\)]?：\s*", "", clean)
                else:
                    m_spk = re.match(r"^([^：:]{2,8}[氏さん]?)[：:]\s*(.*)", clean)
                    if m_spk:
                        raw_spk = m_spk.group(1).replace("氏", "").replace("さん", "").strip()
                        spk_map = {"石原": "石原恒和", "川島": "川岛优志", "増田": "增田顺一"}
                        current_spk = spk_map.get(raw_spk, raw_spk)
                        text = m_spk.group(2).strip()
                    else:
                        text = clean
                
                if text and len(text) > 5:
                    items.append({"type": "speech", "speaker": current_spk, "text": text})
        return items

    items1 = extract_page_items(url1, "前篇")
    items2 = extract_page_items(url2, "后篇")
    all_raw = items1 + items2
    print(f"Total extracted items from Denfamini GO: {len(all_raw)}")

    glossary = load_glossary()
    full_text = " ".join(it["text"] for it in all_raw)
    glossary_matches = find_glossary_matches(full_text, glossary)

    parallel_items = []
    if "group_main.jpg" in local_images:
        parallel_items.append({
            "type": "image",
            "image": local_images["group_main.jpg"],
            "caption_original": "川島優志氏（Niantic）、石原恒和氏（株式会社ポケモン）、増田順一氏（ゲームフリーク）",
            "caption_translation": "从左至右：Niantic 副总裁川岛优志、宝可梦社长石原恒和、Game Freak 董事增田顺一。"
        })

    chunk_size = 8
    for i in range(0, len(all_raw), chunk_size):
        chunk = all_raw[i:i+chunk_size]
        print(f"   Translating chunk {i//chunk_size + 1}/{(len(all_raw)-1)//chunk_size + 1}...")
        segments = translate_chunk(chunk, glossary_matches)
        for seg in segments:
            parallel_items.append({
                "speaker": seg.get("speaker", ""),
                "original": seg.get("original", ""),
                "translation": seg.get("translation", ""),
                "note": seg.get("note", "")
            })
        
        if i == 18 and "ishihara_1.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["ishihara_1.jpg"],
                "caption_original": "石原恒和氏：『Ingress』のハイレベルプレイヤーであり、『ポケモン GO』の共同開発を即断。",
                "caption_translation": "石原恒和：身为《Ingress》高等级资深玩家，在会面约翰·汉克后当场促成了《Pokémon GO》的诞生。"
            })
        elif i == 48 and "kawashima_1.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["kawashima_1.jpg"],
                "caption_original": "川島優志氏：Nianticアジア統括本部長。Google時代のエイプリルフール企画から奔走した立役者。",
                "caption_translation": "川岛优志：Niantic 亚洲区副总裁，从 2014 年 Google 愚人节宝可梦挑战赛一路推动两家公司的联手。"
            })
        elif i == 84 and "masuda_1.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["masuda_1.jpg"],
                "caption_original": "増田順一氏：BGM作曲を手がけ、捕獲の「ボールを投げる手応え」を徹底的に監修。",
                "caption_translation": "增田顺一：亲自为本作作曲配乐，并反复调试精灵球抛掷触感与捕捉判定以保持宝可梦核心魅力。"
            })
        elif i == 120 and "roundtable.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["roundtable.jpg"],
                "caption_original": "前代未聞のリアル連動ゲームが起こした社会現象の舞台裏を語り合う3氏。",
                "caption_translation": "三位主创畅谈这场席卷全球的真实世界 AR 游戏奇迹与背后的技术抗压经历。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 电玩志三巨头对谈：石原恒和 × 川岛优志 × 增田顺一谈《Pokemon GO》奇迹与现实交汇",
        "original_title": "【ポケモンGOの奇跡】石原恒和×川島優志×増田順一が語る、前代未聞のリアル連動ゲームが起こした社会現象の舞台裏",
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
        "tags": ["Pokemon", "Pokemon GO", "石原恒和", "川岛优志", "增田顺一", "Niantic", "Game Freak", "AR", "位置游戏", "Ingress"],
        "archive_type": "interview_translation",
        "source": {
            "title": "電ファミニコゲーマー (Denfaminicogamer 2018-06-08)",
            "url": url1,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": url1,
        "summary": "2018 年 6 月，电玩志（Denfaminicogamer）集结宝可梦社长石原恒和、Niantic 亚太副总裁川岛优志、Game Freak 董事增田顺一展开里程碑级深度长篇对谈。访谈完整还原了《Pokémon GO》从 2014 年谷歌地图愚人节彩蛋、石原恒和作为高等级 Ingress 玩家与约翰·汉克一拍即合、到 2016 年夏全球服务器承受超出 50 倍极限洪峰的惊险时刻；同时深挖了增田顺一如何亲自为手机端编写战斗音乐、调校抛掷精灵球的触控物理手感，以及将宝可梦世界观无缝融入真实地理空间的哲学思考。",
        "entities": {
            "people": ["石原恒和", "川岛优志", "增田顺一", "约翰·汉克", "野村达雄"],
            "games": ["Pokémon GO", "Ingress", "宝可梦 红·绿", "精灵宝可梦 Let's Go！皮卡丘／Let's Go！伊布"]
        },
        "parallel_items": parallel_items
    }

    post_path = POSTS_DIR / f"{slug}.md"
    yaml_str = yaml.dump(post_meta, allow_unicode=True, sort_keys=False, width=1000)
    post_path.write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"\n[SUCCESS] Post written to {post_path.name} with {len(parallel_items)} items!")

    clean_post(post_path)


# =========================================================================
# 3. Famitsu E3 2019 (2019-06-13) SwSh Masuda & Ohmori
# =========================================================================
def import_famitsu_swsh():
    url = "https://www.famitsu.com/news/201906/13177936.html"
    slug = "2019-06-13-interview-famitsu-swsh-masuda-ohmori-e3"
    print(f"\n========================================================")
    print("=== Importing #3: Famitsu E3 2019 SwSh Masuda & Ohmori ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    artwork_map = {
        "grookey.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/810.png",
        "scorbunny.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/813.png",
        "sobble.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/816.png",
        "zacian.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/888.png",
        "zamazenta.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/889.png"
    }
    local_images = {}
    for fn, u in artwork_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")

    m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', raw_html, re.DOTALL)
    body = m.group(1) if m else raw_html

    ps = re.findall(r'<p>(.*?)</p>', body, re.DOTALL)

    raw_items = []
    current_spk = ""
    for p in ps:
        clean = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        if not clean:
            continue
        if "E3 2019情報まとめ" in clean or "特設サイト" in clean or "一部記事内容を修正致しました" in clean or "配信をキャプチャーしたもの" in clean:
            continue

        if clean.startswith("――") or clean.startswith("──"):
            current_spk = "提问"
            text = re.sub(r"^[―─]+\s*", "", clean)
        elif clean.startswith("増田　") or clean.startswith("増田：") or clean.startswith("増田 "):
            current_spk = "增田顺一"
            text = re.sub(r"^増田[　：\s]*", "", clean)
        elif clean.startswith("大森　") or clean.startswith("大森：") or clean.startswith("大森 "):
            current_spk = "大森滋"
            text = re.sub(r"^大森[　：\s]*", "", clean)
        else:
            text = clean

        raw_items.append({"speaker": current_spk, "text": text})

    print(f"Extracted {len(raw_items)} paragraphs from Famitsu E3 2019.")

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
        
        if i == 0 and "grookey.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["grookey.png"],
                "caption_original": "Grookey, Scorbunny, Sobble - the Galar region starter Pokémon.",
                "caption_translation": "敲音猴、炎兔儿、泪眼蜥：伽勒尔地区初学者宝可梦，开发团队强调了各自独特的个性与成长期待。"
            })
        elif i == 12 and "zacian.png" in local_images and "zamazenta.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["zacian.png"],
                "caption_original": "Zacian and Zamazenta, the legendary Pokémon of Pokémon Sword and Shield.",
                "caption_translation": "苍响与藏玛然特：《宝可梦 剑·盾》封面传说的宝可梦。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Fami通 E3 直击专访增田顺一与大森滋：《宝可梦 剑·盾》旷野地带、极巨化与全国图鉴决断",
        "original_title": "『ポケットモンスター ソード・シールド』の“いま聞きたいこと”について増田順一氏、大森滋氏を直撃。「連れて来られるポケモンの話」にも言及！【E3 2019】",
        "date": "2019-06-13",
        "era": "2017–2021 · Switch Microsite 触控时代",
        "era_skin": "2019",
        "publication": "ファミ通.com (Famitsu)",
        "source_kind": "web_magazine",
        "author": "ファミ通取材班 (Famitsu Editorial)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 大森滋",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "剑·盾", "增田顺一", "大森滋", "E3 2019", "旷野地带", "极巨化", "Pokemon Home", "全国图鉴", "伽勒尔地区"],
        "archive_type": "interview_translation",
        "source": {
            "title": "ファミ通.com (Famitsu 2019-06-13)",
            "url": url,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "2019 年 6 月洛杉矶 E3 展会期间，Fami通直击《宝可梦 剑·盾》制作人增田顺一与总监大森滋。访谈直面了玩家社区最关注的核心话题：针对《Pokemon Home》无法将全世代宝可梦带入剑盾的决断，增田顺一详尽阐述了硬件升级至 Nintendo Switch 后的全模型重构、高画质动作渲染时间成本以及 800+ 宝可梦对战数值平衡的现实抉择；大森滋则揭秘了旷野地带（Wild Area）无缝大地图视角自由控制、极巨化（Dynamax）与极巨团体战的机制初衷，以及第八世代御三家进化的设计方向。",
        "entities": {
            "people": ["增田顺一", "大森滋"],
            "games": ["宝可梦 剑·盾", "Pokémon HOME", "宝可梦 太阳·月亮"],
            "pokemon": ["敲音猴", "炎兔儿", "泪眼蜥", "苍响", "藏玛然特"]
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

    # 1. Update PKMN-0001 (Pokemon Peer)
    for it in data:
        if it.get("id") == "PKMN-0001" or "pokemon-peer" in it.get("url", ""):
            it["title"] = "Pokemon Peer 官方专访：杉森建、大村祐介、井部真那与田上怜子谈《黑·白》设计秘辛"
            it["original_title"] = "‘Pokemon Peer’ Interview Translations: Designing the Unova Pokémon"
            it["date"] = "2010-09-10"
            it["outlet"] = "Pokemon Peer (ポケモン ピア) / Pokebeach"
            it["people"] = ["杉森建", "大村祐介", "井部真那", "田上怜子"]
            it["post_file"] = "_posts/2010-09-10-interview-pokemon-peer-sugimori-ohmori-designers.md"
            it["status"] = "imported"
            it["era_skin"] = "2011"
            print("Updated PKMN-0001 in catalog.")
            break

    # 2. Update PKMN-0079 / PKMN-0678 (Denfamini GO)
    for it in data:
        if it.get("id") in ["PKMN-0079", "PKMN-0678"] or "180608" in it.get("url", ""):
            it["title"] = "电玩志三巨头对谈：石原恒和 × 川岛优志 × 增田顺一谈《Pokemon GO》奇迹与现实交汇"
            it["original_title"] = "【ポケモンGOの奇跡】石原恒和×川島優志×増田順一が語る、前代未聞のリアル連動ゲームが起こした社会現象の舞台裏"
            it["date"] = "2018-06-08"
            it["outlet"] = "電ファミニコゲーマー (Denfaminicogamer)"
            it["people"] = ["石原恒和", "川岛优志", "增田顺一"]
            it["post_file"] = "_posts/2018-06-08-interview-denfaminicogamer-pokemon-go-miracle.md"
            it["status"] = "imported"
            it["era_skin"] = "2019"
            print(f"Updated {it.get('id')} in catalog.")
            break

    # 3. Update PKMN-0013 (Famitsu E3 2019 SwSh)
    for it in data:
        if it.get("id") == "PKMN-0013" or "13177936" in it.get("url", ""):
            it["title"] = "Fami通 E3 直击专访增田顺一与大森滋：《宝可梦 剑·盾》旷野地带、极巨化与全国图鉴决断"
            it["original_title"] = "『ポケットモンスター ソード・シールド』の“いま聞きたいこと”について増田順一氏、大森滋氏を直撃。「連れて来られるポケモンの話」にも言及！【E3 2019】"
            it["date"] = "2019-06-13"
            it["outlet"] = "ファミ通.com (Famitsu)"
            it["people"] = ["增田顺一", "大森滋"]
            it["post_file"] = "_posts/2019-06-13-interview-famitsu-swsh-masuda-ohmori-e3.md"
            it["status"] = "imported"
            it["era_skin"] = "2019"
            print("Updated PKMN-0013 in catalog.")
            break

    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Catalog synchronization complete.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "peer":
        import_pokemon_peer()
        sync_catalog()
    elif action == "denfamini":
        import_denfamini_go()
        sync_catalog()
    elif action == "famitsu":
        import_famitsu_swsh()
        sync_catalog()
    elif action == "sync":
        sync_catalog()
    elif action == "all":
        import_pokemon_peer()
        import_denfamini_go()
        import_famitsu_swsh()
        sync_catalog()
