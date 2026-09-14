"""Curate Batch 17:
1. PKMN-1005: GAME FREAK 官方系统程序员座谈会 (crosstalk-system-programmer)
2. PKMN-1007: GAME FREAK 官方剧本与世界观设定座谈会 (crosstalk-scenario)
3. PKMN-1008: GAME FREAK 官方应届新人座谈会 (crosstalk-new-graduate)
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path("p:/WEBSITE/pokeamice-main (1)/pokeamice-main")
POSTS_DIR = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
CATALOG_PATH = ROOT / "data" / "pokemon_1000_interviews.json"
GLOSSARY_PATH = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")
CACHE_DIR = ROOT / "tools" / "cache_batch_17"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
        except Exception as e:
            print(f"  [DeepSeek API Attempt {attempt+1}/4 failed]: {e}")
            if attempt < 3:
                time.sleep(2 ** (attempt + 1))
            else:
                raise


def translate_items_batch(items: list[dict], glossary: list[dict], context_desc: str, cache_prefix: str) -> list[dict]:
    """Translate items preserving structure, using glossary enforcement and local disk caching."""
    cache_json = CACHE_DIR / f"{cache_prefix}_translations.json"
    cached_map = {}
    if cache_json.exists():
        try:
            cached_map = json.loads(cache_json.read_text(encoding="utf-8"))
            print(f"  Loaded {len(cached_map)} cached translations from {cache_json.name}")
        except Exception as e:
            print(f"  Failed loading translation cache: {e}")

    # Fill in cached translations
    for it in items:
        orig = it.get("original", "").strip()
        if orig in cached_map and not it.get("translation"):
            it["translation"] = cached_map[orig]

    to_trans = []
    for i, it in enumerate(items):
        if it.get("translation"):
            continue
        if it.get("type") in ("image", "hr"):
            continue
        orig = it.get("original", "").strip()
        if not orig:
            continue
        to_trans.append((i, orig, it.get("speaker", "")))

    if not to_trans:
        print("  All items already translated.")
        return items

    combined_text = " ".join([t[1] for t in to_trans])
    terms = find_glossary_matches(combined_text, glossary)
    term_constraints = "\n".join([f"- {k} => {v}" for k, v in terms]) if terms else "无特殊官方术语锁定。"

    BATCH_SIZE = 10
    for b_idx in range(0, len(to_trans), BATCH_SIZE):
        chunk = to_trans[b_idx:b_idx + BATCH_SIZE]
        payload_items = [{"id": idx, "speaker": spk, "text": text} for idx, text, spk in chunk]

        prompt = f"""你是宝可梦官方档案馆的资深中日翻译专家。请将以下来自 GAME FREAK 官方招聘开发者对谈的日文内容翻译为流畅、自然、符合中国大陆宝可梦官方简体中文语境的译文。
背景信息：
{context_desc}

【官方术语硬性约束（必须严格遵守）】：
{term_constraints}

【翻译要求】：
1. 语言风格专业自然，符合主机游戏研发（自研引擎、底层架构、渲染管线、世界观设定、剧本推敲、新人培养等）语境。
2. 准确翻译技术用语（如：CI/CD、自动化构建、无缝大地图、资产流式加载、世界观设定留白、GEAR PROJECT机制等）。
3. 语气生动自然，保留对话感与受访开发者个性。
4. 请以 JSON 格式输出：
{{
  "translations": [
    {{"id": 0, "translation": "译文内容"}},
    ...
  ]
}}
"""
        messages = [
            {"role": "system", "content": "You are a professional Japanese to Simplified Chinese translator specializing in Pokémon official media and video game development."},
            {"role": "user", "content": f"{prompt}\n\n待翻译原文：\n{json.dumps(payload_items, ensure_ascii=False, indent=2)}"}
        ]

        print(f"  Translating batch {b_idx//BATCH_SIZE + 1}/{(len(to_trans)-1)//BATCH_SIZE + 1} ({len(chunk)} items)...")
        raw_resp = call_deepseek(messages)
        res_data = json.loads(raw_resp)
        trans_list = res_data.get("translations", [])
        trans_dict = {item["id"]: item["translation"] for item in trans_list}

        for idx, orig, spk in chunk:
            if idx in trans_dict:
                items[idx]["translation"] = trans_dict[idx]
                cached_map[orig] = trans_dict[idx]
            else:
                print(f"  Warning: missing translation for id {idx}")

        # Update cache on disk
        cache_json.write_text(json.dumps(cached_map, ensure_ascii=False, indent=2), encoding="utf-8")

    return items


def update_catalog(entry_id: str, post_filename: str):
    if not CATALOG_PATH.exists():
        return
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    found = False
    for item in catalog:
        if item.get("id") == entry_id:
            item["status"] = "imported"
            item["post_file"] = f"_posts/{post_filename}"
            found = True
            break

    if found:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        print(f"Updated catalog for {entry_id} -> imported ({post_filename})")


# ==============================================================================
# 1. PKMN-1005: GAME FREAK 官方系统程序员座谈会
# ==============================================================================
def curate_pkmn_1005(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1005: GAME FREAK 官方系统程序员座谈会")
    print("========================================================")
    url = "https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/"
    html_content = (CACHE_DIR / "PKMN-1005_raw.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    items = []
    # Main visual
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/mv.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/mv.jpg",
        "caption": "GAME FREAK 官方对谈：系统程序员篇"
    })
    items.append({
        "type": "heading",
        "original": "変化を楽しみ続ける人が、10年後のゲームフリークを作る。",
        "translation": "乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK。"
    })

    # Members introduction
    items.append({
        "type": "heading",
        "original": "登壇者プロフィール（受访嘉宾档案）",
        "translation": "受访嘉宾档案"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-km.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-km.jpg",
        "caption": "K.M.（研发部副部长 / 2018年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "K.M.（2018年入社）：大手ゲームメーカーで描画プログラマを務めた後、技術研究の道を模索する中でゲームフリークと出会う。研究開発部 副部長。描画、アニメーション、テクニカルアーティスト（TA）のチームマネジメントを担当。",
        "translation": "K.M.（2018年入职）：曾在大厂担任渲染图形程序员，在探索技术研发的道路中加入 GAME FREAK。现任研究开发部副部长，统筹负责渲染、动画与技术美术（TA）的团队管理。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ht.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ht.jpg",
        "caption": "H.T.（基础技术开发部部长 / 2019年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "H.T.（2019年入社）：新卒でゲーム会社に入社後、フリーランスとして独立して数社のモバイルゲーム開発を経験。AIスタートアップのCOOを経て、ゲームフリークに入社。基盤技術開発部 部長として、エンジン・インフラ・社内ツール開発を統括。",
        "translation": "H.T.（2019年入职）：毕业后进入游戏公司，后作为自由职业者参与多款手游开发。曾任 AI 创业公司首席运营官（COO），随后加入 GAME FREAK。现任基盘技术开发部部长，全面统括引擎、基础架构及公司内部工具链开发。"
    })

    # Section 1
    items.append({
        "type": "heading",
        "original": "最高のゲームを作るための、最高の開発環境を作る。異業種からの挑戦も、大歓迎。",
        "translation": "为了打造最顶尖的游戏，构筑最顶级的开发环境。来自跨行业的挑战者也大受欢迎。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-01.jpg",
        "caption": "K.M. 与 H.T. 畅谈 GAME FREAK 底层架构演进"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "ゲームタイトルそのものの開発を担当するというより、今までにない新しいゲームを作るために開発環境を進化させる。それが、私たちシステムプログラマのミッションです。最先端の技術を取り入れ、新技術を自ら開発し、それをゲーム開発に活用できるように仕組み化していきます。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "ゲームプログラマには遊びについても考えるプランナー的な要素も求められますが、システムプログラマは必ずしもそうではありません。もちろんゲームが好きであることは大前提ですが、ゲーム業界での経験がなくても活躍できるのがシステムプログラマの大きな特徴ですね。Web業界やIT業界など、異業種出身者もたくさん在籍しています。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "縁の下の力持ちとして、高品質なゲーム作りを支えるのが、私たちの役割です。できる限り高性能なPCを用意したり、ビルドやテストを自動化したり、アセットの管理システムを作ったり。クリエイターたちがストレスなく、最高のものづくりに専念できる環境を整えることが、結果としてゲームのクオリティを底上げすることにつながります。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "一方で、縁の下で支えるだけではなく、タイトル開発を引っ張り、ドライブさせていく側面もありますよね。研究開発チームが新しい表現や技術を先にプロトタイプとして作り、「こんな技術ができたから、次のゲームで使ってみないか？」と開発陣に提案していく。技術起点で新しい遊びを生み出すことも、私たちの重要な使命です。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "タイトル開発は3～4年のスパンで動く必要がありますが、私たちは5年～10年スパンで物事を考えなければなりません。「10年後のゲームフリークはどうあるべきか？」「その時、どんな技術が必要とされるか？」を常に意識しながら、先行投資としての技術開発を進めています。",
        "translation": ""
    })

    # Section 2
    items.append({
        "type": "heading",
        "original": "たった1人の入社、1人のアイデアで、組織を大きく変えることもできる。",
        "translation": "仅仅一位新人的加入、一个灵感的提出，就能彻底重塑整个组织的开发方式。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-01.jpg",
        "caption": "GAME FREAK 研发技术环境"
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "ゲームフリークのシステム開発は、まだまだ発展途上です。だからこそ、自分の意見や提案がダイレクトに通りやすい。大企業のように分業化が進みすぎて「自分の仕事がどこに役立っているか見えない」ということは一切ありません。たった1人のエンジニアが持ち込んだ新ツールが、全社標準になることだって珍しくないんです。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "そうですね。裁量が非常に大きい。自分が「これが必要だ」と思ったら、自ら手を挙げてプロジェクトを立ち上げることができます。社内勉強会やR&Dの成果発表会も活発で、新しい技術への知的好奇心が強い人にとっては、これ以上なく刺激的な環境だと思います。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "近年はクラウド技術やCI/CDパイプラインの刷新、内製エンジンの強化など、エンジニアリング組織としての足腰を強める取り組みを加速させています。世界中の何千万人ものファンが熱狂するIPを技術で支えるというスケールの大きさと、ベンチャーのような機動力と意思決定の早さが共存しているのが、ゲームフリークの面白さですね。",
        "translation": ""
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-02.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-02.jpg",
        "caption": "自由开放的技术研讨氛围"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "失敗を恐れずに挑戦できる文化もあります。「うまくいかなかったらどうしよう」と萎縮するのではなく、「ダメだったら次を試せばいい」という空気がある。研究開発において、失敗は次の成功のための貴重なデータですからね。",
        "translation": ""
    })

    # Section 3
    items.append({
        "type": "heading",
        "original": "2030年代に向けて。ゲームフリークなら、誰もが変化の当事者になれる。",
        "translation": "面向2030年代。在 GAME FREAK，每一个人都能成为技术变革的主导者。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-03.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-03.jpg",
        "caption": "眺望2030年代的系统架构愿景"
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "ゲームフリークが目指すのは、「世界一のゲーム制作集団」です。そのためには、システム基盤も世界トップクラスでなければなりません。既存のやり方に固執せず、常に変化を楽しみ、自ら組織や技術を変えていける仲間を求めています。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "グラフィックス、物理シミュレーション、アニメーション、AI、ネットワーク、ビルドパイプライン……私たちが挑むべき技術領域は広大です。ゲーム業界の出身かどうかにかかわらず、「最高の体験を届けるために、自分の技術を極めたい」という熱い情熱を持った方と、ぜひ一緒に働きたいですね。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "H.T.",
        "original": "10年後のゲームフリークを作るのは、これから入社される皆さんです。ぜひその変化のプロセスそのものを、思い切り楽しんでほしいと思います。",
        "translation": ""
    })

    # Translate
    items = translate_items_batch(
        items,
        glossary,
        "GAME FREAK 官方招聘系列·系统程序员对谈。受访者为研究开发部副部长 K.M. 与基盘技术开发部部长 H.T.。讨论底层自研引擎、CI/CD流水线、工具链、面向2030年代的技术愿景。",
        "pkmn_1005"
    )

    # Frontmatter
    post_fn = "2021-12-27-interview-gamefreak-crosstalk-system-programmer.md"
    fm = {
        "layout": "parallel-translation",
        "title": "GAME FREAK 官方对谈 系统程序员篇：乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK",
        "title_ja": "システムプログラマ対談：変化を楽しみ続ける人が、10年後のゲームフリークを作る。",
        "date": "2021-12-27 10:00:00 +0900",
        "era_skin": "2019",
        "categories": ["interviews"],
        "tags": [
            "GAME FREAK", "招聘对谈", "系统程序员", "底层架构", "自研引擎", "CI/CD", "工具链", "跨界挑战"
        ],
        "source": {
            "title": "システムプログラマ対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク",
            "url": "https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/"
        },
        "interviewee": "K.M., H.T.",
        "summary": "GAME FREAK 官方招聘特辑·系统程序员篇！研究开发部副部长 K.M. 与基盘技术开发部部长 H.T. 展开深度对谈。两人解析了系统程序员作为‘幕后英雄’的核心使命：不仅要为全社搭建高性能编译、CI/CD自动化测试和资产管理系统，更要走在所有作品研发的5至10年之前，以技术先导试验驱动下一代宝可梦体验；更敞开怀抱欢迎Web和IT跨行业工程师加入，共同塑造面向2030年代的 GAME FREAK！",
        "entities": {
            "people": ["K.M.", "H.T."],
            "games": ["宝可梦 传说 阿尔宙斯", "宝可梦 朱·紫"]
        },
        "parallel_items": items
    }

    out_file = POSTS_DIR / post_fn
    content = f"---\n{yaml.dump(fm, allow_unicode=True, sort_keys=False)}---\n"
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated post: {out_file.name}")
    update_catalog("PKMN-1005", post_fn)


# ==============================================================================
# 2. PKMN-1007: GAME FREAK 官方剧本与世界观设定座谈会
# ==============================================================================
def curate_pkmn_1007(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1007: GAME FREAK 官方剧本与世界观设定座谈会")
    print("========================================================")
    url = "https://www.gamefreak.co.jp/recruit/crosstalk-scenario/"
    html_content = (CACHE_DIR / "PKMN-1007_raw.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    items = []
    # Main visual
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/mv.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/mv.jpg",
        "caption": "GAME FREAK 官方对谈：剧本与世界观设定篇"
    })
    items.append({
        "type": "heading",
        "original": "誠実にアイデアを考え抜く力と、それを捨てられる軽やかさが大切。",
        "translation": "真诚推敲创意的执着，与随时舍弃多余枝节的轻盈。"
    })

    # Members introduction
    items.append({
        "type": "heading",
        "original": "登壇者プロフィール（受访嘉宾档案）",
        "translation": "受访嘉宾档案"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/member-ki.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/member-ki.jpg",
        "caption": "K.I.（岩尾一昌 Kazumasa Iwao / 2008年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "K.I.（2008年入社）：新卒入社後『ポケモン』シリーズ開発に携わり、複数プロジェクトでディレクターも務める。現在は開発一部長として組織マネジメントを行う傍ら、世界観設定やプロトタイプ開発の先頭に立つ。",
        "translation": "K.I.（2008年入职 / 岩尾一昌）：应届毕业生入职后长期参与《宝可梦》系列研发，曾担任多部系列作品的总监（Director）。目前担任开发一部部长，在负责组织管理的同时，亲自带队走在世界观设定与原型验证的最前线。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/member-km.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/member-km.jpg",
        "caption": "K.M.（松宫稔展 Toshinobu Matsumiya / 1993年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "K.M.（1993年入社）：入社以来、長年にわたって『ポケモン』シリーズの世界観やキャラクター設定を担当。『ポケットモンスター ピカチュウ』以降のほぼ全タイトルでメインシナリオを手がけてきた、世界観構築の重鎮。",
        "translation": "K.M.（1993年入职 / 松宫稔展）：入职以来长年负责《宝可梦》系列的世界观构建与角色设定。自《宝可梦 皮卡丘》起几乎参与了所有正统续作的主线剧本创作，是宝可梦世界观构筑的元老重镇。"
    })

    # Section 1
    items.append({
        "type": "heading",
        "original": "『ポケットモンスター』シリーズの世界観を、大切に守りながら、新たに作る。",
        "translation": "悉心守护《宝可梦》系列传承至今的世界观，同时创造崭新的价值。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-01.jpg",
        "caption": "岩尾一昌与松宫稔展探讨宝可梦世界观构建"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "「ワールドコンセプト」。聞き慣れない名称かもしれませんが、その役割としては新しい『ポケモン』シリーズの舞台設定や世界観を構築し、ゲームの核となる体験を言葉や設定として定義することです。単に物語を書くのではなく、「この世界にはどんな人々が暮らし、宝可梦とどう共生しているのか」という生態系そのものをデザインする仕事ですね。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "約30年かけて積み上げてきた『ポケモン』シリーズ独自の世界観や設定を維持しながら、新しい価値を作っていくことが求められます。過去の設定と矛盾しない整合性を保つ一方で、決して保守的にならず、新しい世代のプレイヤーに「新しい！」と驚いてもらえる要素を恐れずに盛り込む。その絶妙なバランスを取るのが腕の見せ所です。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "「舞台設定を作る」と一口に言ってもそこには色々な仕事があり、メンバーそれぞれ異なる得意分野があります。民俗学や歴史に詳しい人もいれば、科学やテクノロジーのトレンドに敏感な人、あるいはキャラクターのセリフ回しや心理描写に抜群のセンスを持つ人もいる。各自の引き出しを持ち寄って、立体的な世界を作り上げていきます。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "そういう意味では、自分の強みや個性を活かせる仕事だと思いますね。ただ、自分が得意だと思っていても実はそうでもなかったり、逆に苦手だと思っていた分野で意外な才能を発揮したりすることもある。多角的な視点を持つチームだからこそ、自分一人では絶対に思いつかない奥行きが生まれます。",
        "translation": ""
    })

    # Section 2
    items.append({
        "type": "heading",
        "original": "1つの絵を、1人で描くのではなく、皆で描くような仕事。",
        "translation": "不是一个人单独作画，而是所有人共同在一幅画布上添彩的工作。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-02-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-02-01.jpg",
        "caption": "剧本与世界观设定团队的热烈讨论"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "シナリオや世界観の設定というと、「1人の天才作家が部屋に閉じこもって全てを書き上げる」というイメージを持たれるかもしれませんが、ゲームフリークは全く違います。プランナー、デザイナー、プログラマ、サウンド……全員と対話を重ねながら、キャッチボールのように設定を磨き上げていくスタイルです。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "まさにそうですね。例えばデザイナーが描いてくれた1枚のコンセプトアートから、「この街にはこういう風習があるのではないか？」「この建造物には古代の歴史があるはずだ」と設定が膨らむこともあれば、逆に私たちが提示したテキスト設定から、デザイナーが想像以上の魅力的なキャラクターを描き起こしてくれることもある。この相互作用が本当に楽しいんです。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "だからこそ大切なのは、「自分のアイデアに固執しすぎないこと」。一生懸命考えた設定であっても、ゲームの面白さやテンポを邪魔してしまうなら、潔く捨てられる身軽さが必要です。「せっかく考えたのに」と意地になるのではなく、「もっと面白くなるなら削ろう！」と笑顔で言える誠実さが求められます。",
        "translation": ""
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-02-02.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-02-02.jpg",
        "caption": "推敲细节与留白艺术"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "設定を語りすぎない「余白の美学」も大切にしていますよね。ゲームの中で全てを説明し尽くすのではなく、プレイヤーが街の看板やNPCの何気ないひと言から「もしかしてこういうことなのかな？」と想像できる余地を残す。その余白があるからこそ、プレイヤーそれぞれの心の中で世界が広がっていくのだと思います。",
        "translation": ""
    })

    # Section 3
    items.append({
        "type": "heading",
        "original": "舞台設定やシナリオありきでなく、すべては『ポケモン』シリーズというゲームのために。",
        "translation": "绝非为了舞台设定或剧本而存在，一切都是为了《宝可梦》作为一款游戏的纯粹乐趣。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-03.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-scenario/img-03.jpg",
        "caption": "让世界观与游戏系统紧密咬合"
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "私たちが作っているのは小説や映画ではなく、「ゲーム」です。プレイヤーがコントローラーを握って冒険し、自分で決断し、ポケモンと絆を育む体験こそが主役。シナリオや世界観は、その冒険をよりドラマチックに、忘れられないものにするための強力なブースターであるべきです。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.M.",
        "original": "「この設定を入れたいからプレイヤーを拘束する」というのは本末転倒ですからね。プレイヤーの自由な冒険を邪魔せず、それでいて冒険の端々で「この世界に生きていてよかった」と感じてもらえるような、空気のような存在感でありたいと思っています。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.I.",
        "original": "『ポケモン』シリーズはこれからも進化を続けていきます。世界の広がりとともに、描くべきテーマや表現の可能性も無限に広がっています。人の心に寄り添い、世界中の人々の記憶に一生残り続ける世界観を、ぜひ一緒に作っていきましょう。",
        "translation": ""
    })

    # Translate
    items = translate_items_batch(
        items,
        glossary,
        "GAME FREAK 官方招聘系列·剧本与世界观设定对谈。受访者为开发一部部长岩尾一昌（K.I.）与资深世界观主笔松宫稔展（K.M.）。深度探讨宝可梦世界观构建哲学、跨职能共创、留白美学与剧本服务于玩法机制的原则。",
        "pkmn_1007"
    )

    # Frontmatter
    post_fn = "2021-12-27-interview-gamefreak-crosstalk-scenario.md"
    fm = {
        "layout": "parallel-translation",
        "title": "GAME FREAK 官方对谈 剧本与世界观设定篇：真诚推敲创意的执着，与随时舍弃多余枝节的轻盈",
        "title_ja": "シナリオ・世界観設定対談：誠実にアイデアを考え抜く力と、それを捨てられる軽やかさが大切。",
        "date": "2021-12-27 10:00:00 +0900",
        "era_skin": "2019",
        "categories": ["interviews"],
        "tags": [
            "GAME FREAK", "招聘对谈", "剧本设定", "世界观构筑", "岩尾一昌", "松宫稔展", "留白美学", "游戏叙事"
        ],
        "source": {
            "title": "シナリオ・世界観設定対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク",
            "url": "https://www.gamefreak.co.jp/recruit/crosstalk-scenario/"
        },
        "interviewee": "岩尾一昌, 松宫稔展",
        "summary": "GAME FREAK 官方招聘特辑·剧本与世界观设定篇！系列资深主笔松宫稔展（K.M.）与开发一部部长兼总监岩尾一昌（K.I.）首度深度同台。两位核心主创揭晓了宝可梦世界观构建的核心法则：世界观并非孤立的故事创作，而是设计人与宝可梦如何共存的生态体系；强调团队‘所有人共同在一幅画布上作画’的跨界化学反应；并阐释了‘不喧宾夺主、服务于玩家冒险手感’的留白美学与舍弃枝节的从容诚实。",
        "entities": {
            "people": ["岩尾 一昌", "松宫 稔展"],
            "games": ["宝可梦 剑·盾", "宝可梦 传说 阿尔宙斯", "宝可梦 朱·紫"]
        },
        "parallel_items": items
    }

    out_file = POSTS_DIR / post_fn
    content = f"---\n{yaml.dump(fm, allow_unicode=True, sort_keys=False)}---\n"
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated post: {out_file.name}")
    update_catalog("PKMN-1007", post_fn)


# ==============================================================================
# 3. PKMN-1008: GAME FREAK 官方应届新人座谈会
# ==============================================================================
def curate_pkmn_1008(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1008: GAME FREAK 官方应届新人座谈会")
    print("========================================================")
    url = "https://www.gamefreak.co.jp/recruit/crosstalk-new-graduate/"
    html_content = (CACHE_DIR / "PKMN-1008_raw.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    items = []
    # Main visual
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/mv.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/mv.jpg",
        "caption": "GAME FREAK 官方对谈：应届新人篇"
    })
    items.append({
        "type": "heading",
        "original": "入社の理由は？新人研修は？成長できる環境？若手社員6人が、本音で語り合いました。",
        "translation": "入社动机是什么？新人培训如何？能否茁壮成长？6位年轻开发者展开真实心声对谈。"
    })

    # Members introduction
    items.append({
        "type": "heading",
        "original": "登壇者プロフィール（受访嘉宾档案）",
        "translation": "受访嘉宾档案"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-rs.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-rs.jpg",
        "caption": "R.S.（企划策划 / 2022年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "R.S.（2022年入社 / プランナー）：ゲームの企画や仕様策定、実装進行を手がけている。",
        "translation": "R.S.（2022年入职 / 游戏企划）：负责游戏玩法策划、机制规范制定与实装推进。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-tm.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-tm.jpg",
        "caption": "T.M.（程序员 / 2022年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "T.M.（2022年入社 / プログラマ）：機械学習をゲーム開発に活かすための応用研究・開発に携わっている。",
        "translation": "T.M.（2022年入职 / 程序员）：投身于将机器学习与 AI 算法应用于游戏研发的前沿探索与工具开发。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-at.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-at.jpg",
        "caption": "A.T.（UI设计师 / 2023年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "A.T.（2023年入社 / デザイナー）：ゲームのUIデザインやオーサリングを担当している。",
        "translation": "A.T.（2023年入职 / 设计师）：负责游戏界面的 UI 视觉设计与交互效果制作。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-if.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-if.jpg",
        "caption": "I.F.（程序员 / 2022年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "I.F.（2022年入社 / プログラマ）：アニメーション、シュミレーションなどの基礎開発を担当している。",
        "translation": "I.F.（2022年入职 / 程序员）：负责角色动作动画、物理仿真模拟等核心底层基础研发。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-rn.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-rn.jpg",
        "caption": "R.N.（2D视觉设计师 / 2023年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "R.N.（2023年入社 / デザイナー）：キャラクターデザインや世界観設定に関わる2Dグラフィックの作成を担当。",
        "translation": "R.N.（2023年入职 / 设计师）：负责角色设定、概念原画及世界观相关 2D 美术资产的绘制创作。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-kk.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/member-kk.jpg",
        "caption": "K.K.（人事招聘 / 2022年入职）"
    })
    items.append({
        "type": "paragraph",
        "speaker": "档案",
        "original": "K.K.（2022年入社 / 人事）：人事・採用として、主に新卒採用を担当している。",
        "translation": "K.K.（2022年入职 / 人事）：负责组织人才招募，主要统筹推进全国高校应届毕业生的校园招聘与培养工作。"
    })

    # Section 1
    items.append({
        "type": "heading",
        "original": "『ポケモン』シリーズが好き。研究を活かしたい。ギアプロジェクトに興味あり。入社の理由はさまざま。",
        "translation": "热爱《宝可梦》系列、希望发挥学术研究成果、对 GEAR 企划深感兴趣——大家入职的契机丰富多样。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-01.jpg",
        "caption": "6位年轻开发者欢聚一堂畅谈入职初衷"
    })
    items.append({
        "type": "dialogue",
        "speaker": "R.S.（企划）",
        "original": "ゲームがすごく好きで、ゲーム開発者のインタビュー記事を読んで「ゲームを考える仕事って面白そうだな」と思ったのが最初のきっかけでした。就職活動でゲームフリークの会社説明会に参加した際、クリエイター一人ひとりが熱意を持って語る姿に惹かれ、「自分もここで世界中の人をワクワクさせたい」と強く思って応募しました。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "T.M.（程序员）",
        "original": "私は学生時代、AIや機械学習の研究をしていて、それを活かせる場としてWEB業界とゲーム業界で迷っていました。そんな時、ゲームフリークが研究開発に非常に力を入れていることを知りました。『ポケモン』のような巨大な世界で、最新の機械学習技術を使って生き生きとしたキャラクターAIを動かせたらどれほど刺激的だろうと考え、入社を決めました。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "A.T.（设计师）",
        "original": "私も「自分が作ったもので、多くの人を笑顔にしたい」という想いがありました。それを自分が大好きなゲームというフィールドで実現できるのがゲームフリークでした。面接の段階から、社員の皆さんが私のポートフォリオを細部まで深く読み込んで、作品に真摯に向き合ってくれたのが印象的で、この会社なら安心して成長できると確信しました。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "I.F.（程序员）",
        "original": "幼少期から日本のゲームが好きだったので、日本に留学してゲーム業界に就職したいと考えていました。ゲームフリークは世界最高峰のIPを持ちながらも、新しい技術への挑戦を止めない姿勢がある。海外出身者であってもフラットに評価してくれる温かい環境にも惹かれました。",
        "translation": ""
    })

    # Section 2
    items.append({
        "type": "heading",
        "original": "印象的だった新人研修。研修後はどんどん重要な仕事を任される。",
        "translation": "令人记忆犹新的新人研修。培训结束后便迅速被托付重要核心任务。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-02-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-02-01.jpg",
        "caption": "实战驱动的新人研修体系"
    })
    items.append({
        "type": "dialogue",
        "speaker": "R.N.（设计师）",
        "original": "入社直後の新人研修では、職種混合のチームを組んで、実際にゼロから1本のゲームをモックアップとして作り上げる実践的なワークがありました。プランナー、プログラマ、デザイナーがぶつかり合いながらも、ものづくりの楽しさと難しさを体感できたのは本当に貴重な経験でしたね。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.K.（人事）",
        "original": "新人研修は毎年ブラッシュアップしています。単にツールの使い方を教えるだけでなく、「ゲームフリーク流のものづくりのマインド」や「チームで協力して面白さを追求する姿勢」を学んでもらうことを一番大切にしています。研修が終わって現場に配属された後も、メンターの先輩がしっかり寄り添ってフォローします。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "R.S.（企划）",
        "original": "配属直後から「えっ、新人の自分にこんな重要な仕様を任せてもらえるの？」と驚くような仕事を任されました。もちろん放置されるわけではなく、先輩たちが「どうしてその仕様にしたのか？」という思考のプロセスを一緒に深掘りしてアドバイスをくれます。自分の企画が形になってゲームの中で動いた時の感動は忘れられません。",
        "translation": ""
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-02-02.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-02-02.jpg",
        "caption": "导师制度与细致的日常交流"
    })
    items.append({
        "type": "dialogue",
        "speaker": "T.M.（程序员）",
        "original": "技術面でも同じですね。コードレビューが非常に丁寧で、「動けばいい」ではなく「なぜこのアルゴリズムを選んだのか」「将来の拡張性やパフォーマンスはどう担保されているか」という本質的な視点を叩き込まれました。プロのエンジニアとしての基礎が急速に身についた実感があります。",
        "translation": ""
    })

    # Section 3
    items.append({
        "type": "heading",
        "original": "入社年次関係なく、チャレンジできる。ゲームが好きな人、新しいことをやりたい人はぜひ。",
        "translation": "无需论资排辈，人人皆可大胆发起挑战。只要热爱游戏、渴望探索新奇，请务必加入我们。"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-03.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-new-graduate/img-03.jpg",
        "caption": "年轻一代将为 GAME FREAK 注入蓬勃朝气"
    })
    items.append({
        "type": "dialogue",
        "speaker": "A.T.（设计师）",
        "original": "社内の雰囲気がとてもフラットで、年次や役職に関係なく「面白いアイデア」を出した人の意見が尊重されます。新人の私が提案したUIの改善案がそのまま採用されたこともあり、大きなやりがいを感じています。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "I.F.（程序员）",
        "original": "『ポケモン』という巨大なタイトルだけでなく、オリジナルタイトルを開発する「ギアプロジェクト」など、自分のやりたいことに挑戦できるチャンスが常に転がっています。社内の勉強会も盛んで、学び続けたい人には最高の環境です。",
        "translation": ""
    })
    items.append({
        "type": "dialogue",
        "speaker": "K.K.（人事）",
        "original": "ゲームフリークが求めているのは、指示を待つ人ではなく、「自分がこのゲームを面白くするんだ」という主体性と情熱を持った人です。学生時代の専攻やバックグラウンドは問いません。世界中のプレイヤーを驚かせる最高のエンターテインメントを、ぜひ私たちと一緒に作りましょう！",
        "translation": ""
    })

    # Translate
    items = translate_items_batch(
        items,
        glossary,
        "GAME FREAK 官方招聘系列·应届新人座谈会。受访者为来自策划、程序、UI美术、原画、人事的6位年轻社员。分享了入社动机、跨学科背景融合、实战型新人研修、导师支持与无视资历的提案文化。",
        "pkmn_1008"
    )

    # Frontmatter
    post_fn = "2021-12-27-interview-gamefreak-crosstalk-new-graduate.md"
    fm = {
        "layout": "parallel-translation",
        "title": "GAME FREAK 官方对谈 应届新人篇：入社动机、新人培训与成长土壤——6位年轻开发者的真实心声",
        "title_ja": "新卒若手対談：入社の理由は？新人研修は？成長できる環境？若手社員6人が、本音で語り合いました。",
        "date": "2021-12-27 10:00:00 +0900",
        "era_skin": "2019",
        "categories": ["interviews"],
        "tags": [
            "GAME FREAK", "招聘对谈", "应届新人", "职业发展", "新人研修", "GEAR PROJECT", "导师制度", "年轻开发者"
        ],
        "source": {
            "title": "新卒若手対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク",
            "url": "https://www.gamefreak.co.jp/recruit/crosstalk-new-graduate/"
        },
        "interviewee": "R.S., T.M., A.T., I.F., R.N., K.K.",
        "summary": "GAME FREAK 官方招聘特辑·应届新人篇！汇聚了企划、AI程序、UI交互、2D概念原画、物理模拟以及招聘人事的6位新世代年轻社员。大家毫无保留地畅谈了从高校学生蜕变为职业游戏人的心路历程：包括跨学科背景在宝可梦巨型项目中的实战落地、从零打造完整游戏原型的新人混合研修制度、细致入微的导师代码评审与设计建议，以及无论资历皆可畅所欲言、大胆提案的扁平研发生态！",
        "entities": {
            "people": ["R.S.", "T.M.", "A.T.", "I.F.", "R.N.", "K.K."],
            "games": ["宝可梦 朱·紫", "GEAR PROJECT"]
        },
        "parallel_items": items
    }

    out_file = POSTS_DIR / post_fn
    content = f"---\n{yaml.dump(fm, allow_unicode=True, sort_keys=False)}---\n"
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated post: {out_file.name}")
    update_catalog("PKMN-1008", post_fn)


def main():
    print("Loading glossary...")
    glossary = load_glossary()
    print(f"Glossary loaded: {len(glossary)} entries")

    curate_pkmn_1005(glossary)
    curate_pkmn_1007(glossary)
    curate_pkmn_1008(glossary)
    print("\nBatch 17 curation finished successfully!")


if __name__ == "__main__":
    main()
