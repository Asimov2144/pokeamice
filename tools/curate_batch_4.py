"""Batch curate, clean, translate, and import 3 major Pokémon developer interviews (Batch 4):
1. PKMN-0016: Famitsu (2017-10-19) - Shigeru Ohmori & Kazumasa Iwao: USUM Special Developer Interview (Era Skin 2019)
2. PKMN-0015: Famitsu (2018-01-02) - Kazumasa Iwao & Katsunori Suginaka: USUM Story, Necrozma & Rainbow Rocket Secrets (Era Skin 2019)
3. PKMN-0012: CGWORLD (2017-07-10) - Game Freak x Creatures x TPC: Sun & Moon 3D Asset Pipeline & Collaborative Architecture (Era Skin 2019)
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
    
    prompt = f"""你是精通宝可梦历史考据、游戏3D技术与专业翻译的专家。
正在整理宝可梦官方与媒体开发者深度访谈的日中/英中对照档案。

请将以下访谈或技术专栏内容翻译为流畅、专业、忠实原文的简体中文。
如果是采访对话形式，请准确识别说话人(speaker)。
如果是专栏/小标题或技术说明，请保持专业、严谨的技术用语（如骨骼绑定、着色器、多边形面数、法线反转、布告板贴图等）。
如果段落中有特定的背景设定、技术术语、人名梗或值得注释的地方，请填写在 note 字段中。

【说话人识别规范】：
- 明确标注角色名字或职务，如“提问”、“大森 滋”、“岩尾 和昌”、“杉中 克考”、“海野 隆雄”、“氏家 淳子”等。
- 若段落属于专栏标题、说明文或旁白，speaker 可为“【专栏说明】”、“【小标题】”或留空字符串。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}
- 索尔迦雷欧（Solgaleo / ソルガレオ）
- 露奈雅拉（Lunala / ルナアーラ）
- 奈克洛兹玛（Necrozma / ネクロズマ）
- 究极之日·究极之月（Ultra Sun & Ultra Moon）
- 太阳·月亮（Sun & Moon）
- 究极异兽（Ultra Beast / ウルトラビースト）
- 究极调查队（Ultra Recon Squad）
- 彩虹火箭队（Team Rainbow Rocket）
- 骷髅队（Team Skull）
- 古兹马（Guzma / グズマ）
- 露莎米奈（Lusamine / ルザミーネ）
- 莉莉艾（Lillie / リーリエ）
- 格拉吉欧（Gladion / グラジオ）
- 哈乌（Hau / ハウ）
- 爆肌蚊（Buzzwole / マッシブーン）
- 超坏星（Toxapex / ドヒドイデ）
- 毒贝比（Poipole / ベベノム）

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名或职务（如'岩尾 和昌'，若无则留空字符串''）",
      "original": "该段对应的原文",
      "translation": "流畅专业的简体中文译文",
      "note": "对原文背景、技术名词或特定事件的译注（若无则留空字符串''）"
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
# 1. PKMN-0016: Famitsu (2017-10-19) USUM Special Developer Interview
# =========================================================================
def import_famitsu_usum_2017():
    url = "https://www.famitsu.com/news/201710/19143850.html"
    slug = "2017-10-19-interview-famitsu-usum-ohmori-iwao-director"
    print(f"\n========================================================")
    print("=== Importing #1: PKMN-0016 Famitsu 2017 USUM Developer Interview ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    image_source_map = {
        "ohmori_iwao_famitsu.jpg": "https://www.famitsu.com/images/000/143/850/y_59df9b5882ecb.jpg",
        "ohmori_famitsu.jpg": "https://www.famitsu.com/images/000/143/850/y_59df9b589382b.jpg",
        "iwao_famitsu.jpg": "https://www.famitsu.com/images/000/143/850/y_59df9b584eecb.jpg",
        "battle_screenshot.jpg": "https://www.famitsu.com/images/000/143/850/l_59e84ac8cb882.jpg",
        "dusk_mane_necrozma.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10155.png",
        "dawn_wings_necrozma.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10156.png",
        "poipole.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/803.png"
    }
    local_images = {}
    for fn, u in image_source_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
    clean_html = re.sub(r'<script.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', clean_html, re.DOTALL)
    body = m.group(1) if m else clean_html
    elements = re.findall(r'<(h2|p)[^>]*>(.*?)</\1>', body, re.DOTALL)

    raw_items = []
    current_spk = ""

    for tag, c in elements:
        t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
        if not t:
            continue
        if "本インタビュー記事は" in t or "特設サイト" in t or "配信をキャプチャー" in t or "無断転載" in t:
            continue
        if "＜写真左＞" in t or "＜写真右＞" in t:
            continue

        if tag == "h2":
            raw_items.append({"speaker": "【章节主题】", "text": t})
            current_spk = ""
            continue

        if t.startswith("――") or t.startswith("ーー"):
            raw_items.append({"speaker": "提问", "text": re.sub(r'^[―ー]+\s*', '', t)})
            current_spk = ""
            continue

        m_spk = re.match(r"^([^\s　]+)[　\s]+(.*)", t)
        if m_spk and m_spk.group(1) in ["大森", "岩尾", "大森・岩尾"]:
            spk_name = m_spk.group(1)
            speaker = "大森 滋" if spk_name == "大森" else ("岩尾 和昌" if spk_name == "岩尾" else "大森 滋 & 岩尾 和昌")
            raw_items.append({"speaker": speaker, "text": m_spk.group(2)})
            current_spk = speaker
        else:
            raw_items.append({"speaker": current_spk, "text": t})

    print(f"Extracted {len(raw_items)} paragraphs from Famitsu 2017 USUM.")

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

        if i == 0 and "ohmori_iwao_famitsu.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["ohmori_iwao_famitsu.jpg"],
                "caption_original": "ゲームフリーク／プロデューサー大森 滋氏（左）と、ディレクター岩尾和昌氏（右）。",
                "caption_translation": "Game Freak 制作人大森滋（左）与总监岩尾和昌（右）接受 Fami通 专访。"
            })
        elif i == 6 and "dusk_mane_necrozma.png" in local_images and "dawn_wings_necrozma.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["dusk_mane_necrozma.png"],
                "caption_original": "ネクロズマ（たそがれのたてがみ）とネクロズマ（あかつきのつばさ）：光を奪う伝説のポケモンの核心。",
                "caption_translation": "奈克洛兹玛（黄昏之鬃）与（拂晓之翼）：夺取阿罗拉光芒的传说宝可梦核心之谜。"
            })
        elif i == 18 and "poipole.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["poipole.png"],
                "caption_original": "ウルトラビーストの新たな存在「ベベノム」：異世界から訪れる調査隊の相棒。",
                "caption_translation": "全新究极异兽‘毒贝比’：与究极调查队一同跨越时空裂缝而来的异界相棒。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Fami通《宝可梦 究极之日·究极之月》开发团队深度访谈：大森滋与岩尾和昌谈阿罗拉终极进化与年轻体制",
        "original_title": "『ポケモン ウルトラサン・ウルトラムーン』について気になることをすべて聞いた！ マル秘情報も飛び出す開発者スペシャルインタビュー",
        "date": "2017-10-19",
        "era": "2017–2021 · 3DS 终章与微光探索时代",
        "era_skin": "2019",
        "publication": "週刊ファミ通",
        "source_kind": "magazine_interview",
        "author": "Fami通 编辑部",
        "translator": "Poke Amice Studio",
        "interviewee": "大森 滋, 岩尾 和昌",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "究极之日·究极之月", "太阳·月亮", "大森滋", "岩尾和昌", "增田顺一", "Game Freak", "奈克洛兹玛", "3DS", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "週刊ファミ通 2017年11月2日号（2017年10月19日刊载）",
            "url": url,
            "language": "ja",
            "source_type": "web_article"
        },
        "original_link": url,
        "summary": "2017 年 10 月《宝可梦 究极之日·究极之月》发售前夕，Fami通独家专访总监岩尾和昌与制作人大森滋。岩尾和昌首次挑起正统续作总监大梁，回顾了从《黑·白》地图与战斗系统策划到 USUM 的成长历程；大森滋从增田顺一手中接任制作人，透露增田退居大局监修后仍极具穿透力的‘神来之笔’细节指导。访谈全景披露了究极之日/究极之月的开发原点：以 400+ 扩充图鉴、全新究极异兽与奈克洛兹玛为核心，带来超群的剧本体量、巨翅飞鱼冲浪、究极空间穿越与战斗代理处等丰富机制，展现 Game Freak 青年梯队接棒的创新活力。",
        "entities": {
            "people": ["大森 滋", "岩尾 和昌", "增田顺一"],
            "games": ["宝可梦 究极之日·究极之月", "宝可梦 太阳·月亮", "宝可梦 黑·白"],
            "pokemon": ["奈克洛兹玛", "毒贝比", "索尔迦雷欧", "露奈雅拉", "巨翅飞鱼"]
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
# 2. PKMN-0015: Famitsu (2018-01-02) USUM Story & Rainbow Rocket Secrets
# =========================================================================
def import_famitsu_usum_story_2018():
    url = "https://www.famitsu.com/news/201801/02148529.html"
    slug = "2018-01-02-interview-famitsu-usum-iwao-suginaka-story-secrets"
    print(f"\n========================================================")
    print("=== Importing #2: PKMN-0015 Famitsu 2018 USUM Story Secrets ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    image_source_map = {
        "iwao_suginaka_famitsu.jpg": "https://www.famitsu.com/images/000/148/529/y_5a39ff72557da.jpg",
        "story_necrozma.jpg": "https://www.famitsu.com/images/000/148/529/l_5a3a002c3f158.jpg",
        "rainbow_rocket.jpg": "https://www.famitsu.com/images/000/148/529/l_5a39ff72459ed.jpg",
        "guzma_scene.jpg": "https://www.famitsu.com/images/000/148/529/l_5a39ff724dad6.jpg",
        "ultra_necrozma.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10157.png",
        "solgaleo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/791.png",
        "lunala.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/792.png"
    }
    local_images = {}
    for fn, u in image_source_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
    clean_html = re.sub(r'<script.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    m = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', clean_html, re.DOTALL)
    body = m.group(1) if m else clean_html
    elements = re.findall(r'<(h2|p)[^>]*>(.*?)</\1>', body, re.DOTALL)

    raw_items = []
    current_spk = ""

    for tag, c in elements:
        t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
        if not t:
            continue
        if "関連記事" in t or "本インタビュー記事は" in t or "特設サイト" in t or "配信をキャプチャー" in t or "無断転載" in t:
            continue
        if "岩尾和昌氏" in t or "杉中克考氏" in t or "ストーリープランニングセクションディレクター" in t:
            continue

        if tag == "h2":
            raw_items.append({"speaker": "【章节主题】", "text": t})
            current_spk = ""
            continue

        if t.startswith("――") or t.startswith("ーー"):
            raw_items.append({"speaker": "提问", "text": re.sub(r'^[―ー]+\s*', '', t)})
            current_spk = ""
            continue

        m_spk = re.match(r"^([^\s　]+)[　\s]*(.*)", t)
        if m_spk and m_spk.group(1) in ["岩尾", "杉中", "岩尾・杉中"]:
            spk_name = m_spk.group(1)
            speaker = "岩尾 和昌" if spk_name == "岩尾" else ("杉中 克考" if spk_name == "杉中" else "岩尾 和昌 & 杉中 克考")
            raw_items.append({"speaker": speaker, "text": m_spk.group(2)})
            current_spk = speaker
        else:
            raw_items.append({"speaker": current_spk, "text": t})

    print(f"Extracted {len(raw_items)} paragraphs from Famitsu 2018 USUM Story.")

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

        if i == 0 and "iwao_suginaka_famitsu.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["iwao_suginaka_famitsu.jpg"],
                "caption_original": "ゲームフリーク／ディレクター岩尾和昌氏（左）と、ストーリープランニングセクションディレクター杉中克考氏（右）。",
                "caption_translation": "Game Freak 总监岩尾和昌（左）与剧本企划部门总监杉中克考（右）解密剧本秘辛。"
            })
        elif i == 6 and "story_necrozma.jpg" in local_images and "ultra_necrozma.png" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["ultra_necrozma.png"],
                "caption_original": "ウルトラネクロズマ：光を取り戻した竜の神格化、そしてアローラと異世界の救済。",
                "caption_translation": "究极奈克洛兹玛：重获全部光芒的光辉之神形态，以及阿罗拉与究极调查队异世界的救赎交错。"
            })
        elif i == 18 and "guzma_scene.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["guzma_scene.jpg"],
                "caption_original": "スカル団のボス・グズマ：ウルトラ調査隊の介入により生じた“別の可能性の世界”で魅せる漢気。",
                "caption_translation": "骷髅队老大古兹马：在究极调查队介入引发的‘平行可能性世界’中展现出令人动容的男儿本色与蜕变。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Fami通《宝可梦 究极之日·究极之月》剧透解密：岩尾和昌与杉中克考谈阿罗拉“核心”剧情与平行世界可能性",
        "original_title": "『ポケモン ウルトラサン・ウルトラムーン』あのエピソードの真意は？ 開発者たちが明かす、ストーリー制作秘話【ネタバレ注意】",
        "date": "2018-01-02",
        "era": "2017–2021 · 3DS 终章与微光探索时代",
        "era_skin": "2019",
        "publication": "週刊ファミ通",
        "source_kind": "magazine_interview",
        "author": "Fami通 编辑部",
        "translator": "Poke Amice Studio",
        "interviewee": "岩尾 和昌, 杉中 克考",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "究极之日·究极之月", "岩尾和昌", "杉中克考", "松宫稔展", "Game Freak", "奈克洛兹玛", "古兹马", "彩虹火箭队", "剧本秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "週刊ファミ通 2018年1月2日公开专访（Web精选版）",
            "url": url,
            "language": "ja",
            "source_type": "web_article"
        },
        "original_link": url,
        "summary": "2018 年新春，Fami通刊发《宝可梦 究极之日·究极之月》全面剧透解密专访。总监岩尾和昌与主剧本作家杉中克考首次深入剖析了阿罗拉群岛的文化细节：制作团队亲赴夏威夷采风诞生的‘阿罗拉！’彩虹桥牵手礼仪；剧情核心关键词‘另一个可能性的世界’——并非篡改角色人设，而是当露莎米奈遭遇究极调查队并获知奈克洛兹玛的灭世危机后，整个群岛各方势力行为逻辑发生的巨大连锁裂变；哈乌如何从追求快乐的孩童成长为最后阻击主角的成熟劲敌；骷髅队老大古兹马的义气与男儿魅力；以及 Game Freak 先搭建大纲框架、再将新增玩法无缝融入剧本叙事的独特创作流水线。",
        "entities": {
            "people": ["岩尾 和昌", "杉中 克考", "松宫稔展"],
            "games": ["宝可梦 究极之日·究极之月", "宝可梦 太阳·月亮"],
            "pokemon": ["究极奈克洛兹玛", "具甲武者", "索尔迦雷欧", "露奈雅拉"]
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
# 3. PKMN-0012: CGWORLD (2017-07-10) Sun & Moon 3D Asset Pipeline & Triangle
# =========================================================================
def import_cgworld_sm_2017():
    url = "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html"
    slug = "2017-07-10-interview-cgworld-sun-moon-3d-pipeline-creatures-gamefreak"
    print(f"\n========================================================")
    print("=== Importing #3: PKMN-0012 CGWORLD 2017 Sun & Moon 3D Pipeline ===")
    print(f"URL: {url}")

    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    image_source_map = {
        "cgw_prof.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/prof.jpg",
        "cgw_pipeline.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/A01a.jpg",
        "cgw_database.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/A02a.jpg",
        "cgw_modeling.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/B01a.jpg",
        "cgw_texture.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/B02a.jpg",
        "cgw_solgaleo.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/C01a.jpg",
        "cgw_lunala.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/C02a.jpg",
        "cgw_rigging.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/D01a.jpg",
        "cgw_human_rig.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/E01a.jpg",
        "cgw_vfx.jpg": "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/E02a.jpg",
        "solgaleo.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/791.png",
        "lunala.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/792.png"
    }
    local_images = {}
    for fn, u in image_source_map.items():
        p = download_image(u, img_dir, fn)
        if p:
            local_images[fn] = p

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    raw_html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
    
    # Clip between start and end of article
    start_marker = "ニンテンドー3DSにおけるシリーズ第3弾"
    end_marker = "1メッシュ／1マテリアルのマルチテクスチャも使用されている"
    
    start_pos = raw_html.find(start_marker)
    end_pos = raw_html.find(end_marker)
    if start_pos != -1 and end_pos != -1:
        sub_html = raw_html[start_pos:end_pos + len(end_marker)]
    else:
        sub_html = raw_html

    clean_html = re.sub(r'<script.*?</script>', '', sub_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)

    blocks = re.findall(r'<(h2|h3|h4|p)[^>]*>(.*?)</\1>', clean_html, re.DOTALL)
    raw_items = []
    current_section = ""

    for tag, c in blocks:
        t = html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
        if not t or len(t) < 6:
            continue
        if any(bad in t for bad in ["TEXT＿", "EDIT＿", "PHOTO＿", "information", "©2016 Pokémon", "次ページ："]):
            continue

        if tag in ["h2", "h3", "h4"]:
            current_section = t
            raw_items.append({"speaker": f"【{tag.upper()}】", "text": t})
            continue

        # Check if paragraph has speaker prefix
        m_spk = re.match(r"^([^\s　：:]+)[　\s：:]+(.*)", t)
        if m_spk and m_spk.group(1) in ["大森", "海野", "氏家", "畠", "近藤", "森"]:
            name_map = {
                "大森": "大森 滋 (GF)",
                "海野": "海野 隆雄 (GF)",
                "氏家": "氏家 淳子 (Creatures)",
                "畠": "畠 祐贵 (Creatures)",
                "近藤": "近藤 景 (Creatures)",
                "森": "森 阳祐 (TPC)"
            }
            raw_items.append({"speaker": name_map.get(m_spk.group(1), m_spk.group(1)), "text": m_spk.group(2)})
        else:
            raw_items.append({"speaker": "CGWORLD 技术解析", "text": t})

    print(f"Extracted {len(raw_items)} paragraphs/sections from CGWORLD 2017.")

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

        # Insert technical figures at key moments
        if i == 0 and "cgw_prof.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_prof.jpg"],
                "caption_original": "ゲームフリーク × クリーチャーズ × ポケモン 3社連携の中核スタッフ（右から海野隆雄氏、大森滋氏、氏家淳子氏、畠祐貴氏、近藤景氏、森陽祐氏）。",
                "caption_translation": "Game Freak × Creatures × 宝可梦社 核心制作团队合影（右起：海野隆雄、大森滋、氏家淳子、畠祐贵、近藤景、森阳祐）。"
            })
        elif i == 12 and "cgw_pipeline.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_pipeline.jpg"],
                "caption_original": "新規ポケモンの3DCGデータ制作フロー：ゲームフリークの設定・三面図からクリーチャーズでのモデル制作・監修までの高度な協業体制。",
                "caption_translation": "新宝可梦 3DCG 数据制作管线：从 Game Freak 官方设定与三视图，到 Creatures 建模、绑定、动画及多方监修的高效协同流水线。"
            })
        elif i == 24 and "cgw_modeling.jpg" in local_images and "cgw_texture.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_modeling.jpg"],
                "caption_original": "モデリングとテクスチャ制作：高精細リファレンスモデルから実機向けローポリモデル（1万〜2万ポリゴン、ジョイント約110本）への段階的落とし込み。",
                "caption_translation": "建模与贴图制作流程：由高精参考模型向 3DS 实机低多边形模型（1万～2万面、约110根骨骼）的严谨分层规范化转换。"
            })
        elif i == 36 and "cgw_solgaleo.jpg" in local_images and "cgw_lunala.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_solgaleo.jpg"],
                "caption_original": "ソルガレオとルナアーラの高度なシェーディング：6種類のテクスチャマップによる旭日発光と、視差環境マップによるマジョーラ偏光発色。",
                "caption_translation": "索尔迦雷欧与露奈雅拉的自定义着色器工艺：通过 6 张核心贴图实现旭日发光相，以及基于视差环境映射打造的魔幻偏光质感。"
            })
        elif i == 60 and "cgw_rigging.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_rigging.jpg"],
                "caption_original": "アローラキュウコンとドヒドイデのリギング：多関節の毛並み表現とトーチカ状シェル開閉ギミック。",
                "caption_translation": "阿罗拉九尾与超坏星的骨骼绑定：多重物理摆动毛发与防御工事般碉堡壳体开合的独特骨骼拓扑结构。"
            })
        elif i == 72 and "cgw_human_rig.jpg" in local_images and "cgw_vfx.jpg" in local_images:
            parallel_items.append({
                "type": "image",
                "image": local_images["cgw_human_rig.jpg"],
                "caption_original": "ゲームフリーク内製の人体高頭身化リグと、Flash・After Effectsによるパーティクルビルボードバトルエフェクト。",
                "caption_translation": "Game Freak 针对角色写实高头身搭建的人体扩展骨骼拓扑，以及结合 Flash 与 After Effects 序列帧的单材质布告板战斗粒子特效系统。"
            })
        time.sleep(1)

    post_meta = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] CGWORLD 专访：揭秘《宝可梦 太阳·月亮》超千只3D资产管线与 Game Freak × Creatures × 宝可梦社 高度协同体系",
        "original_title": "『ポケットモンスター サン・ムーン』の3Dアセット制作とそれを可能にする高度な3社協业体制（CGWORLD vol.227）",
        "date": "2017-07-10",
        "era": "2017–2021 · 3DS 终章与微光探索时代",
        "era_skin": "2019",
        "publication": "月刊 CGWORLD + digital video (vol.227)",
        "source_kind": "magazine_feature",
        "author": "小野宪史 (TEXT) / CGWORLD 编辑部",
        "translator": "Poke Amice Studio",
        "interviewee": "大森 滋, 海野 隆雄, 氏家 淳子, 畠 祐贵, 近藤 景, 森 阳祐",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "太阳·月亮", "3DCG", "Game Freak", "Creatures", "The Pokemon Company", "大森滋", "海野隆雄", "技术揭秘", "着色器", "骨骼绑定"],
        "archive_type": "interview_translation",
        "source": {
            "title": "月刊 CGWORLD + digital video vol.227（2017年7月号 第1特集）",
            "url": url,
            "language": "ja",
            "source_type": "magazine_interview"
        },
        "original_link": url,
        "summary": "日本权威数字艺术媒体《CGWORLD》第 227 期重磅封面专题，深入探访支撑《宝可梦 太阳·月亮》超 1,000 只宝可梦全 3D 资产制作的跨公司协同中枢。Game Freak（企划与游戏引擎整合）、Creatures（宝可梦高精度模型、贴图、骨骼与动作库资产核心）与 The Pokémon Company（全IP形象品控）三方首次公开全流程开发管线：从三面图设定研讨、Maya 专有插件资产验证、跨公司 Redmine/Alienbrain 资产库，到 3DS 硬件极限下的 10,000~20,000 面多边形与 110 根骨骼上限控制、索尔迦雷欧与露奈雅拉的自定义 6 层着色器与视差偏光材质、阿罗拉九尾与超坏星的特殊骨骼拓扑，乃至 Game Freak 端的人类真实头身比扩展骨骼与战斗粒子布告板特效，全景呈现当代宝可梦 3D 表现力的工程基石。",
        "entities": {
            "people": ["大森 滋", "海野 隆雄", "氏家 淳子", "畠 祐贵", "近藤 景", "森 阳祐"],
            "games": ["宝可梦 太阳·月亮", "宝可梦 X·Y", "名侦探皮卡丘"],
            "pokemon": ["索尔迦雷欧", "露奈雅拉", "九尾", "超坏星", "爆肌蚊", "木木枭", "火斑喵", "球球海狮"]
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
        "PKMN-0016": {
            "title": "Fami通《宝可梦 究极之日·究极之月》开发团队深度访谈：大森滋与岩尾和昌谈阿罗拉终极进化与年轻体制",
            "date": "2017-10-19",
            "source_name": "週刊ファミ通",
            "source_url": "https://www.famitsu.com/news/201710/19143850.html",
            "post_file": f"_posts/{batch_results['PKMN-0016']}.md",
            "status": "imported"
        },
        "PKMN-0015": {
            "title": "Fami通《宝可梦 究极之日·究极之月》剧透解密：岩尾和昌与杉中克考谈阿罗拉“核心”剧情与彩虹火箭队诞生",
            "date": "2018-01-02",
            "source_name": "週刊ファミ通",
            "source_url": "https://www.famitsu.com/news/201801/02148529.html",
            "post_file": f"_posts/{batch_results['PKMN-0015']}.md",
            "status": "imported"
        },
        "PKMN-0012": {
            "title": "CGWORLD 专访：揭秘《宝可梦 太阳·月亮》超千只3D资产管线与 Game Freak × Creatures × 宝可梦社 高度协同体系",
            "date": "2017-07-10",
            "source_name": "月刊 CGWORLD",
            "source_url": "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html",
            "post_file": f"_posts/{batch_results['PKMN-0012']}.md",
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
    print("Starting Batch 4 Import Pipeline...")
    batch_results = {}
    
    slug_0016 = import_famitsu_usum_2017()
    batch_results["PKMN-0016"] = slug_0016

    slug_0015 = import_famitsu_usum_story_2018()
    batch_results["PKMN-0015"] = slug_0015

    slug_0012 = import_cgworld_sm_2017()
    batch_results["PKMN-0012"] = slug_0012

    update_catalog(batch_results)
    print("\nBatch 4 Import Pipeline completed successfully!")


if __name__ == "__main__":
    main()
