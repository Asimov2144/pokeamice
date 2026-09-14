"""Curate Batch 19:
GAME FREAK 官方创作者档案·核心程序员特写四部曲 (2021)
- PKMN-1014: T.K. (游戏玩法与动作程序员 / 玩家行为实现主力)
- PKMN-1015: K.O. (系统与底层程序员 / CI与构建系统)
- PKMN-1016: K.M. (研发总监 / 图形与自研引擎专家 / CG技术实验室总监)
- PKMN-1017: H.T. (环境团队组长 / 全云端架构工程师 / R&D兼开发二部)
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
CACHE_DIR = ROOT / "tools" / "cache_batch_19"
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

        prompt = f"""你是宝可梦官方档案馆的资深中日翻译专家与游戏引擎技术架构专家。请将以下来自 GAME FREAK 官方一线核心程序员/技术总监访谈的日文内容翻译为通顺、优美、严谨专业、忠实于原意、符合中国大陆宝可梦官方简体中文语境的译文。
背景信息：
{context_desc}

【官方术语硬性约束（必须严格遵守）】：
{term_constraints}

【翻译要求】：
1. 语言风格兼具主机游戏顶尖软件工程的专业性（如持续集成 CI/CD、自动化构建流水线、着色器 Shader、动作形变 Deform、自研专用引擎架构、全云端原生环境、状态机与玩家物理操控）与行业访谈的流畅感。
2. 保持受访者自然诚恳的职场第一人称叙述口吻，行文凝练生动，准确传达 GAME FREAK “以人为本、解决一切困难、实现极致考究”的极客匠心。
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
                "content": "You are a professional Japanese to Simplified Chinese translator specializing in Pokémon official media, game engine architecture, and software development engineering.",
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


PROGRAMMERS_DATA = [
    {
        "id": "PKMN-1014",
        "short_id": "tk",
        "name": "T.K.",
        "html_slug": "interview-pg-tk",
        "img_remote_dir": "tk2",
        "img_local_dir": "gamefreak-recruit-tk",
        "slug": "2021-12-27-interview-gamefreak-recruit-programmer-tk.md",
        "role_zh": "游戏玩法与动作程序员（Game Programmer / Player Behavior Lead）",
        "title_zh": "GAME FREAK 官方程序员特写 T.K.：如果程序员轻言“不可能”，那么任何天马行空的创意都将化为泡影",
        "title_ja": "プログラマが「無理」と言ったら、どんなアイデアも実現できない。｜プログラマ社員紹介 T.K.",
        "slogan_ja": "プログラマが「無理」と言ったら、どんなアイデアも実現できない。",
        "slogan_zh": "如果程序员轻言“不可能”，那么任何天马行空的创意都将化为泡影。",
        "profile_ja": "専門学校卒業後、『ポケットモンスター ソード・シールド』で「ポケモンキャンプ」のミニゲーム開発を担当。『Pokémon LEGENDS アルセウス』からはプレイヤー挙動実装の主担当となる。",
        "profile_zh": "专门学校毕业后入职 GAME FREAK。在《宝可梦 剑／盾》中负责核心互动玩法“宝可梦露营”的迷你游戏开发。在《宝可梦传说 阿尔宙斯》中担纲主角行为与实时操控逻辑的主力实现负责人。",
        "summary": "GAME FREAK 官方一线程序员深度特写：专门学校毕业即投身主机研发的 T.K.，分享在《宝可梦 剑／盾》中开发“宝可梦露营”迷你游戏、在《宝可梦传说 阿尔宙斯》中担纲主角奔跑、翻滚、潜行与投掷精灵球等全套实时动作交互核心逻辑的心路历程；揭示策划与程序员紧密协同、扁平碰撞的团队文化；并阐述“程序员绝不轻言放弃，要成为用技术攻克一切创意难题的解决者”的工程师信念。",
        "works": ["宝可梦 剑／盾", "宝可梦传说 阿尔宙斯"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "T.K.", "游戏程序员", "宝可梦传说 阿尔宙斯", "剑／盾", "动作系统", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网程序员特写，受访者为游戏程序员T.K.，负责《剑／盾》宝可梦露营迷你游戏，以及《宝可梦传说 阿尔宙斯》主角操作行为主程，探讨引入动作要素、策划与程序紧密合作、解决难题而非单纯照搬需求的极客精神。",
        "captions": [
            "GAME FREAK 游戏程序员 T.K. 主视觉：如果程序员轻言“不可能”，任何创意都将化为泡影",
            "T.K. 在双屏开发环境下编写并单步调试实时玩家物理与状态机逻辑",
            "跨越工种壁垒，与动作设计师及策划在真机上高频迭代手感反馈",
            "秉持“用技术攻克难题而非单纯实现需求”的攻坚工程信条",
        ],
    },
    {
        "id": "PKMN-1015",
        "short_id": "ko",
        "name": "K.O.",
        "html_slug": "interview-pg-ko",
        "img_remote_dir": "ko",
        "img_local_dir": "gamefreak-recruit-ko",
        "slug": "2021-12-27-interview-gamefreak-recruit-programmer-ko.md",
        "role_zh": "系统与底层程序员（System Programmer / CI & Build Engineer）",
        "title_zh": "GAME FREAK 官方系统程序员特写 K.O.：深信自身的持续成长，必然带动 GAME FREAK 整体的飞跃",
        "title_ja": "自分の成長が、ゲームフリークの成長につながると信じて。｜プログラマ社員紹介 K.O.",
        "slogan_ja": "自分の成長が、ゲームフリークの成長につながると信じて。",
        "slogan_zh": "深信自身的持续成长，必然带动 GAME FREAK 整体的飞跃。",
        "profile_ja": "奈良先端科学技術大学院大学修了。幼い頃からゲームプログラマを志し、念願叶ってゲームフリークへ。システムプログラマ。",
        "profile_zh": "国立奈良先端科学技术大学院大学（NAIST）修了。自幼立志成为游戏程序员，如愿加入 GAME FREAK 担任系统程序员。主力负责全公司自动化构建系统、持续集成（CI）工具研发与大型开发流水线运维。",
        "summary": "GAME FREAK 官方一线系统程序员深度特写：毕业于国立情报科学顶级研究生院（NAIST）的 K.O.，讲述其自幼对宝可梦的热爱与成长为核心系统工程师的历程；详述管理全团队自动化构建与日常集成流水线时“牵一发而动全身”的沉甸甸责任感；以及在公司浓厚的技术钻研氛围中，如何通过引入前沿系统架构与工具链优化，持续为数百名开发者的日常研发提质增效。",
        "works": ["宝可梦 剑／盾", "宝可梦传说 阿尔宙斯"],
        "organizations": ["株式会社ゲームフリーク", "奈良先端科学技術大学院大学"],
        "tags": ["GAME FREAK", "K.O.", "系统程序员", "构建系统", "自动化测试", "持续集成", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网程序员特写，受访者为系统程序员K.O.，工科名门研究生背景，负责CI持续集成、全项目代码与资产自动化构建系统，探讨支持数百人开发团队的工程责任感与最新技术探索。",
        "captions": [
            "GAME FREAK 系统程序员 K.O. 主视觉：深信自身的持续成长必然带动团队的整体飞跃",
            "K.O. 实时监控数以百计工程分支的自动化持续构建流水线与测试日志",
            "与多技术工种协同推敲更敏捷高效的跨平台资源打包与发布规范",
            "以前沿工程理念与自动化工具，持续为大型主机开发环境减负提速",
        ],
    },
    {
        "id": "PKMN-1016",
        "short_id": "km",
        "name": "K.M.",
        "html_slug": "interview-pg-km",
        "img_remote_dir": "km",
        "img_local_dir": "gamefreak-recruit-km",
        "slug": "2021-12-27-interview-gamefreak-recruit-programmer-km.md",
        "role_zh": "研发总监 / 图形与自研引擎专家（CG Technology Lab Director / R&D）",
        "title_zh": "GAME FREAK 官方研发总监特写 K.M.：我们所研发的，正是 GAME FREAK 的未来",
        "title_ja": "開発しているのは、ゲームフリークの未来です。｜プログラマ社員紹介 K.M.",
        "slogan_ja": "開発しているのは、ゲームフリークの未来です。",
        "slogan_zh": "我们所研发的，正是 GAME FREAK 的未来。",
        "profile_ja": "大手ゲームメーカーで描画プログラマやリードプログラマを担当。その後、技術研究の道を模索する中で、ゲームフリークと出会う。研究開発部 CGテクノロジーラボ ディレクター。",
        "profile_zh": "曾在大手游戏企业担纲图形渲染程序员与主程序员。后在探索前沿技术攻关道路上加入 GAME FREAK。现任研究开发部（R&D）CG技术实验室总监（Director of CG Technology Lab），统领面向未来 5 年的专有引擎与千只宝可梦多边形形变体系重塑。",
        "summary": "GAME FREAK 官方研究开发部（R&D）总监深度特写：曾在大厂掌舵渲染与主程的 K.M.，坦诚道出“宝可梦拥有 1,000 只以上各不相同的模型，世上没有任何商业引擎能完美承载，唯有自研”的技术决断；详解面向 5 年后前瞻布局的动作形变（Deform）与角色渲染技术路线图；以及在业内顶尖专家云集、福利作息极其优渥的工程师文化中，如何以“解决所有‘困难’，实现所有‘极致考究’”为信条打造下一代技术底座。",
        "works": ["宝可梦系列专有引擎研发", "宝可梦 剑／盾", "宝可梦传说 阿尔宙斯"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "K.M.", "研究开发部", "自研引擎", "图形渲染", "R&D", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网程序员特写，受访者为研究开发部CG技术实验室总监K.M.，曾任大厂主程，探讨为超1000只宝可梦不同模型自主打造专有游戏引擎、前瞻5年布局渲染与形变技术路线图，以及技术专家的优渥研发环境。",
        "captions": [
            "GAME FREAK R&D 总监 K.M. 主视觉：我们所研发的正是 GAME FREAK 的未来",
            "K.M. 钻研面向千只宝可梦复杂几何形变的前瞻着色器与变形管线算法",
            "汇聚各大游戏名企资深专家的研究开发部展开架构层级研讨",
            "以解决所有“困难”、实现所有“极致考究”为使命筑造自研技术基石",
        ],
    },
    {
        "id": "PKMN-1017",
        "short_id": "ht-pg",
        "name": "H.T.",
        "html_slug": "interview-pg-ht",
        "img_remote_dir": "ht2",
        "img_local_dir": "gamefreak-recruit-ht-pg",
        "slug": "2021-12-27-interview-gamefreak-recruit-programmer-ht.md",
        "role_zh": "环境团队组长 / 全云端架构工程师（Environment Team Leader / Build Engineer）",
        "title_zh": "GAME FREAK 官方云端架构工程师特写 H.T.：全面强化组织效能——推动开发环境向全云端架构演进",
        "title_ja": "「組織の効率」強化へ。開発環境をフルクラウド化したい。｜プログラマ社員紹介 H.T.",
        "slogan_ja": "「組織の効率」強化へ。開発環境をフルクラウド化したい。",
        "slogan_zh": "全面强化“组织效能”——推动开发环境向全云端架构演进。",
        "profile_ja": "新卒でゲーム会社に入社後、フリーランスとして独立して数社のモバイルゲーム開発を経験。AIスタートアップのCOOを経て、ゲームフリークへ。研究開発部と開発二部の両方で環境チームのリーダーを務める。",
        "profile_zh": "应届进入游戏公司后独立成为自由职业者，主导过多款移动游戏开发。历任 AI 创业公司的 COO（首席运营官），随后加入 GAME FREAK。现同时兼任研究开发部（R&D）与开发二部的环境团队组长（Environment Team Leader），致力于推动全公司开发管线的全云端演进。",
        "summary": "GAME FREAK 官方一线环境与架构工程师深度特写：历经移动游戏大潮与 AI 创业公司 COO 磨砺的 H.T.，分享重返热爱的主机游戏界并加入 GAME FREAK 的心路历程；详解在兼顾研究开发部前沿技术与开发二部主线生产管线中，如何通过构建工程自动化提升全组织效率；深入剖析在兼顾远程在家办公与外协安全协作的大背景下，全面推进 GAME FREAK 开发环境“全云端原生化（Full Cloud Native）”的宏伟愿景与“创作者第一（Creator First）”的开明公司文化。",
        "works": ["宝可梦 剑／盾", "开发环境全云端架构"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "H.T.", "环境团队", "云原生开发", "CI/CD", "组织效能", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网程序员特写，受访者为环境团队组长H.T.，前AI创业公司COO背景，兼任R&D与开发二部，探讨推动开发管线全云端化、组织效能提升、创作者第一的敏捷决策文化与弹性办公福利。",
        "captions": [
            "GAME FREAK 环境团队组长 H.T. 主视觉：全面强化组织效能，推进开发环境全云端化",
            "H.T. 在现代化工作站前规划云端分布式编译与高效协同网络拓扑",
            "连接研发一线与管理层，践行以人为本、迅速决策的“创作者第一”文化",
            "通过技术架构创新与弹性办公制度，让团队研发效能与生活品质双向共赢",
        ],
    },
]


def curate_programmer(item_data: dict, glossary: list[dict]):
    short_id = item_data["short_id"]
    print(f"\n==================================================")
    print(f"Curating {item_data['id']}: {item_data['name']} ({short_id})")
    print(f"==================================================")

    url = f"https://www.gamefreak.co.jp/recruit/{item_data['html_slug']}/"
    raw_html_path = CACHE_DIR / f"{item_data['html_slug']}.html"
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

    # Download images
    img_local_dir = IMG_BASE_DIR / item_data["img_local_dir"]
    img_local_dir.mkdir(parents=True, exist_ok=True)

    img_urls = [
        f"https://www.gamefreak.co.jp/assets/recruit/img/interview/{item_data['img_remote_dir']}/mv.jpg",
        f"https://www.gamefreak.co.jp/assets/recruit/img/interview/{item_data['img_remote_dir']}/img-01.jpg",
        f"https://www.gamefreak.co.jp/assets/recruit/img/interview/{item_data['img_remote_dir']}/img-02.jpg",
        f"https://www.gamefreak.co.jp/assets/recruit/img/interview/{item_data['img_remote_dir']}/img-03.jpg",
    ]
    img_names = ["mv.jpg", "img-01.jpg", "img-02.jpg", "img-03.jpg"]

    for u_img, name in zip(img_urls, img_names):
        local_f = img_local_dir / name
        if not local_f.exists() or local_f.stat().st_size == 0:
            try:
                req = urllib.request.Request(u_img, headers={"User-Agent": "Mozilla/5.0"})
                img_data = urllib.request.urlopen(req, context=ctx, timeout=15).read()
                local_f.write_bytes(img_data)
                print(f"  Saved image {name} ({len(img_data)} bytes)")
            except Exception as e:
                print(f"  Error downloading image {u_img}: {e}")
        else:
            print(f"  Image {name} already exists ({local_f.stat().st_size} bytes)")

    parallel_items = []

    # Item 0: Lead image
    lead_img_path = f"/assets/img/interviews/{item_data['img_local_dir']}/mv.jpg"
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
        img_name = img_names[u_idx + 1]
        unit_img_path = f"/assets/img/interviews/{item_data['img_local_dir']}/{img_name}"
        parallel_items.append({
            "type": "image",
            "src": unit_img_path,
            "caption": item_data["captions"][u_idx + 1]
        })

        # Paragraphs
        for p_tag in u.find_all("p"):
            p_text = p_tag.get_text(strip=True)
            if p_text:
                parallel_items.append({
                    "type": "text",
                    "speaker": item_data["name"],
                    "speaker_orig": item_data["name"],
                    "original": p_text,
                    "translation": "" # to be translated
                })

    # Translate items
    print(f"  Translating {len(parallel_items)} items...")
    translate_items_batch(
        parallel_items,
        glossary,
        item_data["context_desc"],
        f"batch19_{short_id}"
    )

    # Post Frontmatter
    post_meta = {
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
        "original_link": f"https://www.gamefreak.co.jp/recruit/{item_data['html_slug']}/",
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
    }

    # Write post file
    post_path = POSTS_DIR / item_data["slug"]
    yaml_str = yaml.dump(
        post_meta,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
        default_flow_style=False,
    )
    post_content = f"---\n{yaml_str}---\n"
    post_path.write_text(post_content, encoding="utf-8")
    print(f"  Written post to {post_path.name} ({len(post_content)} chars)")

    # Update catalog
    update_catalog(item_data["id"], item_data["slug"])


def main():
    print("Starting Curate Batch 19: GAME FREAK 官方程序员特写四部曲...")
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    for item_data in PROGRAMMERS_DATA:
        curate_programmer(item_data, glossary)

    print("\nBatch 19 Complete!")


if __name__ == "__main__":
    main()
