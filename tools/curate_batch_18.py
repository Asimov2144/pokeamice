"""Curate Batch 18:
GAME FREAK 官方创作者档案·设计师特写四部曲 (2021)
- PKMN-1010: K.N. (3D场景模型设计师 / 场景设计组长)
- PKMN-1011: M.I. (动作与UI设计师 / 游戏策划)
- PKMN-1012: E.K. (UI设计团队组长)
- PKMN-1013: H.T. (场景概念设计 / GEAR PROJECT 原创IP艺术总监)
"""

import html
import json
import os
import re
import ssl
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
IMG_BASE_DIR = ROOT / "assets" / "img" / "interviews"
CATALOG_PATH = ROOT / "data" / "pokemon_1000_interviews.json"
GLOSSARY_PATH = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")
CACHE_DIR = ROOT / "tools" / "cache_batch_18"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


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
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
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
    term_constraints = (
        "\n".join([f"- {k} => {v}" for k, v in terms])
        if terms
        else "无特殊官方术语锁定。"
    )

    BATCH_SIZE = 10
    for b_idx in range(0, len(to_trans), BATCH_SIZE):
        chunk = to_trans[b_idx : b_idx + BATCH_SIZE]
        payload_items = [
            {"id": idx, "speaker": spk, "text": text} for idx, text, spk in chunk
        ]

        prompt = f"""你是宝可梦官方档案馆的资深中日翻译专家。请将以下来自 GAME FREAK 官方一线设计师访谈的日文内容翻译为通顺、优美、忠实于原意、符合中国大陆宝可梦官方简体中文语境的译文。
背景信息：
{context_desc}

【官方术语硬性约束（必须严格遵守）】：
{term_constraints}

【翻译要求】：
1. 语言风格专业自然，符合主机游戏研发（3D场景建模、地形动线、UI/UX无障碍交互、动画动作与关键帧、原创IP孵化GEAR PROJECT机制、自研引擎规范等）语境。
2. 保持受访者自然诚恳的职场第一人称叙述口吻，行文凝练优美，保留生动的创作细节。
3. 请以 JSON 格式输出：
{{
  "translations": [
    {{"id": 0, "translation": "译文内容"}},
    ...
  ]
}}
"""
        messages = [
            {
                "role": "system",
                "content": "You are a professional Japanese to Simplified Chinese translator specializing in Pokémon official media and video game development.",
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n待翻译原文：\n{json.dumps(payload_items, ensure_ascii=False, indent=2)}",
            },
        ]

        print(
            f"  Translating batch {b_idx//BATCH_SIZE + 1}/{(len(to_trans)-1)//BATCH_SIZE + 1} ({len(chunk)} items)..."
        )
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
        cache_json.write_text(
            json.dumps(cached_map, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return items


def update_catalog(entry_id: str, post_filename: str):
    if not CATALOG_PATH.exists():
        print(f"Warning: catalog file {CATALOG_PATH} not found.")
        return

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    found = False
    slug = post_filename.replace(".md", "")
    # Remove date prefix for slug if standard Jekyll format
    slug_clean = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)

    for item in data:
        if item.get("id") == entry_id:
            item["status"] = "imported"
            item["imported_post_slug"] = slug_clean
            item["imported_post_path"] = f"_posts/{post_filename}"
            found = True
            break

    if found:
        CATALOG_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  Updated catalog entry {entry_id} -> {slug_clean}")
    else:
        print(f"  Warning: catalog entry {entry_id} not found.")


DESIGNERS_DATA = [
    {
        "id": "PKMN-1010",
        "short_id": "kn",
        "name": "K.N.",
        "slug": "2021-12-27-interview-gamefreak-recruit-designer-kn.md",
        "role_zh": "3D场景模型设计师 / 场景设计组长（Field Leader）",
        "title_zh": "GAME FREAK 官方3D场景设计师特写 K.N.：善于倾听每一份声音，方能打磨出深获喜爱的游戏世界",
        "title_ja": "みんなの声を活かすから、みんなに愛されるゲームになる。｜デザイナー社員紹介 K.N.",
        "slogan_ja": "みんなの声を活かすから、みんなに愛されるゲームになる。",
        "slogan_zh": "正是因为善于吸纳大家的建言，才能打磨出被所有人深爱的游戏。",
        "profile_ja": "千葉工業大学大学院修了。学生時代から趣味を兼ねて絵の仕事を受けていた。 メーカーの内定を辞退し、小さい頃から好きだった『ポケモン』の世界でデザインの仕事がしたいとゲームフリークへ。",
        "profile_zh": "千叶工业大学研究生院毕业（工学研究科机器人工程学专攻）。学生时代起便兼职承接商业插画与绘图委托。后毅然辞退大型制造企业的内定录用，怀揣着“渴望在从小就深爱的宝可梦世界中施展设计抱负”的坚定初心加入 GAME FREAK。在《宝可梦 Let's Go! 皮卡丘／Let's Go! 伊布》开发中首次担纲场景设计组长（Field Leader）。",
        "summary": "GAME FREAK 官方一线设计师深度特写：千叶工业大学工学研究生毕业的 K.N.，分享其从机器人工程跨界游戏美术、因对宝可梦世界的热爱辞退制造企业内定加入 GAME FREAK 的心路历程；详解在《宝可梦 Let's Go! 皮卡丘／Let's Go! 伊布》中担纲场景模型组长时，如何从零构筑3D关卡地形、以倾听姿态凝聚团队智慧的领导风格；以及在任天堂 Switch 高清世代下，如何通过严谨的逻辑推敲精准提炼并传承“宝可梦独有韵味”的创作哲学。",
        "works": ["宝可梦 Let's Go! 皮卡丘／Let's Go! 伊布", "宝可梦 剑／盾"],
        "organizations": ["株式会社ゲームフリーク", "千葉工業大学"],
        "tags": ["GAME FREAK", "K.N.", "3D场景建模", "关卡设计", "Let's Go! 皮卡丘／伊布", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网设计师特写，受访者为3D场景模型设计师兼场景组长K.N.，工科研究生背景，曾担任《Let's Go! 皮卡丘／伊布》场景设计组长，探讨从零搭建3D场景、微差把控、Switch时代的技术演进与‘宝可梦独有韵味’的逻辑传承。",
        "captions": [
            "GAME FREAK 3D场景模型设计师 K.N. 主视觉：善于倾听大家的建言，方能打磨出深获喜爱的游戏",
            "K.N. 在多屏工作站前雕琢3D场景几何体与环境光影细节",
            "与场景及程序团队针对关卡地形动线与微观细节展开严谨推敲",
            "探求在现代高清硬件上如何精准承袭与表达“宝可梦独有韵味”的设计规范",
        ],
    },
    {
        "id": "PKMN-1011",
        "short_id": "mi",
        "name": "M.I.",
        "slug": "2021-12-27-interview-gamefreak-recruit-designer-mi.md",
        "role_zh": "动作与UI设计师 / 游戏策划（Motion & UI Designer / Planner）",
        "title_zh": "GAME FREAK 官方动作与UI设计师特写 M.I.：不局限于美术图形，而要全盘融入游戏构筑的无限可能",
        "title_ja": "入社したのは、グラフィックだけでなく、ゲームづくりを丸ごとやりたかったから。｜デザイナー社員紹介 M.I.",
        "slogan_ja": "入社したのは、グラフィックだけでなく、ゲームづくりを丸ごとやりたかったから。",
        "slogan_zh": "之所以选择入职，是因为我不仅想做美术图形，更想全盘参与游戏制作。",
        "profile_ja": "4年制の専門学校で、CGやアニメーション、特にモーションを専攻。 ゲーム制作のあらゆる面に関わることができるゲームフリークに魅力を感じて入社。",
        "profile_zh": "四年制专门学校毕业，主修 3D CG 与动画设计，尤以角色与物理动作（Motion）为专长。被 GAME FREAK“不仅能钻研美术图形，更能全方位介入策划与游戏构筑全流程”的独特创作机制所吸引而入社。入社第一年即以美术身份承担游戏玩法与支线事件策划。",
        "summary": "GAME FREAK 官方一线设计师深度特写：四年制专门学校主修 3D 动画与动作设计的 M.I.，回顾自己被 GAME FREAK“全员皆可全盘参与游戏研发”的扁平创作机制所吸引的求职初心；讲述入职培训时两人组队独立开发迷你游戏、入社第一年便跨界承担剧情与动作策划的难忘体验；以及在崇尚“产出严谨、沟通坦率”的团队氛围中，与一群永葆童心的游戏匠人共同打造梦想作品的真实感受。",
        "works": ["宝可梦 剑／盾"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "M.I.", "动作设计", "UI设计", "游戏策划", "扁平文化", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网设计师特写，受访者为动作与UI设计师M.I.，探讨为何选择Game Freak而非纯外包或传统流水线公司、入职第一年即参与玩法企划的扁平社风，以及保持爱玩童心的创作理念。",
        "captions": [
            "GAME FREAK 动作与UI设计师 M.I. 主视觉：不局限于美术图形，而要全盘融入游戏构筑的无限可能",
            "M.I. 在手绘数位屏上精细调校角色骨骼动态与关键帧动作曲线",
            "跨越工种壁垒，与策划及程序员在开放办公区热烈推敲趣味交互机制",
            "永葆少年般的好奇童心，在纯粹的游戏热爱中迸发蓬勃灵感",
        ],
    },
    {
        "id": "PKMN-1012",
        "short_id": "ek",
        "name": "E.K.",
        "slug": "2021-12-27-interview-gamefreak-recruit-designer-ek.md",
        "role_zh": "UI/UX设计团队组长（UI Design Team Leader）",
        "title_zh": "GAME FREAK 官方UI设计组长特写 E.K.：自由建言与持续进修，打造全年龄友好的无障碍UI体验",
        "title_ja": "好きに意見が言える。好きに学べる。いちばん楽しい職場です。｜デザイナー社員紹介 E.K.",
        "slogan_ja": "好きに意見が言える。好きに学べる。いちばん楽しい職場です。",
        "slogan_zh": "畅所欲言发表意见，随心所欲钻研学习。这是最让人开心的职场。",
        "profile_ja": "美大卒業後、大手のコンシューマーゲーム開発会社2社を経て、ゲームフリークへ。 UIデザインチームのリーダーを務める。",
        "profile_zh": "美术大学毕业后，历经两家大型家用主机游戏开发企业的千锤百炼，随后加入 GAME FREAK。现任 UI 设计团队组长（UI Design Team Leader）。全面主导《宝可梦 太阳／月亮》等作品的界面系统设计，并推动公司设立针对员工的外部专业教育进修支持制度。",
        "summary": "GAME FREAK 官方一线设计师深度特写：历经两家大型游戏企业历练后加入 GAME FREAK 的 UI 设计团队负责人 E.K.，分享在开放坦诚的团队氛围中打破职能界限协作的愉悦体验；深入剖析在《宝可梦 太阳／月亮》与《剑／盾》中，面对系统日益庞大与信息量激增的挑战，如何始终坚持“让从初学者到资深玩家都能无障碍轻松上手”的易用性设计哲学；以及在公司支持下每周公费进修前沿 3D CG 课程、探索 3D 动态 UI 革命的进取历程。",
        "works": ["宝可梦 太阳／月亮", "宝可梦 剑／盾"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "E.K.", "UI设计", "用户体验", "无障碍设计", "教育进修", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网设计师特写，受访者为UI设计组长E.K.，拥有两家大厂从业经历，分享跨工种沟通协作、全年龄向UI界面信息减负与无障碍易用性设计原则，以及公司支持员工每周六进修3DCG学校的学习制度。",
        "captions": [
            "GAME FREAK UI设计组长 E.K. 主视觉：畅所欲言与持续进修，打造最让人开心的职场",
            "E.K. 在双屏工作站前构建清晰直观的游戏操作界面流与信息层级",
            "面向全年龄与全球玩家，深度考量无障碍认知与操作舒适度的界面推敲",
            "利用公司教育支持制度进修前沿 3D CG 渲染与动态三维 UI 融合技巧",
        ],
    },
    {
        "id": "PKMN-1013",
        "short_id": "ht",
        "name": "H.T.",
        "slug": "2021-12-27-interview-gamefreak-recruit-designer-ht.md",
        "role_zh": "场景概念设计 / GEAR PROJECT 原创IP艺术总监（Art Director）",
        "title_zh": "GAME FREAK 官方原创IP艺术总监特写 H.T.：在Gear Project中让原创构想破土成蝶",
        "title_ja": "ギアプロジェクトなら、自分のアイディアをゲームにできる。だから、面白い。｜デザイナー社員紹介 H.T.",
        "slogan_ja": "ギアプロジェクトなら、自分のアイディアをゲームにできる。だから、面白い。",
        "slogan_zh": "在Gear Project中，能把自己的构想亲手做成游戏。正因如此，才妙趣横生。",
        "profile_ja": "美術大学卒業後、コンシューマーゲームの開発会社に入社。背景を担当したのち、ゲームフリークへ。 ギアプロジェクトで『リトルタウンヒーロー』のアートディレクターを務める。",
        "profile_zh": "美术大学毕业后入职家用主机游戏开发企业担任场景背景美术，后加入 GAME FREAK。深受公司原创孵化机制“GEAR PROJECT”感召，在全原创IP单机RPG《小镇英雄》（Little Town Hero）中担纲艺术总监（Art Director）。主张游戏从业者应超越“设计师”局限，具备独立游戏制作人思维。",
        "summary": "GAME FREAK 官方一线设计师深度特写：曾在大厂从事背景美术、因向往“GEAR PROJECT”原创机制而加入 GAME FREAK 的 H.T.，分享从主系列关卡设计中感受到的“草丛分布与遇敌率极致打磨”的工匠精神；回顾在全原创单机 RPG《小镇英雄》中全面担纲艺术总监、从草图构想到终版交付全流程把控的敏捷开发历程；并真诚呼吁比起单纯想当“美术设计师”的人，更期待渴望成为“全面游戏创作者”的新鲜血液加入团队。",
        "works": ["小镇英雄", "宝可梦 剑／盾"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "H.T.", "GEAR PROJECT", "小镇英雄", "艺术总监", "场景设计", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网设计师特写，受访者为场景概念设计师兼原创单机作品《小镇英雄》艺术总监H.T.，分享宝可梦关卡设计的极致考究、GEAR PROJECT原创孵化机制的敏捷决策与全流程把控，以及呼唤具备全面游戏制作人思维的创作者加入。",
        "captions": [
            "GAME FREAK 原创IP艺术总监 H.T. 主视觉：在Gear Project中把构想亲手变成游戏",
            "H.T. 在数位板前精心构画童话般温馨细腻的原创城镇概念全貌",
            "在敏捷扁平的 GEAR PROJECT 核心团队中统括美术风格与视觉世界观",
            "打破工种界限，以全能创作者的宏阔视野探索前沿艺术表现",
        ],
    },
]


def curate_designer(item_data: dict, glossary: list[dict]):
    short_id = item_data["short_id"]
    print(f"\n==================================================")
    print(f"Curating {item_data['id']}: {item_data['name']} ({short_id})")
    print(f"==================================================")

    url = f"https://www.gamefreak.co.jp/recruit/interview-gr-{short_id}/"
    raw_html_path = CACHE_DIR / f"interview-gr-{short_id}.html"
    if not raw_html_path.exists():
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html_bytes = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        raw_html_path.write_bytes(html_bytes)
        print(f"  Downloaded HTML ({len(html_bytes)} bytes)")
    else:
        html_bytes = raw_html_path.read_bytes()
        print(f"  Loaded cached HTML ({len(html_bytes)} bytes)")

    soup = BeautifulSoup(html_bytes, "html.parser")
    units = soup.find_all("section", class_=lambda c: c and "contents__unit" in c)
    if len(units) != 3:
        raise ValueError(f"Expected 3 units for {short_id}, found {len(units)}")

    parallel_items = []

    # Item 0: Lead image
    lead_img_path = f"/assets/img/interviews/gamefreak-recruit-{short_id}/mv.jpg"
    parallel_items.append({
        "type": "image",
        "src": lead_img_path,
        "caption": item_data["captions"][0]
    })

    # Item 1: Slogan H2
    parallel_items.append({
        "type": "heading",
        "level": 2,
        "original": item_data["slogan_ja"],
        "translation": item_data["slogan_zh"]
    })

    # Units 1, 2, 3
    for u_idx, u in enumerate(units):
        h_tag = u.find(["h2", "h3"])
        h_text = h_tag.get_text(strip=True) if h_tag else ""
        
        # Heading 3
        parallel_items.append({
            "type": "heading",
            "level": 3,
            "original": h_text,
            "translation": "" # to be translated
        })

        # Unit image
        img_src = f"/assets/img/interviews/gamefreak-recruit-{short_id}/img-0{u_idx+1}.jpg"
        parallel_items.append({
            "type": "image",
            "src": img_src,
            "caption": item_data["captions"][u_idx+1]
        })

        # Paragraphs
        p_tags = [p.get_text(strip=True) for p in u.find_all("p") if p.get_text(strip=True)]
        for p_text in p_tags:
            parallel_items.append({
                "type": "text",
                "speaker": item_data["name"],
                "speaker_orig": item_data["name"],
                "original": p_text,
                "translation": "" # to be translated
            })

    # Translate missing items
    parallel_items = translate_items_batch(
        parallel_items, glossary, item_data["context_desc"], f"designer_{short_id}"
    )

    # Build Markdown post
    frontmatter = {
        "layout": "parallel-translation",
        "title": item_data["title_zh"],
        "title_ja": item_data["title_ja"],
        "date": "2021-12-27 10:00:00 +0900",
        "era": "2021",
        "era_skin": "2019",
        "categories": ["developer-interviews", "gamefreak-recruit"],
        "tags": item_data["tags"],
        "interview_id": item_data["id"],
        "publication": "GAME FREAK 採用情報",
        "original_link": url,
        "author": "GAME FREAK 官方",
        "interviewee": item_data["name"],
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "summary": item_data["summary"],
        "entities": {
            "people": [item_data["name"]],
            "works": item_data["works"],
            "organizations": item_data["organizations"],
        },
        "parallel_items": parallel_items,
        "source": {
            "title": item_data["title_ja"],
            "url": url,
        }
    }

    # Profile card HTML
    profile_html = f"""<div class="interview-profile-card mb-4 p-4 rounded bg-light border">
  <div class="row align-items-center">
    <div class="col-md-4 text-center">
      <img src="{lead_img_path}" alt="{item_data['name']} {item_data['role_zh']}" class="img-fluid rounded shadow-sm" style="max-height: 280px; object-fit: cover;">
    </div>
    <div class="col-md-8">
      <h3 class="fw-bold mb-2">{item_data['name']}</h3>
      <p class="text-muted mb-1"><strong>所属职务：</strong>开发本部 视觉设计部门（{item_data['role_zh']}）</p>
      <p class="mb-0"><strong>主要履历：</strong>{item_data['profile_zh']}</p>
    </div>
  </div>
</div>
"""

    post_content = "---\n" + yaml.dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + profile_html

    out_file = POSTS_DIR / item_data["slug"]
    out_file.write_text(post_content, encoding="utf-8")
    print(f"  Successfully wrote post: {out_file.name}")

    # Update Catalog
    update_catalog(item_data["id"], item_data["slug"])


def main():
    print("Starting Batch 18 Curation...")
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    for d in DESIGNERS_DATA:
        curate_designer(d, glossary)

    print("\nBatch 18 Curation completed successfully!")


if __name__ == "__main__":
    main()
