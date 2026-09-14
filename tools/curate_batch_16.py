"""Curate Batch 16:
1. PKMN-1004: GAME FREAK 官方游戏程序员座谈会 (crosstalk-game-programmer)
2. PKMN-1006: GAME FREAK 官方企划座谈会 (crosstalk-planner)
3. PKMN-1033: 宝可梦公司 (TPC) 官方专访 新人篇 (newgeneration.html)
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
CACHE_DIR = ROOT / "tools" / "cache_batch_16"
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


def translate_items_batch(items: list[dict], glossary: list[dict], context_desc: str) -> list[dict]:
    """Translate items preserving structure, using glossary enforcement."""
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
        return items

    combined_text = " ".join([t[1] for t in to_trans])
    terms = find_glossary_matches(combined_text, glossary)
    term_constraints = "\n".join([f"- {k} => {v}" for k, v in terms]) if terms else "无特殊官方术语锁定。"

    BATCH_SIZE = 12
    for b_idx in range(0, len(to_trans), BATCH_SIZE):
        chunk = to_trans[b_idx:b_idx + BATCH_SIZE]
        payload_items = [{"id": idx, "speaker": spk, "text": text} for idx, text, spk in chunk]

        prompt = f"""你是宝可梦官方档案馆的资深中日翻译专家。请将以下来自宝可梦官方研发与招聘专访的日文内容翻译为流畅、自然、符合中国大陆宝可梦官方简体中文语境的译文。
背景信息：
{context_desc}

【官方术语硬性约束（必须严格遵守）】：
{term_constraints}

【翻译要求】：
1. 语言风格严谨得体、符合游戏工业与互联网开发语境（如：游戏程序员、企划、自研引擎、无缝大地图、碰撞检测、手感调校等）。
2. 保留原说话者的人格魅力与敬语谦词的中文对应，语气自然、不出现生硬机翻腔。
3. 请以 JSON 格式输出，格式为：
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
        print(f"  Translating chunk {b_idx//BATCH_SIZE + 1}/{(len(to_trans)-1)//BATCH_SIZE + 1} ({len(chunk)} items)...")
        res_str = call_deepseek(messages)
        res_json = json.loads(res_str)
        t_map = {item["id"]: item["translation"] for item in res_json.get("translations", [])}

        for idx, _, _ in chunk:
            if idx in t_map:
                items[idx]["translation"] = t_map[idx]
            else:
                print(f"  Warning: missing translation for id {idx}")

    return items


def download_image(url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        clean_url = url.split("?")[0]
        req = urllib.request.Request(clean_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            if len(data) > 500:
                dest_path.write_bytes(data)
                print(f"  Saved image: {dest_path.name} ({len(data)} bytes)")
                return True
    except Exception as e:
        print(f"  Failed to download image {url}: {e}")
    return False


# ==============================================================================
# 1. PKMN-1004: GAME FREAK 游戏程序员座谈会
# ==============================================================================
def curate_pkmn_1004(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1004: GAME FREAK 官方游戏程序员座谈会")
    print("========================================================")
    url = "https://www.gamefreak.co.jp/recruit/crosstalk-game-programmer/"
    cache_file = CACHE_DIR / "pkmn_1004_raw.html"
    if not cache_file.exists():
        req = urllib.request.Request(url, headers=HEADERS)
        html_content = urllib.request.urlopen(req).read().decode("utf-8")
        cache_file.write_text(html_content, encoding="utf-8")
    else:
        html_content = cache_file.read_text(encoding="utf-8")

    img_dir = IMG_DIR / "2021-gamefreak-crosstalk-game-programmer"
    img_dir.mkdir(parents=True, exist_ok=True)

    # Download key images
    images_to_fetch = [
        ("mv.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/game-programmer/mv.jpg"),
        ("member-mo.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/game-programmer/member-mo.jpg"),
        ("member-ki.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/game-programmer/member-ki.jpg"),
        ("img-01.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/game-programmer/img-01.jpg"),
        ("img-03.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/game-programmer/img-03.jpg")
    ]
    for fname, img_url in images_to_fetch:
        download_image(img_url, img_dir / fname)

    # Structured items
    items = []
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/mv.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/mv.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "一番大切なのは、「遊びの本質」を捉えているかどうか。",
        "translation": "最重要的是否能把握住“玩法的本质”。",
        "speaker": None
    })

    # Members introduction
    items.append({
        "type": "heading",
        "original": "登壇者プロフィール（受访嘉宾档案）",
        "translation": "登场成员档案",
        "speaker": None
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/member-mo.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/member-mo.jpg",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "original": "M.O.（2010年入社）：『ポケットモンスターブラック・ホワイト』からシリーズタイトルの開発に携わる。現在は開発一部プログラマのセクションディレクターと、プログラマ職種の採用責任者を務める。",
        "translation": "M.O.（2010年入职）：从《宝可梦 黑／白》开始参与系列正统作品的研发。目前担任开发一部程序员模块总监（Section Director）兼程序员职能招聘负责人。",
        "speaker": "档案"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/member-ki.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/member-ki.jpg",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "original": "K.I.（2010年入社）：幼少期に『ポケットモンスター 赤・緑』と出会い、ゲームプログラマを志す。入社後は数々の『ポケモン』シリーズの開発に携わり、ディレクターも担当。現在は開発二部長を務める。",
        "translation": "K.I.（2010年入职）：童年时代与《宝可梦 红／绿》相遇，立志成为游戏程序员。入职后参与了多部《宝可梦》系列作品的开发，并担任过总监。现任开发二部部长。",
        "speaker": "档案"
    })

    # Section 1
    items.append({
        "type": "heading",
        "original": "大きく変わろうとしているゲーム作り。それをリードしていくのが、ゲームプログラマ。",
        "translation": "正在经历深刻巨变的游戏制作——而引领这一切的，正是游戏程序员。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "ゲームフリークでは今、ゲームの作り方そのものが大きく変わりつつあります。例えば『Pokémon LEGENDS アルセウス』。このゲームは今までとは全く異なるアプローチで開発を進めました。新しい体験を提供するために、これまでの常識にとらわれず、新しい技術や手法を積極的に取り入れています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "今までの開発プロセスを取っ払って、一からゲームを作っていくようなものでしたね。プロジェクトを進めていく前に、まず「野生のポケモンがフィールドにいて、そこにボールを投げて捕まえる」というコアな遊びのプロトタイプを作り、面白さを徹底的に検証しました。その中心にいたのが、ゲームプログラマでした。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "試作段階から、「茂みに隠れてポケモンに近づく時、ポケモンの視線や動きがどうなれば生き物として自然で、面白く感じられるか？」ということまで突き詰めていました。企画者が頭で考えた仕様をただ実装するのではなく、プログラマ自らが「こう動かしたらもっとリアルで面白いのでは」と提案し、形にしていったんです。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "最近は試作フェーズにより時間をかけるようになりましたね。それにより、ゲームの世界にそのままポケモンが生活しているような、リアリティ溢れる新しい体験を実現できました。ゲームプログラマが遊びのアイデアを直接コードに落とし込み、手触りを確かめながら進化させていく文化が、より強固になっています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "『ポケモン』シリーズでは毎タイトル、アクションゲームの要素やオープンワールドの要素など、新しい遊びに挑戦しています。新しいことにチャレンジする時こそ、ゲームプログラマの腕の見せ所です。未知の課題に対して「どう実現するか」を楽しみながら突破していける人が求められています。",
        "translation": ""
    })

    # Section 2
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/img-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/img-01.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "「ゲームの面白さ」を作る方法をみんなで共有し、新しい遊びを開発する集団へ。",
        "translation": "将创造“游戏趣味”的方法与全员共享，进化为开创全新玩法的集体。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "これからのゲームプログラマのビジョンとして、「ゲームの面白さ」を体系化していきたいと考えています。これまで各々が試行錯誤して作ってきたノウハウや手触りの感覚を、組織全体の知見として共有し、誰でも高いクオリティの遊びを生み出せるような基盤を作りたいんです。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "ジャンプ一つとっても、ユーザーが気持ち良く操作できるように作るのはすごく難しい。私自身もすごく苦労した経験があります。踏み切りの挙動、滞空時間、着地の硬直、重力の掛け方……それらの数値をどう調整すれば「気持ちいい」と感じられるのか。そうした感覚的な部分を言語化し、ノウハウとして蓄積していくことが大切です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "例えば、投げたボールの回転や軌跡がどうなっているとユーザーが気持ち良いのかということを検証して調整したり。フィールドで走りながら旋回する時の慣性やカメラの追従具合など、細部に宿る「快感」を突き詰めるのがゲームプログラマの仕事です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "ゲームプログラマがシステムプログラマと違うのは、「遊び」を考え、具体的な形にしていくことに特化している点です。「人は何を楽しいと感じるのか」「どういう入力に対してどういうフィードバックがあれば快感を得られるのか」。心理学や人間工学に近い視点も持ちながら、プログラムを書いていきます。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "そんな「面白さの追求」という感覚的な部分に興味がある人を、もっと増やしていきたいですよね。現在、システムプログラマがさまざまな技術基盤や開発効率化を整えてくれているので、ゲームプログラマはより一層「遊びの面白さ」に集中できる環境が整ってきています。",
        "translation": ""
    })

    # Section 3
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/img-03.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-game-programmer/img-03.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "多様な興味を持つ人たちと、世界中を楽しませるゲームを作りたい。",
        "translation": "希望能与拥有多元兴趣的人们一起，制作能够给全世界带来欢笑的游戏。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "求める人物像としては、やはり「遊びの本質を捉えている人」です。例えば「いないいないばあをした時に、何で赤ちゃんが喜ぶのか？」「積み木が崩れた時に、なぜ子どもは笑うのか？」。そういった日常の中にある感情の動きや遊びの根本に興味を持てる人が向いています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "『ポケモン』シリーズは、さまざまな遊びの要素を内包し、世界中で多くの方に親しまれているタイトルです。RPGの要素に加えてアクション性や探索、コミュニケーションなど、多面的な魅力を持っています。だからこそ、ゲームだけでなく幅広いカルチャーや体験にアンテナを張っている人と一緒に働きたいですね。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "M.O.",
        "original": "ゲームが好きなことはもちろん、スポーツが好き、アウトドアが好きなど、何でもいい。それぞれの経験から遊びの本質につながりそうなものを見つけ出し、ゲームに落とし込める引き出しの多さが強みになります。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.I.",
        "original": "「それ面白いね、ゲームになりそうだね」「やってみようか！」といった会話が日常的に行われ、新しい提案が生まれる。それを、スピード感を持ってプロトタイプとして実装できるのが、ゲームフリークのプログラマの最高の面白さだと思います。",
        "translation": ""
    })

    # Translation
    items = translate_items_batch(
        items,
        glossary,
        "GAME FREAK 官方招聘系列·游戏程序员座谈会。受访者包括开发一部总监 M.O. 与开发二部长 K.I.。重点讨论《Pokémon LEGENDS 阿尔宙斯》的核心玩法原型验证、野生宝可梦潜行捕捉手感、跳跃与投掷球体的手感调校、以及从日常生活中洞察‘玩法的本质’。"
    )

    # Post frontmatter
    fm = {
        "layout": "parallel-translation",
        "title": "GAME FREAK 官方对谈 游戏程序员篇：最重要的是否能把握住“玩法的本质”（M.O. × K.I.）",
        "date": "2021-12-27 12:00:00 +0900",
        "author": "GAME FREAK 招聘团队",
        "categories": ["interviews"],
        "tags": ["GAME FREAK", "程序员", "宝可梦传说 阿尔宙斯", "招聘访谈", "底层架构", "游戏设计"],
        "era_skin": "2019",
        "source": {
            "title": "ゲームプログラマ対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク",
            "url": "https://www.gamefreak.co.jp/recruit/crosstalk-game-programmer/",
            "source_type": "official_recruit"
        },
        "interviewee": "M.O., K.I.",
        "parallel_items": items
    }

    out_file = POSTS_DIR / "2021-12-27-interview-gamefreak-crosstalk-game-programmer.md"
    body = "\n\n> 本篇访谈译自 GAME FREAK 官方招聘网站“Cross Talk 社员对谈”企划，深入探讨了在《宝可梦传说 阿尔宙斯》开发过程中，游戏程序员如何从零颠覆固有流程、打磨野生宝可梦生态交互与操作手感的珍贵内幕。\n"
    yaml_text = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_text}---\n{body}", encoding="utf-8")
    print(f"Saved: {out_file.name} (Total items: {len(items)})")


# ==============================================================================
# 2. PKMN-1006: GAME FREAK 企划座谈会
# ==============================================================================
def curate_pkmn_1006(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1006: GAME FREAK 官方企划座谈会")
    print("========================================================")
    url = "https://www.gamefreak.co.jp/recruit/crosstalk-planner/"
    cache_file = CACHE_DIR / "pkmn_1006_raw.html"
    if not cache_file.exists():
        req = urllib.request.Request(url, headers=HEADERS)
        html_content = urllib.request.urlopen(req).read().decode("utf-8")
        cache_file.write_text(html_content, encoding="utf-8")
    else:
        html_content = cache_file.read_text(encoding="utf-8")

    img_dir = IMG_DIR / "2021-gamefreak-crosstalk-planner"
    img_dir.mkdir(parents=True, exist_ok=True)

    # Download key images
    images_to_fetch = [
        ("mv.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/planner/mv.jpg"),
        ("member-kf.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/planner/member-kf.jpg"),
        ("member-ht.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/planner/member-ht.jpg"),
        ("img-01.jpg", "https://www.gamefreak.co.jp/assets/recruit/img/crosstalk/planner/img-01.jpg")
    ]
    for fname, img_url in images_to_fetch:
        download_image(img_url, img_dir / fname)

    # Structured items
    items = []
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/mv.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/mv.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "まず、私たちを驚かせてほしい。周りを振り回してくれる人、募集。",
        "translation": "首先，请让我们大吃一惊吧——寻找能够颠覆规则、引领周围人的企划者。",
        "speaker": None
    })

    # Members introduction
    items.append({
        "type": "heading",
        "original": "登壇者プロフィール（受访嘉宾档案）",
        "translation": "登场成员档案",
        "speaker": None
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/member-kf.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/member-kf.jpg",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "original": "K.F.：プランナーとしてソーシャルゲーム開発会社から、ゲームフリークに転職。開発一部のディレクターと、開発二部で『Pokémon HOME』のディレクターを兼任。",
        "translation": "K.F.：作为策划从社交游戏开发公司跳槽加入 GAME FREAK。现兼任开发一部总监以及开发二部《Pokémon HOME》的总监。",
        "speaker": "档案"
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/member-ht.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/member-ht.jpg",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "original": "H.T.：ゲームプログラマを経て、プランナーとしてゲームフリークに入社。開発二部で『ポケットモンスター ソード・シールド エキスパンションパス』のディレクターを務めた。",
        "translation": "H.T.：经历游戏程序员岗位后，作为策划加入 GAME FREAK。在开发二部担任《宝可梦 剑／盾 扩展票》的总监。",
        "speaker": "档案"
    })

    # Section 1
    items.append({
        "type": "heading",
        "original": "とにかく、キャラが濃い！ゲーム好きでタフ。個が立ったチームです。",
        "translation": "总之，性格极度鲜明！热爱游戏且抗压坚韧。这是一个个性极其突出的团队。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "ゲームフリークのプランナーは、純粋に「とにかく面白いものを作ってやる！」と考えている人が多いですよね。ディレクターやプロデューサーの意向を踏まえながらも、そこに自分の色をどう混ぜていくかということに情熱を注いでいる人が集まっています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "企画を考えるときに、プログラムやグラフィックも含めたゲームとしての仕上がりまで考えることができる人が活躍していますね。ただ企画を考えるだけでは、ゲームフリークでは通用しません。「どう実装するか」「どう見せるか」まで踏み込んで提案できる強さが必要です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "「1年目だから下積み」という文化もないですね。新人でも、自分の担当企画を大なり小なり持っていますし、自分から発案してもらうこともあります。入社後いきなり大きなパートを任されることもあるので、受け身ではなく自発的に動ける人にとっては非常に刺激的な環境だと思います。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "『ポケットモンスター』シリーズは世界的なタイトルですので、勿論世界に通用するものを考えなければならない。でも世界を考えるよりもまずは、自分が本当に面白いと思えるものに徹底的にこだわること。「自分が最初のプレイヤー」として妥協しない姿勢が大切です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "プランナーによって「面白い」という感覚は違うので、ディレクターの意図に沿いつつその人らしさを出せた方がより尖ったものができる。歴代の『ポケモン』シリーズが毎回新しい魅力を放っているのも、そうした個々のプランナーのこだわりが随所に散りばめられているからだと思います。",
        "translation": ""
    })

    # Section 2
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/img-01.jpg",
        "translation": "/assets/img/interviews/2021-gamefreak-crosstalk-planner/img-01.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "開発環境も、勤務体系も。クオリティが上がるなら、何でも取り入れる文化。",
        "translation": "无论是开发环境还是工作体制：只要能够提升品质，就毫无保留地全面吸纳。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "開発環境の特徴としては、研究開発部が作った『ポケモン』シリーズタイトル開発に特化した専用の自社エンジンとフレームワークを持っています。一方で、企画の検証段階ではUnreal EngineやUnityなどを柔軟に使うこともありますし、目的に応じて最適なツールを自由に選択できます。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "他職種との連携もかなり密にやっています。それぞれのメンバーに直接伝えて実装していくのが、ゲームフリークの特徴。誰かを介さないといけないような縦割り組織ではなく、プログラマやデザイナーの席に行って「これ作ってみたいんだけど、どうかな？」と直接相談できるフラットさがあります。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "「こうすれば効率が良くなる」というものがあれば、分け隔てなく取り入れる文化がありますよね。ツールも何でも使いますし、気になるものがあればどんどん試してみる。常に制作環境をアップデートしていこうという意識が社内全体に浸透しています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "勤務体系も、状況に合わせて最も生産性の高いものに変えていっていますね。昨今の情勢に合わせて即座に在宅勤務環境が整えられました。今は在宅と出社を組み合わせたハイブリッドワークが定着していて、それぞれのライフスタイルに合わせた柔軟な働き方ができています。",
        "translation": ""
    })

    # Section 3
    items.append({
        "type": "heading",
        "original": "自分を信じ、人の心を動かせる人と理想のチームをつくりたい。",
        "translation": "希望能与坚信自己、能够打动人心的人，一同构筑理想的团队。",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "理想のチームのかたちはこれから見定めていくところですが、個々人が面白いと思うことをきちんと言えるチームでありたいですね。そのためには、自分自身の「好き」や「面白い」に自信を持っていることが不可欠です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "「うるさいよ！」と言われるくらいでちょうどいいですね（笑）。課題の解決策や新しい遊びの企画等において、こういうアプローチをしてくれる人がいるとチームが活性化します。既存の枠組みを疑い、新しい風を吹き込んでくれる人を求めています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "その上で、周りを巻き込んでいける人がいいですね。自分の思想で巻き込んでいくのもいいし、作ったものを見せまくって巻き込んでいってもいい。「これを形にしたいんだ」という熱量でプログラマやデザイナーを動かせるプランナーが、ゲームフリークでは一番輝きます。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "私は、人の心を動かせる人と働きたいです。人の心を動かせない人では、ユーザーの心も動かせませんから。そして、芯がある人。「何となく会社に来て言われたことをこなす」のではなく、「自分はこれを作りたいんだ」という意志を強く持っている人に来てほしいですね。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "K.F.",
        "original": "自ら「これをやりたい」と意思を表明したら、やらせてもらえる会社ですよね。開発一部は「このプロジェクトをやりたい」と手を挙げるところから始まりますし、チャンスはいくらでも転がっています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "H.T.",
        "original": "「『ポケモン』シリーズとはこういうものだ」と思い込まずに、「もっと面白くするために、こうしたい！」と言ってほしい。単なるファンではなく、クリエイターとして宝可梦の未来を一緒に切り拓いていける仲間を待っています。",
        "translation": ""
    })

    # Translation
    items = translate_items_batch(
        items,
        glossary,
        "GAME FREAK 官方招聘系列·企划座谈会。受访者为《Pokémon HOME》总监 K.F. 与《宝可梦 剑／盾 扩展票》总监 H.T.。重点探讨企划团队极具个性的团队氛围、自研专用引擎与自研框架、新人从第一年起主导核心功能、以及敢于颠覆系列常识的热情。"
    )

    # Post frontmatter
    fm = {
        "layout": "parallel-translation",
        "title": "GAME FREAK 官方对谈 企划篇：首先，请让我们大吃一惊吧——寻找能够颠覆规则的企划者（K.F. × H.T.）",
        "date": "2021-12-27 12:00:00 +0900",
        "author": "GAME FREAK 招聘团队",
        "categories": ["interviews"],
        "tags": ["GAME FREAK", "企划", "宝可梦 剑·盾", "Pokémon HOME", "招聘访谈", "开发体制"],
        "era_skin": "2019",
        "source": {
            "title": "プランナー対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク",
            "url": "https://www.gamefreak.co.jp/recruit/crosstalk-planner/",
            "source_type": "official_recruit"
        },
        "interviewee": "K.F., H.T.",
        "parallel_items": items
    }

    out_file = POSTS_DIR / "2021-12-27-interview-gamefreak-crosstalk-planner.md"
    body = "\n\n> 本篇访谈译自 GAME FREAK 官方招聘网站“Cross Talk 社员对谈”企划，两位年轻一代的核心总监深入揭示了 GAME FREAK 企划团队“从不让新人熬资历、靠热量与作品引领全员”的独特创作氛围与自研引擎生态。\n"
    yaml_text = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_text}---\n{body}", encoding="utf-8")
    print(f"Saved: {out_file.name} (Total items: {len(items)})")


# ==============================================================================
# 3. PKMN-1033: 宝可梦公司 (TPC) 官方新人篇
# ==============================================================================
def curate_pkmn_1033(glossary: list[dict]):
    print("\n========================================================")
    print("Curating PKMN-1033: 宝可梦公司 (TPC) 官方专访 新人篇")
    print("========================================================")
    url = "https://recruit.pokemon.co.jp/saiyo/interview/newgeneration.html"
    cache_file = CACHE_DIR / "pkmn_1033_raw.html"
    if not cache_file.exists():
        req = urllib.request.Request(url, headers=HEADERS)
        html_content = urllib.request.urlopen(req).read().decode("utf-8")
        cache_file.write_text(html_content, encoding="utf-8")
    else:
        html_content = cache_file.read_text(encoding="utf-8")

    img_dir = IMG_DIR / "2022-tpc-recruit-new-generation"
    img_dir.mkdir(parents=True, exist_ok=True)

    # Download key images
    images_to_fetch = [
        ("newgeneration_img.jpg", "https://recruit.pokemon.co.jp/saiyo/interview/img/newgeneration/newgeneration_img.jpg"),
        ("answer_img.jpg", "https://recruit.pokemon.co.jp/saiyo/interview/img/newgeneration/answer_img.jpg"),
        ("answer_img2.jpg", "https://recruit.pokemon.co.jp/saiyo/interview/img/newgeneration/answer_img2.jpg"),
        ("answer_img3.jpg", "https://recruit.pokemon.co.jp/saiyo/interview/img/newgeneration/answer_img3.jpg"),
        ("answer_img4.jpg", "https://recruit.pokemon.co.jp/saiyo/interview/img/newgeneration/answer_img4.jpg")
    ]
    for fname, img_url in images_to_fetch:
        download_image(img_url, img_dir / fname)

    # Structured items
    items = []
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2022-tpc-recruit-new-generation/newgeneration_img.jpg",
        "translation": "/assets/img/interviews/2022-tpc-recruit-new-generation/newgeneration_img.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "Special Interview 「最初の１年を振り返る」",
        "translation": "特别专访：回顾入职第一年——在数千亿级IP舞台上找寻角色定位与蜕变",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "original": "株式会社ポケモンに入社して1年が経過した新卒社員たちが集結。なぜポケモンを選んだのか、どんな雰囲気の会社なのか、そして1年間でどのような成長を遂げたのかを語り合います。",
        "translation": "入职株式会社宝可梦（The Pokémon Company）满一年的应届毕业生齐聚一堂。大家共同探讨：为何选择加入宝可梦？这究竟是一家拥有怎样企业氛围的公司？以及在这一年间，每个人在岗位上收获了怎样的蜕变与成长。",
        "speaker": "TPC 招聘专栏"
    })

    # Question 1
    items.append({
        "type": "heading",
        "original": "Q1. 入社理由：なぜ株式会社ポケモンを選んだのですか？",
        "translation": "Q1. 入职理由：当初为什么选择加入株式会社宝可梦？",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "伊藤",
        "original": "一番の理由は、小さいころからポケモンが大好きだったからです。しかも、株式会社ポケモンはさまざまな事業や活動を行っていて、可能性を狭めずにいろいろなことをやってみたいと思ったのが決め手でした。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "天天",
        "original": "私もポケモンが大好きで、ポケモンに関わる仕事をすることが昔からの夢でした。一度きりの人生だから、たくさんのことを経験したい、チャレンジしたい、という想いで入社を決めました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "查查",
        "original": "2人と似たところもありつつ、私の出身国であるタイは、日米欧と比較するとまだまだ伸びしろがあるところが面白いです。自分の学んできたことや言語力、感覚をフルに使って、まだ宝可梦の魅力が十分に届いていない地域に広げていきたいと思いました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "余",
        "original": "私はアニメを見始めてポケモンを知り、次第にゲームにハマっていきました。1人で遊ぶだけではなく、人とつながって世界や体験が豊かになったことに感動したんです。この感動を、今度は自分が届ける側に立ちたいと思いました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "石黑",
        "original": "こういう感じで、いろんなバックグラウンドを持った人たちの共通の話題になって盛り上がっていることが、ポケモンの良さなんだと思います。家族でイギリスに住んでいた時期にも、現地の学校でポケモンを通じて友達ができた経験があり、その強さに惹かれました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "星",
        "original": "私も、ポケモンを通じて出会った人たちとのつながりで、人生が変わったというくらいの経験をしていますので、人との交流を生み出すことの可能性に強く惹かれています。そういった体験を自分たちの手で生み出していきたいと考えました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "山口",
        "original": "私は、面接の中で社員の方から伺った、「私たちはポケモンのことだけを手掛ける会社だから、ポケモンが永く愛され続けるように日々努力する。それができなくなったら、会社が存在する意味がなくなってしまう」という言葉が深く刺さりました。その覚悟に共感したのが一番の理由です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "赵",
        "original": "その考え方は私も好きです。今ある人気や影響力を利用して短期的な利益をあげることではなくて、時代の奔流に飲み込まれない強さや長期的に持続する価値を生み出すことを目指している。そこに魅力を感じました。",
        "translation": ""
    })

    # Question 2
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img.jpg",
        "translation": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "Q2. 社風・人：株式会社ポケモンは、どんな会社・職場ですか？",
        "translation": "Q2. 企业风气与团队：株式会社宝可梦是怎样的一家公司与职场？",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "山口",
        "original": "想像以上に幅広い経歴を持った人たちが働いていて、それぞれの多様な経験や個性を仕事に生かしている印象です。新しいテーマや課題に取り組む上でも、それぞれの得意分野を持ち寄って解決していく風土があります。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "赵",
        "original": "助け合うことが根付いているというか、より良くするために力を出し合う、結集するということが自然になっていますね。変化や競争が激しい業界ですので、入社前は同僚の間でギスギスすることもあるのかなと少し心配でしたが、まったくそんなことはありませんでした。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "伊藤",
        "original": "気さくな方も多くて、話しかけやすい雰囲気です。入社してすぐの時期は特に、質問をさせていただく機会が多いですが、分かりにくい質問も受け止め、丁寧に答えてくださる先輩ばかりで安心しました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "余",
        "original": "オフィスもオープンで、他の部署の方とも話しやすいです。それぞれの事業やプロジェクトが連動して大きな波をつくっていく、ポケモンらしい環境だと思いました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "石黑",
        "original": "私も、誠実で優しい方が多い印象を持っています。ポケモンと向き合うために求められる誠実さや責任感が、一緒に働く仲間への向き合い方につながっているような気がしています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "星",
        "original": "自由度が高く発言できる環境について、自由だから楽というわけではないんだな、と思ったことがあります。年代や経験年数によらずに、ポケモンのために何がベストかを全員が真真剣に考えているからこそ、意見を言う責任もあると感じています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "查查",
        "original": "仕事が好きな人が多い会社だな、と思いますね。もちろん大変なときもありますけど、全体的に賑やかで、生き生きとしていますよね。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "石黑",
        "original": "自分たちが関わった企画が実現して、世界中たくさんの人たちに喜んでもらっている、という実感があるからだと思います。お祭りの準備期間と当日が次々来るみたいな感じですよね。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "天天",
        "original": "わかります（笑）。誰かに楽しんでもらいたいと思って準備することって、大変だったとしても、準備中からワクワクするじゃないですか。そういうことですよね。",
        "translation": ""
    })

    # Question 3
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img2.jpg",
        "translation": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img2.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "Q3. 1年間の成長：この1年間で、どんな成長を実感しましたか？",
        "translation": "Q3. 一年间的成长：在这入职的第一年中，切实感受到了怎样的蜕变？",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "查查",
        "original": "短期間で日本語のスキルが上がりました。わかりやすく表現すること、魅力を最大限に伝える方法について考えること、調整やディレクションの業務を行うことで鍛えられました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "余",
        "original": "私も、日本語で自分の意見を語る、提案するということができるようになって、自ら発信する機会を増やすことができたと思います。学業では困ることがないレベルの語学力があっても、ビジネスの場ではまた違った難しさがありますから、実践の中で大きく伸びたと実感しています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "天天",
        "original": "私もコミュニケーション面で自分の成長を感じました。もともと自分は人とのコミュニケーションがうまいほうではないと思っていましたが、さまざまな部署や社外のパートナーと連携する中で、相手の立場に立って伝える力が身につきました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "星",
        "original": "さまざまな人たちと話す中で、自分の中での意見の軸を強く意識するようになったと思います。面白いかどうかって、主観的になりがちですよね。チームとして合意形成を図るために、なぜそれが良いのかを客観的に論理立てて説明する力が鍛えられました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "伊藤",
        "original": "私はポケモンセンター・ポケモンストアで販売する商品の企画を行う業務を担当しているので、街にあふれる商品一つ一つに込められた企画者の意図に想いを巡らせるようになりました。日常のあらゆる体験が企画のインスピレーションになっています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "山口",
        "original": "物事の見方が変わったのは、私も似ています。今までは、ポケモンを見ていても、単純に「かわいいな」「かっこいいな」という感想だったのが、「この見せ方なら、ポケモンの生態や個性がより際立つのではないか」と多角的に捉えるようになりました。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "赵",
        "original": "社内でもよく言われている、「自分たちの企画やプロモーションで、ポケモンに新たなパワーをもたらすことができるか」という観点ですね。私は企画やプロダクトの監修を中心に行っていますが、ただチェックするだけでなく、どうすればさらに魅力が高まるかを提案できるようになってきました。",
        "translation": ""
    })

    # Question 4
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img3.jpg",
        "translation": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img3.jpg",
        "speaker": None
    })
    items.append({
        "type": "heading",
        "original": "Q4. メッセージ：求職者や後輩たちへのメッセージをお願いします",
        "translation": "Q4. 寄语：对今后有意加入宝可梦公司的求职者与后辈们有什么想说的？",
        "speaker": None
    })
    items.append({
        "type": "paragraph",
        "speaker": "伊藤",
        "original": "1年目から貴重な経験ができ、大きなやりがいを感じました。やりがい・やりごたえを望む方に、お勧めの環境です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "山口",
        "original": "オンライン、オフライン問わずさまざまな形で、ファンやユーザーの方の熱量や喜びを感じることができる仕事だと思います。自分やほかのたくさんの人が好きなポケモンを、自分の手でさらに盛り上げていきたい方をお待ちしています。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "石黑",
        "original": "自分が担当する仕事の中で、自分がまだ訪れたことのないインドの都市の方から「ポケモンだいすきだよ‼」というコメントをいただいたとき、何か元気づけられたような気がしました。国境を越えて人々と通じ合える素晴らしい仕事です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "天天",
        "original": "博士号を持っている人の強みを事業に活かせている、珍しい会社だと思います。博士だけれど研究活動以外のことにも興味がある方、ポケモンが大好きな方に、お勧めします。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "余",
        "original": "ポケモンのことを大事に考え、長期的な視点を大切に努力してきた強みのある会社だと感じています。そこに共感できる人は、きっと相性がいいと思います。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "星",
        "original": "自分が考えたアイディアが採用されて、実現されるときの嬉しさ、そしてそれを世界中のユーザーに遊んでもらえるドキドキ感が、存分に味わえる仕事です。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "查查",
        "original": "それぞれ大きな仕事を担当している中でも、いつでも話したり聞けたりする雰囲気を作ってくれる先輩や上司は、本当にすごいと思います。早く一人前になって、会社と宝可梦に貢献していきたいです。",
        "translation": ""
    })
    items.append({
        "type": "paragraph",
        "speaker": "赵",
        "original": "面接に参加したとき、形式的なものではなく、研究テーマや得意なこと、好きなことについてたくさん質問をもらって、「この会社は、一人ひとりをしっかり見てくれる」と実感しました。自分らしさを発揮したい方には最高の環境です。",
        "translation": ""
    })
    items.append({
        "type": "image",
        "original": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img4.jpg",
        "translation": "/assets/img/interviews/2022-tpc-recruit-new-generation/answer_img4.jpg",
        "speaker": None
    })

    # Translation
    items = translate_items_batch(
        items,
        glossary,
        "株式会社宝可梦（The Pokémon Company）官方招聘系列·新人座谈会专访。受访嘉宾为入职第一年的应届毕业生群体（伊藤、天天、查查、余、石黑、星、山口、赵）。涵盖跨国多元文化背景、企业哲学‘我们是唯一只做宝可梦的公司，如果宝可梦不再被喜爱，公司就失去存在意义’、首年业务成长、以及面向全球粉丝的责任心。"
    )

    # Post frontmatter
    fm = {
        "layout": "parallel-translation",
        "title": "宝可梦公司官方专访 新人篇：回顾这一年——在数千亿IP舞台上找寻角色定位与蜕变",
        "date": "2022-03-01 12:00:00 +0900",
        "author": "The Pokémon Company 招聘专栏",
        "categories": ["interviews"],
        "tags": ["宝可梦公司", "TPC", "招聘访谈", "企业文化", "品牌运营", "全球化"],
        "era_skin": "2019",
        "source": {
            "title": "Special Interview 「最初の１年を振り返る」｜株式会社ポケモン採用情報",
            "url": "https://recruit.pokemon.co.jp/saiyo/interview/newgeneration.html",
            "source_type": "official_recruit"
        },
        "interviewee": "TPC 新入职员工座谈会（伊藤、天天、查查、余、石黑、星、山口、赵）",
        "parallel_items": items
    }

    out_file = POSTS_DIR / "2022-03-01-interview-tpc-recruit-new-generation.md"
    body = "\n\n> 本篇访谈译自株式会社宝可梦（The Pokémon Company）官方招聘网站特别专栏。来自不同国家、拥有多元学术背景的新卒一代在此畅谈初入宝可梦公司的真实体验、业务监修的心得以及企业长青的核心哲学。\n"
    yaml_text = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    out_file.write_text(f"---\n{yaml_text}---\n{body}", encoding="utf-8")
    print(f"Saved: {out_file.name} (Total items: {len(items)})")


def update_catalog():
    print("\nUpdating data/pokemon_1000_interviews.json...")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    updates = {
        "PKMN-1004": {
            "status": "imported",
            "post_file": "2021-12-27-interview-gamefreak-crosstalk-game-programmer.md",
            "era": "2019"
        },
        "PKMN-1006": {
            "status": "imported",
            "post_file": "2021-12-27-interview-gamefreak-crosstalk-planner.md",
            "era": "2019"
        },
        "PKMN-1033": {
            "status": "imported",
            "post_file": "2022-03-01-interview-tpc-recruit-new-generation.md",
            "era": "2019"
        }
    }
    updated_count = 0
    for entry in catalog:
        e_id = entry.get("id")
        if e_id in updates:
            entry["status"] = updates[e_id]["status"]
            entry["post_file"] = updates[e_id]["post_file"]
            entry["era"] = updates[e_id]["era"]
            updated_count += 1
            print(f"  Updated {e_id} -> status: {entry['status']}, post_file: {entry['post_file']}")

    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Catalog updated successfully! {updated_count} entries updated.")


def main():
    glossary = load_glossary()
    print(f"Loaded glossary: {len(glossary)} entries.")

    curate_pkmn_1004(glossary)
    curate_pkmn_1006(glossary)
    curate_pkmn_1033(glossary)

    update_catalog()
    print("\nBatch 16 curation fully complete!")


if __name__ == "__main__":
    main()
