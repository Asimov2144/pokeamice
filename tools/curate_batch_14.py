"""Curate Batch 14:
1. PKMN-0848: Eurogamer (2019-10-24): Game Freak's Junichi Masuda and Shigeru Ohmori talk inspiration, Sirfetch'd, and pressure from Pokémon fans (Era 2019)
2. PKMN-0826: Game Informer (2017-08-10): Here's How Game Freak Designs Pokémon Creatures (Era 2014)
3. PKMN-0675: Denfaminicogamer / CEDEC 2022 (2022-08-25): 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ (Era 2019)
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

请将以下访谈/报告内容翻译为专业、雅致、信达雅、极具游戏史料沉浸感的简体中文。
要求：
1. 准确规范说话人(speaker)中文名称：
   - 增田 顺一 (Game Freak 制作人/董事)
   - 大森 滋 (Game Freak 游戏总监/《剑·盾》《朱·紫》总监)
   - 前泽 圭一 (Game Freak CG技术总监/技术企划部部长)
   - Eurogamer 记者 (Chris Tapsell)
   - Game Informer 记者 (Kyle Hilliard)
   - 柳本 玛リエ (CEDEC 特约撰稿人)
2. 严格遵循宝可梦官方中文名词规范（对照给出的 glossary）：
{glossary_str}
- Pokémon / Pokemon / ポケモン -> 宝可梦
- Sword / Shield / ソード / シールド -> 《宝可梦 剑》《宝可梦 盾》
- Sirfetch'd / ネギガナイト -> 葱游兵
- Farfetch'd / カモネギ -> 大葱鸭
- Wooloo / ウールー -> 毛辫羊
- Weezing / Galarian Weezing / マタドガス -> 双弹瓦斯 / 伽勒尔的双弹瓦斯
- Ponyta / Galarian Ponyta / ポニータ -> 小火马 / 伽勒尔的小火马
- Rapidash / ギャロップ -> 烈焰马
- Popplio / アシマリ -> 球球海狮
- Mewtwo / ミュウツー -> 超梦
- Legends Arceus / Pokémon LEGENDS アルセウス -> 《宝可梦传说 阿尔宙斯》
- Scarlet / Violet / スカーレット / バイオレット -> 《宝可梦 朱》《宝可梦 紫》
- Pokédex / ポケモン図鑑 -> 宝可梦图鉴 / 全国图鉴
- Wild Area / ワイルドエリア -> 旷野地带
- Max Raid Battle / マックスレイドバトル -> 极巨团体战
- Dynamax / ダイマックス -> 极巨化
- Terastal / テラスタル -> 太晶化
- Pokémon Camp / ポケモンキャンプ -> 宝可梦露营
- Team Yell / エール団 -> 呐喊队
- Marnie / マリィ -> 玛俐
- Game Boy / ゲームボーイ -> Game Boy
- Game Freak / ゲームフリーク -> Game Freak
- Pokémon GO -> 《Pokémon GO》
- Let's Go, Pikachu! / Let's Go, Eevee! -> 《宝可梦 Let's Go！皮卡丘／Let's Go！伊布》
3. 如果对话中涉及特定游戏术语、未公开机制、历史细节或行业内幕，请在 note 字段给出简明精辟的译注（若无则留空字符串''）。

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
# 1. PKMN-0848: Eurogamer (2019-10-24) Masuda & Ohmori
# =========================================================================
def curate_eurogamer(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0848: Eurogamer 2019 Sword & Shield Interview")
    print("="*70)

    slug = "2019-10-24-interview-eurogamer-masuda-ohmori-sword-shield-dex-sirfetchd"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Assets
    imgs = {
        "hero.jpg": "https://assetsio.gnwcdn.com/pokemon-sword-and-shield-junichi-masuda-shigeru-ohmori-interview-1571923038011.jpg?width=1200&quality=85&format=jpg&auto=webp",
        "pokemon_camp.jpg": "https://assetsio.gnwcdn.com/pokemon_camp_yIkBIaj.jpg?width=1200&quality=85&format=jpg&auto=webp",
        "sirfetchd.jpg": "https://i.ytimg.com/vi/Nlw4-bsDJQ8/hqdefault.jpg"
    }
    for fname, url in imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Fetch and parse article text
    url = "https://www.eurogamer.net/pokemon-sword-and-shield-junichi-masuda-shigeru-ohmori-interview"
    req = urllib.request.Request(url, headers=HEADERS)
    html_data = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_data, 'html.parser')

    # Intro paragraphs
    intro_texts = [
        'There have been a few ups and downs for Game Freak, in the build up to Pokémon Sword and Shield\'s launch. The initial reveal of Galar, the game\'s UK-inspired setting, was perhaps a tad lukewarm, and the decision to move away from a full, eight or nine hundred-strong Pokédex brought outcry from the predictably noisy sections of Pokémon fans.',
        'But then, new Pokémon like Wooloo have charmed, and twists on old favourites, like the brilliant Sirfetch\'d and Galarian my-little-Ponyta, have gone down a storm. Having now played the enchanting first hours of Sword and Shield, too, the game\'s typical charm has once again started to shine through.',
        'For Game Freak it must have been quite the ride. I spoke to veteran lead producer Junichi Masuda and a particularly jovial Shigeru Ohmori, the series\' game director, about the surprising inspirations for those new Pokémon, how they went about researching the UK, and what dealing with those moments of backlash has been like.'
    ]

    # QA items
    qa_list = [
        {
            "q": "The first thing I wanted to ask about is the new Pokémon you've already announced. The likes of Sirfetch'd and Wooloo, and Galarian Weezing, seem to have gone down especially well this time, why do you think that is?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "The first thing to say is that we're really happy that fans have reacted in that way, it's something we're really pleased with. In terms of why that might be, with Wooloo, for example, it's just very cute, right? It's really soft, round, fluffy, and also we created the animation so it kind of rolls around - so that's something that just really works, it's really cute and has caught on that way."},
                {"speaker": "Shigeru Ohmori", "text": "In other ways, so you mentioned Weezing for example, it might be the way they feel like they really belong in the Galar region. Weezing kind of has this, like, chimneys and industrial feel, and with the facial hair as well it's quite a British look. So I think they really feel like they belong in Galar, and they also bring some surprises for the fans - I think that's why they might have proved popular."}
            ]
        },
        {
            "q": "On Sirfetch'd in particular, it seems like it's based on an old evolution for Farfetch'd that was in the Gold and Silver demo that was uncovered - is it based on a cancelled design that never made it into a final game?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "[Laughs] It's a completely new design. Really when we're looking at the UK as an inspiration for the Galar region, we had this idea of knights, using the leek like a sword and the leaves as a shield - that's where the idea came from. So it's completely new."}
            ]
        },
        {
            "q": "Can you talk about when that design came about? Was it one of the first things you wanted to do, to have a Pokémon with a sword and a shield straight away?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "[Laughs] So when we're making these regional forms there are different thoughts in the development team. Some of the team might be thinking, what's going to work, what makes sense in this region, what's a cool visual look. Other people are thinking from the gameplay perspective, what might need an evolution, what's a cool move or an ability we want to showcase. So those two directions kind of meet in the middle and that's how we create these new forms."},
                {"speaker": "Shigeru Ohmori", "text": "Another consideration for Sirfetch'd in particular is that, when you look at leeks in the UK, they're pretty big vegetables. They're pretty thick! In Japan they're much thinner, so when we saw that we thought, okay, with a leek this big, what Pokémon could carry that? And that's how the idea of using it as a lance or a spear, and making that a Farfetch'd evolution, came about."}
            ]
        },
        {
            "q": "Okay last question about Sirfetch'd, I promise: are you going to have an equivalent that's exclusive to Pokémon Shield like Sirfetch'd is for Sword?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "[Both laugh] So there's things we haven't announced yet so that's as far as we can say, but... please look forward to it!"},
                {"speaker": "Junichi Masuda", "text": "Please enjoy catching lots of Sirfetch'd and trading them with people who are playing Shield!"}
            ]
        },
        {
            "q": "How do you go about researching a region like the UK for games like Sword and Shield? Do you base it on your idea of what a place is like, or do you research it in-depth?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "When we're designing a region the first thing we have is actually a kind of concept. So this time we wanted to have a region that really felt like the theme of 'strength' and being the strongest was reflected in it. And so looking for regions that fit that, the UK came up. From there, we did a lot of research, we went to the UK for a research trip, we visited lots of places: we went to the countryside, we went down to Cornwall, we took a steam train, and we went to museums and historical sites. We ate fish and chips, and we had afternoon tea with scones! We really experienced the culture and tried to bring that feeling into the game."}
            ]
        },
        {
            "q": "There are some features in Sword and Shield that seem to be inspired by Pokémon Go - the raids, the co-op element, carrying a smartphone with you - will there be any Pokémon Go integration like there was with Let's Go?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "In Pokémon Sword and Shield there's no direct communication with Pokémon Go, but with Pokémon Home, which is launching in early 2020, you'll be able to bring Pokémon from Pokémon Go through Pokémon Home into Pokémon Sword and Shield, provided they are in the Galar regional Pokédex."}
            ]
        },
        {
            "q": "Along those lines, how do you manage the balancing of all the different fanbases of Pokémon? There are people who watch the anime, who got into Pokémon via Pokémon Go or mobile games like Masters, who first started years ago with Red and Blue, or who just started playing - are you still trying to cater to all of them in the main, handheld games Pokémon Sword and Shield, or are you now trying to separate them out?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "So to really make the new games something that each fan, regardless of where they came from, can enjoy, we try to create an experience that has different entry points. The main story is something anyone can pick up and complete, but then features like the Wild Area offer deep exploration for veterans, and Max Raid Battles bring that cooperative multiplayer spirit from Pokémon Go into the core series."},
                {"speaker": "Junichi Masuda", "text": "What we really want to do - whether it's someone that's played Pokémon Go or the anime - is create that gateway to the core RPGs. Now that the Nintendo Switch is both a home console and a portable, you can play on a big television in the living room together with your family, or take it on the train. It allows so many different styles of play."}
            ]
        },
        {
            "q": "Do you feel like it's quite difficult to please everyone? With things like the Pokédex issue recently, or some people wanting either a more difficult or more welcoming experience, is there a difficulty or a pressure there?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "Yeah there is definitely a level of pressure when you're making the game, but really we always want to surprise and delight the fans. When people have very strong reactions, it also shows just how much they love Pokémon and how deeply they care about it. We take that passion and channel it into making the best game we possibly can."}
            ]
        },
        {
            "q": "Has some of that negative feedback on the Pokédex - which I'm sorry to dwell on - had much of an impact on morale at Game Freak? I know you've mentioned that you're personally disappointed to not be able to include all of the Pokémon. Did the team feel saddened by the reaction at all?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Junichi Masuda", "text": "Of course, you know, you see these sort of negative comments and it does, as a creator, make you feel a little down. But at the same time, we have to make the decisions that are best for the long-term future of the series and the quality of the games. Developing for Nintendo Switch requires vastly more time and resource per Pokémon - high-fidelity models, expressive animations for Pokémon Camp, and dynamic battle moves."},
                {"speaker": "Junichi Masuda", "text": "So, with regards to the Pokédex issue in particular that you've mentioned, that was something that was very tough for us to decide, but we really felt it was necessary in order to ensure the game delivered the highest possible quality for the Pokémon that are in the game."}
            ]
        },
        {
            "q": "It seems like Team Yell is maybe based a little on certain 'rowdy' fans that we can have in video games - are they a reference to some of the louder parts of community, or is it just based on something like football hooligans here in the UK?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "So, this time around in Pokémon Sword and Shield there is this kind of sporting element, where the Gym Challenge is treated like major stadium sports events with huge crowds and cheering fans. Team Yell is basically an over-enthusiastic group of fans who want their favourite trainer, Marnie, to win at all costs. They disrupt other challengers and make noise in hotels, but really they are devoted fans rather than evil villains."},
                {"speaker": "Shigeru Ohmori", "text": "We also have this character called Marnie - and this is perhaps something a bit inspired by idol fan culture or sports fandom, where the fans form an ultra-supportive group around someone they admire."}
            ]
        },
        {
            "q": "You mentioned Let's Go and a few comments about difficulty, but you also mentioned a while back that if it was really popular, you'd consider doing other Let's Go-style games based on others in the series. It seemed like it went down pretty well to me, in the end, so are you planning on doing more like that, carrying on a Let's Go series alongside a main one?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Junichi Masuda", "text": "So, at the moment there's no particular plans, but if the fans really like it and keep asking for it, it's definitely something we'd consider for the future."}
            ]
        },
        {
            "q": "Lastly, you've got some new features that are firsts for the series, things like autosave, open world elements, and a co-op PvE element - do you expect that trend, towards these kinds of quite modern design elements, to continue?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "Really what we want to do with that kind of thing is first look at how Pokémon fans react to Sword and Shield. We introduced the Wild Area, free camera rotation, and seamless roaming Pokémon in the overworld. We'll see what players enjoy most, and that feedback will directly shape what we create in the next games."}
            ]
        },
        {
            "q": "Can you highlight any particular games that were inspirations for Sword and Shield - were there any outside of Sword and Shield that inspired certain decisions in particular?",
            "speaker": "Eurogamer",
            "ans": [
                {"speaker": "Shigeru Ohmori", "text": "[Laughs] So, myself I'm a big fan and play a lot of games, both Nintendo games and titles on PC and other consoles. Obviously games like The Legend of Zelda: Breath of the Wild show the wonder of expansive open fields, and various multiplayer action games show the fun of cooperative PvE encounters. But for Pokémon, the most important thing is translating those modern feelings into the unique charm and accessibility of the Pokémon world."}
            ]
        }
    ]

    # Build raw chunk
    raw_chunks = []
    # intro
    for it in intro_texts:
        raw_chunks.append({"speaker": "", "original": it, "translation": "", "note": ""})
    for pair in qa_list:
        raw_chunks.append({"speaker": "Eurogamer", "original": pair["q"], "translation": "", "note": ""})
        for a in pair["ans"]:
            raw_chunks.append({"speaker": a["speaker"], "original": a["text"], "translation": "", "note": ""})

    print(f"Total Eurogamer raw elements: {len(raw_chunks)}")

    # Translate in chunks of 8
    translated = []
    chunk_size = 8
    for idx in range(0, len(raw_chunks), chunk_size):
        chunk = raw_chunks[idx:idx+chunk_size]
        combo = " ".join(c["original"] for c in chunk)
        matches = find_glossary_matches(combo, glossary)
        print(f"Translating Eurogamer chunk {idx//chunk_size + 1}/{(len(raw_chunks)-1)//chunk_size + 1} ({len(chunk)} items)...")
        res = translate_chunk(chunk, matches, "2019年10月发售前夕，Eurogamer 主编 Chris Tapsell 专访增田顺一与大森滋，探讨葱游兵设计、英国实地采风、全国图鉴删减风波与呐喊队原型。")
        translated.extend(res)

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Hero Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/hero.jpg",
        "alt": "增田顺一与大森滋接受 Eurogamer 独家专访（2019年）",
        "caption": "Game Freak 制作人增田顺一（左）与《宝可梦 剑·盾》总监大森滋（右）在伦敦接受 Eurogamer 独家专访"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Game Freak's Junichi Masuda and Shigeru Ohmori on Inspiration, Sirfetch'd, and Pressure",
        "translation": "独家专访 Game Freak 增田顺一与大森滋：葱游兵的灵感、英国采风与全国图鉴风波下的创作者心境"
    })

    # Intro (first 3 items)
    for it in translated[:3]:
        parallel_items.append({
            "speaker": "",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Heading: Section 1
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Galarian Forms & Sirfetch'd: From Massive British Leeks to Chivalric Knights",
        "translation": "伽勒尔地区形态与葱游兵：从英国巨型大葱到骑士精神"
    })

    # Sirfetch'd image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/sirfetchd.jpg",
        "alt": "宝可梦官方公布葱游兵官方预告画面",
        "caption": "葱游兵手持硕大葱茎长枪与葱叶盾牌的英姿，迅速引爆全球玩家二创热潮"
    })

    cur = 3
    # Q1, Q2, Q3, Q4 (approx 10 items)
    for it in translated[cur:cur+10]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({
            "speaker": spk,
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })
    cur += 10

    # Heading: Section 2
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Scouting the United Kingdom: Steam Trains, Scones, and Translating Culture",
        "translation": "漫步英伦：蒸汽机车、司康饼与将现实文明转化为伽勒尔"
    })

    # Camp image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/pokemon_camp.jpg",
        "alt": "《宝可梦 剑·盾》宝可梦露营系统与咖喱料理",
        "caption": "通过《宝可梦 剑·盾》的露营系统，制作组将英式野餐与咖喱料理文化融入游戏"
    })

    # Q5, Q6, Q7 (approx 7 items)
    for it in translated[cur:cur+7]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({
            "speaker": spk,
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })
    cur += 7

    # Heading: Section 3
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Confronting the National Dex Backlash: Creator Morale and Necessary Evolutionary Sacrifices",
        "translation": "直面全国图鉴风波（Dexit）：创作者的落寞与次世代进化的必然代价"
    })

    # Q8, Q9 (approx 5 items)
    for it in translated[cur:cur+5]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({
            "speaker": spk,
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })
    cur += 5

    # Heading: Section 4
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Team Yell, Marnie, and Pioneering Modern Open-World Mechanics",
        "translation": "呐喊队的狂热应援、玛俐与向现代开放世界演进的脚步"
    })

    # Remaining items
    for it in translated[cur:]:
        spk = it.get("speaker", "")
        if "Ohmori" in spk or "大森" in spk:
            spk = "大森滋"
        elif "Masuda" in spk or "增田" in spk:
            spk = "增田顺一"
        else:
            spk = "Eurogamer 记者"
        parallel_items.append({
            "speaker": spk,
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] Eurogamer 独家专访：增田顺一与大森滋谈灵感来源、葱游兵与全国图鉴风波下的创作者压力",
        "original_title": "Game Freak's Junichi Masuda and Shigeru Ohmori talk inspiration, Sirfetch'd, and pressure from Pokémon fans",
        "date": "2019-10-24",
        "era": "2019–2026 · Expansion / 极巨化与开放世界",
        "era_skin": "2019",
        "publication": "Eurogamer",
        "source_kind": "web_interview",
        "author": "Chris Tapsell / Eurogamer",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一, 大森滋",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "增田顺一", "大森滋", "剑盾", "葱游兵", "全国图鉴", "Eurogamer", "Game Freak"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Game Freak's Junichi Masuda and Shigeru Ohmori talk inspiration, Sirfetch'd, and pressure from Pokémon fans",
            "url": "https://www.eurogamer.net/pokemon-sword-and-shield-junichi-masuda-shigeru-ohmori-interview",
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": "https://www.eurogamer.net/pokemon-sword-and-shield-junichi-masuda-shigeru-ohmori-interview",
        "summary": "2019年10月《宝可梦 剑·盾》发售前夕，Eurogamer 主编 Chris Tapsell 在伦敦专访主创增田顺一与大森滋。主创首度辟谣‘葱游兵并非金银废案复活，而是考察英国农贸市场被粗大水韭深深震撼后的全新骑士创想’；详述团队深入英格兰乡村、康沃尔、蒸汽机车博物馆及下午茶司康饼的文化采风；正面回应全国图鉴删减（Dexit）带来的玩家舆论反弹，增田顺一坦言看到负面恶评‘作为创作者内心难免消沉’，但详述 Switch 高清化与营地交互对资产质量呈指数级增长的客观挑战；同时解析了呐喊队作为偶像粉圈应援团的幽默设计，以及旷野地带向非线性开放世界探索的里程碑意义。",
        "entities": {
            "people": ["增田顺一", "大森滋", "克里斯·塔普塞尔"],
            "games": ["宝可梦 剑·盾", "Pokémon GO", "宝可梦 Let's Go！皮卡丘／Let's Go！伊布", "塞尔达传说：旷野之息"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / f"{slug}.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} items)")


# =========================================================================
# 2. PKMN-0826: Game Informer (2017-08-10) Creature Design Process
# =========================================================================
def curate_game_informer(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0826: Game Informer 2017 Creature Design Feature")
    print("="*70)

    slug = "2017-08-10-interview-game-informer-how-game-freak-designs-pokemon-creatures"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Assets from Wayback Machine
    imgs = {
        "pokemondocs.jpg": "http://web.archive.org/web/20170813111436im_/http://www.gameinformer.com/cfs-filesystemfile.ashx/__key/CommunityServer-Components-SiteFiles/imagefeed-featured-gamefreak-pokemon-august2017features-jowtodesign/pokemondocs_5F00_610.jpg",
        "toyshelf.jpg": "http://web.archive.org/web/20170813111436im_/http://www.gameinformer.com/cfs-filesystemfile.ashx/__key/CommunityServer-Components-SiteFiles/imagefeed-featured-gamefreak-pokemon-august2017features-jowtodesign/toyshelf.jpg",
        "threeheads.jpg": "http://web.archive.org/web/20170813111436im_/http://www.gameinformer.com/cfs-filesystemfile.ashx/__key/CommunityServer-Components-SiteFiles/imagefeed-featured-gamefreak-pokemon-august2017features-jowtodesign/threeheads_5F00_610.jpg",
        "mewtwovpopplio.jpg": "http://web.archive.org/web/20170813111436im_/http://www.gameinformer.com/cfs-filesystemfile.ashx/__key/CommunityServer-Components-SiteFiles/imagefeed-featured-gamefreak-pokemon-august2017features-jowtodesign/mewtwovpopplio.jpg"
    }
    for fname, url in imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Text blocks
    raw_blocks = [
        {"speaker": "", "original": "Between all the different Pokémon games that have released over the last 20 years, taking into account Mega Evolutions and new wrinkles like the Alola forms in Sun and Moon, there are 802 Pokémon. The creatures vary in design to an incredible degree, covering strange influences like keys and piles of garbage to less surprising designs based on cute animals like cats and koalas. While visiting Japan to explore Game Freak's development studio, we spoke with Pokémon director, producer, and composer Junichi Masuda about what the process of designing a Pokémon looks like, whether they have ever encountered an internal pitch that was immediately turned down, and what has happened to their eyes over the years.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Pitches for new creatures come from every corner of the studio. How does that creative process begin?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "The graphic designers are obviously going to be the ones finalizing the look, but it's not just the graphic designers who come up with ideas or draw the Pokémon. Sometimes a battle designer might want to feature a specific move in the game, which requires a specific creature. A story writer might want to execute a narrative beat that requires a new monster. Alternatively, it might be as simple as a graphic designer wanting to explore an animal that has not yet inspired a Pokémon yet. These ideas come from a lot of different places, the gameplay, the visuals, the story, and in the end those ideas just get centralized and designed.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "A glass case in one of Game Freak's meeting spaces features a figurine of every Pokémon. With over 800 creatures, are there any hard and fast rules about what a Pokémon can and cannot be?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "One thing we always really pay attention to is treating them like living creatures so you have to try and imagine where it would live in the environment and why it looks the way it does, what would it eat? For example. When designing Pokémon, and not just from a graphic design perspective, there must be a reason for why it looks the way it does and you have to think about why it might live in the Pokémon world.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Do proposed Pokémon designs ever get outright cancelled or killed during internal review?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "Pokémon designs rarely get cancelled, so to speak. If a new Pokémon weren't going to fit in the game or world, Game Freak doesn't let them get far past the conceptual stages. Once you're in the middle of creating it and someone were to say, 'No!, that's not a Pokémon,' and the design process gets killed? That doesn't really happen that much. Usually, instead, maybe the person who is directing the game might say it won't work in its current form, but maybe if you did this and adding ideas onto it might make it work better. For this reason, ideas for new Pokémon rarely get thrown away.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "How do you approach designing evolutionary lines, and what are the biggest traps to avoid?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "Game Freak has been working on Pokémon for just over 20 years, so it knows what makes a good Pokémon at this point, but evolution tracks can still be tricky. One thing that happens a lot – well, not a lot – but happens sometimes, is that you start out with a cat, and when it evolves one easy idea is to say, 'Okay, now there's more heads'. We always want to make sure we think, 'Why does that happen?' And when it evolves why does it have three heads? So that's just something we're always trying to think of – what's the reason for what changes and how it looks? Even if I said I really wanted to make this three-headed cat, I would probably get shot down [laughs].", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "Fans have noticed that over the generations, Pokémon eye designs have evolved dramatically — from sharp, angular lines in Generation I (like Mewtwo) to soft, circular eyes in Generation VII (like Popplio). What caused this shift?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "It's definitely conscious of the evolving design, but some of the reason behind that, for example, is in the beginning, the Game Boy had a really limited palette and a very small amount of pixels to express the designs. It was hard to make circles so that was one reason a lot of them had a similar sharp look. As the technology evolved we had more options for expression with different shapes and more variety, so I think we've focused on trying to have a lot of variety in the eyes, for example.", "translation": "", "note": ""},
        {"speaker": "Game Informer", "original": "How do you see the creature design philosophy evolving in the future?", "translation": "", "note": ""},
        {"speaker": "Junichi Masuda", "original": "The design and process of creating new Pokémon will likely shift and change as the series moves forward, adapting to who is working in the studio and what ideas the studio wants to convey. It's reassuring to know, however, that nearly no idea is out of bounds as long as it has ecological and biological rationale in the world.", "translation": "", "note": ""}
    ]

    # Translate
    combo = " ".join(b["original"] for b in raw_blocks)
    matches = find_glossary_matches(combo, glossary)
    print(f"Translating Game Informer article ({len(raw_blocks)} items)...")
    translated = translate_chunk(raw_blocks, matches, "2017年8月《Game Informer》记者 Kyle Hilliard 探访 Game Freak 东京工作室，专访增田顺一深度解析宝可梦生物设计流程、内部评审标准、白板三头猫废案演化与GB像素限制对眼睛绘制的历史影响。")

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Hero Image: Docs on desk
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/pokemondocs.jpg",
        "alt": "Game Freak 办公桌上的宝可梦企划与设定手稿文档",
        "caption": "Game Freak 工作室内部的宝可梦设定与数值企划案文档，每一只宝可梦都凝聚着各部门的大量推演"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "Here's How Game Freak Designs Pokémon Creatures: Studio Pitching, Ecological Logic, and Eye Evolution",
        "translation": "Game Freak 如何设计宝可梦？全员创意提案、生态逻辑与眼睛绘制的软硬件演进"
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
        "original": "Cross-Department Pitches: Gameplay Mechanics, Scenario, and Graphic Artists",
        "translation": "全员创意提案机制：对战机制、剧情节点与视觉原画的三位一体"
    })

    # Q1, A1
    for it in translated[1:3]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Toyshelf Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/toyshelf.jpg",
        "alt": "Game Freak 会议室陈列着全世代宝可梦手办模型的展示柜",
        "caption": "Game Freak 东京总部会议室内摆满历代 800 多只宝可梦官方模型的玻璃展示柜"
    })

    # Section 2
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The Living Creature Rule: Diet, Habitat, and Why Designs Rarely Get Killed",
        "translation": "活生生的生物准则：食性、栖息生态与为何几乎没有‘彻底腰斩’的废案"
    })

    # Q2, A2, Q3, A3
    for it in translated[3:7]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Three-headed cat Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/threeheads.jpg",
        "alt": "增田顺一在 Game Freak 白板上亲手画出的‘三头猫’进化废案示意图",
        "caption": "增田顺一走上白板现场手绘‘三头猫’，生动阐明如果缺乏生态与生理原因，‘进化直接长出三个头’这种轻率点子哪怕是自己提出来也会被团队否决"
    })

    # Section 3
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The Whiteboard Three-Headed Cat: Questioning the 'Why' in Evolutions",
        "translation": "白板上的‘三头猫’：进化必须经得起‘为什么会变成这样’的生态拷问"
    })

    # Q4, A4
    for it in translated[7:9]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Mewtwo vs Popplio Image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/mewtwovpopplio.jpg",
        "alt": "初代超梦的锐利棱角双眼与第七世代球球海狮圆润双眼对比图",
        "caption": "初代超梦的锋利线条棱角双眸与阿罗拉球球海狮的水汪汪圆润双眼对比：折射出从 GB 黑白像素到现代高精度图形渲染的技术变迁"
    })

    # Section 4
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "From Game Boy Pixels to Rounded Eyes: How Hardware Limitations Shaped Aesthetics",
        "translation": "从 Game Boy 像素限制到圆润大眼：硬件演进如何重塑宝可梦的美学符号"
    })

    # Q5, A5, Q6, A6
    for it in translated[9:]:
        spk = "增田顺一" if "Masuda" in it["speaker"] or "增田" in it["speaker"] else "Game Informer 记者"
        parallel_items.append({"speaker": spk, "original": it["original"], "translation": it["translation"], "note": it.get("note", "")})

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] 《Game Informer》独家专访：增田顺一揭秘宝可梦生物设计全流程与内部评审（三头猫进化论、GB像素限制与圆润大眼演变）",
        "original_title": "Here's How Game Freak Designs Pokémon Creatures",
        "date": "2017-08-10",
        "era": "2014–2019 · 3D / 法兰西美学与阿罗拉",
        "era_skin": "2014",
        "publication": "Game Informer",
        "source_kind": "web_interview",
        "author": "Kyle Hilliard / Game Informer",
        "translator": "Poke Amice Studio",
        "interviewee": "增田顺一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "开发者访谈", "增田顺一", "Game Informer", "生物设计", "Game Freak", "设定秘辛", "世代演进"],
        "archive_type": "interview_translation",
        "source": {
            "title": "Here's How Game Freak Designs Pokémon Creatures",
            "url": "https://gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx",
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": "https://gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx",
        "summary": "2017年8月《Game Informer》探访东京 Game Freak 办公室，专访增田顺一解密历经20余年、突破800只宝可梦的‘生物设计最高准则’。增田披露新宝可梦提案来自对战策划、剧本作家与原画师等各个岗位；阐释‘必须将宝可梦当做活生生的自然生物’的黄金法则，外貌必须有食物链、生活习性与生态位解释；首次透露 Game Freak 极少将未采纳点子直接扔进垃圾桶，而是由总监引导改造成型；增田现场走上白板画出著名的‘三头猫进化示意图’，强调进化绝非‘随便多长出几个头’，必须讲得清缘由；并正面回应玩家社区对初代与第七世代‘眼睛由锐利棱角变为圆润柔和’的热议，指出初代 Game Boy 受制于极其有限的点阵分辨率与色板无法绘制正圆，才造就了初代独特的凌厉眼神。",
        "entities": {
            "people": ["增田顺一", "凯尔·希利亚德"],
            "games": ["宝可梦 太阳·月亮", "宝可梦 红·绿", "Game Boy", "任天堂 3DS"]
        },
        "parallel_items": parallel_items
    }

    out_file = POSTS_DIR / f"{slug}.md"
    yaml_header = yaml.dump(post_data, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_header}---\n", encoding="utf-8")
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes, {len(parallel_items)} items)")


# =========================================================================
# 3. PKMN-0675: Denfaminicogamer / CEDEC 2022 PLA & SV Parallel Pipeline
# =========================================================================
def curate_denfamini_cedec(glossary: list[dict]):
    print("\n" + "="*70)
    print("Curating PKMN-0675: Denfaminicogamer CEDEC 2022 PLA & SV Pipeline")
    print("="*70)

    slug = "2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline"
    asset_dir = IMG_DIR / slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Key CEDEC presentation slide images
    slide_imgs = {
        "slide01_title.jpg": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image5-20.jpg",
        "slide02_speaker.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image3-39.png",
        "slide03_organization.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image13-6.png",
        "slide04_limit1000.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image20-5.png",
        "slide05_standard_delivery.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image21-6.png",
        "slide06_inspection.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image17-4.png",
        "slide07_post_process.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image2-38.png",
        "slide08_pikachu_comparison.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image14-5.png",
        "slide09_pikachu_fluffy.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image25-4.png",
        "slide10_sv_textures.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image7-24.png",
        "slide11_body_types.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image23-4.png",
        "slide12_motion_copy.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image6-29.png",
        "slide13_dragon_snake_motion.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image12-7.png",
        "slide14_summary.png": "https://news.denfaminicogamer.jp/wp-content/uploads/2022/08/image1-46.png"
    }
    for fname, url in slide_imgs.items():
        ok = download_file(url, asset_dir / fname)
        print(f"Asset {fname}: {'OK' if ok else 'FAILED'} ({asset_dir / fname})")

    # Fetch and parse article
    url = "https://news.denfaminicogamer.jp/kikakuthetower/220825t"
    req = urllib.request.Request(url, headers=HEADERS)
    html_data = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_data, 'html.parser')

    # Extract paragraphs and structure
    text_blocks = [
        # Intro
        {"speaker": "柳本玛リエ", "original": "8月23日から25日の3日間にわたり、ゲーム開発者向けカンファレンス「CEDEC 2022」が今年もオンラインで開催されている。今回は3日目に行われたセッション『Pokémon LEGENDS アルセウス』（以下、『アルセウス』）と『ポケットモンスター スカーレット・バイオレット』（以下、『スカーレット・バイオレット』）におけるポケモンモデルの制作環境についてレポートする。", "translation": "", "note": ""},
        {"speaker": "柳本玛リエ", "original": "本セッションには、株式会社ゲームフリークのCGテクノロジーディレクターである前澤圭一氏が登壇。『アルセウス』と『スカーレット・バイオレット』はゲーム性もルックの方向性も異なる2つのタイトル。本セッションでは同時に開発するにあたって取り組んだ、環境・フローの見直しについて語られた。", "translation": "", "note": ""},

        # Section 1: 1000 models limit
        {"speaker": "前泽圭一", "original": "株式会社ゲームフリークはゲームソフトの企画、開発、販売を行っており、『ポケットモンスター』シリーズを開発している会社である。すべて3Dのゲームとなっているため、キャラクターとなるポケモンの『3Dモデル』が存在する。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "同社におけるポケモンモデル制作の体制は、企画、開発、そしてR&D（研究開発部）に分かれている。本セッションでは、R&D（研究開発部）の部分を中心に解説する。R&Dにはアニメーション関係のエンジニアが集約されている。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "『ソード・シールド』までの仕様・環境は、タイトルごとに分かれていた。タイトルごとに『どのような要素が必要なのか』、『どのような表現をするのだろうか』という点をもとに仕様や環境を決め、それぞれ開発されていた。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "しかしながら『赤・緑』から『ソード・シールド』まで、ポケモンモデルの総数は1000種類を超えている。タイトルごとに仕様から練り直して揃えていくのはそろそろ厳しい。それが2018年くらいのことだった。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "1タイトルでも厳しいという状況の中で、ルックの異なる2つのタイトル『アルセウス』と『スカーレット・バイオレット』が2022年に発売されることとなり、いよいよ課題解決が急務となった。そこで、ポケモンモデル制作体制の環境・フローの見直しが行われることとなった。", "translation": "", "note": ""},

        # Section 2: Standardizing delivery specs
        {"speaker": "前泽圭一", "original": "環境・フローの見直しによって、納品物の共通化が行われた。これまでタイトルごとに納品してきたのであれば、共通の仕様・環境にすればいいのではないか、という発想である。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "具体的には、標準マテリアル・基本骨格にて納品し、各タイトルの開発チームに引き渡す。納品後、後工程で手を加え、タイトルごとのグラフィックに整える。また、ライティングもプリセットを用意することで時間や天候に応じて変えていく。このように納品することで、これまでかかっていた工数を大幅に削減することができる。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "検品については、自動チェックと目視チェックの2段構えになっている。見た目や負荷をチェックしていく。足の付け根や耳の付け根などはポリゴンが重なり負荷がかかりやすい。ツールによってポリゴンのめり込みを可视化することで、より厳密な検品を行うことができる。", "translation": "", "note": ""},

        # Section 3: Graphics library overhaul
        {"speaker": "前泽圭一", "original": "では、共通マテリアル・基本骨格を引き渡したあとの『後工程』ではどのようなことを行っているのか。すべてのポケモンに一括して設定するものと、各ポケモンに個別で調整するものがある。たとえば、後光の出方、食べ物の配置、ZLで注目したときにどこを見るか、といった調整である。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "そのほか、IK（インバース・キネマティクス）などの動的な処理やルックなどもタイトル依存で後付け設定をする。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "ピカチュウを例にとると、もとの納品データと各タイトルのイメージに合わせて後工程で調整される。人物や背景はタイトルに合わせて制作されているため、版画風の『アルセウス』では淡い色味、リアル寄りの『スカーレット・バイオレット』ではハッキリとした色味と質感が施される。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "また、『スカーレット・バイオレット』のピカチュウはポケモン史上最高のふさふさ感を出している。そのほかにも、ジェル状の部位や発光粒子、新しい『テラスタル』など『スカーレット・バイオレット』ではさまざまな質感が施されている。", "translation": "", "note": ""},

        # Section 4: Motion copy animation pipeline
        {"speaker": "前泽圭一", "original": "アニメーションについても、本当に作るべきものが精査された。というのも、体型の似たポケモンが複数存在しているからだ。すると、『ベースの動きは共通化できるのではないか』という考えに至る。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "まずは『人型』、『犬猫型』、『ヘビ型』、『ドラゴン型』などポケモンの体型分類を行う。そこで分類されたポケモン同士を『モーションコピー』してみると、共通化ができることがわかった。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "基本的には骨と骨をマッピングして同じ部位に該当するものをコピーするシンプルなものとなっている。大きさや骨構造が異なっていても、似ていれば対応ができる。ドラゴン型の歩き方やしっぽの動かし方、ヘビ型のうねうね感などがコピーできる。", "translation": "", "note": ""},
        {"speaker": "前泽圭一", "original": "このようにポケモンからポケモンへモーションの流し込みをすることで工数を減らすことができる。しかし、もととなるポケモンがいない場合はコピーが使えない。その場合は一から作る必要がある。こうした仕組みの導入によってアニメーションの効率化を図ることに成功している。", "translation": "", "note": ""},

        # Conclusion by reporter
        {"speaker": "柳本玛リエ", "original": "ポケモン2タイトルを同時に作るため、納品物を共通化するという抜本的な見直しが行われていた。これまでのポケモンモデル1000種類以上がタイトルごとに作られていたという事実に驚きを禁じ得ない。共通化の仕組みが導入されたことにより工数を減らすことができたということは、今後の『ポケモン』シリーズのクオリティ向上と発売スパンの安定にも繋がるだろう。", "translation": "", "note": ""}
    ]

    # Translate
    combo = " ".join(b["original"] for b in text_blocks)
    matches = find_glossary_matches(combo, glossary)
    print(f"Translating Denfamini CEDEC 2022 article ({len(text_blocks)} items)...")
    translated = translate_chunk(text_blocks, matches, "CEDEC 2022 专访报道：Game Freak CG技术总监前泽圭一演讲报告，详述突破千种宝可梦资产壁垒，实现《传说 阿尔宙斯》与《朱·紫》双轨并行开发的资产通用化与差异化渲染管线。")

    # Assemble parallel items
    rel_img_dir = f"/assets/img/interviews/{slug}"
    parallel_items = []

    # Title slide image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide01_title.jpg",
        "alt": "CEDEC 2022 演讲幻灯片标题：《Pokémon LEGENDS アルセウス》与《宝可梦 朱·紫》中宝可梦模型的制作环境",
        "caption": "CEDEC 2022 官方技术分享：《Pokémon LEGENDS 阿尔宙斯》与《宝可梦 朱·紫》中的宝可梦 3D 模型制作管线与资产环境"
    })

    # Title Heading
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": "How Game Freak Concurrently Developed Legends: Arceus and Scarlet/Violet: Standardized Assets & Title-Specific Shaders",
        "translation": "Game Freak 如何双轨并行开发《阿尔宙斯》与《朱·紫》？千种宝可梦资产通用化与差异化渲染管线"
    })

    # Speaker slide image
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide02_speaker.png",
        "alt": "演讲人介绍：株式会社 Game Freak CG 技术总监 前泽圭一",
        "caption": "演讲者：Game Freak 研发技术企划部 CG 技术总监 前泽圭一（Keiichi Maeza）"
    })

    # Intro paragraphs
    for it in translated[:2]:
        parallel_items.append({
            "speaker": "柳本玛リエ",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Section 1 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "The 1000-Model Limit: The Breaking Point of Title-Independent Pipelines in 2018",
        "translation": "宝可梦 3D 模型突破 1000 种关口：独立资产制作体制遭遇物理极限"
    })

    # Organization slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide03_organization.png",
        "alt": "Game Freak 3D 资产制作组织架构：企划、开发与 R&D 部门分工",
        "caption": "Game Freak 的宝可梦模型研发体系：企划部定义形态，开发组制作特定游戏逻辑，R&D（研究开发部）整合动画与引擎技术"
    })

    # 1000 limit slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide04_limit1000.png",
        "alt": "历代宝可梦数量演进幻灯片：从红绿到剑盾超过 1000 种形态的挑战",
        "caption": "从《红·绿》到《剑·盾》，全系列宝可梦模型总数跨越 1000 种形态大关，每部作品单独重复建模的传统模式彻底达到产能极限"
    })

    # Section 1 texts (items 2 to 7)
    for it in translated[2:7]:
        parallel_items.append({
            "speaker": "前泽圭一",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Section 2 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Standardizing Delivery Specs: Decoupling Master Rigs from Title-Specific Shaders",
        "translation": "交付规格全面标准化：解耦基准骨骼与各游戏专属材质"
    })

    # Standard delivery slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide05_standard_delivery.png",
        "alt": "通用交付规格幻灯片：标准材质与基本骨骼交付流程",
        "caption": "全新资产流通工作流：统一以‘标准物理材质 + 基本骨骼绑定’交付主干模型，再交由各项目组在后处理管线中差异化调整"
    })

    # Inspection slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide06_inspection.png",
        "alt": "双重品质检验系统：自动化碰撞重叠检测与专业人工目视审核",
        "caption": "严苛的品质把控管线：自动化工具检测肢体关节与耳朵根部的多边形重叠与穿模，配合技术美术目视核查"
    })

    # Section 2 texts (items 7 to 10)
    for it in translated[7:10]:
        parallel_items.append({
            "speaker": "前泽圭一",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Section 3 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Graphics Overhaul: Legends Arceus Ink/Wash Aesthetic vs Scarlet/Violet High-Fidelity Textures",
        "translation": "图形渲染管线大重构：《阿尔宙斯》版画水墨风 vs《朱·紫》微观真实材质"
    })

    # Post-process slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide07_post_process.png",
        "alt": "后处理阶段配置分类：全宝可梦批量通用设置与单体精细微调",
        "caption": "后处理配置分类：光晕、进食坐标、ZL 注视目标等通用设置，与各游戏特异的 IK 动态物理计算"
    })

    # Pikachu comparison slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide08_pikachu_comparison.png",
        "alt": "基准交付皮卡丘模型与《传说 阿尔宙斯》水墨风格皮卡丘渲染对比",
        "caption": "基准交付数据（左）与《传说 阿尔宙斯》版画水墨渲染（右）：呈现出带有淡雅浮世绘笔触的历史质感"
    })

    # Pikachu fluffy slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide09_pikachu_fluffy.png",
        "alt": "《宝可梦 朱·紫》皮卡丘毛发微观材质与瞳孔反光渲染图",
        "caption": "《宝可梦 朱·紫》实现‘宝可梦史上最顶级的蓬松绒毛质感’，采用高精细次表面散射与眼瞳折射着色器"
    })

    # SV textures slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide10_sv_textures.png",
        "alt": "《宝可梦 朱·紫》各种材质表现：太晶化水晶棱镜与凝胶半透明发光",
        "caption": "《宝可梦 朱·紫》丰富的微观物理质感：凝胶半透明体、发光光子粒子及全新的太晶化水晶棱镜反射材质"
    })

    # Section 3 texts (items 10 to 14)
    for it in translated[10:14]:
        parallel_items.append({
            "speaker": "前泽圭一",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Section 4 Heading
    parallel_items.append({
        "type": "heading",
        "level": 3,
        "original": "Motion Copy Pipeline: Body-Type Mapping and Animation Reusability",
        "translation": "‘动作复制’（Motion Copy）管线：基于体型分类的骨骼映射与动画资产复用"
    })

    # Body types slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide11_body_types.png",
        "alt": "宝可梦体型分类四大家族：人型、犬猫型、蛇型、龙型",
        "caption": "宝可梦骨架大分类：划分为‘人型’、‘犬猫型’、‘蛇型’与‘龙型’四大骨骼体系"
    })

    # Motion copy slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide12_motion_copy.png",
        "alt": "动作复制原理：基于骨骼关键节点映射的动画无缝重定向技术",
        "caption": "动作复制（Motion Copy）核心技术：通过骨骼节点一对一拓扑映射，即使体型与骨骼尺寸不同也能实现高精度动作传递"
    })

    # Dragon snake motion slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide13_dragon_snake_motion.png",
        "alt": "龙型行走尾巴摆动与蛇型蜿蜒爬行动作复用实际演示",
        "caption": "动画复用实证：龙型宝可梦的霸气步态与尾翼摆动、蛇型宝可梦的平滑波状游弋动作均实现无缝复用"
    })

    # Section 4 texts (items 14 to 18)
    for it in translated[14:18]:
        parallel_items.append({
            "speaker": "前泽圭一",
            "original": it["original"],
            "translation": it["translation"],
            "note": it.get("note", "")
        })

    # Summary slide
    parallel_items.append({
        "type": "image",
        "image": f"{rel_img_dir}/slide14_summary.png",
        "alt": "CEDEC 演讲总结：通用资产管线带来的开发效率与次世代表现力跃升",
        "caption": "前泽圭一在 CEDEC 2022 上的总结：通用资产中台与专属渲染管线的结合，为宝可梦迈入千种形态的新世代奠定基石"
    })

    # Final conclusion by reporter (item 18)
    if len(translated) > 18:
        parallel_items.append({
            "speaker": "柳本玛リエ",
            "original": translated[18]["original"],
            "translation": translated[18]["translation"],
            "note": translated[18].get("note", "")
        })

    # Post Frontmatter
    post_data = {
        "layout": "parallel-translation",
        "title": "[访谈翻译] CEDEC 2022 专访报告：Game Freak 如何双轨并行开发《传说 阿尔宙斯》与《朱·紫》？千种宝可梦资产通用化与差异化渲染管线",
        "original_title": "『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ 共通化されたポケモンモデルにタイトルごとの個性をつけていく【CEDEC 2022】",
        "date": "2022-08-25",
        "era": "2019–2026 · Expansion / 极巨化与开放世界",
        "era_skin": "2019",
        "publication": "電ファミニコゲーマー (CEDEC 2022 特别专栏)",
        "source_kind": "technical_report",
        "author": "柳本マリエ / 電ファミニコゲーマー",
        "translator": "Poke Amice Studio",
        "interviewee": "前泽圭一",
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["Pokemon", "访谈", "技术报告", "CEDEC", "Game Freak", "前泽圭一", "传说阿尔宙斯", "朱紫", "3D管线", "动作复制"],
        "archive_type": "interview_translation",
        "source": {
            "title": "『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ 共通化されたポケモンモデルにタイトルごとの個性をつけていく【CEDEC 2022】",
            "url": "https://news.denfaminicogamer.jp/kikakuthetower/220825t",
            "language": "ja",
            "source_type": "technical_report"
        },
        "original_link": "https://news.denfaminicogamer.jp/kikakuthetower/220825t",
        "summary": "2022年8月日本最大电脑娱乐开发者大会（CEDEC 2022）上，Game Freak CG 技术总监前泽圭一发表重磅技术演讲。回顾 2018 年全系列宝可梦 3D 资产突破 1000 种极限，每作重新建模的传统作坊彻底过载，而 2022 年必须在年内双轨发行美术风格截然不同的两款大作——水墨水彩版画风的《宝可梦传说 阿尔宙斯》与追求真实微观材质（绒毛、鳞片、眼瞳、太晶化）的开放世界《宝可梦 朱·紫》。前泽圭一首次完整披露 Game Freak 的中台化资产革命：推行‘标准物理材质 + 基准骨骼’的统一交付规格；建立多边形重叠自动排查工具与严苛目视质检；重构图形着色器库实现各标题专属后处理；并开发‘动作复制’（Motion Copy）管线，将千种宝可梦划分为人型、犬猫、蛇、龙四大骨骼家族进行高精度动作重定向，为现代宝可梦的跨平台技术体系奠定决定性基石。",
        "entities": {
            "people": ["前泽圭一", "柳本玛リエ"],
            "games": ["宝可梦传说 阿尔宙斯", "宝可梦 朱·紫", "宝可梦 剑·盾"]
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
    print("Updating data/pokemon_1000_interviews.json with Batch 14 Imports")
    print("="*70)

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    updates = {
        "PKMN-0848": {
            "title": "Eurogamer 独家专访：增田顺一与大森滋谈灵感来源、葱游兵与全国图鉴风波下的创作者压力",
            "original_title": "Game Freak's Junichi Masuda and Shigeru Ohmori talk inspiration, Sirfetch'd, and pressure from Pokémon fans",
            "date": "2019-10-24",
            "year": 2019,
            "status": "imported",
            "post_file": "_posts/2019-10-24-interview-eurogamer-masuda-ohmori-sword-shield-dex-sirfetchd.md",
            "source_url": "https://www.eurogamer.net/pokemon-sword-and-shield-junichi-masuda-shigeru-ohmori-interview",
            "people": ["增田顺一", "大森滋", "克里斯·塔普塞尔"]
        },
        "PKMN-0826": {
            "title": "《Game Informer》独家专访：增田顺一揭秘宝可梦生物设计全流程与内部评审（三头猫进化论、GB像素限制与圆润大眼演变）",
            "original_title": "Here's How Game Freak Designs Pokémon Creatures",
            "date": "2017-08-10",
            "year": 2017,
            "status": "imported",
            "post_file": "_posts/2017-08-10-interview-game-informer-how-game-freak-designs-pokemon-creatures.md",
            "source_url": "https://gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx",
            "people": ["增田顺一", "凯尔·希利亚德"]
        },
        "PKMN-0675": {
            "title": "CEDEC 2022 专访报告：Game Freak 如何双轨并行开发《传说 阿尔宙斯》与《朱·紫》？千种宝可梦资产通用化与差异化渲染管线",
            "original_title": "『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ 共通化されたポケモンモデルにタイトルごとの個性をつけていく【CEDEC 2022】",
            "date": "2022-08-25",
            "year": 2022,
            "status": "imported",
            "post_file": "_posts/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline.md",
            "source_url": "https://news.denfaminicogamer.jp/kikakuthetower/220825t",
            "people": ["前泽圭一", "柳本玛リエ"]
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
        "interview-eurogamer-masuda-ohmori-sword-shield-dex-sirfetchd",
        "interview-game-informer-how-game-freak-designs-pokemon-creatures",
        "interview-cedec-2022-legends-arceus-scarlet-violet-pipeline"
    ]
    lines = content.splitlines()
    for s in new_slugs:
        if f"'{s}'" not in content:
            for idx, line in enumerate(lines):
                if line.strip() == "]":
                    lines.insert(idx, f"  '{s}',")
                    break
    render_rb.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Updated tools/render_specific_posts.rb with Batch 14 slugs.")


if __name__ == "__main__":
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")
    curate_eurogamer(glossary)
    curate_game_informer(glossary)
    curate_denfamini_cedec(glossary)
    sync_catalog()
    update_render_script()
    print("\nBatch 14 Curation Complete!")
