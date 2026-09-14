"""Curate Batch 20:
GAME FREAK 官方创作者档案·策划与技术美术特写收官篇 (2021)
- PKMN-1018: R.M. (游戏策划组长 / 扩充票与新项目团队负责人)
- PKMN-1019: K.F. (策划兼总监 / 《Pokémon HOME》总监 / 云端生态)
- PKMN-1020: T.K. (技术美术专家 / 1000只宝可梦模型管线 / 研发部兼开发二部)
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
CACHE_DIR = ROOT / "tools" / "cache_batch_20"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def load_glossary() -> list[dict]:
    if not GLOSSARY_PATH.exists():
        local_glossary = ROOT / "data" / "glossary-master.json"
        if local_glossary.exists():
            data = json.loads(local_glossary.read_text(encoding="utf-8"))
            return [{"target": item.get("target"), "terms": item.get("terms") or []} for item in data.get("entries", []) if item.get("target")]
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

        prompt = f"""你是宝可梦官方档案馆的资深中日翻译专家、游戏企划与技术美术（TA）管线专家。请将以下来自 GAME FREAK 官方一线核心策划/技术美术访谈的日文内容翻译为通顺、优美、严谨专业、忠实于原意、符合中国大陆宝可梦官方简体中文语境的译文。
背景信息：
{context_desc}

【官方术语硬性约束（必须严格遵守）】：
{term_constraints}

【翻译要求】：
1. 语言风格兼具顶级游戏策划与技术美术工程的专业性（如技术美术 TA、Houdini、动作捕捉 MoCap、DCC 软件、3D模型制作规约、云端生态 Pokémon HOME、扩充票、策划立项机制等）与行业访谈的流畅感。
2. 保持受访者自然诚恳的职场第一人称叙述口吻，行文凝练生动，准确传达 GAME FREAK “以作品说话、不按资排辈、鼓励颠覆性创意”的开拓精神。
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
                "content": "You are a professional Japanese to Simplified Chinese translator specializing in Pokémon official media, game design planning, and technical art pipeline engineering.",
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


BATCH_20_DATA = [
    {
        "id": "PKMN-1018",
        "short_id": "rm",
        "name": "R.M.",
        "html_slug": "interview-pl-rm",
        "img_remote_dir": "rm",
        "img_local_dir": "gamefreak-recruit-rm",
        "slug": "2021-12-27-interview-gamefreak-recruit-planner-rm.md",
        "role_zh": "游戏策划组长（Game Planner / Team Leader）",
        "title_zh": "GAME FREAK 官方策划特写 R.M.：哪怕是普通的文科生，也能向着顶级游戏策划发起冲击",
        "title_ja": "普通の文系学生でも、めざせ！ ゲームプランナー。｜プランナー社員紹介 R.M.",
        "slogan_ja": "普通の文系学生でも、めざせ！ ゲームプランナー。",
        "slogan_zh": "哪怕是普通的文科生，也能向着顶级游戏策划发起冲击。",
        "profile_ja": "4年制大学の教育学部を卒業。入社後は『ポケットモンスター ソード・シールド エキスパンションパス』および新規プロジェクトのチームリーダーを務める。",
        "profile_zh": "四年制大学教育学部毕业。文科出身入职 GAME FREAK，先后担纲《宝可梦 剑／盾 扩充票》核心策划以及全新项目的团队组长（Team Leader）。",
        "summary": "GAME FREAK 官方一线游戏策划深度特写：毕业于综合大学教育学部的文科生 R.M.，坦诚分享在求职面试时直言指出宝可梦作品改进空间的大胆经历；详述入职仅第 2 年便被破格提拔为《宝可梦 剑／盾 扩充票》团队负责人的挑战与成长；深刻展现 GAME FREAK“不按资排辈、倾听所有人创意”的扁平文化；并畅谈作为团队领头羊，如何带领跨职种成员共同磨砺兼具惊喜感与完成度的顶级游戏企划。",
        "works": ["宝可梦 剑／盾 扩充票", "全新企划项目"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "R.M.", "游戏策划", "宝可梦 剑／盾", "扩充票", "团队管理", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网策划特写，受访者为游戏策划组长R.M.，四年制大学教育学部文科背景，入职第2年即担任《宝可梦 剑／盾 扩充票》及新项目团队负责人，探讨文科生立志成为游戏策划、面试中直言发表见解、打破年资的唯才评价机制，以及带领团队打造创意的领导者信念。",
        "captions": [
            "GAME FREAK 游戏策划组长 R.M. 主视觉：哪怕是普通的文科生，也能向着顶级游戏策划发起冲击",
            "R.M. 在工位梳理玩法规则设计案与跨工种协同需求规范",
            "入职第 2 年破格担纲团队负责人，与各职种成员扁平探讨创意可行性",
            "以“未来的团队领袖”之姿，为全球玩家打造兼具新鲜感与深度的游玩体验",
        ],
    },
    {
        "id": "PKMN-1019",
        "short_id": "kf",
        "name": "K.F.",
        "html_slug": "interview-pl-kf",
        "img_remote_dir": "kf",
        "img_local_dir": "gamefreak-recruit-kf",
        "slug": "2021-12-27-interview-gamefreak-recruit-planner-kf.md",
        "role_zh": "策划兼总监（Game Planner / Director of Pokémon HOME）",
        "title_zh": "GAME FREAK 官方策划特写 K.F.：颠覆世界的机遇，往往隐匿在意料之外的角落",
        "title_ja": "世界を変えるチャンスは、意外な場所にある。｜プランナー社員紹介 K.F.",
        "slogan_ja": "世界を変えるチャンスは、意外な場所にある。",
        "slogan_zh": "颠覆世界的机遇，往往隐匿在意料之外的角落。",
        "profile_ja": "フリーのサウンドデザイナーを経て、プランナーとしてソーシャルゲーム開発会社へ。その後、ゲームフリークに入社。『Pokémon HOME』のディレクターを担当。",
        "profile_zh": "曾任自由职业声音设计师，后转战社交网络游戏公司担任策划。加入 GAME FREAK 后担纲云端跨平台宝可梦生态服务《Pokémon HOME》的执行总监（Director）。",
        "summary": "GAME FREAK 官方核心策划兼总监深度特写：从自由声音设计师跨界为主力策划的 K.F.，详述执导《Pokémon HOME》前瞻云端服务的心路历程；提出“宝可梦不能只停留在一部游戏完结，而要通过生态服务深深扎根于玩家现实日常”的企划哲学；深刻阐释 GAME FREAK 绝无“打杂熬资历”的陈规，鼓励新人不拘泥于既定套路、勇敢提出颠覆性构想，并以“如何以企划撬动世界”的格局将创意推向全球。",
        "works": ["Pokémon HOME", "宝可梦系列生态架构"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "K.F.", "游戏策划", "Pokémon HOME", "游戏总监", "云端生态", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网策划特写，受访者为策划兼《Pokémon HOME》总监K.F.，跨界背景，深入阐述宝可梦不仅是单部主机游戏、更是融入日常生活的跨平台体验，探讨GAME FREAK无下积（熬资历）概念、新人直面世界级企划的文化，以及抓住偶然机遇改变世界的策划胸怀。",
        "captions": [
            "GAME FREAK 策划兼《Pokémon HOME》总监 K.F. 主视觉：颠覆世界的机遇，往往隐匿在意料之外的角落",
            "K.F. 规划《Pokémon HOME》跨越全世代作品与移动端的云端交互架构",
            "坚守宝可梦精神内核的同时，以“如何改变与拓展系列”为课题审视企划",
            "在全员倾听、包容多元的开发氛围中，将自己的灵感构想推向全世界",
        ],
    },
    {
        "id": "PKMN-1020",
        "short_id": "ta-tk",
        "name": "T.K.",
        "html_slug": "interview-ta-tk",
        "img_remote_dir": "tk",
        "img_local_dir": "gamefreak-recruit-ta-tk",
        "slug": "2021-12-27-interview-gamefreak-recruit-ta-tk.md",
        "role_zh": "技术美术专家（Technical Artist / R&D & 2nd Dev Dept）",
        "title_zh": "GAME FREAK 官方技术美术（TA）特写 T.K.：敏锐预判创作者需求、亲手开拓崭新环境的 TA 之道",
        "title_ja": "作り手のニーズを先読みし、新しい環境を創造するTAでありたい。｜テクニカルアーティスト社員紹介 T.K.",
        "slogan_ja": "作り手のニーズを先読みし、新しい環境を創造するTAでありたい。",
        "slogan_zh": "敏锐预判创作者需求、亲手开拓崭新环境的 TA 之道。",
        "profile_ja": "専門学校でCGを学び、ゲーム会社でのデザイナー業務と映像制作会社でのエンジニア業務を経験。TA（テクニカルアーティスト）としてゲームフリークに入社。開発二部と研究開発部を兼務。",
        "profile_zh": "专门学校学习 CG 艺术，先后历练游戏公司美术设计师与影像制作公司引擎技术研发。作为首批 TA（技术美术）加入 GAME FREAK，同时兼任开发二部与研究开发部（R&D）核心管线工作。",
        "summary": "GAME FREAK 官方一线技术美术（TA）深度特写：历经 10 年 PC 游戏开发与前沿影像技术洗礼的 T.K.，讲述因童年挚爱《耀西的蛋》而结缘 GAME FREAK 的历程；深度揭秘在《宝可梦 剑／盾》中全面操刀“超 1,000 只宝可梦 3D 模型制作环境规范与资产管理大冒险”；详述研究开发部引入 Houdini 程序化生成与动作捕捉（MoCap）体系、攻克大地图海量数据瓶颈并全面反哺《宝可梦传说 阿尔宙斯》的硬核经验；并分享“敏锐预判需求、跳出思维定式”的技术美术职业信条。",
        "works": ["宝可梦 剑／盾", "宝可梦传说 阿尔宙斯", "Houdini管线研发", "动作捕捉系统"],
        "organizations": ["株式会社ゲームフリーク"],
        "tags": ["GAME FREAK", "T.K.", "技术美术", "TA", "宝可梦 剑／盾", "宝可梦传说 阿尔宙斯", "Houdini", "招聘访谈"],
        "context_desc": "GAME FREAK 2021年招聘官网TA特写，受访者为技术美术T.K.，曾在大厂担任PC游戏程序与CG技术，负责《剑／盾》超1000只宝可梦模型制作规范、解决开放大地图性能数据瓶颈，并将经验运用于《宝可梦传说 阿尔宙斯》，兼任开发二部与R&D，推动动捕与Houdini工具导入。",
        "captions": [
            "GAME FREAK 技术美术 T.K. 主视觉：敏锐预判创作者需求、亲手开拓崭新环境的 TA 之道",
            "T.K. 在 Houdini 与 DCC 软件中推演程序化地图生成与资源轻量化管线",
            "统领超 1,000 只宝可梦模型规范，作为程序与美术不可或缺的桥梁纽带",
            "以突破思维定式的极客视野，为下一代宝可梦探路全新开发环境",
        ],
    },
]


def curate_item(item_data: dict, glossary: list[dict]):
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
            "translation": ""  # to be translated
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
                    "translation": ""  # to be translated
                })

    # Translate items
    print(f"  Translating {len(parallel_items)} items...")
    translate_items_batch(
        parallel_items,
        glossary,
        item_data["context_desc"],
        f"batch20_{short_id}"
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
    print("Starting Curate Batch 20: GAME FREAK 官方策划与技术美术特写收官篇...")
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    for item_data in BATCH_20_DATA:
        curate_item(item_data, glossary)

    print("\nBatch 20 Complete!")


if __name__ == "__main__":
    main()
