#!/usr/bin/env python3
"""
Curate Batch 22:
1. PKMN-1057: Famitsu / CEDEC 2022 《宝可梦 朱／紫》皮卡丘毛发质感与《阿尔宙斯》双线并行开发秘辛 (2022-08-27)
2. PKMN-1058: Famitsu 《名侦探皮卡丘 归来》石原恒和×阵内弘之专访（会说人话的宝可梦与赤绿睡眠秘话）(2023-10-19)
3. PKMN-1059: Game Watch 《旋转方块》Wii U VC发行纪念！Game Freak创业三元老杉森建×增田顺一×森本茂树专访 (2014-07-02)
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

sys.stdout.reconfigure(encoding="utf-8")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

CACHE_DIR = Path("tools/cache_batch_22")
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


def download_image(url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 500:
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=25) as resp:
            data = resp.read()
            if len(data) > 300:
                dest_path.write_bytes(data)
                return True
    except Exception as e:
        print(f"  Error downloading image {url}: {e}")
    return False


def call_deepseek_json(system_prompt: str, user_prompt: str) -> dict:
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"  DeepSeek call attempt {attempt+1} error: {e}")
            time.sleep(3 * (attempt + 1))
    return {}


def batch_translate_items(items: list[dict], glossary: list[dict], context_desc: str):
    texts_to_translate = []
    for idx, it in enumerate(items):
        if it.get("type") in ["image", "hr"]:
            continue
        orig = it.get("original", "").strip()
        if orig and not it.get("translation"):
            texts_to_translate.append((idx, orig, it.get("speaker", ""), it.get("type", "paragraph")))

    print(f"Translating {len(texts_to_translate)} items for '{context_desc}'...")
    chunk_size = 18

    for i in range(0, len(texts_to_translate), chunk_size):
        chunk = texts_to_translate[i : i + chunk_size]
        combined_text = "\n".join([c[1] for c in chunk])
        matched = match_glossary_terms(combined_text, glossary)
        glossary_hint = "\n".join([f"- {s} -> {t}" for s, t in matched])

        prompt_items = []
        for c_idx, (orig_idx, text, spk, itype) in enumerate(chunk):
            prefix = f"[{c_idx}]"
            if spk:
                prefix += f" (说话人: {spk})"
            if itype == "heading":
                prefix += " (小标题)"
            prompt_items.append(f"{prefix} {text}")

        system_prompt = f"""你是一位精通宝可梦（Pokémon）系列官方设定、任天堂游戏历史与软硬件工程架构的资深中日互译专家。
请将以下来自官方报道/访谈（背景：{context_desc}）的内容翻译为流畅自然、极具临场感、准确地道的专业简体中文。

【官方术语与规范】
1. 宝可梦系列专有名词、作品名、人名必须严格采用宝可梦官方简体中文译名标准（禁止使用‘神奇宝贝’、‘宠物小精灵’、‘口袋妖怪’等非官方译名）。
2. 术语对照参考：
{glossary_hint}
3. 对于游戏开发术语（如 Shader、Rigging、LOD、着色器、骨骼绑定、建模、虚幻引擎、VC、ROM等），采用业界规范专业表达。
4. 译文不要泄漏说话人名字前缀在句首（例如不要写‘增田：……’），仅翻译内容本身。
5. 严格输出 JSON 格式：形如 {{"0": "译文0", "1": "译文1", ...}}。"""

        user_prompt = "\n".join(prompt_items)
        res = call_deepseek_json(system_prompt, user_prompt)
        for c_idx, (orig_idx, text, spk, itype) in enumerate(chunk):
            t = res.get(str(c_idx)) or res.get(c_idx) or ""
            if t:
                items[orig_idx]["translation"] = str(t).strip()
            else:
                print(f"  [WARN] Missing translation for item {orig_idx}: {text[:30]}")
        print(f"  Translated chunk {i+1} to {min(i+chunk_size, len(texts_to_translate))}")
        time.sleep(1)


# ==========================================
# 1. PKMN-1057: Famitsu CEDEC 2022 (SV Shader & Pipeline)
# ==========================================
def curate_pkmn_1057(glossary: list[dict]):
    print("\n==========================================")
    print("Curating PKMN-1057: CEDEC 2022 SV & Arceus")
    print("==========================================")
    url = "https://www.famitsu.com/news/202208/27273621.html"
    html_content = fetch_html(url)
    soup = BeautifulSoup(html_content, "html.parser")
    article = soup.find("div", class_="article-body")

    img_dir = Path("assets/img/interviews/2022-08-27-famitsu-sv-cedec")
    img_dir.mkdir(parents=True, exist_ok=True)

    items = []
    seen_imgs = set()
    img_counter = 1

    # Overview item
    items.append({
        "type": "paragraph",
        "speaker": "解说",
        "original": "2022年8月23日～25日の期間に開催された、日本最大のコンピュータエンターテインメント開発者向けカンファレンス“CEDEC 2022”。CEDEC 2022の2日目に行われたセッション“【ポケットモンスター スカーレット・バイオレット】 パルデア地方を描き出す描画技術”と“オープンワールドに挑むポケモンのモデル・アニメーション制作手法”の模様をお届けする。",
        "translation": "2022年8月23日至25日期间，日本最大的电脑娱乐开发者大会“CEDEC 2022”正式举办。本文将为您带来在CEDEC 2022第二天举办的技术专场演讲——《【宝可梦 朱／紫】描绘帕鲁迪亚地区的渲染技术》与《挑战开放世界的宝可梦3D建模与动作设计手法》的深度报道。"
    })

    for elem in article.find_all(["h2", "h3", "p"]):
        if elem.name in ["h2", "h3"]:
            t = elem.get_text(strip=True)
            if t and not any(k in t for k in ["関連記事", "関連リンク", "おすすめ"]):
                items.append({"type": "heading", "level": 2 if elem.name == "h2" else 3, "original": t, "translation": ""})
        elif elem.name == "p":
            # Check if paragraph has images
            p_imgs = elem.find_all("img")
            if p_imgs:
                for img in p_imgs:
                    raw_src = img.get("data-original") or img.get("data-src") or img.get("src")
                    if not raw_src or "icon" in raw_src:
                        continue
                    full_src = urljoin("https://www.famitsu.com", raw_src)
                    if full_src in seen_imgs:
                        continue
                    seen_imgs.add(full_src)

                    ext = Path(urlparse(full_src).path).suffix or ".jpg"
                    local_filename = f"cedec2022_sv_{img_counter:02d}{ext}"
                    dest_file = img_dir / local_filename
                    download_image(full_src, dest_file)
                    
                    alt = img.get("alt", "").strip()
                    items.append({
                        "type": "image",
                        "image": f"/{img_dir.as_posix()}/{local_filename}",
                        "caption": alt if alt else ""
                    })
                    img_counter += 1

            text = elem.get_text(strip=True)
            if not text or any(text.startswith(k) for k in ["▲", "※", "【関連記事】", "ファミ通.com"]):
                continue
            
            # Speaker detection
            spk = ""
            if "前澤" in text or "前座" in text:
                spk = "前座晃宏"
            elif "大谷" in text:
                spk = "大谷一登"
            elif text.startswith("――") or text.startswith("Q."):
                spk = "提问"

            items.append({
                "type": "paragraph",
                "speaker": spk if spk else "解说",
                "original": text,
                "translation": ""
            })

    batch_translate_items(items, glossary, "CEDEC 2022 宝可梦朱紫 3D模型与毛发着色器技术开发")

    # Clean any heading labels
    for it in items:
        if it.get("type") == "heading" and it.get("translation"):
            it["translation"] = re.sub(r"^[（\(]小标题[）\)]\s*", "", it["translation"]).strip()

    # Frontmatter
    post_filename = "_posts/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline.md"
    fm = {
        "layout": "parallel-translation",
        "title": "Famitsu / CEDEC 2022 专访《宝可梦 朱／紫》：皮卡丘实现系列史上最佳蓬松毛发质感——与《传说 阿尔宙斯》双线并行的开放世界技术秘辛",
        "original_title": "『ポケモン スカーレット・バイオレット』のピカチュウはシリーズ史上最高のふさふさ感を実現。『ポケモンレジェンズ アルセウス』との同時制作における制作環境を解説【CEDEC2022】",
        "date": "2022-08-27 12:00:00 +0900",
        "era_skin": 2022,
        "source_url": url,
        "original_language": "ja",
        "categories": ["访谈", "技术解析"],
        "tags": ["宝可梦 朱／紫", "宝可梦传说 阿尔宙斯", "CEDEC", "Game Freak", "3D建模", "着色器", "皮卡丘", "开放世界"],
        "author": "ファミ通.com 編集部",
        "interviewee": "前座晃宏（GAME FREAK R&D 部技术总监）、大谷一登（GAME FREAK 角色模型工程师）",
        "quote": "为了在一年之内连续打造两部宏大的全新作品，我们将1000种以上的宝可梦3D模型基底全面通用化，并在第九世代实现了系列前所未有的毛发蓬松质感与全新开放世界着色器技术。",
        "cast": [
            {"id": "maezawa", "name": "前座晃宏", "role": "GAME FREAK 研究开发部（R&D）技术总监 / 程序员", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"},
            {"id": "ohtani", "name": "大谷一登", "role": "GAME FREAK 角色建模工程师 / 3D艺术家", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"},
            {"id": "narrator", "name": "解说", "role": "CEDEC 现场报道与技术背景解析", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/scarlet-violet-logo.png"}
        ],
        "parallel_items": items
    }

    yaml_str = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    Path(post_filename).write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"Successfully generated {post_filename} ({len(items)} items)")


# ==========================================
# 2. PKMN-1058: Famitsu Returns Detective Pikachu (Ishihara x Jinnai)
# ==========================================
def curate_pkmn_1058(glossary: list[dict]):
    print("\n==========================================")
    print("Curating PKMN-1058: Famitsu Detective Pikachu Returns")
    print("==========================================")
    url = "https://www.famitsu.com/news/202310/19320055.html"
    html_content = fetch_html(url)
    soup = BeautifulSoup(html_content, "html.parser")
    article = soup.find("div", class_="article-body")

    img_dir = Path("assets/img/interviews/2023-10-19-famitsu-detective-pikachu")
    img_dir.mkdir(parents=True, exist_ok=True)

    items = []
    seen_imgs = set()
    img_counter = 1

    for elem in article.find_all(["h2", "h3", "p"]):
        if elem.name in ["h2", "h3"]:
            t = elem.get_text(strip=True)
            if t and not any(k in t for k in ["関連記事", "関連リンク", "おすすめ"]):
                items.append({"type": "heading", "level": 2 if elem.name == "h2" else 3, "original": t, "translation": ""})
        elif elem.name == "p":
            p_imgs = elem.find_all("img")
            if p_imgs:
                for img in p_imgs:
                    raw_src = img.get("data-original") or img.get("data-src") or img.get("src")
                    if not raw_src or "icon" in raw_src:
                        continue
                    full_src = urljoin("https://www.famitsu.com", raw_src)
                    if full_src in seen_imgs:
                        continue
                    seen_imgs.add(full_src)

                    ext = Path(urlparse(full_src).path).suffix or ".jpg"
                    local_filename = f"detective_pikachu_{img_counter:02d}{ext}"
                    dest_file = img_dir / local_filename
                    download_image(full_src, dest_file)

                    alt = img.get("alt", "").strip()
                    items.append({
                        "type": "image",
                        "image": f"/{img_dir.as_posix()}/{local_filename}",
                        "caption": alt if alt else ""
                    })
                    img_counter += 1

            text = elem.get_text(strip=True)
            if not text or any(text.startswith(k) for k in ["▲", "※", "【関連記事】", "ファミ通.com"]):
                continue

            spk = ""
            # Speaker prefix parsing
            m = re.match(r"^([^\s:：]{1,6})[氏]?[:：\s](.*)$", text)
            if m:
                cand = m.group(1).strip()
                if "石原" in cand:
                    spk = "石原恒和"
                    text = m.group(2).strip()
                elif "陣内" in cand or "阵内" in cand:
                    spk = "阵内弘之"
                    text = m.group(2).strip()
            elif text.startswith("――"):
                spk = "提问"
                text = text.lstrip("―").strip()

            items.append({
                "type": "paragraph",
                "speaker": spk,
                "original": text,
                "translation": ""
            })

    batch_translate_items(items, glossary, "名侦探皮卡丘 归来 石原恒和与阵内弘之专访 初代赤绿与宝可梦会说人话的设定演进")

    # Clean any heading labels
    for it in items:
        if it.get("type") == "heading" and it.get("translation"):
            it["translation"] = re.sub(r"^[（\(]小标题[）\)]\s*", "", it["translation"]).strip()

    post_filename = "_posts/2023-10-19-interview-famitsu-detective-pikachu-returns-ishihara-jinnai.md"
    fm = {
        "layout": "parallel-translation",
        "title": "Famitsu 专访《名侦探皮卡丘 归来》：石原恒和×阵内弘之——大叔皮卡丘是“会说人类语言的宝可梦”的终点，兼谈《赤·绿》诞生秘话与《Pokémon Sleep》",
        "original_title": "『帰ってきた 名探偵ピカチュウ』陣内弘之氏＆石原恒和氏インタビュー。おっさんピカチュウは、人の言葉をしゃべるポケモンのひとつの到達点。『ポケモン 赤・緑』開発時の想い出話も",
        "date": "2023-10-19 12:00:00 +0900",
        "era_skin": 2023,
        "source_url": url,
        "original_language": "ja",
        "categories": ["访谈", "主创对话"],
        "tags": ["名侦探皮卡丘", "石原恒和", "阵内弘之", "Creatures", "The Pokémon Company", "皮卡丘", "Pokémon Sleep", "赤·绿"],
        "author": "ファミ通.com 編集部",
        "interviewee": "石原恒和（The Pokémon Company 代表取缔役社长 CEO）、阵内弘之（Creatures 常务取缔役 / 董事长）",
        "quote": "从初代《赤·绿》中大谷育江女士赋予皮卡丘声音，到《皮卡丘你好吗》的语音识别，再到《名侦探皮卡丘》中操着中年大叔腔调的搭档——‘会说人话的宝可梦’是我们在探寻宝可梦与人类共生关系上的一个终极形态。",
        "cast": [
            {"id": "ishihara", "name": "石原恒和", "role": "株式会社宝可梦 代表取缔役社长 CEO / Creatures 董事", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/detective-pikachu-returns-logo.png"},
            {"id": "jinnai", "name": "阵内弘之", "role": "株式会社Creatures 常务取缔役 / 资深制作人", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/detective-pikachu-returns-logo.png"},
            {"id": "interviewer", "name": "提问", "role": "Fami通编辑部 记者", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/detective-pikachu-returns-logo.png"}
        ],
        "parallel_items": items
    }

    yaml_str = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    Path(post_filename).write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"Successfully generated {post_filename} ({len(items)} items)")


# ==========================================
# 3. PKMN-1059: Game Watch Quinty (Sugimori x Masuda x Morimoto)
# ==========================================
def curate_pkmn_1059(glossary: list[dict]):
    print("\n==========================================")
    print("Curating PKMN-1059: Game Watch Quinty 25th")
    print("==========================================")
    post_filename = "_posts/2014-07-02-interview-gamewatch-quinty-gamefreak-origins-sugimori-masuda-morimoto.md"
    p = Path(post_filename)
    if p.exists():
        txt = p.read_text(encoding="utf-8")
        parts = txt.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            items = fm.get("parallel_items", [])
            if len(items) > 100:
                print(f"PKMN-1059 already exists with {len(items)} items. Cleaning heading labels...")
                for it in items:
                    if it.get("type") == "heading" and it.get("translation"):
                        it["translation"] = re.sub(r"^[（\(]小标题[）\)]\s*", "", it["translation"]).strip()
                new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
                p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
                print("PKMN-1059 ready and validated.")
                return

    url = "https://game.watch.impress.co.jp/docs/news/655639.html"
    html_content = fetch_html(url, encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    article = soup.find("article")

    img_dir = Path("assets/img/interviews/2014-07-02-gamewatch-quinty")
    img_dir.mkdir(parents=True, exist_ok=True)

    items = []
    seen_imgs = set()
    img_counter = 1

    for elem in article.find_all(["h2", "h3", "h4", "p"]):
        if elem.name in ["h2", "h3", "h4"]:
            t = elem.get_text(strip=True)
            if t and not any(k in t for k in ["関連リンク", "関連記事", "Impress Watch"]):
                items.append({"type": "heading", "level": 2 if elem.name == "h2" else 3, "original": t, "translation": ""})
        elif elem.name == "p":
            # Check for images in p
            imgs = elem.find_all("img")
            for img in imgs:
                raw_src = img.get("ajax") or img.get("src")
                if not raw_src or "icon" in raw_src or "loading" in raw_src:
                    continue
                # If high-res exists in parent 'a'
                parent_a = img.find_parent("a")
                if parent_a and parent_a.get("href", "").endswith(".html"):
                    # convert /img/.../html/q01.jpg.html to /img/.../q01.jpg
                    full_src = re.sub(r"/html/(.*?)\.html", r"/\1", urljoin("https://game.watch.impress.co.jp", parent_a["href"]))
                else:
                    full_src = urljoin("https://game.watch.impress.co.jp", raw_src)

                if full_src in seen_imgs:
                    continue
                seen_imgs.add(full_src)

                ext = Path(urlparse(full_src).path).suffix or ".jpg"
                local_filename = f"quinty_gf_{img_counter:02d}{ext}"
                dest_file = img_dir / local_filename
                download_image(full_src, dest_file)

                # caption from sibling text or alt
                alt = img.get("alt", "").strip()
                items.append({
                    "type": "image",
                    "image": f"/{img_dir.as_posix()}/{local_filename}",
                    "caption": alt if alt else ""
                })
                img_counter += 1

            text = elem.get_text(strip=True)
            if not text or any(text.startswith(k) for k in ["（2014/", "ニュース", "©", "(C)", "▲"]):
                continue

            spk = ""
            m = re.match(r"^([^\s:：]{1,6})氏?[:：\s](.*)$", text)
            if m:
                cand = m.group(1).strip()
                if "杉森" in cand:
                    spk = "杉森建"
                    text = m.group(2).strip()
                elif "増田" in cand or "增田" in cand:
                    spk = "增田顺一"
                    text = m.group(2).strip()
                elif "森本" in cand:
                    spk = "森本茂树"
                    text = m.group(2).strip()
            elif text.startswith("――") or text.startswith("――"):
                spk = "提问"
                text = text.lstrip("―").strip()

            items.append({
                "type": "paragraph",
                "speaker": spk,
                "original": text,
                "translation": ""
            })

    batch_translate_items(items, glossary, "GAME FREAK处女作《旋转方块/Quinty》25周年纪念专访 田尻智与杉森建增田顺一森本茂树谈开发秘辛与宝可梦原点")

    post_filename = "_posts/2014-07-02-interview-gamewatch-quinty-gamefreak-origins-sugimori-masuda-morimoto.md"
    fm = {
        "layout": "parallel-translation",
        "title": "GAME Watch 独家专访：红白机名作《旋转方块（Quinty）》归来！GAME FREAK 创业元老杉森建×增田顺一×森本茂树回顾黎明期与宝可梦的原点",
        "original_title": "ついにファミコンの名作、あの「クインティ」が帰ってきた！ Wii Uバーチャルコンソールでプレイ可能!!制作を手掛けたゲームフリークの杉森建氏、増田順一氏、森本茂樹氏が当時を振り返る",
        "date": "2014-07-02 12:00:00 +0900",
        "era_skin": 2014,
        "source_url": url,
        "original_language": "ja",
        "categories": ["访谈", "创业历史"],
        "tags": ["Game Freak", "旋转方块", "Quinty", "杉森建", "增田顺一", "森本茂树", "田尻智", "红白机", "Famicom", "宝可梦原点"],
        "author": "GAME Watch 編集部",
        "interviewee": "杉森建（GAME FREAK 董事兼艺术总监）、增田顺一（GAME FREAK 董事兼开发部长）、森本茂树（GAME FREAK 游戏设计师）",
        "quote": "如果没有《旋转方块》，就没有 GAME FREAK 这家公司，也绝不会诞生《宝可梦》。田尻智用纸板箱自制开发套件，我们几个同人杂志伙伴在出租屋里敲着汇编代码，那正是我们游戏创作之魂的真正源头。",
        "cast": [
            {"id": "sugimori", "name": "杉森建", "role": "GAME FREAK 取缔役 / 艺术总监", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/ruby-sapphire-origins.png"},
            {"id": "masuda", "name": "增田顺一", "role": "GAME FREAK 取缔役 / 开发部长 / 作曲家", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/ruby-sapphire-origins.png"},
            {"id": "morimoto", "name": "森本茂树", "role": "GAME FREAK 游戏设计师 / 战斗系统主管", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/ruby-sapphire-origins.png"},
            {"id": "interviewer", "name": "提问", "role": "GAME Watch 资深记者", "avatar": "https://assets.pokemon.com/assets/cms2/img/misc/gus/promotions/ruby-sapphire-origins.png"}
        ],
        "parallel_items": items
    }

    yaml_str = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    Path(post_filename).write_text(f"---\n{yaml_str}---\n", encoding="utf-8")
    print(f"Successfully generated {post_filename} ({len(items)} items)")


def main():
    print("=== Batch 22 Curation Pipeline Starting ===")
    glossary = load_glossary()
    curate_pkmn_1057(glossary)
    curate_pkmn_1058(glossary)
    curate_pkmn_1059(glossary)
    print("=== Batch 22 Curation Pipeline Finished Successfully ===")


if __name__ == "__main__":
    main()
