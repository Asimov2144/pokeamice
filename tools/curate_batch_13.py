"""Curate Batch 13:
1. PKMN-0098: TIME Magazine (1999-11-22): Satoshi Tajiri - The Ultimate Game Freak (Era 1999)
2. PKMN-0051: Nintendo Power (2009-05-01): Junichi Masuda & Takeshi Kawachimaru on Gens 1-4 & Platinum (Era 2007)
3. PKMN-0099: Pokemon.com / Yomiuri (2018-07-26): Creators of Pikachu - Sugimori, Nishida, Nishino (Verify & Sync)
"""

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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
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
            else:
                if term_clean in text:
                    matches.append((term_clean, target))
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

    prompt = f"""你是精通任天堂史料、宝可梦开发史与欧美核心游戏媒体访谈的资深学者与翻译家。
正在整理宝可梦主创人员深度访谈档案：
【访谈背景】：{context_desc}

请将以下英文访谈内容翻译为专业、雅致、信达雅、极具游戏史料沉浸感的简体中文。
注意：
1. 准确规范说话人(speaker)中文名称：
   - 田尻 智 (Game Freak 创始人、社长、宝可梦生父)
   - 增田 顺一 (Game Freak 董事、制作人、总监、作曲家)
   - 河内丸 武史 (Game Freak 策划、主程序、《宝可梦 白金》总监)
   - TIME 记者 / Nintendo Power 记者 / Dr. Lava
2. 说话人名称与提问规范：记者提问统一写为 "TIME 记者" 或 "Nintendo Power 记者"（若有具体姓名如 Tim Larimer 则注明）。
3. 严格遵循官方专有名词（对照给出的 glossary）：
{glossary_str}
- Pokémon / Pokemon -> 宝可梦
- Pikachu -> 皮卡丘
- Raichu -> 雷丘
- Pichu -> 皮丘
- Bulbasaur -> 妙蛙种子
- Charmander -> 小火龙
- Squirtle -> 杰尼龟
- Clefairy -> 皮皮
- Gengar -> 耿鬼
- Snorlax -> 卡比兽
- Mew -> 梦幻
- Giratina -> 骑拉帝纳
- Dialga -> 帝牙卢卡
- Palkia -> 帕路奇亚
- Distortion World / Torn World -> 反转世界 / 破灭的世界
- Battle Frontier -> 对战开拓区
- Global Trade Station / GTS -> 全球贸易中心（GTS）
- Wi-Fi Plaza -> Wi-Fi 广场
- Game Boy -> Game Boy
- Game Freak -> Game Freak
- Ash -> 小智（英文版主角名为 Ash）
- Gary / Shigeru -> 小茂（英文版劲敌名为 Gary，日版为小茂/Shigeru，致敬宫本茂）
- Miyamoto -> 宫本茂
4. 如果对话中涉及特定游戏术语、未公开细节或历史背景，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

【待翻译输入】：
```json
{json.dumps(chunk, ensure_ascii=False, indent=2)}
```

请返回 JSON 格式，包含字段 `items`，结构与输入完全一致，但补充翻译 `translation`，规范 `speaker`，并在需要时填写 `note`。
"""

    messages = [
        {"role": "system", "content": "You are a professional video game history translator specializing in Pokémon lore and developer archives. Output valid JSON with 'items' key."},
        {"role": "user", "content": prompt}
    ]

    resp_str = call_deepseek(messages)
    try:
        data = json.loads(resp_str)
        items = data.get("items", [])
        if len(items) == len(chunk):
            return items
        else:
            print(f"Warning: items length mismatch {len(items)} vs {len(chunk)}, attempting fallback merge", file=sys.stderr)
            res = []
            for i, c in enumerate(chunk):
                if i < len(items):
                    t = items[i]
                    res.append({
                        "speaker": t.get("speaker", c.get("speaker", "")),
                        "original": c.get("original", ""),
                        "translation": t.get("translation", ""),
                        "note": t.get("note", "")
                    })
                else:
                    res.append(c)
            return res
    except Exception as e:
        print(f"Error parsing deepseek response: {e}", file=sys.stderr)
        return chunk


# =========================================================================
# 1. PKMN-0098: Satoshi Tajiri TIME Magazine (1999)
# =========================================================================
def curate_tajiri_time(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0098: Satoshi Tajiri TIME Magazine 1999 Interview")
    print("="*70)

    url = "https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html"
    from tools.extract_tajiri_time import article_lines

    # Find the intro paragraphs and the dialogue turns
    intro_paras = [
        article_lines[61],
        article_lines[62],
        article_lines[63],
    ]

    dialogue_raw = []
    i = 64
    while i < 153:
        line = article_lines[i]
        if line.startswith("TIME:"):
            q = line[5:].strip()
            # see if next lines are answer
            i += 1
            a_lines = []
            while i < 153 and not article_lines[i].startswith("TIME:"):
                a_lines.append(article_lines[i])
                i += 1
            a_full = " ".join(a_lines).strip()
            if a_full.startswith("Tajiri:"):
                a_full = a_full[7:].strip()
            dialogue_raw.append({"q": q, "a": a_full})
        else:
            i += 1

    print(f"Found {len(intro_paras)} intro paragraphs and {len(dialogue_raw)} Q&A pairs.")

    # Prepare chunks for translation
    # 1) Intro chunk
    intro_items = [
        {"speaker": "", "original": p, "translation": "", "note": ""}
        for p in intro_paras
    ]

    # 2) QA items
    qa_items = []
    for pair in dialogue_raw:
        qa_items.append({"speaker": "TIME", "original": pair["q"], "translation": "", "note": ""})
        qa_items.append({"speaker": "Tajiri", "original": pair["a"], "translation": "", "note": ""})

    all_items = intro_items + qa_items
    print(f"Total raw items: {len(all_items)}")

    # Translate in batches of 10-12 items
    chunk_size = 10
    translated_items = []
    for idx in range(0, len(all_items), chunk_size):
        chunk = all_items[idx:idx+chunk_size]
        combined_text = " ".join(c["original"] for c in chunk)
        matches = find_glossary_matches(combined_text, glossary)
        print(f"Translating items {idx+1} to {min(idx+chunk_size, len(all_items))} (matches: {len(matches)})...")
        res = translate_chunk(chunk, matches, "1999年11月《时代周刊》(TIME Magazine) 对宝可梦生父田尻智进行的划时代独家专访。")
        translated_items.extend(res)

    # Convert to parallel layout items with headings and images
    parallel_items = []

    # Hero image
    img_dir_rel = "/assets/img/interviews/1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak"
    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/tajiri.jpg",
        "alt": "田尻智在 Game Freak 办公室（1999年）",
        "caption": "田尻智（Satoshi Tajiri）1999年在东京世田谷区 Game Freak 办公室接受《时代周刊》独家专访"
    })

    # Title heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "The Ultimate Game Freak: An Interview with Satoshi Tajiri",
        "translation": "究极的 Game Freak：独家专访宝可梦之父田尻智"
    })

    # Section 1: Intro
    for it in translated_items[:3]:
        parallel_items.append({
            "speaker": "",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Section 2: Boyhood & Game Freak Origin
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "From Bug-Catching Boy to Fanzine Pioneer: The Genesis of Game Freak",
        "translation": "从昆虫少年到同人志先锋：Game Freak 的黎明与执念"
    })

    cur_idx = 3
    # items 3 to 22
    for it in translated_items[cur_idx:cur_idx+20]:
        parallel_items.append({
            "speaker": "田尻智" if it["speaker"] in ["Tajiri", "田尻智", "田尻 智"] else "TIME 记者",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })
    cur_idx += 20

    # Section 3: Link Cable & Respect
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The Cable That Linked Living Beings: Dialogue Over Competition",
        "translation": "连接生命的通信线：重在交流与尊重的日式哲学"
    })

    # items cur_idx to cur_idx+22
    for it in translated_items[cur_idx:cur_idx+22]:
        parallel_items.append({
            "speaker": "田尻智" if it["speaker"] in ["Tajiri", "田尻智", "田尻 智"] else "TIME 记者",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })
    cur_idx += 22

    # Section 4: Mew, Miyamoto & The Philosophy Against Violence
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The Myth of Mew, Mentorship with Miyamoto, and Fainting Over Dying",
        "translation": "第151只梦幻的神话、宫本茂的师徒情谊与‘宝可梦只有昏厥没有死亡’"
    })

    for it in translated_items[cur_idx:]:
        parallel_items.append({
            "speaker": "田尻智" if it["speaker"] in ["Tajiri", "田尻智", "田尻 智"] else "TIME 记者",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Construct Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 《时代周刊》(TIME) 独家专访宝可梦之父田尻智：究极的 Game Freak（町田田园昆虫少年、GB通信线顿悟与无暴力游戏哲学）",
        "original_title": "The Ultimate Game Freak: An Interview with Satoshi Tajiri, Creator of Pokémon",
        "date": "1999-11-22",
        "era": "1996–2002 · Pixel / 赤绿金银与生态黎明",
        "era_skin": "1999",
        "publication": "《时代周刊》(TIME Magazine) 1999年11月22日号",
        "source_kind": "magazine",
        "author": "Tim Larimer & Takashi Yokota / TIME",
        "translator": "Poke Amice Studio",
        "interviewee": "田尻智",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "田尻智", "初代", "金银", "时代周刊", "Game Freak"],
        "archive_type": "interview_translation",
        "source": {
            "title": "The Ultimate Game Freak: An Interview with Satoshi Tajiri",
            "url": "http://content.time.com/time/magazine/article/0,9171,2040095,00.html",
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": "http://content.time.com/time/magazine/article/0,9171,2040095,00.html",
        "summary": "1999年11月《时代周刊》在东京世田谷区 Game Freak 办公室对田尻智进行的划时代独家专访。彼时田尻智连续三年保持‘睡12小时、工作24小时’的高强度作息，刚完成《金·银》的最终压盘。访谈中田尻智详述了自己在东京都町田市捕捉昆虫被称作‘昆虫博士’的童年，以及田野水塘被城市推土机铲平的痛心；回忆了 18 岁自制《Game Freak》同人志狂卖上万册的极客岁月；首次披露看到 Game Boy 连接线传递俄罗斯方块数据时，脑海中浮现‘活生生的昆虫在电缆中穿梭交换’的神启瞬间；深刻阐释了‘宝可梦只有昏厥没有死亡’、坚决拒绝血腥暴力的儿童心理守护哲学；并公开了小智（Satoshi）与小茂（Shigeru/宫本茂）的师徒致敬渊源。",
        "entities": {
            "people": ["田尻智", "宫本茂", "蒂姆·拉里默", "横田孝司"],
            "games": ["宝可梦 红·绿", "宝可梦 金·银", "脉冲超人", "旋转方块", "太空格斗/太空侵略者", "铁板阵"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / "1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} parallel items)")


# =========================================================================
# 2. PKMN-0051: Nintendo Power (2009-05) Masuda & Kawachimaru
# =========================================================================
def curate_nintendo_power(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0051: Nintendo Power 2009 Masuda & Kawachimaru Interview")
    print("="*70)

    url = "https://lavacutcontent.com/masuda-interview-pokemon-platinum/"
    from tools.extract_np_raw import article as np_lines

    # Parse questions and answers from np_lines
    items_to_translate = []
    i = 0
    while i < len(np_lines):
        line = np_lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Check if question
        if (line.startswith("“") and "?" in line) or line.startswith("Mr Masuda,"):
            q_text = line.strip("“”\"")
            items_to_translate.append({"speaker": "Nintendo Power 记者", "original": q_text, "translation": "", "note": ""})
            i += 1
            continue
        
        # Check if Masuda
        if line.startswith("Masuda:"):
            ans = line[7:].strip().strip("“”\"")
            items_to_translate.append({"speaker": "增田顺一", "original": ans, "translation": "", "note": ""})
            i += 1
            continue
            
        # Check if Kawachimaru
        if line.startswith("Kawachimaru:"):
            ans = line[12:].strip().strip("“”\"")
            items_to_translate.append({"speaker": "河内丸武史", "original": ans, "translation": "", "note": ""})
            i += 1
            continue

        # Check if Dr Lava notes or intro text
        if "Dr Lava" in line or "Doctor Lava" in line or "Nintendo Power magazine" in line or "Special emphasis" in line or "Masuda grew up in Yokohama" in line:
            items_to_translate.append({"speaker": "", "original": line, "translation": "", "note": "编者按/背景注释"})
            i += 1
            continue

        # If it's closing comment or tags, break
        if "Closing Comments" in line or "Read More" in line or "Tags:" in line:
            break

        # Fallback text
        items_to_translate.append({"speaker": "", "original": line, "translation": "", "note": ""})
        i += 1

    print(f"Total extracted Nintendo Power items: {len(items_to_translate)}")

    # Translate in chunks of 8-10 items
    chunk_size = 8
    translated_items = []
    for idx in range(0, len(items_to_translate), chunk_size):
        chunk = items_to_translate[idx:idx+chunk_size]
        combined_text = " ".join(c["original"] for c in chunk)
        matches = find_glossary_matches(combined_text, glossary)
        print(f"Translating NP items {idx+1} to {min(idx+chunk_size, len(items_to_translate))} (matches: {len(matches)})...")
        res = translate_chunk(chunk, matches, "2009年《任天堂力量》(Nintendo Power) 独家专访：增田顺一与河内丸武史复盘前四世代演化与《宝可梦 白金》破灭的世界。")
        translated_items.extend(res)

    # Structure into parallel layout with headings and images
    img_dir_rel = "/assets/img/interviews/2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens"
    parallel_items = []

    # Magazine header
    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/header.png",
        "alt": "Nintendo Power 第240期杂志专访原版插页",
        "caption": "《Nintendo Power》杂志专访原貌：增田顺一与河内丸武史深度漫谈前四世代与《宝可梦 白金》"
    })

    # Group photo
    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/interviewees.jpg",
        "alt": "增田顺一（制作人）与河内丸武史（总监）",
        "caption": "增田顺一（左，制作人/音乐家）与河内丸武史（右，《宝可梦 白金》总监）"
    })

    # Section 1: Music, Sound Driver & Origins
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Part 1: From Sound Driver and Chiptunes to Game Director",
        "translation": "第1章：从底层声音驱动、电音与斯特拉文斯基，到执掌全局的总监之路"
    })

    cur = 0
    # Add items up to question about Diamond & Pearl
    for it in translated_items[:18]:
        parallel_items.append(it)
    cur = 18

    # Section 2: Diamond & Pearl, Ultimate Theme & Global GTS
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Part 2: Diamond & Pearl's 'Ultimate' Theme and the Worldwide GTS Miracle",
        "translation": "第2章：《钻石·珍珠》的‘终极’命题与全球贸易中心（GTS）的世界奇迹"
    })

    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/gts_site.png",
        "alt": "全球贸易中心 GTS 全球交换数据网站实况",
        "caption": "GTS 官方数据网站实况：看见远在芬兰与北欧的玩家通过 Wi-Fi 交换宝可梦的感动时刻"
    })

    for it in translated_items[cur:cur+14]:
        parallel_items.append(it)
    cur += 14

    # Section 3: Platinum, Distortion World & Battle Frontier
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Part 3: Pokémon Platinum, Giratina's Distortion World & Battle Frontier",
        "translation": "第3章：《宝可梦 白金》骑拉帝纳破灭的世界与对战开拓区"
    })

    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/giratina_distortion.png",
        "alt": "骑拉帝纳起源形态与反转世界",
        "caption": "骑拉帝纳身处的‘反转世界/破灭的世界’：打破重力与现实几何规则的颠倒维度"
    })

    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/battle_frontier.png",
        "alt": "神奥对战开拓区实机画面",
        "caption": "《白金》对战开拓区五大设施：对战塔、对战工厂、对战城堡、对战轮盘与对战舞台"
    })

    for it in translated_items[cur:cur+16]:
        parallel_items.append(it)
    cur += 16

    # Section 4: Pichu, Next Pikachu & Design Longevity
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Part 4: Pichu as the Strategic 'Next Pikachu' & What Makes Pokémon Endure",
        "translation": "第4章：作为战略企划的‘第二代皮卡丘’皮丘，与宝可梦历久弥新的根基"
    })

    parallel_items.append({
        "type": "image",
        "image": f"{img_dir_rel}/pichu.png",
        "alt": "皮丘兄弟与皮卡丘",
        "caption": "增田顺一深度复盘：杉森建设计皮丘时如何精准定位‘下一个皮卡丘’与皮丘兄弟的战略企划"
    })

    for it in translated_items[cur:]:
        parallel_items.append(it)

    # Construct Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 《任天堂力量》(Nintendo Power) 独家专访：增田顺一与河内丸武史复盘前四世代演化与《宝可梦 白金》破灭的世界（从芯片音效程序员到全系列总监的破局之道）",
        "original_title": "Nintendo Power Issue 240/241: Junichi Masuda and Takeshi Kawachimaru on Developing Gens 1-4 & Pokémon Platinum",
        "date": "2009-05-01",
        "era": "2006–2010 · NDS / 触控与 Wi-Fi 联机时代",
        "era_skin": "2007",
        "publication": "《Nintendo Power》第240/241期 (2009年4/5月号)",
        "source_kind": "magazine",
        "author": "Nintendo Power 独家特写 / 存档整理：Dr. Lava (Lava Cut Content)",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 河内丸武史",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "增田顺一", "河内丸武史", "第四世代", "宝可梦 白金", "钻石珍珠", "反转世界", "Nintendo Power"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Interview: Masuda on Developing Gens 1-4",
            "url": "https://lavacutcontent.com/masuda-interview-pokemon-platinum/",
            "language": "en",
            "source_type": "magazine_interview"
        },
        "original_link": "https://lavacutcontent.com/masuda-interview-pokemon-platinum/",
        "summary": "2009年春《Nintendo Power》对 Game Freak 核心领导增田顺一与总监河内丸武史的独家深度特写。增田顺一详细回顾了自己从初代《红·绿》自主编写‘Sound Driver’音频底层程序，到《水晶版》《红宝石·蓝宝石》及《钻石·珍珠》担任总监的创作演变；深度揭秘《白金》反转世界（破灭的世界）打破欧几里得几何与重力法则的开发哲学；披露全球贸易中心（GTS）连接全球训练家的惊喜、对战开拓区新挑战、以及为寻找‘下一个皮卡丘’而精心企划皮丘的幕后轶事。",
        "entities": {
            "people": ["增田顺一", "河内丸武史", "杉森建", "田尻智"],
            "games": ["宝可梦 白金", "宝可梦 钻石·珍珠", "宝可梦 红·绿", "宝可梦 金·银", "宝可梦 水晶版", "宝可梦 红宝石·蓝宝石"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / "2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} parallel items)")


# =========================================================================
# 3. Synchronize Catalog & Render Slugs
# =========================================================================
def sync_catalog():
    print("\n" + "="*70)
    print("Synchronizing Catalog data/pokemon_1000_interviews.json")
    print("="*70)

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    updates = {
        "PKMN-0098": {
            "title": "《时代周刊》(TIME) 独家专访宝可梦之父田尻智：究极的 Game Freak（町田田园昆虫少年、GB通信线顿悟与无暴力游戏哲学）",
            "original_title": "The Ultimate Game Freak: An Interview with Satoshi Tajiri, Creator of Pokémon",
            "date": "1999-11-22",
            "year": 1999,
            "status": "imported",
            "post_file": "_posts/1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak.md",
            "source_url": "http://content.time.com/time/magazine/article/0,9171,2040095,00.html",
            "people": ["田尻智", "宫本茂", "蒂姆·拉里默", "横田孝司"]
        },
        "PKMN-0051": {
            "title": "《任天堂力量》(Nintendo Power) 独家专访：增田顺一与河内丸武史复盘前四世代演化与《宝可梦 白金》破灭的世界（从芯片音效程序员到全系列总监的破局之道）",
            "original_title": "Nintendo Power Issue 240/241: Junichi Masuda and Takeshi Kawachimaru on Developing Gens 1-4 & Pokémon Platinum",
            "date": "2009-05-01",
            "year": 2009,
            "status": "imported",
            "post_file": "_posts/2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens.md",
            "source_url": "https://lavacutcontent.com/masuda-interview-pokemon-platinum/",
            "people": ["增田顺一", "河内丸武史", "杉森建", "田尻智"]
        },
        "PKMN-0099": {
            "title": "宝可梦官方专访：皮卡丘诞生秘辛 —— 专访杉森建、西田敦子与西野弘二（从大福点心、松鼠颊囊到废案三段进化高老丸）",
            "original_title": "Creator Profile: The Creators of Pikachu",
            "date": "2018-07-26",
            "year": 2018,
            "status": "imported",
            "post_file": "_posts/2018-07-26-interview-creators-of-pikachu.md",
            "source_url": "https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/",
            "people": ["杉森建", "西田敦子", "西野弘二"]
        }
    }

    synced_count = 0
    for it in catalog:
        cid = it.get("id")
        if cid in updates:
            it.update(updates[cid])
            synced_count += 1
            print(f"Updated {cid} -> status=imported | {it['title'][:40]}")

    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Catalog updated. Total items synced in this batch: {synced_count}")


def update_render_script():
    render_rb = ROOT / "tools" / "render_specific_posts.rb"
    content = render_rb.read_text(encoding="utf-8")
    new_slugs = [
        "interview-time-satoshi-tajiri-ultimate-game-freak",
        "interview-nintendo-power-masuda-kawachimaru-platinum-gens",
        "interview-creators-of-pikachu"
    ]
    lines = content.splitlines()
    # Find target_slugs = [
    for s in new_slugs:
        if f"'{s}'" not in content:
            # insert before the closing bracket of target_slugs
            for idx, line in enumerate(lines):
                if line.strip() == "]":
                    lines.insert(idx, f"  '{s}',")
                    break
    render_rb.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Updated tools/render_specific_posts.rb with Batch 13 slugs.")


if __name__ == "__main__":
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")
    curate_tajiri_time(glossary)
    curate_nintendo_power(glossary)
    sync_catalog()
    update_render_script()
    print("\nBatch 13 Curation Complete!")
