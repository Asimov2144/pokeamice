#!/usr/bin/env python3
"""
Curate Batch 21:
1. PKMN-1054: Dengeki Online 《心金·魂银》总监森本茂树独家专访 (2009-09-18)
2. PKMN-1055: Famitsu.com 《名侦探皮卡丘》主创专访（阵内弘之×宫下尚生）(2018-03-30)
3. PKMN-1056: Famitsu.com 《New 宝可梦随乐拍》石原恒和社长×须崎春树总监访谈 (2021-04-30)
And fix metadata link for PKMN-0014 (2083.jp Sound Team inheritance).
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

CACHE_DIR = Path("tools/cache_batch_21")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


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
        for term in [item.get("source_term", ""), item.get("source_term_ja", ""), item.get("source_term_en", "")]:
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
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
        raw = resp.read()
    try:
        html = raw.decode(encoding)
    except:
        html = raw.decode("utf-8", "replace")
    cache_path.write_text(html, encoding="utf-8")
    return html


def download_image(url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = resp.read()
        dest_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"  [Image Download Failed] {url} -> {e}")
        return False


def call_deepseek(messages: list[dict], max_tokens: int = 4096, temperature: float = 0.3) -> str:
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY is not set")
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  [DeepSeek API Attempt {attempt+1}/4 failed]: {e}")
            if attempt < 3:
                time.sleep(2 ** (attempt + 1))
            else:
                raise


def translate_items_batch(
    items: list[dict], glossary: list[dict], context_desc: str, cache_prefix: str
) -> list[dict]:
    cache_json = CACHE_DIR / f"{cache_prefix}_translations.json"
    cached_map = {}
    if cache_json.exists():
        try:
            cached_map = json.loads(cache_json.read_text(encoding="utf-8"))
            print(f"  Loaded {len(cached_map)} cached translations from {cache_json.name}")
        except Exception as e:
            print(f"  Failed loading cache: {e}")

    for it in items:
        orig = it.get("original", "").strip()
        if orig in cached_map and not it.get("translation"):
            it["translation"] = cached_map[orig]

    to_trans = []
    for i, it in enumerate(items):
        if it.get("type") in ["image"]:
            continue
        orig = it.get("original", "").strip()
        if not orig:
            continue
        if not it.get("translation"):
            to_trans.append((i, orig))

    if not to_trans:
        print(f"  All {len(items)} items already translated!")
        return items

    print(f"  Translating {len(to_trans)} items via DeepSeek API...")
    batch_size = 10
    for b_idx in range(0, len(to_trans), batch_size):
        chunk = to_trans[b_idx : b_idx + batch_size]
        chunk_text = "\n".join([f"[{k}] {orig}" for k, orig in chunk])
        matched = match_glossary_terms(chunk_text, glossary)
        glossary_rules = "\n".join([f"- {s} -> {t}" for s, t in matched])

        prompt = f"""你是一名精通任天堂与《宝可梦》系列历史的顶级专业游戏本地化翻译专家。
请将以下日语采访文本翻译为自然、地道、信达雅的简体中文。

【背景信息】
{context_desc}

【术语强制对照规范】
- 统一使用中国大陆官方宝可梦译名：宝可梦、宝可梦球、关都地区、城都地区、丰缘地区、神奥地区、合众地区、卡洛斯地区、阿罗拉地区、伽勒尔地区、洗翠地区、帕底亚地区。
- 特性、性格、努力值、个体值、招式等专有名词严格规范。
- 严禁出现“宠物小精灵”、“口袋妖怪”、“神奇宝贝”等非官方译名。
- 请保留人物说话口吻（谦逊、热情、严谨），敬语与称呼自然转换。

【本段匹配词表】
{glossary_rules}

【待翻译条目（JSON格式输入）】
{json.dumps([{"id": k, "original": orig} for k, orig in chunk], ensure_ascii=False, indent=2)}

【输出格式】
必须严格输出合法的 JSON 格式，如下所示：
{{
  "translations": [
    {{"id": 0, "translation": "..."}},
    ...
  ]
}}
"""
        messages = [
            {"role": "system", "content": "You are a professional Japanese to Simplified Chinese translator specializing in Pokémon video game developer interviews. Always reply in valid JSON format."},
            {"role": "user", "content": prompt}
        ]
        try:
            resp_str = call_deepseek(messages)
            res_json = json.loads(resp_str)
            trans_list = res_json.get("translations", [])
            for tr in trans_list:
                item_id = tr.get("id")
                trans_text = tr.get("translation", "").strip()
                if item_id is not None and trans_text:
                    items[item_id]["translation"] = trans_text
                    cached_map[items[item_id]["original"].strip()] = trans_text
            cache_json.write_text(json.dumps(cached_map, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"    Translated batch {b_idx//batch_size + 1}/{(len(to_trans)+batch_size-1)//batch_size} ({len(chunk)} items)")
        except Exception as e:
            print(f"    Error translating batch {b_idx//batch_size + 1}: {e}")
            raise

    return items


# ==========================================
# 1. PARSE DENGEKI HGSS MORIMOTO (PKMN-1054)
# ==========================================
def curate_dengeki_hgss(glossary: list[dict]):
    print("\n" + "="*50)
    print("Curating PKMN-1054: Dengeki Online Morimoto HGSS")
    print("="*50)
    url = "https://dengekionline.com/elem/000/000/193/193021/"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    img_dir = Path("assets/img/interviews/2009-09-18-interview-dengeki-hgss-shigeki-morimoto")
    img_dir.mkdir(parents=True, exist_ok=True)

    items = []
    # Lead-in
    lead_paragraphs = [
        "9月12日に発売されたDS用ソフト『ポケットモンスター ハートゴールド・ソウルシルバー（以下、ハートゴールド・ソウルシルバー）』。そのディレクターであるゲームフリークの森本茂樹さんにインタビューを行った。",
        "『ハートゴールド・ソウルシルバー』は、1999年に発売されたゲームボーイ用ソフト『ポケットモンスター 金・銀（以下、金・銀）』のリメイク作。従来のシリーズに搭載されたさまざまな機能なども踏襲し、ポケモンの連れ歩きや、ポケモンと一緒に遊べる“ポケスロン”、サファリゾーンのカスタマイズなど、新要素もたくさん追加されている。",
        "本作の発売にあたり、ディレクターを務める森本さんにインタビューを行った。開発の経緯などはもちろん、同梱される周辺機器“ポケウォーカー”や、公式全国大会“ワールドチャンピオンシップス”などについてもお話を伺ったので、ぜひご覧いただきたい。なお本文の各タイトルの表記は、以下のもので統一する。",
        "注：記事中の表記・『ポケットモンスター 青』……『青』・『ポケットモンスター ピカチュウ』……『ピカチュウ』バージョン・『ポケットモンスター 金・銀・クリスタルバージョン』……『金・銀・クリスタル』・『ポケットモンスター ファイアレッド・リーフグリーン』……『ファイアレッド・リーフグリーン』・『ポケットモンスター ルビー・サファイア』……『ルビー・サファイア』・『ポケットモンスター ダイヤモンド・パール・プラチナ』……『ダイヤモンド・パール・プラチナ』・『ポケットモンスター ハートゴールド・ソウルシルバー』……『ハートゴールド・ソウルシルバー』"
    ]
    for p in lead_paragraphs:
        items.append({"original": p})

    # Dengeki images to download and include
    dengeki_imgs = [
        ("https://dengekionline.com/elem/000/000/193/193057/c20090908_poke3_01_cs1w1_143x.jpg", "hgss_pack_gold.jpg", "『心金』游戏包装盒与宝可梦计步器“宝可步数计”"),
        ("https://dengekionline.com/elem/000/000/193/193058/c20090908_poke3_02_cs1w1_143x.jpg", "hgss_pack_silver.jpg", "『魂银』游戏包装盒与宝可梦计步器“宝可步数计”"),
        ("https://dengekionline.com/elem/000/000/193/193022/c20090908_poke1_01_cs1w1_143x.jpg", "hgss_morimoto_01.jpg", "GAME FREAK 开发总监森本茂树接受电击独家专访"),
        ("https://dengekionline.com/elem/000/000/193/193023/c20090908_poke1_02_cs1w1_143x.jpg", "hgss_morimoto_02.jpg", "森本茂树手持 DS 与宝可步数计畅谈设计哲学"),
        ("https://dengekionline.com/elem/000/000/193/193024/c20090908_poke1_03_cs1w1_143x.jpg", "hgss_morimoto_03.jpg", "森本茂树展示全 493 只宝可梦跟随系统与触控界面"),
        ("https://dengekionline.com/elem/000/000/193/193025/c20090908_poke1_04_cs1w1_143x.jpg", "hgss_morimoto_04.jpg", "森本茂树：将10年间宝可梦系列的优点融于一炉"),
    ]
    for img_url, fn, caption in dengeki_imgs:
        download_image(img_url, img_dir / fn)

    # Insert package shot
    items.append({
        "type": "image",
        "image": f"/assets/img/interviews/2009-09-18-interview-dengeki-hgss-shigeki-morimoto/{dengeki_imgs[0][1]}",
        "alt": dengeki_imgs[0][2],
        "caption": dengeki_imgs[0][2],
    })

    # Main interview content from HTML
    # Parse all paragraphs in the article
    for p in soup.find_all(["h2", "h3", "p"]):
        txt = p.get_text(strip=True)
        if not txt:
            continue
        if any(skip in txt for skip in ["9月12日に発売されたDS用ソフト", "『ハートゴールド・ソウルシルバー』は、1999年に発売", "本作の発売にあたり", "注：記事中の表記", "電撃オンライン", "最新記事", "Amazon", "関連サイト"]):
            continue
        if txt.startswith("■"):
            items.append({"type": "heading", "level": 2, "original": txt[1:].strip()})
        elif txt.startswith("――"):
            items.append({"speaker": "电击编辑部", "speaker_orig": "――", "original": txt[2:].strip()})
        elif txt.startswith("森本さん："):
            items.append({"speaker": "森本茂树", "speaker_orig": "森本さん", "original": txt[5:].strip()})
        elif txt.startswith("※"):
            items.append({"original": txt})
        else:
            items.append({"original": txt})

    # Add middle images
    # Insert morimoto photo at reasonable intervals
    if len(items) > 12:
        items.insert(8, {
            "type": "image",
            "image": f"/assets/img/interviews/2009-09-18-interview-dengeki-hgss-shigeki-morimoto/{dengeki_imgs[2][1]}",
            "alt": dengeki_imgs[2][2],
            "caption": dengeki_imgs[2][2],
        })
    if len(items) > 20:
        items.insert(18, {
            "type": "image",
            "image": f"/assets/img/interviews/2009-09-18-interview-dengeki-hgss-shigeki-morimoto/{dengeki_imgs[4][1]}",
            "alt": dengeki_imgs[4][2],
            "caption": dengeki_imgs[4][2],
        })

    # Translate
    context = "2009年《宝可梦 心金·魂银》发售之际，电击在线专访GAME FREAK总监森本茂树。探讨从GB金银到DS的十周年进化、全493只宝可梦跟随、宝可全能竞技赛（Pokeathlon）、宝可步数计（Pokewalker）、关都城都两地区平衡、以及当年在初代红绿中偷塞梦幻的秘辛。"
    items = translate_items_batch(items, glossary, context, "hgss_morimoto")

    post_content = f"""---
layout: parallel-translation
title: 电击独家专访《心金·魂银》总监森本茂树：集大成之作与梦幻诞生秘辛
title_ja: 電撃オンライン：『ポケットモンスター』最新作についてディレクターの森本茂樹さんを直撃！
date: 2009-09-18 10:00:00 +0900
era: '2009'
era_skin: '2010'
publication: 電撃オンライン
original_link: https://dengekionline.com/elem/000/000/193/193021/
source:
  name: 電撃オンライン
  url: https://dengekionline.com/elem/000/000/193/193021/
source_url: https://dengekionline.com/elem/000/000/193/193021/
author: 電撃オンライン編集部
interviewee: 森本茂樹（GAME FREAK 开发总监）
categories:
- developer-interviews
- official-archives
parallel_items:
"""
    # Dump items
    post_yaml = yaml.dump(items, allow_unicode=True, sort_keys=False)
    full_md = post_content + post_yaml + "\n---\n"
    target_file = Path("_posts/2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md")
    target_file.write_text(full_md, encoding="utf-8")
    print(f"Created {target_file} ({len(items)} items)")


# =========================================================
# 2. PARSE FAMITSU DETECTIVE PIKACHU JINNAI & MIYASHITA (PKMN-1055)
# =========================================================
def curate_famitsu_detective_pikachu(glossary: list[dict]):
    print("\n" + "="*50)
    print("Curating PKMN-1055: Famitsu Detective Pikachu Jinnai & Miyashita")
    print("="*50)
    url = "https://www.famitsu.com/news/201803/30154405.html"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    img_dir = Path("assets/img/interviews/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita")
    img_dir.mkdir(parents=True, exist_ok=True)

    # Download images
    images_to_download = [
        ("https://www.famitsu.com/images/000/154/405/l_5ab9389033668.jpg", "dp_main_pika.jpg", "《名侦探皮卡丘》：手持放大镜、热爱黑咖啡的自称名侦探皮卡丘"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938904dc44.jpg", "dp_coffee_scene.jpg", "在海德咖啡馆与皮卡丘畅饮咖啡的经典侦探场景"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938901e28e.jpg", "dp_creatures_duo.jpg", "Creatures 制片人阵内弘之（右）与总监宫下尚生（左）"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab9388fefa1e.jpg", "dp_ryme_city.jpg", "人类与宝可梦和谐共处的生态大都会——莱姆市"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938902675d.jpg", "dp_facial_capture.jpg", "由老牌声优大川透献声并进行面部表情动作捕捉的皮卡丘"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938902f015.jpg", "dp_tim_pikachu.jpg", "主角提姆与大叔皮卡丘联手破获系列迷案"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938901176d.jpg", "dp_jinnai_talking.jpg", "阵内弘之畅谈大叔皮卡丘的诞生契机与世界观塑造"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab938902a9c5.jpg", "dp_case_investigation.jpg", "在莱姆市大街小巷向宝可梦与人类取证侦查"),
        ("https://www.famitsu.com/images/000/154/405/l_5ab9389037cb5.jpg", "dp_amiibo_giant.jpg", "特别推出的超大尺寸名侦探皮卡丘 amiibo"),
    ]
    for img_url, fn, caption in images_to_download:
        download_image(img_url, img_dir / fn)

    items = []
    # Main hero image
    items.append({
        "type": "image",
        "image": f"/assets/img/interviews/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita/{images_to_download[0][1]}",
        "alt": images_to_download[0][2],
        "caption": images_to_download[0][2],
    })

    # Lead paragraphs
    items.append({
        "original": "2018年3月23日、ニンテンドー3DSソフト『名探偵ピカチュウ』が発売された。“シネマティックアドベンチャー”として発売された本作は、失踪した父親を捜す主人公ティムが、人間の言葉を話す“自称名探偵”のピカチュウとともにさまざまな事件に立ち向かっていくというゲームだ。"
    })
    items.append({
        "original": "最大の特徴は、なんといってもピカチュウの声。なんと、テレビアニメでおなじみの大谷育江さんによるかわいい声ではなく、大川透さんによるダンディーな“おっさん”の声で話すのだ。さらに、コーヒーが好きで、少しふてぶてしかったりと、どこまでも“おっさん”のような自称“名探偵”のピカチュウ。このピカチュウ誕生の裏には、どんな意図があるのか？\u3000多くのポケモンファンが気になっているであろう疑問を本作のプロデューサー陣内弘之氏とディレクターの宮下尚生氏（ともにクリーチャーズ）にぶつけてみた。"
    })
    items.append({
        "type": "image",
        "image": f"/assets/img/interviews/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita/{images_to_download[2][1]}",
        "alt": images_to_download[2][2],
        "caption": images_to_download[2][2],
    })
    items.append({
        "original": "陣内弘之氏（じんない ひろゆき／写真右）\n株式会社クリーチャーズ 取締役。『名探偵ピカチュウ』プロデューサー。"
    })
    items.append({
        "original": "宮下尚生氏（みやした なおき／写真左）\n株式会社クリーチャーズ クリエイティブディレクター。『名探偵ピカチュウ』ディレクター。"
    })

    # Parse dialogue body
    for p in soup.find_all(["h2", "h3", "p"]):
        txt = p.get_text(strip=True)
        if not txt:
            continue
        if any(stop in txt for stop in ["集計期間", "発売日：", "※記載されている価格", "本記事はアフィリエイトプログラム", "週刊ファミ通"]):
            break
        if any(skip in txt for skip in [
            "2018年3月23日、ニンテンドー3DSソフト『名探偵ピカチュウ』が発売された",
            "最大の特徴は、なんといってもピカチュウの声",
            "株式会社クリーチャーズ 取締役",
            "株式会社クリーチャーズ クリエイティブディレクター",
            "ファミ通.com", "株式会社KADOKAWA", "Twitterでシェア", "ページの先頭へ"
        ]):
            continue
        if txt.startswith("陣内弘之氏") or txt.startswith("宮下尚生氏"):
            continue

        if txt.startswith("■"):
            items.append({"type": "heading", "level": 2, "original": txt[1:].strip()})
        elif p.name in ["h2", "h3"]:
            items.append({"type": "heading", "level": int(p.name[1]), "original": txt})
        elif txt.startswith("――"):
            items.append({"speaker": "Fami通编辑部", "speaker_orig": "――", "original": txt[2:].strip()})
        elif txt.startswith("陣内　") or txt.startswith("陣内 "):
            items.append({"speaker": "阵内弘之", "speaker_orig": "陣内", "original": txt[3:].strip()})
        elif txt.startswith("陣内"):
            items.append({"speaker": "阵内弘之", "speaker_orig": "陣内", "original": txt[2:].strip()})
        elif txt.startswith("宮下　") or txt.startswith("宮下 "):
            items.append({"speaker": "宫下尚生", "speaker_orig": "宮下", "original": txt[3:].strip()})
        elif txt.startswith("宮下"):
            items.append({"speaker": "宫下尚生", "speaker_orig": "宮下", "original": txt[2:].strip()})
        else:
            items.append({"original": txt})

    # Insert contextual screenshots in between sections
    # Find heading positions
    insert_positions = []
    for idx, it in enumerate(items):
        if it.get("type") == "heading":
            insert_positions.append(idx)

    # Sprinkle images
    img_inserts = [
        (images_to_download[1], 1), # coffee
        (images_to_download[3], 2), # ryme city
        (images_to_download[4], 3), # facial mocap
        (images_to_download[5], 4), # tim & pikachu
        (images_to_download[6], 5), # jinnai talking
        (images_to_download[7], 6), # case investigation
        (images_to_download[8], 7), # giant amiibo
    ]
    offset = 0
    for img_info, pos_idx in img_inserts:
        if pos_idx < len(insert_positions):
            target_idx = insert_positions[pos_idx] + offset
            items.insert(target_idx, {
                "type": "image",
                "image": f"/assets/img/interviews/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita/{img_info[1]}",
                "alt": img_info[2],
                "caption": img_info[2],
            })
            offset += 1

    # Translate
    context = "2018年3月《名侦探皮卡丘》发售之际，法米通专访Creatures制片人阵内弘之与导演宫下尚生。探讨大叔皮卡丘的诞生、声优大川透的大叔低沉嗓音、皮卡丘爱喝黑咖啡与嫌弃甜食的设定、人类与宝可梦共生的莱姆市生态、以及电影化企划展开。"
    items = translate_items_batch(items, glossary, context, "detective_pikachu")

    post_content = f"""---
layout: parallel-translation
title: Fami通专访《名侦探皮卡丘》主创：热爱咖啡的大叔皮卡丘与人类宝可梦共生莱姆市
title_ja: ファミ通：コーヒー好きの“ピカチュウ（CV大川透）”はこうして生まれた――『名探偵ピカチュウ』開発陣に直撃インタビュー！
date: 2018-03-30 10:00:00 +0900
era: '2018'
era_skin: '2019'
publication: ファミ通.com
original_link: https://www.famitsu.com/news/201803/30154405.html
source:
  name: ファミ通.com
  url: https://www.famitsu.com/news/201803/30154405.html
source_url: https://www.famitsu.com/news/201803/30154405.html
author: ファミ通.com編集部
interviewee: 陣内弘之（Creatures 取缔役兼制片人）、宮下尚生（Creatures 创意总监兼开发总监）
categories:
- developer-interviews
- official-archives
parallel_items:
"""
    post_yaml = yaml.dump(items, allow_unicode=True, sort_keys=False)
    full_md = post_content + post_yaml + "\n---\n"
    target_file = Path("_posts/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md")
    target_file.write_text(full_md, encoding="utf-8")
    print(f"Created {target_file} ({len(items)} items)")


# =========================================================
# 3. PARSE FAMITSU NEW POKEMON SNAP ISHIHARA & SUZAKI (PKMN-1056)
# =========================================================
def curate_famitsu_new_pokemon_snap(glossary: list[dict]):
    print("\n" + "="*50)
    print("Curating PKMN-1056: Famitsu New Pokemon Snap Ishihara & Suzaki")
    print("="*50)
    url = "https://www.famitsu.com/news/202104/30218824.html"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    img_dir = Path("assets/img/interviews/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki")
    img_dir.mkdir(parents=True, exist_ok=True)

    # Article images from Famitsu CDN
    snap_imgs = [
        ("https://www.famitsu.com/images/000/218/824/y_6082d9133eb13.jpg", "snap_hero_boxart.jpg", "《New 宝可梦随乐拍》探索未知蓝蒂尔群岛的摄影冒险"),
        ("https://www.famitsu.com/images/000/218/824/y_6082d9134ea26.jpg", "snap_ishihara_suzaki.jpg", "宝可梦公司社长石原恒和（左）与万代南梦宫工作室总监须崎春树（右）"),
        ("https://www.famitsu.com/images/000/218/824/y_6082d91347015.jpg", "snap_neoone_vehicle.jpg", "自然调查载具“新壹号”穿行于茂密森林与深海"),
        ("https://www.famitsu.com/images/000/218/824/y_6082d9134316f.jpg", "snap_lumina_phenomenon.jpg", "蓝蒂尔群岛独特的自然生态与“发光现象”"),
    ]
    for img_url, fn, caption in snap_imgs:
        download_image(img_url, img_dir / fn)

    items = []
    # Hero image
    items.append({
        "type": "image",
        "image": f"/assets/img/interviews/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki/{snap_imgs[0][1]}",
        "alt": snap_imgs[0][2],
        "caption": snap_imgs[0][2],
    })

    # Lead paragraphs
    items.append({
        "original": "2021年4月30日に発売されたNintendo Switchソフト『New ポケモンスナップ』。本作は、1999年3月21日に発売されたニンテンドウ64ソフト『ポケモンスナップ』のゲーム性をベースにした完全新作カメラアクションゲームだ。"
    })
    items.append({
        "original": "1999年というと、カメラ付き携帯電話がまだ普及していない時代。それに比べて、スマートフォンで簡単に高画質な写真が撮れるようになった現代では、誰にとっても“写真を撮ること”が身近なものとなった。そんな時代の変化に『New ポケモンスナップ』はどのように適応しているのか。写真を撮ることがより手軽になった現代において、“写真を撮ること”をテーマにしたゲームを作る難しさや、22年ぶりに新作を作るに至った経緯などを、本作のプロデューサーを務めるポケモン代表取締役社長の石原恒和氏と、開発を担当したバンダイナムコスタジオの須崎春樹ディレクターに伺った。"
    })
    items.append({
        "type": "image",
        "image": f"/assets/img/interviews/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki/{snap_imgs[1][1]}",
        "alt": snap_imgs[1][2],
        "caption": snap_imgs[1][2],
    })
    items.append({
        "original": "石原 恒和（いしはら つねかず／写真左）\n株式会社ポケモン代表取締役社長・最高経営責任者。『ポケットモンスター 赤・緑』を始め、ポケモンのビデオゲーム全作品でプロデューサーを務める。"
    })
    items.append({
        "original": "須崎 春樹（すざき はるき／写真右）\nバンダイナムコスタジオ所属。ポケモンと鉄拳がコラボした『ポッ拳 POKKÉN TOURNAMENT』のディレクターを担当し、本作『New ポケモンスナップ』でもディレクターを務める。"
    })

    # Parse dialogues
    for p in soup.find_all(["h2", "h3", "p"]):
        txt = p.get_text(strip=True)
        if not txt:
            continue
        if any(stop in txt for stop in ["集計期間", "発売日：", "※記載されている価格", "本記事はアフィリエイトプログラム", "週刊ファミ通"]):
            break
        if any(skip in txt for skip in [
            "2021年4月30日に発売されたNintendo Switchソフト",
            "1999年というと、カメラ付き携帯電話がまだ普及していない時代",
            "株式会社ポケモン代表取締役社長",
            "バンダイナムコスタジオ所属",
            "ファミ通.com", "株式会社KADOKAWA", "Twitterでシェア", "ページの先頭へ",
            "週刊ファミ通", "Amazon", "Book walker"
        ]):
            continue
        if txt.startswith("石原 恒和") or txt.startswith("須崎 春樹") or txt.startswith("石原恒和氏") or txt.startswith("須崎春樹氏"):
            continue

        if txt.startswith("■"):
            items.append({"type": "heading", "level": 2, "original": txt[1:].strip()})
        elif p.name in ["h2", "h3"]:
            items.append({"type": "heading", "level": int(p.name[1]), "original": txt})
        elif txt.startswith("――"):
            items.append({"speaker": "Fami通编辑部", "speaker_orig": "――", "original": txt[2:].strip()})
        elif txt.startswith("石原　") or txt.startswith("石原 "):
            items.append({"speaker": "石原恒和", "speaker_orig": "石原", "original": txt[3:].strip()})
        elif txt.startswith("石原"):
            items.append({"speaker": "石原恒和", "speaker_orig": "石原", "original": txt[2:].strip()})
        elif txt.startswith("須崎　") or txt.startswith("須崎 "):
            items.append({"speaker": "须崎春树", "speaker_orig": "須崎", "original": txt[3:].strip()})
        elif txt.startswith("須崎"):
            items.append({"speaker": "须崎春树", "speaker_orig": "須崎", "original": txt[2:].strip()})
        else:
            items.append({"original": txt})

    # Insert remaining images
    if len(items) > 30:
        items.insert(25, {
            "type": "image",
            "image": f"/assets/img/interviews/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki/{snap_imgs[2][1]}",
            "alt": snap_imgs[2][2],
            "caption": snap_imgs[2][2],
        })
    if len(items) > 70:
        items.insert(65, {
            "type": "image",
            "image": f"/assets/img/interviews/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki/{snap_imgs[3][1]}",
            "alt": snap_imgs[3][2],
            "caption": snap_imgs[3][2],
        })

    # Translate
    context = "2021年4月《New 宝可梦随乐拍》在Nintendo Switch发售之际，法米通专访宝可梦社长石原恒和与万代南梦宫工作室总监须崎春树。深度剖析从1999年N64胶卷冲印到2021年智能手机与社交媒体普及这22年间的时代剧变、照相机摄影玩法的本质演化、宝可梦自然生态行为设计、以及光影发光机制。"
    items = translate_items_batch(items, glossary, context, "new_pokemon_snap")

    post_content = f"""---
layout: parallel-translation
title: Fami通专访《New 宝可梦随乐拍》：石原恒和社长×须崎春树总监畅谈相机生态与22年跨越
title_ja: ファミ通：石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話。写真を撮ることがより手軽になった2021年、ゲームデザインは前作からどう進化したのか？
date: 2021-04-30 10:00:00 +0900
era: '2021'
era_skin: '2019'
publication: ファミ通.com
original_link: https://www.famitsu.com/news/202104/30218824.html
source:
  name: ファミ通.com
  url: https://www.famitsu.com/news/202104/30218824.html
source_url: https://www.famitsu.com/news/202104/30218824.html
author: ファミ通.com編集部
interviewee: 石原恒和（株式会社宝可梦代表取缔役社长兼CEO）、須崎春樹（万代南梦宫工作室开发总监）
categories:
- developer-interviews
- official-archives
parallel_items:
"""
    post_yaml = yaml.dump(items, allow_unicode=True, sort_keys=False)
    full_md = post_content + post_yaml + "\n---\n"
    target_file = Path("_posts/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki.md")
    target_file.write_text(full_md, encoding="utf-8")
    print(f"Created {target_file} ({len(items)} items)")


# =========================================================
# 4. SYNC DATA CATALOGS
# =========================================================
def sync_catalogs():
    print("\n" + "="*50)
    print("Syncing Catalogs: pokemon_1000_interviews.json & curation JSON")
    print("="*50)

    p_1000 = Path("data/pokemon_1000_interviews.json")
    interviews = json.loads(p_1000.read_text(encoding="utf-8"))

    # Fix PKMN-0014
    for it in interviews:
        if it.get("id") == "PKMN-0014":
            it["translation_file"] = "_posts/2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md"
            it["imported_post_slug"] = "2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras"
            it["imported_post_path"] = "_posts/2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md"
            it["post_file"] = "_posts/2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md"
            it["status"] = "imported"
            print("Fixed PKMN-0014 post file link!")

    existing_ids = {it.get("id") for it in interviews}

    # Add PKMN-1054, PKMN-1055, PKMN-1056 if not present
    new_entries = [
        {
            "id": "PKMN-1054",
            "title": "电击独家专访《心金·魂银》总监森本茂树：集大成之作与梦幻诞生秘辛",
            "original_title": "『ポケットモンスター』最新作についてディレクターの森本茂樹さんを直撃！",
            "url": "https://dengekionline.com/elem/000/000/193/193021/",
            "date": "2009-09-18",
            "people": ["森本茂树"],
            "generation": "Gen 4",
            "language": "JA",
            "outlet": "電撃オンライン",
            "type": "Web Interview",
            "tags": ["心金·魂银", "森本茂树", "GAME FREAK", "第四世代", "HGSS", "宝可步数计", "梦幻", "JA"],
            "summary": "电击在线独家专访GAME FREAK总监森本茂树，详解《心金·魂银》作为集系列十载大成之作的开发哲学、全493只宝可梦跟随系统、触控UI革新与梦幻诞生真相。",
            "status": "imported",
            "imported_post_slug": "2009-09-18-interview-dengeki-hgss-shigeki-morimoto",
            "imported_post_path": "_posts/2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md",
            "post_file": "_posts/2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md",
        },
        {
            "id": "PKMN-1055",
            "title": "Fami通专访《名侦探皮卡丘》主创：热爱咖啡的大叔皮卡丘与人类宝可梦共生莱姆市",
            "original_title": "コーヒー好きの“ピカチュウ（CV大川透）”はこうして生まれた――『名探偵ピカチュウ』開発陣に直撃インタビュー！",
            "url": "https://www.famitsu.com/news/201803/30154405.html",
            "date": "2018-03-30",
            "people": ["阵内弘之", "宫下尚生"],
            "generation": "Gen 7",
            "language": "JA",
            "outlet": "ファミ通.com",
            "type": "Web Interview",
            "tags": ["名侦探皮卡丘", "阵内弘之", "宫下尚生", "Creatures", "大川透", "第七世代", "JA"],
            "summary": "法米通深度专访Creatures制片人阵内弘之与总监宫下尚生，披露大叔皮卡丘的大叔音、爱喝咖啡与讨厌甜食设定、莱姆市共生生态与面部表情动捕幕后。",
            "status": "imported",
            "imported_post_slug": "2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita",
            "imported_post_path": "_posts/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md",
            "post_file": "_posts/2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md",
        },
        {
            "id": "PKMN-1056",
            "title": "Fami通专访《New 宝可梦随乐拍》：石原恒和社长×须崎春树总监畅谈相机生态与22年跨越",
            "original_title": "石原社長＆須崎Dに聞く『New ポケモンスナップ』開発秘話。写真を撮ることがより手軽になった2021年、ゲームデザインは前作からどう進化したのか？",
            "url": "https://www.famitsu.com/news/202104/30218824.html",
            "date": "2021-04-30",
            "people": ["石原恒和", "须崎春树"],
            "generation": "Gen 8",
            "language": "JA",
            "outlet": "ファミ通.com",
            "type": "Web Interview",
            "tags": ["New 宝可梦随乐拍", "石原恒和", "须崎春树", "株式会社宝可梦", "万代南梦宫", "第八世代", "JA"],
            "summary": "法米通专访宝可梦社长石原恒和与万代南梦宫总监须崎春树，畅谈时隔22年从N64到Switch摄影文化变迁、自然生态动作设计与发光现象调查。",
            "status": "imported",
            "imported_post_slug": "2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki",
            "imported_post_path": "_posts/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki.md",
            "post_file": "_posts/2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki.md",
        }
    ]

    for ne in new_entries:
        if ne["id"] not in existing_ids:
            interviews.append(ne)
            existing_ids.add(ne["id"])
            print(f"Added {ne['id']}: {ne['title']}")
        else:
            for idx, it in enumerate(interviews):
                if it.get("id") == ne["id"]:
                    interviews[idx] = ne
                    print(f"Updated existing {ne['id']}")

    p_1000.write_text(json.dumps(interviews, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {p_1000} ({len(interviews)} entries)")

    # Update curation JSON
    p_cur = Path("data/unimported_japanese_interviews_curation.json")
    if p_cur.exists():
        cur_list = json.loads(p_cur.read_text(encoding="utf-8"))
        for it in cur_list:
            u = it.get("url", "")
            if "193021" in u:
                it["status"] = "imported"
                it["imported_id"] = "PKMN-1054"
            elif "154405" in u:
                it["status"] = "imported"
                it["imported_id"] = "PKMN-1055"
            elif "218824" in u:
                it["status"] = "imported"
                it["imported_id"] = "PKMN-1056"
            elif "201410gamefreak" in u:
                it["status"] = "imported"
                it["imported_id"] = "PKMN-0014"
        p_cur.write_text(json.dumps(cur_list, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved {p_cur}")


def main():
    glossary = load_glossary()
    curate_dengeki_hgss(glossary)
    curate_famitsu_detective_pikachu(glossary)
    curate_famitsu_new_pokemon_snap(glossary)
    sync_catalogs()
    print("\n" + "="*50)
    print("Batch 21 curation completed successfully!")
    print("="*50)


if __name__ == "__main__":
    main()
