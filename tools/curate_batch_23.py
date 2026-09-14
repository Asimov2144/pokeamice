#!/usr/bin/env python3
"""
Curate Batch 23:
1. PKMN-1060: Game Informer 2017: Here's How Game Freak Designs Pokémon Creatures (2017-08-10)
   - Ken Sugimori & Junichi Masuda on Design Rules, Workflow & 3D Evolution
   - Notion item 39 / Stage 1 #5
2. PKMN-1061: Game Informer 2017: Why Ruby And Sapphire Were The Most Challenging Pokémon To Make (2017-08-14)
   - Junichi Masuda on GBA Transition, Stress, & Re-inventing the Series
3. PKMN-1062: FUN'S PROJECT 2018: にしだあつこ対談-中川翔子のポップカルチャー・ラボ (2018-06-25)
   - Atsuko Nishida × Shoko Nakagawa on Pikachu Conception, Dot Art, and Silhouette Philosophy
   - Notion item 168 / Stage 8 #10
"""

import os
import re
import ssl
import sys
import json
import time
import urllib.request
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

CACHE_DIR = Path("tools/cache_batch_23")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def load_glossary() -> list[dict]:
    candidates = [
        Path("data/glossary-master.json"),
        Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json"),
    ]
    for c in candidates:
        if c.exists():
            try:
                data = json.loads(c.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    print(f"Loaded master glossary ({len(data)} terms) from {c}")
                    return data
            except Exception as e:
                print(f"Error reading {c}: {e}")
    return []


def match_glossary_terms(text: str, glossary: list[dict]) -> list[tuple[str, str]]:
    matches = []
    text_lower = text.lower()
    for item in glossary:
        target = item.get("target_zh", "")
        for term in [
            item.get("source_term", ""),
            item.get("source_term_ja", ""),
            item.get("source_term_en", ""),
        ]:
            if not term:
                continue
            t = term.strip()
            if not t or len(t) <= 1:
                continue
            if re.search(r"[a-zA-Z]", t):
                if len(t) <= 2:
                    continue
                if re.search(r"\b" + re.escape(t.lower()) + r"\b", text_lower):
                    matches.append((t, target))
            else:
                if t in text:
                    matches.append((t, target))
    seen = set()
    unique = []
    for term, target in sorted(matches, key=lambda x: -len(x[0])):
        if term not in seen:
            seen.add(term)
            unique.append((term, target))
    return unique[:60]


def fetch_html(url: str, encoding: str = "utf-8") -> str:
    cache_name = re.sub(r"[^a-zA-Z0-9]", "_", url)[:80] + ".html"
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
        raw = resp.read()
    try:
        html = raw.decode(encoding)
    except:
        html = raw.decode("utf-8", "replace")
    cache_path.write_text(html, encoding="utf-8")
    return html


def download_image(img_url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(img_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = resp.read()
        if len(data) > 500:
            dest_path.write_bytes(data)
            print(f"Downloaded image: {dest_path.name} ({len(data)} bytes)")
            return True
    except Exception as e:
        print(f"Failed to download image {img_url}: {e}")
    return False


def call_deepseek(prompt: str, system_prompt: str = "") -> str:
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY is not set!")
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
                or (
                    "你是一名拥有20年宝可梦历史考据经验的资深游戏本地化翻译专家兼历史研究学者。"
                    "你的翻译风格典雅、准确、信达雅，严谨保留专访人物的原有语调与生动细节。"
                    "必须严格执行官方简体中文规范译名（宝可梦、招式、特性、道具等），严禁使用已废弃的旧译名（如口袋妖怪、宠物小精灵、神奇宝贝、怪兽球等）。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        data=data_bytes,
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"DeepSeek call attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("DeepSeek call failed after multiple attempts")


def translate_segments(segments: list[dict], source_lang: str, glossary: list[dict], post_cache_id: str) -> list[dict]:
    cache_file = CACHE_DIR / f"{post_cache_id}_translated.json"
    if cache_file.exists():
        try:
            cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
            if len(cached_data) == len(segments):
                print(f"Using cached translations ({len(cached_data)} items) for {post_cache_id}")
                return cached_data
        except Exception as e:
            print(f"Error loading translation cache {cache_file}: {e}")

    print(f"Translating {len(segments)} segments for {post_cache_id}...")
    batch_size = 8
    translated_segments = []

    for i in range(0, len(segments), batch_size):
        batch = segments[i : i + batch_size]
        # Check which need translation
        to_translate = []
        for idx_in_batch, item in enumerate(batch):
            itype = item.get("type", "paragraph")
            if itype in ("image", "hr"):
                continue
            orig = item.get("original", "").strip()
            if orig and not item.get("translation"):
                to_translate.append((idx_in_batch, item))

        if to_translate:
            combined_text = "\n".join([f"[{k}] {item['original']}" for k, item in to_translate])
            matched = match_glossary_terms(combined_text, glossary)
            glossary_hint = "\n".join([f"- {s} => {t}" for s, t in matched])

            lang_name = "英文" if source_lang == "en" else "日文"
            prompt = f"""请将以下来自宝可梦历史深度访谈的{lang_name}文本逐条翻译为地道、典雅、专业的简体中文。
严格要求：
1. 保持原意完整，绝不漏译、删减或自我总结；
2. 术语严格遵照宝可梦官方规范（禁止出现旧译名如神奇宝贝、口袋妖怪等）：
{glossary_hint}
3. 保持序号格式输出，格式如：
[0] 对应中文译文
[1] 对应中文译文

原文列表：
{combined_text}
"""
            res = call_deepseek(prompt)
            # Parse responses
            res_dict = {}
            for line in res.split("\n"):
                m = re.match(r"^\[(\d+)\]\s*(.*)$", line.strip())
                if m:
                    res_dict[int(m.group(1))] = m.group(2).strip()

            for k, item in to_translate:
                if k in res_dict:
                    item["translation"] = res_dict[k]
                else:
                    # fallback single
                    single_prompt = f"请翻译以下{lang_name}句子为简体中文（严守宝可梦官方名词规范）：\n{item['original']}"
                    item["translation"] = call_deepseek(single_prompt)
            time.sleep(0.5)

        for item in batch:
            translated_segments.append(item)
        print(f"  Processed {min(i+batch_size, len(segments))}/{len(segments)} segments...")

    cache_file.write_text(json.dumps(translated_segments, ensure_ascii=False, indent=2), encoding="utf-8")
    return translated_segments


# ---------------------------------------------------------------------------
# 1. PKMN-1060: Game Informer 2017 Creature Design
# ---------------------------------------------------------------------------
def curate_pkmn_1060(glossary: list[dict]):
    slug = "2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures"
    url = "https://www.gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx"
    print(f"\n========================================\nCurating PKMN-1060: {url}\n========================================")
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_="field--name-body")
    if not article:
        raise ValueError("Article body not found in GI Design")

    img_dir = Path(f"assets/img/interviews/{slug}")
    img_dir.mkdir(parents=True, exist_ok=True)

    segments = []
    # GI Design has lead text, quotes from Ken Sugimori & Junichi Masuda
    raw_paragraphs = article.find_all(["p", "h2", "h3", "figure", "img"], recursive=False)
    
    img_counter = 1
    for el in raw_paragraphs:
        # Check image
        img = el.find("img") or (el if el.name == "img" else None)
        if img:
            src = img.get("src", "")
            if src:
                if src.startswith("/"):
                    src = "https://www.gameinformer.com" + src
                ext = Path(urlparse(src).path).suffix or ".jpg"
                local_img_name = f"design_{img_counter:02d}{ext}"
                local_img_path = img_dir / local_img_name
                download_image(src, local_img_path)
                
                caption = ""
                # check if there's caption text in p
                txt = el.get_text(strip=True)
                if txt and not txt.startswith("/s3/"):
                    caption = txt

                segments.append({
                    "type": "image",
                    "image": f"/assets/img/interviews/{slug}/{local_img_name}",
                    "caption": caption,
                    "alt": f"Game Informer - How Game Freak Designs Pokémon Creatures - Figure {img_counter}"
                })
                img_counter += 1
                if caption:
                    continue

        txt = el.get_text(strip=True)
        if not txt or txt.startswith("/s3/") or "check out the latest issue" in txt.lower():
            continue

        if el.name in ["h2", "h3"]:
            segments.append({
                "type": "section",
                "level": 2 if el.name == "h2" else 3,
                "original": txt,
                "translation": ""
            })
            continue

        # Check speaker in paragraph
        # Quotes often have: Sugimori says, Masuda says, or "quote" - Sugimori
        speaker = None
        # Check if the whole paragraph is spoken by Sugimori or Masuda
        if "Sugimori says" in txt or "says Sugimori" in txt or txt.endswith("– Sugimori") or txt.endswith("- Sugimori"):
            speaker = "杉森建"
        elif "Masuda says" in txt or "says Masuda" in txt or txt.endswith("– Masuda") or txt.endswith("- Masuda"):
            speaker = "增田顺一"
        
        segments.append({
            "type": "paragraph",
            "original": txt,
            "translation": "",
            "speaker": speaker
        })

    # Translate
    translated = translate_segments(segments, "en", glossary, "pkmn_1060")

    # Frontmatter
    fm = {
        "layout": "parallel-translation",
        "title": "Game Informer 独家特写：Game Freak 是如何设计宝可梦的？——杉森建与增田顺一深度复盘生物设计法则、评审委员会机制与 3D 演进",
        "original_title": "Here's How Game Freak Designs Pokémon Creatures",
        "date": "2017-08-10 12:00:00 +0900",
        "era": "2017–2021 · Switch / 开放世界探索",
        "era_skin": "2019",
        "publication": "Game Informer 独家封面特辑",
        "source_kind": "web",
        "source": {
            "title": "Here's How Game Freak Designs Pokémon Creatures",
            "url": url,
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "2017年《Game Informer》深入探访 Game Freak 东京总部，艺术总监杉森建与制作人增田顺一首次完整解密宝可梦的诞生管线：从全员提案制、由核心主创组成的‘设计评审委员会’，到杉森建独创的‘反差美学法则’（在帅气的怪物上加点滑稽，在可爱的精灵上加点惊悚），以及从 2D 点阵过渡到 3D 全模型时代对宝可梦眼部表情与动态剪影的严苛要求。",
        "categories": ["访谈翻译", "角色设计", "开发历史"],
        "tags": [
            "Game Informer",
            "Game Freak",
            "杉森建",
            "增田顺一",
            "宝可梦设计",
            "生物设计",
            "角色设计",
            "第七世代",
            "日月",
            "3D建模"
        ],
        "author": "Kyle Hilliard (Game Informer)",
        "interviewee": "杉森建（GAME FREAK 艺术总监）、增田顺一（GAME FREAK 制作人）",
        "cast": [
            {
                "id": "sugimori",
                "name": "杉森建",
                "role": "GAME FREAK 董事兼艺术总监",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            },
            {
                "id": "masuda",
                "name": "增田顺一",
                "role": "GAME FREAK 董事兼制作人",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            },
            {
                "id": "gi",
                "name": "Game Informer",
                "role": "采访媒体 / 记者",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            }
        ],
        "parallel_items": translated
    }

    out_file = Path(f"_posts/{slug}.md")
    out_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    out_file.write_text(out_content, encoding="utf-8")
    print(f"Generated post: {out_file} ({len(translated)} items)")


# ---------------------------------------------------------------------------
# 2. PKMN-1061: Game Informer 2017 Ruby/Sapphire Most Challenging
# ---------------------------------------------------------------------------
def curate_pkmn_1061(glossary: list[dict]):
    slug = "2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging"
    url = "https://www.gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx"
    print(f"\n========================================\nCurating PKMN-1061: {url}\n========================================")
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_="field--name-body")
    if not article:
        raise ValueError("Article body not found in GI RS")

    img_dir = Path(f"assets/img/interviews/{slug}")
    img_dir.mkdir(parents=True, exist_ok=True)

    segments = []
    raw_paragraphs = article.find_all(["p", "h2", "h3", "figure", "img"], recursive=False)
    
    img_counter = 1
    for el in raw_paragraphs:
        img = el.find("img") or (el if el.name == "img" else None)
        if img:
            src = img.get("src", "")
            if src:
                if src.startswith("/"):
                    src = "https://www.gameinformer.com" + src
                ext = Path(urlparse(src).path).suffix or ".jpg"
                local_img_name = f"rs_dev_{img_counter:02d}{ext}"
                local_img_path = img_dir / local_img_name
                download_image(src, local_img_path)
                
                caption = ""
                txt = el.get_text(strip=True)
                if txt and not txt.startswith("/s3/"):
                    caption = txt

                segments.append({
                    "type": "image",
                    "image": f"/assets/img/interviews/{slug}/{local_img_name}",
                    "caption": caption,
                    "alt": f"Game Informer - Why Ruby And Sapphire Were The Most Challenging Pokémon To Make - Figure {img_counter}"
                })
                img_counter += 1
                if caption:
                    continue

        txt = el.get_text(strip=True)
        if not txt or txt.startswith("/s3/") or "check out the latest issue" in txt.lower():
            continue

        if el.name in ["h2", "h3"]:
            segments.append({
                "type": "section",
                "level": 2 if el.name == "h2" else 3,
                "original": txt,
                "translation": ""
            })
            continue

        speaker = None
        if "Masuda says" in txt or "says Masuda" in txt or txt.startswith('"I got really stressed') or txt.startswith('"The morning of'):
            speaker = "增田顺一"

        segments.append({
            "type": "paragraph",
            "original": txt,
            "translation": "",
            "speaker": speaker
        })

    translated = translate_segments(segments, "en", glossary, "pkmn_1061")

    fm = {
        "layout": "parallel-translation",
        "title": "Game Informer 独家专访：为何《红宝石·蓝宝石》是 Game Freak 史上最艰巨的一役？——增田顺一复盘 GBA 转型阵痛、健康危机与破局之道",
        "original_title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
        "date": "2017-08-14 12:00:00 +0900",
        "era": "2002–2006 · GBA / 丰缘与无线对战",
        "era_skin": "2003",
        "publication": "Game Informer 独家特写",
        "source_kind": "web",
        "source": {
            "title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
            "url": url,
            "language": "en",
            "source_type": "web_interview"
        },
        "original_link": url,
        "summary": "在第三世代《宝可梦 红宝石·蓝宝石》开发期间，Game Freak 面临前所未有的生死关头：坊间充斥着‘宝可梦热潮已死’的断言，技术从黑白GB一跃进入GBA色彩绚烂的全新硬件。首次独自挑起总监兼作曲重担的增田顺一，因背负全社命运的极端焦虑与高压突发重度胃病送医急救、佩戴动态心电监护仪坚持研发。本访谈真实还原了增田顺一如何带领团队以特性、性格、双打对战等划时代系统实现逆风翻盘的悲壮历史。",
        "categories": ["访谈翻译", "开发历史", "总监专访"],
        "tags": [
            "Game Informer",
            "Game Freak",
            "增田顺一",
            "红宝石·蓝宝石",
            "GBA",
            "第三世代",
            "开发秘辛",
            "丰缘地区"
        ],
        "author": "Kyle Hilliard (Game Informer)",
        "interviewee": "增田顺一（GAME FREAK 制作人／《红宝石·蓝宝石》游戏总监兼作曲）",
        "cast": [
            {
                "id": "masuda",
                "name": "增田顺一",
                "role": "《红宝石·蓝宝石》游戏总监 / 作曲 / 制作人",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            },
            {
                "id": "gi",
                "name": "Game Informer",
                "role": "采访媒体 / 记者",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            }
        ],
        "parallel_items": translated
    }

    out_file = Path(f"_posts/{slug}.md")
    out_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    out_file.write_text(out_content, encoding="utf-8")
    print(f"Generated post: {out_file} ({len(translated)} items)")


# ---------------------------------------------------------------------------
# 3. PKMN-1062: FUN'S PROJECT 2018 Atsuko Nishida × Shoko Nakagawa
# ---------------------------------------------------------------------------
def curate_pkmn_1062(glossary: list[dict]):
    slug = "2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design"
    url_p1 = "https://funs-project.com/poplab/007/"
    url_p2 = "https://funs-project.com/poplab/007/index_2.html"
    print(f"\n========================================\nCurating PKMN-1062: {url_p1}\n========================================")

    img_dir = Path(f"assets/img/interviews/{slug}")
    img_dir.mkdir(parents=True, exist_ok=True)

    segments = []
    pages = [
        (url_p1, "前篇：设计宝可梦时，为何要尽可能精简部件？"),
        (url_p2, "后篇：点阵绘图是我的原点——皮卡丘之母的插画哲思"),
    ]

    img_counter = 1
    seen_images = set()

    for page_idx, (p_url, page_heading) in enumerate(pages, 1):
        html = fetch_html(p_url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Add section heading for page
        segments.append({
            "type": "section",
            "level": 2,
            "original": f"【第{page_idx}回】" + ("前編：ポケモンをデザインする際、出来るだけパーツを少なくする理由" if page_idx == 1 else "後編：「ドット絵は私の原点」（にしだあつこ）"),
            "translation": page_heading
        })

        # Collect images on page
        # Check images inside .specialOuter or .mainContents
        art = soup.find("article", class_="specialOuter") or soup.find("body")
        for img in art.find_all("img"):
            src = img.get("src", "")
            if any(k in src for k in ["007", "poplab", "spe_", "special"]) and not any(k in src for k in ["btn", "icon", "arrow", "logo", "tw", "fb"]):
                abs_src = urljoin(p_url, src)
                if abs_src not in seen_images:
                    seen_images.add(abs_src)
                    ext = Path(urlparse(abs_src).path).suffix or ".jpg"
                    local_img_name = f"funs_007_{img_counter:02d}{ext}"
                    local_img_path = img_dir / local_img_name
                    if download_image(abs_src, local_img_path):
                        caption = img.get("alt", "")
                        segments.append({
                            "type": "image",
                            "image": f"/assets/img/interviews/{slug}/{local_img_name}",
                            "caption": caption,
                            "alt": f"FUN'S PROJECT 西田敦子×中川翔子 角色设计对谈 - 图{img_counter}"
                        })
                        img_counter += 1

        # Collect QA dialogues
        qa = soup.find("div", class_="specialQA")
        if qa:
            for child in qa.children:
                if not child.name:
                    continue
                # heading inside QA
                if child.name in ["h2", "h3"]:
                    htxt = child.get_text(strip=True)
                    if htxt and "Profile" not in htxt and "＞＞" not in htxt:
                        segments.append({
                            "type": "section",
                            "level": 3,
                            "original": htxt,
                            "translation": ""
                        })
                    continue

                if child.name == "p":
                    ptxt = child.get_text(strip=True)
                    if not ptxt or "Profile" in ptxt or "＞＞" in ptxt or "Photo :" in ptxt:
                        continue
                    # Check if paragraph has lead intro
                    segments.append({
                        "type": "paragraph",
                        "original": ptxt,
                        "translation": "",
                        "speaker": None
                    })
                    continue

                if child.name == "dl":
                    # Dialogue term / description
                    dtxt = child.get_text(strip=True)
                    if not dtxt:
                        continue
                    speaker = None
                    clean_orig = dtxt
                    if dtxt.startswith("中川"):
                        speaker = "中川翔子"
                        clean_orig = re.sub(r"^中川\s*", "", dtxt)
                    elif dtxt.startswith("にしだ"):
                        speaker = "西田敦子"
                        clean_orig = re.sub(r"^にしだ\s*", "", dtxt)

                    segments.append({
                        "type": "paragraph",
                        "original": clean_orig,
                        "translation": "",
                        "speaker": speaker
                    })

    # Translate
    translated = translate_segments(segments, "ja", glossary, "pkmn_1062")

    fm = {
        "layout": "parallel-translation",
        "title": "FUN'S PROJECT 独家对谈：皮卡丘之母西田敦子 × 中川翔子角色设计特辑——从大福饼、松鼠颊囊到点阵原画与女性创作者心得",
        "original_title": "グラフィックデザイナー・イラストレーター にしだあつこ対談 - 中川翔子のポップカルチャー・ラボ",
        "date": "2018-06-25 12:00:00 +0900",
        "era": "2017–2021 · Switch / 开放世界探索",
        "era_skin": "2019",
        "publication": "DNP 大日本印刷 FUN'S PROJECT",
        "source_kind": "web",
        "source": {
            "title": "グラフィックデザイナー・イラストレーター にしだあつこ対談 - 中川翔子のポップカルチャー・ラボ",
            "url": url_p1,
            "language": "ja",
            "source_type": "web_interview"
        },
        "original_link": url_p1,
        "summary": "大日本印刷创作者共创服务‘FUN'S PROJECT’专栏特辑。宝可梦初代王牌设计师、‘皮卡丘之母’西田敦子与知名艺人兼漫画家中川翔子展开深度对谈。西田敦子首次详述：仙子伊布为何采用粉红配天蓝的大胆配色、成吉思汗烤肉如何启发风妖精、随身携带的A5大学笔记里藏着的‘大福饼’构想、宝可梦设计精髓‘尽量精简部件以确保剪影辨识度’的黄金法则，以及早期受制于Game Boy点阵与色阶限制如何反而锤炼出传世设计的独到心法。",
        "categories": ["访谈翻译", "角色设计", "对谈"],
        "tags": [
            "西田敦子",
            "中川翔子",
            "皮卡丘",
            "仙子伊布",
            "风妖精",
            "角色设计",
            "点阵绘",
            "FUN'S PROJECT",
            "伊布",
            "初代开发"
        ],
        "author": "Takanori Kuroda (FUN'S PROJECT)",
        "interviewee": "西田敦子（插画师／角色设计师）、中川翔子（艺人／歌手／插画家）",
        "cast": [
            {
                "id": "nishida",
                "name": "西田敦子",
                "role": "角色设计师 / 插画师 / 皮卡丘原案设计",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            },
            {
                "id": "nakagawa",
                "name": "中川翔子",
                "role": "艺人 / 歌手 / 漫画家 / 宝可梦狂热粉丝",
                "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"
            }
        ],
        "parallel_items": translated
    }

    out_file = Path(f"_posts/{slug}.md")
    out_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    out_file.write_text(out_content, encoding="utf-8")
    print(f"Generated post: {out_file} ({len(translated)} items)")


def main():
    glossary = load_glossary()
    curate_pkmn_1060(glossary)
    curate_pkmn_1061(glossary)
    curate_pkmn_1062(glossary)
    print("\nAll 3 Batch 23 interviews curated successfully!")


if __name__ == "__main__":
    main()
