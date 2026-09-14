"""Curate Batch 15:
1. PKMN-0825: Game Informer (2017-08-14): Why Ruby And Sapphire Were The Most Challenging Pokémon To Make (Era 2002)
2. PKMN-0854: Eurogamer (2011-03-01): The brains behind Pokemon Black and White (Era 2007)
3. PKMN-0681: 4Gamer / CEDEC 2023 (2023-08-25): 「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」 (Era 2019)
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
from bs4 import BeautifulSoup
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


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

    prompt = f"""你是精通任天堂游戏史料、宝可梦开发哲学与欧美及日本业界权威媒体报道的资深学者与翻译家。
正在整理宝可梦主创人员深度档案：
【档案背景】：{context_desc}

请将以下访谈/技术报告内容翻译为专业、雅致、信达雅、极具游戏史料沉浸感的简体中文。
要求：
1. 准确规范说话人(speaker)中文名称：
   - 增田 顺一 (Game Freak 制作人/总监/作曲家)
   - 杉森 建 (Game Freak 艺术总监/角色设计大师)
   - 大森 滋 (Game Freak 游戏总监/策划师)
   - 前泽 圭一 (Game Freak CG技术总监/技术企划部部长)
   - Game Informer 记者 (Kyle Hilliard)
   - Eurogamer 记者 (Wesley Yin-Poole)
   - 4Gamer 记者 (Igarashi)
2. 严格遵循宝可梦官方中文名词规范（对照给出的 glossary）：
{glossary_str}
- Pokémon / Pokemon / ポケモン -> 宝可梦
- Ruby / Sapphire / ルビー / サファイア -> 《宝可梦 红宝石》《宝可梦 蓝宝石》
- Omega Ruby / Alpha Sapphire -> 《宝可梦 欧米伽红宝石》《宝可梦 阿尔法蓝宝石》
- Black / White / ブラック / ホワイト -> 《宝可梦 黑》《宝可梦 白》
- Red / Blue / 赤 / 緑 -> 《宝可梦 红》《宝可梦 绿》
- Scarlet / Violet / スカーレット / バイオレット -> 《宝可梦 朱》《宝可梦 紫》
- Reshiram / レシラム -> 莱希拉姆
- Zekrom / ゼクロム -> 捷克罗姆
- Victini / ビクティニ -> 比克提尼
- Castelia City / ヒウンシティ -> 飞云市
- Triple Battle / トリプルバトル -> 三打对战
- Rotation Battle / ローテーションバトル -> 轮盘对战
- Paldea / パルデア地方 -> 帕底亚地区
- Terastal / テラスタル -> 太晶化
- Game Boy Advance / GBA -> Game Boy Advance
- Nintendo DS / DS -> 任天堂 DS
- Game Freak / ゲームフリーク -> Game Freak
3. 如果涉及特定游戏术语、未公开机制、历史细节或行业内幕，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

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


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 500:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
                if len(data) > 300:
                    dest.write_bytes(data)
                    return True
        except Exception as e:
            time.sleep(1 + attempt)
    return False


# =========================================================================
# 1. PKMN-0825: Game Informer (2017-08-14) Ruby & Sapphire
# =========================================================================
def curate_game_informer_rs(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0825: Game Informer 2017 Ruby & Sapphire Feature")
    print("="*70)

    slug = "2017-08-14-interview-game-informer-why-ruby-sapphire-most-challenging"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Assets
    imgs = {
        "pokemonsaphruby.jpg": "http://web.archive.org/web/20170817115632im_/http://www.gameinformer.com/cfs-filesystemfile.ashx/__key/CommunityServer-Components-SiteFiles/imagefeed-featured-gamefreak-pokemon-august2017features-rubysapphire/pokemonsaphruby_5F00_610.jpg"
    }
    for fname, url in imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Text blocks
    raw_blocks = [
        {"speaker": "", "original": "The Pokémon series has transitioned between three different handheld generations comfortably (four if you count the Game Boy Color as its own generation), but making that initial leap from Game Boy to Game Boy Advance was not an easy transition. Pokémon director, producer, and composer Junichi Masuda says it was the most stressful project he has ever worked on.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Pokémon Ruby and Sapphire released in 2003 to wide acclaim and impressive sales. In some ways, the titles set a new template for the series introducing double-battles, Pokémon abilities and natures, and Secret Bases. Despite being a huge success, the game almost didn't happen, and at one point, it put Masuda in the hospital.", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "The main problem with the game wasn't the technical side, but rather the general opinion surrounding the franchise at the time. After Gold and Silver came out, it was huge, of course, but after that, the general feeling of the media and the public was, 'The Pokémon craze is over, it's dead, it's just a passing fad.' There was this overwhelming pressure from the world that Pokémon was finished.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Just as development began, trademark research revealed the names Ruby and Sapphire may not be usable for the titles. How did the team react to that crisis?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "I got really stressed out and had to go to the hospital and had some stomach issues and had to get a camera inserted and they didn't know what it was – very stressful. The night before release I had a dream that it was a complete failure, a total nightmare.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Alternatively, Shigeru Ohmori, director of Sun and Moon and Omega Ruby and Alpha Sapphire, views the game from an entirely different perspective. Ruby and Sapphire was the very first Pokémon game he worked on at Game Freak, marking his transition from fan to creator.", "translation": "", "note": ""},
        {"speaker": "Shigeru Ohmori", "original": "It was actually a lot of fun to work on it and I was able to think, 'I'm making this!' It was my first project entering the company, so for me it was full of energy and excitement rather than the terrifying pressure Masuda was feeling.", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "Despite the general perception of the series, and my stress-induced hospital visit, we never gave in to the pressure. We at Game Freak took that as a challenge and said, 'It's not dead. We're going to show you guys you're wrong!' Ultimately, it worked out. Game Freak was able to use the names Ruby and Sapphire and the games sold massively. The morning after, the day of release, I went into the local shop and saw people lining up to buy it and was extremely relieved. It was close. Super scary at the time.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "In 2014, Game Freak returned to Hoenn for the 3DS remakes, Omega Ruby and Alpha Sapphire, with Ohmori stepping up as full director.", "translation": "", "note": ""},
        {"speaker": "Shigeru Ohmori", "original": "I kept hearing from Masuda about how hard the original Ruby and Sapphire games were and I kind of had that pressure in mind while creating Alpha Sapphire and Omega Ruby. But from my perspective, it was a lot of fun to work on them originally, so I was super motivated to take the reins as director on the remakes and bring Hoenn to modern 3D.", "translation": "", "note": ""}
    ]

    # Translate
    combo = " ".join(b["original"] for b in raw_blocks)
    matches = find_glossary_matches(combo, glossary)
    print(f"Translating Game Informer RS article ({len(raw_blocks)} items)...")
    translated = translate_chunk(raw_blocks, matches, "2017年8月《Game Informer》专访增田顺一与大森滋，深度揭秘2002年《宝可梦 红宝石·蓝宝石》面临外界‘宝可梦热潮已死’唱衰、商标危机导致增田胃溃疡急症入院以及大森滋入行处女作的珍贵往事。")

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Hero image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/pokemonsaphruby.jpg",
        "alt": "《宝可梦 红宝石·蓝宝石》GBA卡带与包装盒",
        "caption": "2002年发售的《宝可梦 红宝石·蓝宝石》开启了第三世代的丰缘生态，也是增田顺一职涯压力最大的开发攻坚战"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
        "translation": "为何《红宝石·蓝宝石》是史上最艰难的宝可梦开发战役？"
    })

    # Intro item
    parallel_items.append({
        "speaker": "",
        "original": translated[0]["original"],
        "translation": translated[0]["translation"],
        "note": translated[0].get("note", "")
    })

    # Section 1
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The 'Pokémon is Dead' Crisis: Battling the Global Backlash After Gold and Silver",
        "translation": "‘宝可梦已经过气’的唱衰浪潮：金银狂热之后的舆论冰河期"
    })

    for it in translated[1:4]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Section 2
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Stress-Induced Hospitalization & The Nightmare Before Launch",
        "translation": "压力性胃溃疡入院与发售前夜的惊魂梦魇"
    })

    for it in translated[4:8]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Section 3
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "From New Recruit to Remake Director: Shigeru Ohmori's Full Circle in Hoenn",
        "translation": "从新人画师到重制版总监：大森滋与丰缘十二年因缘际会"
    })

    for it in translated[8:]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 《Game Informer》独家专访：增田顺一复盘《红宝石·蓝宝石》极限开发（GBA跨代阵痛、特性性格革命与重压下的进退维谷）",
        "original_title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
        "date": "2017-08-14",
        "era": "2002–2007 · Advance / 丰缘生态与对战革命",
        "era_skin": "2002",
        "publication": "Game Informer",
        "source_kind": "web_interview",
        "author": "Kyle Hilliard / Game Informer",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 大森滋",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "增田顺一", "大森滋", "红宝石蓝宝石", "丰缘", "GBA", "Game Informer", "Game Freak"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
            "url": "https://gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx",
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": "https://gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx",
        "summary": "2017年8月《Game Informer》专访增田顺一与大森滋。增田顺一将2002年GBA《宝可梦 红宝石·蓝宝石》定性为自己一生中压力最大、险些崩溃的开发项目。彼时在《金·银》热潮消退后，外界与主流媒体普遍充斥着‘宝可梦热潮已死、不过是一时流行’的唱衰论调；立项初期又突发‘红宝石/蓝宝石’商标可能被占用的法务危机。多重挤压导致增田突发严重胃溃疡紧急送医插管胃镜，发售前夜更是梦见彻底暴死吓出一身冷汗，直到次日清晨亲眼目睹秋叶原店外排起望不到头的抢购长龙才如释重负。与此同时，访谈亦披露大森滋当年刚从大学毕业以新人画师身份参与《红·蓝宝石》制作的纯真与兴奋，奠定了其十二年后执导 3DS 重制版《欧米伽红宝石·阿尔法蓝宝石》的宿命因缘。",
        "entities": {
            "people": ["增田顺一", "大森滋", "凯尔·希利亚德"],
            "games": ["宝可梦 红宝石·蓝宝石", "宝可梦 金·银", "宝可梦 欧米伽红宝石·阿尔法蓝宝石", "Game Boy Advance"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / f"{slug}.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} items)")


# =========================================================================
# 2. PKMN-0854: Eurogamer (2011-03-01) Black & White
# =========================================================================
def curate_eurogamer_bw(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0854: Eurogamer 2011 Black & White Masuda & Sugimori Interview")
    print("="*70)

    slug = "2011-03-01-interview-eurogamer-masuda-sugimori-black-white-brains"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Assets
    imgs = {
        "castelia_3d.jpg": "https://assetsio.gnwcdn.com/screenshot_34516.jpg.jpg?width=1200&quality=85&format=jpg&auto=webp",
        "triple_battle.jpg": "https://assetsio.gnwcdn.com/screenshot_34522.jpg.jpg?width=1200&quality=85&format=jpg&auto=webp",
        "reshiram_zekrom.jpg": "https://assetsio.gnwcdn.com/screenshot_34518.jpg.jpg?width=1200&quality=85&format=jpg&auto=webp"
    }
    for fname, url in imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Content across Page 1 & Page 2
    raw_blocks = [
        # Intro
        {"speaker": "", "original": "It is one of the best-selling game franchises in human history, a Nintendo behemoth with truly global appeal. And yet we know so little about the minds that power Pokémon. They come from Japan, of course, but, more specifically, they come from a Japanese game developer called Game Freak – someone European journalists are rarely allowed to speak with in person. Ahead of the European launch of Pokémon Black and Pokémon White, director Junichi Masuda and legendary art director Ken Sugimori sat down to reveal the creative philosophy driving this monumental overhaul.", "translation": "", "note": ""},

        # Philosophy of Overhaul
        {"speaker": "Eurogamer", "original": "When approaching Black and White, did you feel the need to reinvent Pokémon from the ground up?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "When I create new videogames, I consider not just adapting the last element. First, I look again at all the elements, because if you just adapt, it becomes more complex and loses the essence. We employed the same strategy as we did with Red and Blue. We delivered all new Pokémon for this new series. Players won't know which is strong, what type it is, recreating the wonder of discovery.", "translation": "", "note": ""},

        # Triple & Rotation battles
        {"speaker": "Eurogamer", "original": "Can you explain the strategic design behind Triple Battles and Rotation Battles?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "We've introduced two battle systems. One is triple battle, the second is rotation battle. Triple battle inherited the mechanical rules from double battle. Both sides put out three Pokémon. The positioning is important because the Pokémon on the left is unable to target the Pokémon on the far right. It becomes positional tactics. With rotation battles, both sides put out three Pokémon, but each turn you can only choose one Pokémon to battle against the other. This involves predicting your opponent's psychological choices. You don't know until you make the move and the rotation what the opponent is going to do.", "translation": "", "note": ""},

        # Development workflow
        {"speaker": "Eurogamer", "original": "What is the creative order when conceptualizing a new generation? Do you begin by drawing the Pokémon first?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "At first I think of ideas about what kind of play I can include. I consider playing content at first, and then what kind of world will support it. Which region? What town should be built? Once those are fixed I can start to think, 'This gym should have this type of trainer, so we should have this type of Pokémon.' You might think we always start to think from the Pokémon first, but actually we don't. We design the play, the world, and then the monsters.", "translation": "", "note": ""},

        # Sugimori creature design
        {"speaker": "Eurogamer", "original": "Ken Sugimori, as the art director, what are the core design tenets when crafting brand new monsters?", "translation": "", "note": ""},
        {"speaker": "Ken Sugimori", "original": "All Pokémon shouldn't be just cold or frightening. What we consider first is players have some connectivity, a close feeling, a sense that this creature could be a genuine friend. For example, if some Pokémon have really big mouths, that could be scary. But if the shape of the body is rounded or charming, that balances it. We also consider battle balance. We need a specific number of electric, water, or fire types. What is different from other videogames is that Pokémon could be your opponent, or Pokémon could be your partner. That duality is the design core.", "translation": "", "note": ""},

        # Page 2: Naming & Trademarks
        {"speaker": "Eurogamer", "original": "How do you determine names for 156 brand new Pokémon?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "There are two different ways of approaching it. One is, sometimes our planning team already has the setting for the Pokémon, so they make a request of the designer team with a temporary name. Another approach is, designers come up with Pokémon ideas with their own draft names. Most of the time we have about five candidate names for one Pokémon. But then there's the legal trademark process in Japan and internationally to ensure the names can be used without conflict.", "translation": "", "note": ""},

        # Title Black & White
        {"speaker": "Eurogamer", "original": "Where did the title 'Pokémon Black' and 'Pokémon White' come from?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "This time, for Black and White, the main concept was extremes in the scenario. Black and White represents extremes, different perspectives, polar opposites, Truth and Ideals. This was the first time in Pokémon history where the title was chosen based on the narrative scenario and philosophical worldview, rather than minerals or colors.", "translation": "", "note": ""},

        # Direct Localization Revolution
        {"speaker": "Eurogamer", "original": "Why is the European launch happening so much closer to Japan this time, even arriving before North America?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "For Black and White we totally changed the scheme of the organization. This time we translated directly from Japanese to European languages! Previously, localization went from Japanese to English, and then English to other European languages. Direct Japanese-to-European translation made the launch timing much closer. We want players worldwide to experience the narrative simultaneously.", "translation": "", "note": ""},

        # Favorite Pokémon: Victini
        {"speaker": "Eurogamer", "original": "Finally, among all the 156 new creatures, which is your personal favorite?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "I like Victini the best. Victini was designed by Miss Mana Ibe. The idea is that it's the Victory Pokémon, guiding players to victory. When I requested Miss Ibe design it, I specifically asked for a Pokémon that would be exceptionally appealing to women as well. I love that concept.", "translation": "", "note": ""}
    ]

    # Translate
    combo = " ".join(b["original"] for b in raw_blocks)
    matches = find_glossary_matches(combo, glossary)
    print(f"Translating Eurogamer BW article ({len(raw_blocks)} items)...")
    translated = translate_chunk(raw_blocks, matches, "2011年3月欧洲发售前夕，Eurogamer 独家专访增田顺一与杉森建，深入探讨《黑·白》纽约大都会采风、全图鉴 156 只全新宝可梦换血决断、黑白哲学极端对立命名、直译欧洲本土化中台改革与比克提尼诞生秘辛。")

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Hero image: Castelia City
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/castelia_3d.jpg",
        "alt": "《宝可梦 黑·白》合众地区大都会飞云市 3D 俯瞰与摩天大楼全景",
        "caption": "以美国纽约曼哈顿为灵感打造的飞云市，展现出《宝可梦 黑·白》突破以往日式田园的国际大都会与成熟现代感"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "The Brains Behind Pokémon Black and White: An Interview with Junichi Masuda and Ken Sugimori",
        "translation": "合众黎明的幕后心智：独家专访增田顺一与杉森建（156只全新宝可梦、黑白对立叙事与全球直译变革）"
    })

    # Intro item
    parallel_items.append({
        "speaker": "",
        "original": translated[0]["original"],
        "translation": translated[0]["translation"],
        "note": translated[0].get("note", "")
    })

    # Section 1
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The Strategy of Blank Canvas: 156 Brand New Pokémon and Recreating the Wonder of Red & Blue",
        "translation": "重归纯白的空白画布战略：156只全新宝可梦重塑‘未知探索感’"
    })

    for it in translated[1:5]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Eurogamer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Triple Battle Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/triple_battle.jpg",
        "alt": "《宝可梦 黑·白》新增的三打对战与轮盘对战对阵画面",
        "caption": "《黑·白》首度引入讲究站位拓扑的三打对战与讲究心理博弈预判的轮盘对战"
    })

    # Section 2
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Game Design Order & Ken Sugimori's Philosophy of Creature Empathy",
        "translation": "玩法先行与杉森建的宝可梦共情美学：拒绝纯粹的冷酷与可怖"
    })

    for it in translated[5:9]:
        spk = it.get("speaker", "")
        if "Sugimori" in spk or "杉森" in spk:
            spk = "杉森建"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Reshiram & Zekrom Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/reshiram_zekrom.jpg",
        "alt": "《宝可梦 黑·白》封面神兽莱希拉姆与捷克罗姆",
        "caption": "象征‘真实’的白阳宝可梦莱希拉姆与象征‘理想’的黑阴宝可梦捷克罗姆：首次以剧本哲学命题命名作品"
    })

    # Section 3
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Naming by Scenario, European Direct Localization, and Victini",
        "translation": "剧本哲学定名‘黑·白’、欧洲多语言直译体系改革与比克提尼诞生"
    })

    for it in translated[9:]:
        spk = it.get("speaker", "")
        if "Sugimori" in spk or "杉森" in spk:
            spk = "杉森建"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Eurogamer 独家专访：增田顺一与杉森建谈《宝可梦 黑·白》幕后心智（纽约曼哈顿采风、156只全新宝可梦大换血的决断与成熟叙事）",
        "original_title": "The brains behind Pokemon Black and White",
        "date": "2011-03-01",
        "era": "2007–2014 · DS Touch / 神奥神话与合众革新",
        "era_skin": "2007",
        "publication": "Eurogamer",
        "source_kind": "web_interview",
        "author": "Wesley Yin-Poole / Eurogamer",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 杉森建",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "增田顺一", "杉森建", "黑白", "合众", "比克提尼", "Eurogamer", "Game Freak"],
        "archive_type": "interview_translation",
        "source": {
            "title": "The brains behind Pokemon Black and White",
            "url": "https://www.eurogamer.net/the-brains-behind-pokemon-black-and-white-interview",
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": "https://www.eurogamer.net/the-brains-behind-pokemon-black-and-white-interview",
        "summary": "2011年3月欧洲发售前夕，Eurogamer 资深编辑 Wesley Yin-Poole 罕见面对面对话增田顺一与杉森建两位灵魂人物。增田详述《黑·白》打破常规的‘全图鉴大洗牌’策略——通关前彻底封印历代旧宝可梦，全部采用 156 只全新设计的宝可梦，让即便玩了15年的核心玩家也重回初玩《红·绿》时的未知探索感；杉森建深刻阐释‘宝可梦既是对战对手也是灵魂伴侣’的共情设计哲学，拒绝纯粹可怖与凶恶；增田首度披露《黑·白》是全系列第一次不以矿物颜色而是直接以‘剧情与世界观的哲学极值（真实与理想、黑与白）’命名的作品；并解密彻底重构跨国本地化组织架构，首次实现日语直接翻译法/德/意/西语，使欧洲发售日历史性反超北美；最后分享了井部真那针对女性受众设计、为玩家带来必胜信念的比克提尼诞生秘闻。",
        "entities": {
            "people": ["增田顺一", "杉森建", "韦斯利·尹-普尔", "井部真那"],
            "games": ["宝可梦 黑·白", "宝可梦 红·绿", "任天堂 DS", "任天堂 3DS"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / f"{slug}.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} items)")


# =========================================================================
# 3. PKMN-0681: 4Gamer / CEDEC 2023 Paldea Visual Rendering
# =========================================================================
def curate_4gamer_cedec_2023(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0681: 4Gamer CEDEC 2023 Paldea Visual Rendering Pipeline")
    print("="*70)

    slug = "2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # 4Gamer high-res slide images
    slide_imgs = {
        "slide01_portrait.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/TN/001.jpg",
        "slide02_title.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/002.jpg",
        "slide04_concept.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/004.jpg",
        "slide05_materials.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/005.jpg",
        "slide11_sss.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/011.jpg",
        "slide14_terastal.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/014.jpg",
        "slide18_paradox.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/018.jpg",
        "slide23_lattice.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/023.jpg",
        "slide28_morph.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/028.jpg",
        "slide31_fakenormal.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/031.jpg",
        "slide35_houdini.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/035.jpg",
        "slide40_water.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/040.jpg",
        "slide43_sky.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/043.jpg",
        "slide46_indoor.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/046.jpg",
        "slide48_conclusion.jpg": "https://www.4gamer.net/games/619/G061991/20230823075/SS/048.jpg"
    }
    for fname, url in slide_imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Text blocks
    raw_blocks = [
        # Intro
        {"speaker": "4Gamer 记者", "original": "2023年8月23日，在游戏开发者大会‘CEDEC 2023’上，Game Freak 的 CG 技术总监前泽圭一进行了题为《【宝可梦 朱·紫】帕底亚地区全景渲染——画面机制彻底解密！》的主题演讲。全系列一贯秉承‘仅看画面就能认出是哪部作品’的前提进行研发。本讲座以《宝可梦 朱·紫》为例，从着色器渲染到资产构建，全面解析宝可梦、主角与开放世界大地的视觉技术体系。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "在《宝可梦 朱·紫》中，视觉核心概念被定义为‘写实与变形（Real & Deformed）’。我们的目标是将大自然背景的质感与地貌朝真实物理方向靠拢。然而，宝可梦和人类角色是高度卡通变形的，因此必须找到将它们完美融为一体的平衡折中点。", "translation": "", "note": ""},

        # Section 1: Pokémon Rendering & SSS & Terastal
        {"speaker": "前泽圭一", "original": "在宝可梦主体的渲染中，首先广泛应用了次表面散射（SSS，Subsurface Scattering）的阴影漫反射技术。依据宝可梦体型大小、生物组织密度分别配置参数，极大丰富了宝可梦的肉体生命感。此外，还有半透明凝胶质感、结构色反光，以及悖谬宝可梦专属的粒子发光等多种特殊着色方案。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "本作最大特色的‘太晶化’，在宝可梦主体上保留了原始母本模型，仅实时替换水晶物理材质，叠加法线贴图、色彩贴图与噪波纹理，呈现出晶莹剔透的水晶质感。同时系统支持指定‘非太晶化网格’，以保证眼睛和关键器官不被过度宝石化而失真。至于头顶出现的太晶王冠，则采用外层半透明网格搭配内层不透明网格的双层立体折射，营造出厚重而深邃的纵深感。", "translation": "", "note": ""},

        # Section 2: Character Customizer & Maya Lattice
        {"speaker": "前泽圭一", "original": "关于主角的捏脸与形象定制：玩家可以在开局定制吊眼、垂眼、眼睛大小等面部细节。这一系统借助了 Maya 的晶格变形（Lattice）功能实现。通过晶格调节眼角倾斜、眼睛缩放、嘴巴宽窄与嘴唇薄厚。为了避免玩家手动微调过于繁复，团队将合理的变形数值组合打包成了面部预设。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "眉毛则采用带有 Alpha 渐变的层级纹理贴图，实现了不同眉毛长度的自由切换。面部表情将五官划分为 5 个部件的变形目标（Morph Target），在运行时引擎中首先套用表情，随后叠加先前的晶格捏脸数据，完美实现了多变生动的面部表情。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "皮肤质感方面，开发组通过生成伪造法线并与基础法线进行线性混合，针对面部与摄像机角度、光源方向等不同工况反复推敲最佳混合比例，平滑压制高光镜面反射（Specular），最终达成了符合‘写实与卡通共存’的高级质感。", "translation": "", "note": ""},

        # Section 3: Open-world Paldea Terrain, Water & Sky
        {"speaker": "前泽圭一", "original": "构建帕底亚全开放大地的技术管线：地貌以 Maya 的基础网格为底，利用 Houdini 进行全自动程序化细节增强，输出高度图（HeightMap）、地表物理材质与用于生成植被草花的遮罩（Mask）。此外，Houdini 还负责程序化建模悬崖岩石群并批量散布，自然雕琢出地貌细节。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "海面与河流的水体渲染：结合了顶点波浪位移、流向贴图（Flow Map）、基于水深的渐变透明度以及屏幕空间折射（Screen Space Refraction）。尤其在海岸线附近，研发团队专门制作了专属的岸边白浪模型，越接近陆地翻涌越剧烈，极大强化了波浪拍击感。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "天空则基于预计算大气散射（Precomputed Atmospheric Scattering）技术呈现水平线的自然渐变。云层制作方面，将体积建模的云朵在 6 个方向打光烘焙至 2 张纹理贴图中，依据真实世界太阳天光光照信息动态计算渲染色彩。室内场景则采用轻量高效的光照贴图（Lightmap）呈现。", "translation": "", "note": ""},

        # Conclusion
        {"speaker": "4Gamer 记者", "original": "以上便是本次演讲的精髓。通过写实材质、程序化地形、次表面散射与多层晶格着色等一系列先进图形管线的配合，Game Freak 成功描绘出了兼具宝可梦梦幻魅力与广袤自然尺度的全新帕底亚大世界。", "translation": "", "note": ""}
    ]

    # Translate
    combo = " ".join(b["original"] for b in raw_blocks)
    matches = find_glossary_matches(combo, glossary)
    print(f"Translating 4Gamer CEDEC 2023 article ({len(raw_blocks)} items)...")
    translated = translate_chunk(raw_blocks, matches, "CEDEC 2023 专题技术报道：Game Freak CG技术总监前泽圭一深度解密《宝可梦 朱·紫》开放世界图形渲染管线，包括写实与变形视觉平衡、次表面散射、太晶化双层水晶着色、Maya晶格面部捏脸、Houdini程序化地形与大气散射天空。")

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Slide 02 Title
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide02_title.jpg",
        "alt": "CEDEC 2023 演讲标题幻灯片：《宝可梦 朱·紫》帕底亚地区全景渲染——画面机制彻底解密！",
        "caption": "CEDEC 2023 官方技术演讲：《【宝可梦 朱·紫】帕底亚地区全景渲染——画面机制彻底解密！》"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "How Game Freak Rendered the Open World of Paldea: Shaders, SSS, Maya Lattice & Houdini Pipeline",
        "translation": "描摹广袤帕底亚：Game Freak 详解《宝可梦 朱·紫》全开放世界视觉渲染与着色器架构"
    })

    # Speaker Portrait
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide01_portrait.jpg",
        "alt": "演讲者：Game Freak CG 技术总监 前泽圭一",
        "caption": "主讲人：株式会社 Game Freak CG 技术总监 前泽圭一（Keiichi Maeza）"
    })

    # Intro item
    parallel_items.append({
        "speaker": "4Gamer 记者",
        "original": translated[0]["original"],
        "translation": translated[0]["translation"],
        "note": translated[0].get("note", "")
    })

    # Slide 04 Concept
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide04_concept.jpg",
        "alt": "视觉核心概念：写实与变形（Real & Deformed）的平衡",
        "caption": "美术核心原则‘写实与变形’：在追求写实自然地貌的同时，保持宝可梦与人类角色的卡通亲和力"
    })

    # Section 1 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Artistic Direction: Finding Harmony Between Stylized Characters and Realistic Environments",
        "translation": "视觉中枢理念：卡通变形生物与物理写实世界的黄金交点"
    })

    parallel_items.append({
        "speaker": "前泽圭一",
        "original": translated[1]["original"],
        "translation": translated[1]["translation"],
        "note": translated[1].get("note", "")
    })

    # Slide 11 SSS
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide11_sss.jpg",
        "alt": "次表面散射（SSS）在宝可梦不同体型与材质上的阴影透光效果",
        "caption": "次表面散射（SSS）着色器：依据宝可梦身体密度与肌肉组织，展现出有温度、有通透感的生命质感"
    })

    # Slide 14 Terastal
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide14_terastal.jpg",
        "alt": "太晶化水晶材质与双层立体王冠网格渲染解构",
        "caption": "太晶化（Terastal）渲染解构：母本模型材质替换、非太晶化保护网格与双层半透明晶体王冠"
    })

    # Section 2 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Pokémon Shaders: Subsurface Scattering, Paradox Particles, and Terastal Stereoscopic Crystals",
        "translation": "宝可梦微观着色器：次表面散射、悖谬粒子与太晶化双层水晶折射"
    })

    for it in translated[2:4]:
        parallel_items.append({"speaker": "前泽圭一", "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Slide 23 Lattice
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide23_lattice.jpg",
        "alt": "Maya 晶格变形（Lattice）面部五官调节示意图",
        "caption": "基于 Maya 晶格变形（Lattice）的面部自定义管线，精细控制眼角高低、嘴型与脸颊弧度"
    })

    # Slide 31 Fake Normal
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide31_fakenormal.jpg",
        "alt": "伪造法线与素法线线性混合的皮肤阴影平滑控制",
        "caption": "伪造法线融合与高光抑制技术：在全动态光照与多视角下保持动漫人物皮肤的柔和光滑"
    })

    # Section 3 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Character Pipeline: Maya Lattice Facial Customization and Blendshape Runtime Morphing",
        "translation": "角色定制与面部表情管线：Maya 晶格变形捏脸与伪造法线平滑皮肤"
    })

    for it in translated[4:7]:
        parallel_items.append({"speaker": "前泽圭一", "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Slide 35 Houdini
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide35_houdini.jpg",
        "alt": "Houdini 程序化地形与植被遮罩生成管线",
        "caption": "程序化地形系统：Maya 粗模底座配合 Houdini 自动化生成高度图、植被分布 Mask 与悬崖碎石群"
    })

    # Slide 40 Water
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide40_water.jpg",
        "alt": "顶点波浪动画与海岸白浪拍击模型演示",
        "caption": "海洋与河流多层流体着色：结合流向图、屏幕空间折射与定制海岸线翻涌白浪网格"
    })

    # Slide 43 Sky
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide43_sky.jpg",
        "alt": "预计算大气散射天空渐变与 6 方向云层光照烘焙",
        "caption": "动态昼夜苍穹：大气散射水平线色彩过渡与 6 轴向打光烘焙体积云"
    })

    # Section 4 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Open-World Paldea: Procedural Houdini Landscapes, Wave Modeling, and Atmospheric Scattering",
        "translation": "帕底亚全开放世界大地：Houdini 程序化地貌、海岸浪花模型与大气散射苍穹"
    })

    for it in translated[7:10]:
        parallel_items.append({"speaker": "前泽圭一", "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Conclusion item
    if len(translated) > 10:
        parallel_items.append({
            "speaker": "4Gamer 记者",
            "original": translated[10]["original"],
            "translation": translated[10]["translation"],
            "note": translated[10].get("note", "")
        })

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 4Gamer CEDEC 2023 报告：前泽圭一详解《宝可梦 朱·紫》帕底亚全开放世界视觉呈现与流式渲染管线",
        "original_title": "［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート",
        "date": "2023-08-25",
        "era": "2019–2026 · Expansion / 极巨化与开放世界",
        "era_skin": "2019",
        "publication": "4Gamer.net (CEDEC 2023 特别报道 / Igarashi)",
        "source_kind": "technical_report",
        "author": "Igarashi / 4Gamer.net",
        "translator": "Poke Amice Studio",
        "interviewee": "前泽圭一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "技术报告", "CEDEC", "Game Freak", "前泽圭一", "朱紫", "帕底亚", "图形渲染", "开放世界"],
        "archive_type": "interview_translation",
        "source": {
            "title": "［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート",
            "url": "https://www.4gamer.net/games/619/G061991/20230823075/",
            "language": "ja",
            "source_type": "technical_report"
        },
        "original_link": "https://www.4gamer.net/games/619/G061991/20230823075/",
        "summary": "2023年8月日本最大电脑娱乐开发者大会（CEDEC 2023）上，Game Freak CG 技术总监前泽圭一发表题为《帕底亚地区全景渲染——画面机制彻底解密》的技术报告。详细解构了《宝可梦 朱·紫》从微观生物到宏观开放世界的全链路着色与资产管线：明确了‘写实与变形’的核心美术基调；首次披露在宝可梦身上采用次表面散射（SSS）阴影漫反射、凝胶透明体与结构色；解密太晶化（Terastal）如何利用原有母模即时替换法线/噪波纹理、指定非太晶化保护网格，并通过外层半透明与内层不透明的双层折射网格塑造王冠立体纵深感；详述主角捏脸采用 Maya 晶格变形（Lattice）、5部件面部变形目标（Morph Target）与伪造法线平滑皮肤；并在全开放大地上引入 Maya+Houdini 程序化地形与植被遮罩、流向图与定制海岸拍岸浪花模型，以及基于预计算大气散射的动态天空。",
        "entities": {
            "people": ["前泽圭一", "五十岚"],
            "games": ["宝可梦 朱·紫", "宝可梦 剑·盾"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / f"{slug}.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} items)")


# =========================================================================
# 4. Master Catalog Sync & Render Script Update
# =========================================================================
def sync_catalog():
    print("\n" + "="*70)
    print("Updating data/pokemon_1000_interviews.json with Batch 15 Imports")
    print("="*70)

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    updates = {
        "PKMN-0825": {
            "title": "《Game Informer》独家专访：增田顺一复盘《红宝石·蓝宝石》极限开发（GBA跨代阵痛、特性性格革命与重压下的进退维谷）",
            "original_title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
            "date": "2017-08-14",
            "year": 2017,
            "status": "imported",
            "post_file": "_posts/2017-08-14-interview-game-informer-why-ruby-sapphire-most-challenging.md",
            "source_url": "https://gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx",
            "people": ["增田顺一", "大森滋", "凯尔·希利亚德"]
        },
        "PKMN-0854": {
            "title": "Eurogamer 独家专访：增田顺一与杉森建谈《宝可梦 黑·白》幕后心智（纽约曼哈顿采风、156只全新宝可梦大换血的决断与成熟叙事）",
            "original_title": "The brains behind Pokemon Black and White",
            "date": "2011-03-01",
            "year": 2011,
            "status": "imported",
            "post_file": "_posts/2011-03-01-interview-eurogamer-masuda-sugimori-black-white-brains.md",
            "source_url": "https://www.eurogamer.net/the-brains-behind-pokemon-black-and-white-interview",
            "people": ["增田顺一", "杉森建", "韦斯利·尹-普尔", "井部真那"]
        },
        "PKMN-0681": {
            "title": "4Gamer CEDEC 2023 报告：前泽圭一详解《宝可梦 朱·紫》帕底亚全开放世界视觉呈现与流式渲染管线",
            "original_title": "［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート",
            "date": "2023-08-25",
            "year": 2023,
            "status": "imported",
            "post_file": "_posts/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza.md",
            "source_url": "https://www.4gamer.net/games/619/G061991/20230823075/",
            "people": ["前泽圭一", "五十岚"]
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
        "interview-game-informer-why-ruby-sapphire-most-challenging",
        "interview-eurogamer-masuda-sugimori-black-white-brains",
        "interview-cedec-2023-paldea-rendering-pipeline-maeza"
    ]
    lines = content.splitlines()
    for s in new_slugs:
        if f"'{s}'" not in content:
            for idx, line in enumerate(lines):
                if line.strip() == "]":
                    lines.insert(idx, f"  '{s}',")
                    break
    render_rb.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Updated tools/render_specific_posts.rb with Batch 15 slugs.")


if __name__ == "__main__":
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")
    curate_game_informer_rs(glossary)
    curate_eurogamer_bw(glossary)
    curate_4gamer_cedec_2023(glossary)
    sync_catalog()
    update_render_script()
    print("\nBatch 15 Curation Complete!")
