#!/usr/bin/env python3
"""职务 / 区块名的中文小字：英文 credits 标题 → 括号里的中文，给名单页、团队画像树和人物页的职务栏用。

    role_zh("Programming Section / Field Team")   → "程序部 / 场景组"
    role_zh("Executive Producers")                 → "执行制作人"
    role_zh("BANDAI NAMCO Studios Inc.")           → None（公司名不译）

规则翻译：先匹配 PHRASES（最长优先），再逐词查 WORDS（复数去 s），查不到的词原样保留；
一个词都没译出来、或整段是公司名 / 平台包装（Staff list (2025)、Credits for …）→ None，页面上就不显示。
英文的修饰语在前、中心词在后，和中文一致，所以按顺序拼就是像样的短语；不像样的加进 OVERRIDES。

    python tools/role-zh.py            打印最常见 300 个区块名的译文（改词典后看一眼）
"""
import re
import sys
import unicodedata

OVERRIDES = {
    "developed by": "开发", "produced by": "制作", "presented by": "出品", "published by": "发行", "pokémon produced by": "宝可梦制作",
    "special thanks": "特别感谢", "very special thanks": "特别鸣谢", "special thanks to": "特别感谢", "thanks to": "感谢",
    "global staff": "全球版人员", "japanese version": "日版", "japanese version staff": "日版人员", "us version staff": "美版人员",
    "european version staff": "欧版人员", "english-version": "英语版", "european-version": "欧洲版", "french-version": "法语版", "german-version": "德语版",
    "list of staff": "名单", "staff": "人员",
    "debug play": "试玩调试", "debug": "调试", "debug management": "调试管理",
    "information supervisors": "信息监修", "information management": "信息管理", "information coordinators": "信息协调",
    "task managers": "任务经理", "task manager": "任务经理",
    "pokédex text": "图鉴文本", "pokémon global link": "宝可梦全球连接", "global link": "全球连接",
    "battle tower data": "对战塔数据", "parametric design": "参数设计", "parametric designers": "参数设计",
    "map data designers": "地图数据设计", "script designers": "脚本设计", "script design": "脚本设计",
    "look development": "视觉开发", "rumble data design": "震动数据设计",
    "dcc support teams": "DCC 支持组", "dcc environment development team": "DCC 环境开发组", "rigging system development team": "绑定系统开发组",
    "communication features team": "通信功能组", "communication features": "通信功能",
    "3d visual section": "3D 视觉部", "pokémon 3d visual team": "宝可梦 3D 视觉组", "pokémon 3d modeling": "宝可梦 3D 建模",
    "pokémon data qa": "宝可梦数据检查", "pokémon series qa": "宝可梦系列 QA", "pokémon attribute team": "宝可梦属性组",
    "pokémon model quality assurance": "宝可梦模型品管", "pokémon modeling quality assurance": "宝可梦模型品管",
    "character & costume design": "角色与服装设计", "world, pokémon & human planning": "世界观、宝可梦与人物企划",
    "design & world concept section": "设计与世界观部", "concept & visual studio": "概念与视觉工作室",
    "research & development": "研发", "research ＆ development": "研发", "cg technology laboratory": "CG 技术实验室", "cg technology section": "CG 技术部",
    "base technology section": "基础技术部", "environment development section": "环境开发部", "software production environment management": "软件生产环境管理",
    "quality assurance system team": "品管系统组", "delivery review team": "交付审查组",
    "game server development": "游戏服务器开发", "server development": "服务器开发",
    "technical support": "技术支持", "development support": "开发支持", "development assistant": "开发助理", "development partners": "开发协力",
    "motion actors": "动捕演员", "motion-capture acting": "动作捕捉表演", "motion-capture studio assistance": "动捕棚协助",
    "sound coordination": "音响协调", "sound effects coordination": "音效协调", "sound environment support": "音响环境支持", "sound partners": "音响协力",
    "recording coordinator": "录音协调", "voice recording": "配音录制", "voice recording director": "配音导演",
    "main theme": "主题曲", "ending theme": "片尾曲", "opening movie": "片头影像",
    "artwork": "美术素材", "chinese artwork": "中文版美术素材", "korean artwork": "韩文版美术素材",
    "english & european graphic design": "英欧版图形设计", "manual editing": "说明书编辑",
    "coordinators": "协调", "coordinator": "协调", "coordination": "协调",
    "producers": "制作人", "producer": "制作人", "executive producers": "执行制作人", "executive producer": "执行制作人",
    "general producers": "总制作人", "general producer": "总制作人", "senior director": "资深总监", "executive director": "执行总监",
    "section director": "部门总监", "section directors": "部门总监", "art director": "美术总监", "supervisor": "监修", "supervisors": "监修",
    "planning & supervision": "企划与监修", "original director": "原作总监", "pokémon original director": "宝可梦原作总监",
    "client engineers": "客户端工程师", "server engineers": "服务器工程师", "infrastructure engineers": "基础设施工程师",
    "in cooperation with": "协力", "cooperative companies": "协力公司", "partners": "合作方",
    "legal": "法务", "brand review and approval": "品牌审核", "sales & promotion": "销售与宣传",
    "product testing": "产品测试", "quality assurance": "品质保证", "language qa": "语言 QA", "qa coordination": "QA 协调",
    "localization": "本地化", "localisation": "本地化", "localization support": "本地化支持", "localisation support": "本地化支持",
    "translation & editing": "翻译与编辑", "text editors": "文本编辑", "text editor": "文本编辑",
    "game design": "游戏设计", "game designers": "游戏设计", "game designer": "游戏设计", "game planning": "游戏企划",
    "map design": "地图设计", "map designers": "地图设计", "field map design": "场景地图设计", "3d map graphics": "3D 地图图形",
    "field team": "场景组", "field programming": "场景程序", "field system design": "场景系统设计", "field & ai team": "场景与 AI 组",
    "field contents programming": "场景内容程序", "field environment programming": "场景环境程序",
    "event team": "事件组", "event programming": "事件程序", "event planning": "事件企划",
    "battle team": "对战组", "battle director": "对战总监", "battle system programming": "对战系统程序", "battle planning": "对战企划",
    "ui team": "界面组", "ui graphic design team": "界面图形设计组", "ui graphic design": "界面图形设计", "ui system programming": "界面系统程序",
    "character team": "角色组", "character modeling team": "角色建模组", "character modeling": "角色建模", "character motion design": "角色动作设计",
    "motion design team": "动作设计组", "motion design": "动作设计", "motion team": "动作组", "model team": "模型组", "debug team": "调试组",
    "lighting team": "灯光组", "movie team": "影像组", "digital movie design": "数字影像设计",
    "special effects graphic design team": "特效图形设计组", "effect design": "特效设计",
    "pokémon character modeling": "宝可梦角色建模", "pokémon character motion": "宝可梦角色动作", "pokémon characters design": "宝可梦角色设计",
    "pokémon & character design": "宝可梦与角色设计", "pokémon design": "宝可梦设计", "pokémon & graphic designers": "宝可梦与图形设计",
    "pokémon model inspection": "宝可梦模型检查", "pokémon modelers": "宝可梦建模",
    "trainer graphics design": "训练家图形设计", "concept illustration / item design": "概念插画 / 道具设计",
    "main scenario": "主线剧本", "story team": "故事组", "scenario": "剧本", "plot scenario": "剧情剧本", "game scenario": "游戏剧本",
    "game dialogue design": "游戏对白设计", "game text localization support": "游戏文本本地化支持",
    "programming section": "程序部", "programming section supervisor": "程序部监修", "programming section directors": "程序部总监", "programming section director": "程序部总监",
    "graphic design section": "图形设计部", "graphic design section directors": "图形设计部总监", "planning section": "企划部", "planning section director": "企划部总监",
    "sound team": "音响组", "sound section": "音响部", "sound programming": "音响程序", "sound effects": "音效", "composers": "作曲", "musicians": "演奏", "voice": "配音",
    "main programmer": "主程序", "main graphic designer": "主图形设计", "program leader": "程序组长", "graphic leader": "图形组长", "music leader": "音乐组长", "game design leader": "游戏设计组长",
    "environment & tool programmers": "环境与工具程序", "tool programming": "工具程序", "library team": "程序库组", "framework team": "框架组",
    "graphics programming team": "图形程序组", "simulation team": "模拟组", "game ai team": "游戏 AI 组", "machine learning team": "机器学习组", "pipeline team": "管线组",
    "pokémon & battle system team": "宝可梦与对战系统组", "general manager": "总经理", "group manager": "组经理", "project managers": "项目经理", "project management": "项目管理",
    "product managers": "产品经理", "product manager": "产品经理", "project director": "项目总监", "assistants": "助理",
    "network programming": "网络程序", "wi-fi server development": "Wi-Fi 服务器开发",
    "the pokémon company": "宝可梦公司", "the pokémon company international": "宝可梦公司国际", "pokémon company": "宝可梦公司",
    "nintendo of america": "美国任天堂", "nintendo of europe": "欧洲任天堂", "nintendo of korea": "韩国任天堂", "north american": "北美", "north america": "北美",
    "special effects": "特效", "special effects graphic design": "特效图形设计", "special appearances by": "特别出演", "with cooperation from": "协力",
    "group leaders": "组长", "group leader": "组长", "manual layout": "说明书排版", "linguistic quality assurance": "语言品质保证",
    "application programming": "应用程序", "digital painters": "数字上色", "design create": "设计制作", "program create": "程序制作", "sound create": "音响制作",
    "creative staff": "创意人员", "development staff": "开发人员", "localization development": "本地化开发",
}

WORDS = {
    "programming": "程序", "programmer": "程序员", "program": "程序", "engineer": "工程师", "engineering": "工程", "software": "软件",
    "design": "设计", "designer": "设计", "designed": "设计", "art": "美术", "artist": "美术", "graphic": "图形", "graphics": "图形", "illustration": "插画", "illustrator": "插画",
    "modeling": "建模", "modeler": "建模", "model": "模型", "motion": "动作", "animation": "动画", "animator": "动画", "effect": "特效", "vfx": "特效", "lighting": "灯光",
    "render": "渲染", "rendering": "渲染", "shader": "着色器", "texture": "贴图", "cg": "CG", "cgi": "CGI", "3d": "3D", "2d": "2D", "3-d": "3D", "visual": "视觉",
    "movie": "影像", "cinematic": "过场影像", "video": "视频", "storyboard": "分镜",
    "sound": "音响", "music": "音乐", "composer": "作曲", "composition": "作曲", "arrangement": "编曲", "audio": "音频", "voice": "配音", "voices": "配音", "recording": "录音",
    "lyrics": "作词", "vocals": "演唱", "vocal": "演唱", "guitar": "吉他", "musician": "演奏", "mixing": "混音", "mastering": "母带",
    "planning": "企划", "planner": "企划", "scenario": "剧本", "script": "脚本", "story": "故事", "plot": "剧情", "text": "文本", "dialogue": "对白", "narrative": "叙事", "writer": "撰稿", "writing": "撰稿",
    "event": "事件", "battle": "对战", "field": "场景", "map": "地图", "world": "世界观", "concept": "概念", "character": "角色", "trainer": "训练家", "costume": "服装", "item": "道具",
    "pokemon": "宝可梦", "pokedex": "图鉴", "monster": "怪兽", "data": "数据", "parameter": "参数", "parametric": "参数", "balance": "平衡", "balancing": "平衡",
    "system": "系统", "ui": "界面", "interface": "界面", "menu": "菜单", "hud": "HUD", "network": "网络", "communication": "通信", "server": "服务器", "online": "在线", "wireless": "无线",
    "tool": "工具", "library": "程序库", "framework": "框架", "pipeline": "管线", "environment": "环境", "infrastructure": "基础设施", "engine": "引擎", "physics": "物理", "simulation": "模拟",
    "ai": "AI", "rigging": "绑定", "dcc": "DCC", "technical": "技术", "technology": "技术", "research": "研究", "development": "开发", "developer": "开发", "developed": "开发",
    "debug": "调试", "debugging": "调试", "test": "测试", "testing": "测试", "tester": "测试", "quality": "品质", "assurance": "保证", "qa": "QA", "check": "检查", "inspection": "检查",
    "localization": "本地化", "localisation": "本地化", "translation": "翻译", "translator": "翻译", "translated": "翻译", "editing": "编辑", "editor": "编辑", "proofreading": "校对",
    "english": "英语", "french": "法语", "german": "德语", "italian": "意大利语", "spanish": "西班牙语", "korean": "韩语", "chinese": "中文", "japanese": "日语", "portuguese": "葡萄牙语",
    "european": "欧洲", "europe": "欧洲", "american": "美国", "america": "美国", "americas": "美洲", "asia": "亚洲", "korea": "韩国", "japan": "日本", "us": "美国", "uk": "英国",
    "latin": "拉丁美洲", "traditional": "繁体", "simplified": "简体", "version": "版", "international": "国际", "global": "全球", "overseas": "海外",
    "section": "部", "team": "组", "unit": "组", "group": "组", "division": "部", "department": "部", "studio": "工作室", "laboratory": "实验室", "lab": "实验室", "office": "办公室",
    "lead": "组长", "leader": "组长", "chief": "主任", "head": "负责人", "main": "主", "senior": "资深", "junior": "初级", "assistant": "助理", "associate": "副", "sub": "副", "deputy": "副",
    "director": "总监", "supervisor": "监修", "supervision": "监修", "advisor": "顾问", "adviser": "顾问", "advised": "顾问", "consultant": "顾问",
    "producer": "制作人", "production": "制作", "produced": "制作", "product": "产品", "project": "项目", "manager": "经理", "management": "管理",
    "coordinator": "协调", "coordination": "协调", "information": "信息", "support": "支持", "assistance": "协助", "cooperation": "协力", "cooperative": "协力", "partner": "合作方",
    "special": "特别", "thanks": "感谢", "general": "总", "executive": "执行", "creative": "创意", "original": "原作", "additional": "追加", "guest": "客座", "opening": "片头", "ending": "片尾",
    "marketing": "市场", "promotion": "宣传", "sales": "销售", "pr": "公关", "legal": "法务", "business": "商务", "brand": "品牌", "licensing": "授权", "customer": "客户", "service": "服务",
    "operations": "运营", "operation": "运营", "package": "包装", "logo": "标志", "manual": "说明书", "web": "网页", "apps": "应用", "app": "应用", "mobile": "移动端", "client": "客户端", "platform": "平台",
    "base": "基础", "core": "核心", "feature": "功能", "features": "功能", "contents": "内容", "content": "内容", "digital": "数字", "capture": "捕捉", "actor": "演员", "acting": "表演", "cast": "演员",
    "dubbing": "配音", "adr": "后期配音", "analyst": "分析", "direction": "指导", "directed": "指导", "created": "制作", "creation": "制作", "action": "动作", "mechanical": "机械", "hardware": "硬件",
    "icon": "图标", "card": "卡牌", "trading": "集换式", "attribute": "属性", "drawing": "绘制", "setting": "设定", "level": "关卡", "language": "语言", "review": "审核", "approval": "审批",
    "human": "人物", "background": "背景", "terrain": "地形", "dungeon": "迷宫", "puzzle": "谜题", "camera": "镜头", "cutscene": "过场", "demo": "演示", "title": "标题", "screen": "画面",
    "mini": "迷你", "game": "游戏", "games": "游戏", "series": "系列", "channel": "频道", "shuffle": "Shuffle", "quest": "Quest", "arena": "竞技场",
    "the": "", "of": "", "and": "与", "for": "", "by": "", "in": "", "at": "", "with": "", "to": "", "a": "", "an": "", "&": "与",
}

def _norm(w):
    s = unicodedata.normalize("NFKD", w)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


OVERRIDES = {_norm(k): v for k, v in OVERRIDES.items()}
WORDS.update({"asian": "亚洲", "linguistic": "语言", "application": "应用", "appearance": "出演", "painter": "上色", "layout": "排版", "create": "制作", "from": "",
              "north": "北", "south": "南", "east": "东", "west": "西", "central": "中", "eu": "欧盟", "worldwide": "全球", "quality-assurance": "品质保证"})

COMPANY = re.compile(r"\b(Inc\.?|Ltd\.?|Co\.,?|GmbH|Corp\.?|Corporation|LLC|L\.L\.C|S\.A\.|Limited|K\.K\.|Studios?\s+Inc|Entertainment\s+Inc|Games\s+Co)\b|株式会社|有限会社", re.I)
WRAPPER = re.compile(r"^(staff list|credits for|list of staff|staff of)\b", re.I)
TOKEN = re.compile(r"[^\W_][^\W_'’\-]*(?:['’\-][^\W_]+)*|\s+|[&/(),:;.!—–\-]+|\S")


def _word(w):
    k = _norm(w)
    if k in WORDS:
        return WORDS[k]
    for suf in ("es", "s"):
        if k.endswith(suf) and k[:-len(suf)] in WORDS:
            return WORDS[k[:-len(suf)]]
    if k.endswith("ies") and k[:-3] + "y" in WORDS:
        return WORDS[k[:-3] + "y"]
    return None


def _part(text):
    """一个路径段。返回 (译文, 译出的词数, 总词数)"""
    key = _norm(text.strip()).replace("（", "(").replace("）", ")")
    key = re.sub(r"\s+", " ", key)
    if key in OVERRIDES:
        return OVERRIDES[key], 1, 1
    toks = TOKEN.findall(text)
    words = [t for t in toks if re.match(r"[^\W_]", t)]
    out, i, hit = [], 0, 0
    while i < len(toks):
        t = toks[i]
        if not re.match(r"[^\W_]", t):
            out.append({"&": "与", "(": "（", ")": "）", ",": "、", ":": "："}.get(t.strip(), t) if t.strip() else " ")
            i += 1
            continue
        # 最长短语优先（最多 5 个词，中间的空格 / & 一起吃）
        best = None
        j, n = i, 0
        while j < len(toks) and n < 5:
            if re.match(r"[^\W_]", toks[j]):
                n += 1
                phrase = _norm("".join(toks[i:j + 1])).replace("  ", " ")
                phrase = re.sub(r"\s+", " ", phrase).strip()
                if phrase in OVERRIDES:
                    best = (j, OVERRIDES[phrase], n)
            elif toks[j].strip() not in ("", "&", "-", "’", "'"):
                break
            j += 1
        if best:
            out.append(best[1])
            hit += best[2]
            i = best[0] + 1
            continue
        w = _word(t)
        if w is None:
            out.append(t)
        else:
            hit += 1
            if w:
                out.append(w)
        i += 1
    s = "".join(out)
    # 中文之间不要空格；中文与保留的英文之间留一个空格
    s = re.sub(r"(?<=[一-鿿）])\s+(?=[一-鿿（])", "", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ")
    s = s.replace("（ ", "（").replace(" ）", "）").replace("、 ", "、")
    return s, hit, len(words)


def role_zh(title):
    """整条职务 / 区块名（可含 " / " 分级）→ 中文；译不出 / 是公司名 / 是包装标题 → None"""
    if not title:
        return None
    parts = [p.strip() for p in title.split(" / ")]
    out, any_hit = [], False
    for p in parts:
        if not p:
            continue
        if COMPANY.search(p) or WRAPPER.match(p):
            out.append(p)
            continue
        zh, hit, n = _part(p)
        if hit and zh and zh != p:
            any_hit = True
            out.append(zh)
        else:
            out.append(p)
    if not any_hit:
        return None
    res = " / ".join(out)
    return None if res == title else res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import io
    from collections import Counter
    from pathlib import Path
    import yaml
    c = Counter()
    for f in (Path(__file__).resolve().parent.parent / "_data" / "credits").glob("*.yml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        for s in d["sections"]:
            c[" / ".join(s["path"])] += len(s["names"])
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    miss = 0
    for k, cnt in c.most_common(n):
        z = role_zh(k)
        miss += z is None
        print(f"{cnt:5d}  {k}  →  {z}")
    print(f"\n{miss}/{n} 无译文")
