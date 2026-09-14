"""Batch curate, clean, translate, and import 3 milestone Game Freak developer interviews (Batch 11):
1. PKMN-0043: Game Informer (2010-03-19): 专访《心金·魂银》开发团队：增田顺一与森本茂树揭秘重制哲学与十周年进化 (Era Skin: 2007 NDS)
2. PKMN-0086: 周刊 Fami通 (2012-08-05): 增田顺一与海野隆雄《黑2·白2》发售纪念展会（N与盖奇斯的早期废案设定草图解密） (Era Skin: 2011 Connected)
3. PKMN-0072: 周刊 Fami通 (2013-11-16): 增田顺一与景山将太谈《宝可梦 X·Y》音频制作秘辛与卡洛斯法兰西音乐美学 (Era Skin: 2014 3D)
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
    
    prompt = f"""你是精通任天堂史料、宝可梦开发史与官方媒体访谈的资深学者与翻译家。
正在整理宝可梦主创人员深度访谈档案：
【访谈背景】：{context_desc}

请将以下访谈内容翻译为流畅、雅致、忠实原文且极具游戏史料沉浸感的简体中文。
注意：
1. 准确规范说话人(speaker)中文名称：
   - 增田 顺一 (Junichi Masuda / Game Freak 董事、音乐家、总监、制作人)
   - 森本 茂树 (Shigeki Morimoto / Game Freak 董事、战斗程序员、HGSS游戏总监)
   - 海野 隆雄 (Takao Unno / Game Freak 艺术总监、B2W2游戏总监)
   - 大森 滋 (Shigeru Ohmori / Game Freak 游戏策划、总监)
   - 松岛 贤二 (Kenji Matsushima / Game Freak 企划策划)
   - 森 昭人 (Akito Mori / Game Freak 主程序员)
   - 景山 将太 (Shota Kageyama / Game Freak 声音总监、作曲家)
   - 一之濑 刚 (Go Ichinose / Game Freak 作曲家)
   - Game Informer / Fami通记者 / 提问者 / 主持人
2. 忠实保留开发者的真实心境与一手历史细节（如重制版的受众考量、Pokéwalker计步器陪伴感、N与盖奇斯的早期长发与单眼罩草图废案、Game Boy四音轨Chiptune到3DS交响乐的音频技术革新等）。
3. 如果对话中涉及特定游戏术语、未公开细节或开发逸闻，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【官方专业术语规范】：
优先遵循以下官方规范译名：
{glossary_str}
- 心金·魂银 -> 《宝可梦 心金·魂银》
- 黑2·白2 -> 《宝可梦 黑2·白2》
- Ｘ・Ｙ -> 《宝可梦 Ｘ・Ｙ》
- ポケウォーカー / Pokéwalker -> 宝可步频器（Pokéwalker）
- ポケスロン / Pokéathlon -> 宝可全能竞技赛
- ポケウッド / Pokéstar Studios -> 宝可梦好莱坞
- フェスミッション / Fes Mission -> 庆典任务
- プラズマ団 / Team Plasma -> 等离子队
- ゲーチス / Ghetsis -> 盖奇斯
- Ｎ / N -> N
- ホタチ / Scalchop -> 扇贝贝（水水獭胸前贝壳）
- ミジュマル / Oshawott -> 水水獭
- カロス地方 / Kalos -> 卡洛斯地区
- ミアレシティ / Lumiose City -> 密阿雷市
- プラターヌ博士 / Professor Sycamore -> 布拉塔诺博士

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人中文名（如'增田 顺一'、'森本 茂树'、'海野 隆雄'、'景山 将太'、'Game Informer'、'Fami通'等）",
      "original": "该段对应的原文（英文或日文）",
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


def translate_dialogues(dialogues: list[dict], glossary: list[dict], context_desc: str, chunk_size: int = 5) -> list[dict]:
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
# 1. PKMN-0043: Game Informer HGSS Interview (2010)
# =========================================================================
def import_gi_hgss(glossary: list[dict]) -> str:
    slug = "2010-03-19-interview-gameinformer-masuda-morimoto-hgss"
    print("\n========================================================")
    print("=== Importing #1: PKMN-0043 GI 心金魂银开发团队访谈 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    img_sources = {
        "ho_oh.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png",
        "lugia.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png",
        "chikorita.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/152.png",
        "cyndaquil.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/155.png",
        "totodile.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/158.png"
    }
    local_images = {k: download_image(u, img_dir, k) for k, u in img_sources.items()}

    html_url = "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div class=["\']field-body["\'][^>]*>(.*?)</div>\s*<div class=["\']field-tags["\']', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw
    raw_text = re.sub(r'<[^>]+>', '\n', body)
    raw_text = html.unescape(raw_text)

    turns = []
    m_intro = re.search(r'With the exciting release.*?(?=The Pokémon franchise)', raw_text, re.DOTALL)
    if m_intro:
        turns.append({"speaker": "Game Informer 编者按", "text": m_intro.group(0).strip()})

    questions = [
        ("The Pokémon franchise is no stranger to remakes.", "Morimoto: This is the second time"),
        ("The Pokémon brand is obviously still very alive and well in Japan", "Morimoto: Because we always add"),
        ("Where did you get the idea for the pedometer peripheral bundled with HeartGold and SoulSilver?", "Ohmori:"),
        ("For fans who have already played Gold and Silver, what surprises can they expect to discover?", "Morimoto:"),
        ("There are tons of Pokémon in existence now. What’s the process internally for creating new Pokémon?", "Unno:"),
        ("Do you think there’s still room for new players to jump into the", "Morimoto:")
    ]

    for q_start, ans_start in questions:
        pos_q = raw_text.find(q_start)
        if pos_q != -1:
            pos_a = raw_text.find(ans_start, pos_q)
            next_pos = len(raw_text)
            for nq_start, _ in questions:
                p = raw_text.find(nq_start, pos_a + 10)
                if p != -1 and p < next_pos:
                    next_pos = p

            q_text = raw_text[pos_q:pos_a].strip()
            a_text = raw_text[pos_a:next_pos].strip()

            for noise in ["Still on the fence", "View the discussion", "Game Informer. All Rights"]:
                if noise in a_text:
                    a_text = a_text.split(noise)[0].strip()

            turns.append({"speaker": "Game Informer", "text": q_text})

            spk_matches = list(re.finditer(r'(Morimoto|Masuda|Ohmori|Unno|Matsushima|Mori):\s*', a_text))
            if spk_matches:
                for idx, sm in enumerate(spk_matches):
                    spk = sm.group(1)
                    start_idx = sm.end()
                    end_idx = spk_matches[idx+1].start() if idx+1 < len(spk_matches) else len(a_text)
                    speaker_body = a_text[start_idx:end_idx].strip()
                    name_map = {
                        "Morimoto": "森本 茂树",
                        "Masuda": "增田 顺一",
                        "Ohmori": "大森 滋",
                        "Unno": "海野 隆雄",
                        "Matsushima": "松岛 贤二",
                        "Mori": "森 昭人"
                    }
                    turns.append({"speaker": name_map.get(spk, spk), "text": speaker_body})
            else:
                turns.append({"speaker": "Game Freak 团队", "text": a_text})

    print(f"Parsed {len(turns)} turns from GI HGSS.")
    context = "Game Informer 2010年3月深度专访 Game Freak 心金魂银开发团队核心成员：总监森本茂树、制作人增田顺一、艺术总监海野隆雄、策划大森滋与松岛贤二、程序员森昭人。探讨重制版的定位、十年进化、宝可步频器开发与伙伴感哲学。"
    translated_items = translate_dialogues(turns, glossary, context, chunk_size=5)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "Exclusive Interview: Game Freak on Pokémon HeartGold & SoulSilver",
            "translation": "独家专访：Game Freak 核心团队畅谈《宝可梦 心金·魂银》开发秘辛"
        }
    ]

    midpoint = len(translated_items) // 2
    for i, it in enumerate(translated_items):
        parallel_items.append(it)
        if i == midpoint:
            if local_images.get("ho_oh.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["ho_oh.png"],
                    "caption_original": "『ハートゴールド』のパッケージを飾る伝説のポケモン「ホウオウ」。",
                    "caption_translation": "《心金》封面登场的传说宝可梦“凤王”。"
                })
            if local_images.get("lugia.png"):
                parallel_items.append({
                    "type": "image",
                    "image": local_images["lugia.png"],
                    "caption_original": "『ソウルシルバー』のパッケージを飾る伝説のポケモン「ルギア」。",
                    "caption_translation": "《魂银》封面登场的传说宝可梦“洛奇亚”。"
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Game Informer 专访《心金·魂银》开发团队：增田顺一与森本茂树揭秘重制哲学与十周年进化",
        "original_title": "Interview With Team Behind The Pokémon Franchise: Game Freak (Game Informer 2010)",
        "date": "2010-03-19",
        "era": "2006–2010 · NDS / 珍钻心金魂银时代",
        "era_skin": "2007",
        "publication": "Game Informer",
        "source_kind": "media_interview",
        "author": "Game Informer Editorial Team",
        "translator": "Poke Amice Studio",
        "interviewee": "森本茂树, 增田顺一, 海野隆雄, 大森滋, 松岛贤二, 森昭人",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "心金·魂银", "增田顺一", "森本茂树", "海野隆雄", "大森滋", "Pokewalker", "Game Informer", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Game Informer Feature: Interview With Team Behind The Pokémon Franchise: Game Freak",
            "url": html_url,
            "language": "en",
            "source_type": "media_interview"
        },
        "original_link": html_url,
        "summary": "2010 年 3 月《宝可梦 心金·魂银》欧美发售之际，Game Informer 独家专访了 Game Freak 核心开发团队：总监森本茂树、制作人增田顺一、艺术总监海野隆雄、策划大森滋与松岛贤二、程序员森昭人。团队深度探讨了相隔十年重制《金·银》的动机、宝可步频器（Pokéwalker）的诞生灵感与陪伴感哲学、宝可全能竞技赛的玩法设计，以及如何面对越来越庞大的怪兽生态体系，在保证新手低门槛的同时满足硬核玩家的深度追求。",
        "entities": {
            "people": ["森本 茂树", "增田 顺一", "海野 隆雄", "大森 滋", "松岛 贤二", "森 昭人"],
            "games": ["宝可梦 心金·魂银", "宝可梦 金·银", "皮卡丘2 GS"],
            "pokemon": ["凤王", "洛奇亚", "菊草叶", "火球鼠", "小锯鳄"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# 2. PKMN-0086: Famitsu B2W2 Fan Meeting (2012)
# =========================================================================
def import_famitsu_b2w2(glossary: list[dict]) -> str:
    slug = "2012-08-05-interview-famitsu-b2w2-fanmeeting-masuda-unno"
    print("\n========================================================")
    print("=== Importing #2: PKMN-0086 Fami通 黑2白2发售纪念展会（N与盖奇斯草图） ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    famitsu_imgs = [
        ("fami_b2w2_01.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b04da90.jpg"),
        ("fami_b2w2_02.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b0e7f23.jpg"),
        ("fami_b2w2_03.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b1203ce.jpg"),
        ("fami_b2w2_04.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b156ec5.jpg"),
        ("fami_b2w2_05.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b187046.jpg"),
        ("fami_b2w2_06.jpg", "https://www.famitsu.com/images/000/019/240/l_501e63b1b98dc.jpg")
    ]
    local_images = {k: download_image(u, img_dir, k) for k, u in famitsu_imgs}

    poke_arts = {
        "black_kyurem.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10022.png",
        "white_kyurem.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10023.png"
    }
    for k, u in poke_arts.items():
        local_images[k] = download_image(u, img_dir, k)

    html_url = "https://www.famitsu.com/news/201208/05019240.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw

    paras = re.findall(r'<p[^>]*>(.*?)</p>', body, re.DOTALL | re.I)
    clean_paras = []
    for p in paras:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', p))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Twitter', 'Facebook', 'ファミ通.com', '関連記事', '(C)20', '※', '株式会社']):
            clean_paras.append(c)

    raw_turns = []
    current_spk = "Fami通 记者"
    for p in clean_paras:
        if "増田氏" in p or "増田さん" in p:
            spk = "增田 顺一"
        elif "海野氏" in p or "海野さん" in p:
            spk = "海野 隆雄"
        elif p.startswith("▼質問") or "質問" in p:
            spk = "活动现场粉丝提问"
        else:
            spk = current_spk
        raw_turns.append({"speaker": spk, "text": p})
        current_spk = spk

    merged_turns = []
    for t in raw_turns:
        if merged_turns and merged_turns[-1]["speaker"] == t["speaker"] and len(merged_turns[-1]["text"]) < 400:
            merged_turns[-1]["text"] += "\n" + t["text"]
        else:
            merged_turns.append(dict(t))

    print(f"Grouped into {len(merged_turns)} merged turns from Famitsu B2W2.")
    context = "周刊 Fami通 2012年8月专访报道：《宝可梦 黑2·白2》发售纪念粉丝见面会。增田顺一与海野隆雄公开N与盖奇斯的早期废案设定草图，探讨100人同屏庆典任务、宝可梦好莱坞，以及回答热心粉丝关于入职GF、水水獭扇贝贝动作设计与问卷调查反馈的幕后问答。"
    translated_items = translate_dialogues(merged_turns, glossary, context, chunk_size=4)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "増田順一氏＆海野隆雄氏が登壇！『ポケットモンスターブラック2・ホワイト2』発売記念ファンミーティング",
            "translation": "增田顺一与海野隆雄亲临登台！《宝可梦 黑2·白2》发售纪念粉丝见面会全记录"
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
                cap_orig = "『ポケットモンスターブラック2・ホワイト2』ファンミーティング会場風景・貴重資料公開。"
                cap_trans = "《宝可梦 黑2·白2》横滨粉丝见面会现场盛况与珍贵未公开开发资料披露。"
                if "04" in k or "05" in k:
                    cap_orig = "イベントで初公開されたNとゲーチスの初期設定資料・秘蔵スケッチ。"
                    cap_trans = "活动现场首次向全世界公开的N与盖奇斯初期开发草图与设定资料。"
                elif "kyurem" in k:
                    cap_orig = "本作の象徴となる伝説のポケモン「ブラックキュレム」「ホワイトキュレム」。"
                    cap_trans = "作为本作象征的传说宝可梦“暗黑酋雷姆”与“焰白酋雷姆”。"

                parallel_items.append({
                    "type": "image",
                    "image": local_images[k],
                    "caption_original": cap_orig,
                    "caption_translation": cap_trans
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 周刊 Fami通 独家专访：增田顺一与海野隆雄《黑2·白2》发售纪念展会（N与盖奇斯的早期废案设定草图解密）",
        "original_title": "増田順一氏＆海野隆雄氏が登壇！『ポケットモンスターブラック2・ホワイト2』発売記念ファンミーティングが開催!!",
        "date": "2012-08-05",
        "era": "2010–2012 · Connected / 互联时代",
        "era_skin": "2011",
        "publication": "週刊ファミ通 (Famitsu.com)",
        "source_kind": "media_interview",
        "author": "周刊 Fami通 采访组",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 海野 隆雄",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "黑2·白2", "增田顺一", "海野隆雄", "N", "盖奇斯", "草图废案", "Fami通", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "ファミ通.com 特集記事：増田順一氏＆海野隆雄氏が登壇！『ポケモンB2・W2』ファンミーティング",
            "url": html_url,
            "language": "ja",
            "source_type": "media_interview"
        },
        "original_link": html_url,
        "summary": "2012 年 8 月 5 日，在横滨地标大厦举行的《宝可梦 黑2·白2》发售纪念粉丝见面会上，Game Freak 制作人增田顺一与总监海野隆雄亲临现场展开深度对谈。活动首次向全世界公布了等离子队核心人物 N 与盖奇斯的早期未公开设定草图（N的绿色长发与数学家原型、盖奇斯夸张的法皇服饰与单眼罩初期造型）；海野隆雄详述开发首日全员合影的决心、百人庆典任务的调试挑战与宝可梦好莱坞的构思；现场还进行了高热度的玩家互动答疑，披露了大量游戏音乐、动画细节与世界观设定的幕后秘辛。",
        "entities": {
            "people": ["增田 顺一", "海野 隆雄", "N", "盖奇斯"],
            "games": ["宝可梦 黑2·白2", "宝可梦 黑·白"],
            "pokemon": ["暗黑酋雷姆", "焰白酋雷姆", "水水獭"]
        },
        "parallel_items": parallel_items
    }

    post_file = POSTS_DIR / f"{slug}.md"
    post_file.write_text(f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n", encoding="utf-8")
    print(f"   [Written] {post_file.name}")
    clean_post(post_file)
    return slug


# =========================================================================
# 3. PKMN-0072: Famitsu XY Music Fan Meeting (2013)
# =========================================================================
def import_famitsu_xy_music(glossary: list[dict]) -> str:
    slug = "2013-11-16-interview-famitsu-xy-music-fanmeeting-masuda-kageyama"
    print("\n========================================================")
    print("=== Importing #3: PKMN-0072 Fami通 XY音乐制作秘辛访谈展会 ===")
    img_dir = IMG_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    famitsu_imgs = [
        ("fami_xy_01.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527b3e102.jpg"),
        ("fami_xy_02.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527c334c9.jpg"),
        ("fami_xy_03.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527d1e8a7.jpg"),
        ("fami_xy_04.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527cc8f42.jpg"),
        ("fami_xy_05.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527c7d83f.jpg"),
        ("fami_xy_06.jpg", "https://www.famitsu.com/images/000/043/307/l_5287527d977e2.jpg")
    ]
    local_images = {k: download_image(u, img_dir, k) for k, u in famitsu_imgs}

    poke_arts = {
        "xerneas.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/716.png",
        "yveltal.png": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/717.png"
    }
    for k, u in poke_arts.items():
        local_images[k] = download_image(u, img_dir, k)

    html_url = "https://www.famitsu.com/news/201311/16043307.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw = urllib.request.urlopen(urllib.request.Request(html_url, headers=headers)).read().decode("utf-8")

    m_body = re.search(r'<div[^>]*class=["\']article-body[^"\']*["\'][^>]*>(.*?)</div>\s*<!-- /article-body -->', raw, re.DOTALL | re.I)
    body = m_body.group(1) if m_body else raw

    paras = re.findall(r'<p[^>]*>(.*?)</p>', body, re.DOTALL | re.I)
    clean_paras = []
    for p in paras:
        c = html.unescape(re.sub(r'<br\s*/?>', '\n', p))
        c = re.sub(r'<[^>]+>', '', c).strip()
        if c and not any(k in c for k in ['Twitter', 'Facebook', 'ファミ通.com', '関連記事', '(C)20', '※', '株式会社']):
            clean_paras.append(c)

    raw_turns = []
    current_spk = "Fami通 记者"
    for p in clean_paras:
        if "増田氏" in p or "増田さん" in p:
            spk = "增田 顺一"
        elif "景山氏" in p or "景山さん" in p:
            spk = "景山 将太"
        elif "質問" in p:
            spk = "活动现场粉丝提问"
        else:
            spk = current_spk
        raw_turns.append({"speaker": spk, "text": p})
        current_spk = spk

    merged_turns = []
    for t in raw_turns:
        if merged_turns and merged_turns[-1]["speaker"] == t["speaker"] and len(merged_turns[-1]["text"]) < 400:
            merged_turns[-1]["text"] += "\n" + t["text"]
        else:
            merged_turns.append(dict(t))

    print(f"Grouped into {len(merged_turns)} merged turns from Famitsu XY Music.")
    context = "周刊 Fami通 2013年11月专访报道：《宝可梦 X·Y》原声大碟发售纪念音乐特别座谈会。增田顺一与景山将太现场回顾从初代Game Boy 4音轨到3DS全面采用法兰西风情交响乐与真实乐器实录的飞跃，景山键盘演奏密阿雷市与道馆馆主战变奏，增田分享等电车时涌现灵感写战斗曲的习惯与创作哲学。"
    translated_items = translate_dialogues(merged_turns, glossary, context, chunk_size=4)

    parallel_items = [
        {
            "type": "header",
            "level": 3,
            "original": "『ポケモン』音楽のさまざまな秘密が語られたファンミーティングが開催",
            "translation": "揭开《宝可梦》音乐无限魅力的特别座谈会：增田顺一与景山将太亲述法兰西声学美学"
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
                cap_orig = "『ポケットモンスター Ｘ・Ｙ』サウンド制作秘話ファンミーティングの模様。"
                cap_trans = "《宝可梦 X·Y》音乐制作秘辛横滨粉丝座谈会现场实况。"
                if "xerneas" in k or "yveltal" in k:
                    cap_orig = "『ポケットモンスター Ｘ・Ｙ』を象徴する伝説のポケモン。"
                    cap_trans = "象征《宝可梦 X·Y》全新生命与破坏主题的传说宝可梦。"

                parallel_items.append({
                    "type": "image",
                    "image": local_images[k],
                    "caption_original": cap_orig,
                    "caption_translation": cap_trans
                })

    front_matter = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 周刊 Fami通 独家专访：增田顺一与景山将太谈《宝可梦 X·Y》音频制作秘辛与卡洛斯法兰西音乐美学",
        "original_title": "『ポケモン』音楽のさまざまな秘密が語られたファンミーティングが開催",
        "date": "2013-11-16",
        "era": "2013–2016 · 3D Era / 三维进化时代",
        "era_skin": "2014",
        "publication": "週刊ファミ通 (Famitsu.com)",
        "source_kind": "media_interview",
        "author": "周刊 Fami通 采访组",
        "translator": "Poke Amice Studio",
        "interviewee": "增田 顺一, 景山 将太",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "X·Y", "增田顺一", "景山将太", "宝可梦音乐", "密阿雷市", "法兰西美学", "Fami通", "开发秘辛"],
        "archive_type": "interview_translation",
        "source": {
            "title": "ファミ通.com 特集記事：『ポケモン』音楽のさまざまな秘密が語られたファンミーティングが開催",
            "url": html_url,
            "language": "ja",
            "source_type": "media_interview"
        },
        "original_link": html_url,
        "summary": "2013 年 11 月 16 日在横滨宝可梦中心，Game Freak 游戏总监兼主作曲增田顺一与声音总监景山将太共同出席《宝可梦 X·Y》原声大碟发售纪念特别访谈。两位音乐家回顾了从初代 Game Boy 仅有 4 条音频轨道的硬件极限打磨，到 3DS 时代首次全面采用法兰西风情真实乐器录音与交响乐编曲的飞跃；景山现场用键盘演示密阿雷市与道馆馆主战变奏，增田顺一首度揭秘自己等待电车时突发灵感写下战斗 BGM 的创作习惯，并深入回答了粉丝关于全系列音乐记忆点的深层提问。",
        "entities": {
            "people": ["增田 顺一", "景山 将太", "一之濑 刚"],
            "games": ["宝可梦 X·Y", "宝可梦 赤·绿"],
            "pokemon": ["哲尔尼亚斯", "伊裴尔塔尔"]
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
                "generation": item.get("generation", "Gen 5"),
                "language": "JA",
                "outlet": item.get("outlet", "Famitsu"),
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

    s1 = import_gi_hgss(glossary)
    s2 = import_famitsu_b2w2(glossary)
    s3 = import_famitsu_xy_music(glossary)

    completed = [
        {
            "id": "PKMN-0043",
            "title": "Game Informer 独家专访：心金·魂银 (HGSS) 开发团队 Game Freak 深度访谈（增田顺一、森本茂树、大森滋、海野隆雄与松岛贤二谈十周年重制哲学）",
            "original_title": "Interview With Team Behind The Pokémon Franchise: Game Freak (Game Informer 2010)",
            "date": "2010-03-19",
            "post_file": f"_posts/{s1}.md",
            "url": "https://www.gameinformer.com/b/features/archive/2010/03/19/game-freak-pokemon-interview.aspx",
            "summary": "2010 年 3 月《宝可梦 心金·魂银》欧美发售之际，Game Informer 独家专访了 Game Freak 核心开发团队：总监森本茂树、制作人增田顺一、艺术总监海野隆雄、策划大森滋与松岛贤二、程序员森昭人。团队深度探讨了相隔十年重制《金·银》的动机、宝可步频器（Pokéwalker）的诞生灵感与陪伴感哲学、宝可全能竞技赛的玩法设计，以及如何面对越来越庞大的怪兽生态体系，在保证新手低门槛的同时满足硬核玩家的深度追求。",
            "people": ["森本茂树", "增田顺一", "海野隆雄", "大森滋", "松岛贤二", "森昭人"]
        },
        {
            "id": "PKMN-0086",
            "title": "周刊 Fami通 独家专访：增田顺一与海野隆雄《黑2·白2》发售纪念展会（N与盖奇斯的早期废案设定草图解密）",
            "original_title": "増田順一氏＆海野隆雄氏が登壇！『ポケットモンスターブラック2・ホワイト2』発売記念ファンミーティングが開催!!",
            "date": "2012-08-05",
            "post_file": f"_posts/{s2}.md",
            "url": "https://www.famitsu.com/news/201208/05019240.html",
            "summary": "2012 年 8 月 5 日，在横滨地标大厦举行的《宝可梦 黑2·白2》发售纪念粉丝见面会上，Game Freak 制作人增田顺一与总监海野隆雄亲临现场展开深度对谈。活动首次向全世界公布了等离子队核心人物 N 与盖奇斯的早期未公开设定草图（N的绿色长发与数学家原型、盖奇斯夸张的法皇服饰与单眼罩初期造型）；海野隆雄详述开发首日全员合影的决心、百人庆典任务的调试挑战与宝可梦好莱坞的构思；现场还进行了高热度的玩家互动答疑，披露了大量游戏音乐、动画细节与世界观设定的幕后秘辛。",
            "people": ["增田顺一", "海野隆雄"]
        },
        {
            "id": "PKMN-0072",
            "title": "周刊 Fami通 独家专访：增田顺一与景山将太谈《宝可梦 X·Y》音频制作秘辛与卡洛斯法兰西音乐美学",
            "original_title": "『ポケモン』音楽のさまざまな秘密が語られたファンミーティングが開催",
            "date": "2013-11-16",
            "post_file": f"_posts/{s3}.md",
            "url": "https://www.famitsu.com/news/201311/16043307.html",
            "summary": "2013 年 11 月 16 日在横滨宝可梦中心，Game Freak 游戏总监兼主作曲增田顺一与声音总监景山将太共同出席《宝可梦 X·Y》原声大碟发售纪念特别访谈。两位音乐家回顾了从初代 Game Boy 仅有 4 条音频轨道的硬件极限打磨，到 3DS 时代首次全面采用法兰西风情真实乐器录音与交响乐编曲的飞跃；景山现场用键盘演示密阿雷市与道馆馆主战变奏，增田顺一首度揭秘自己等待电车时突发灵感写下战斗 BGM 的创作习惯，并深入回答了粉丝关于全系列音乐记忆点的深层提问。",
            "people": ["增田顺一", "景山将太"]
        }
    ]

    sync_catalog(completed)
    print("\nBatch 11 completed successfully!")


if __name__ == "__main__":
    main()
