"""The works' icons, one rule: a title Pokémon HOME knows wears its HOME icon; every other
work wears the classic mark - a tile in its version colour with a Poké Ball on it (the
design of SteamGridDB icon 49670, drawn here for the whole set so no version is missing);
Black and White keep their official DS icons (SteamGridDB 42737 / FloweyGaming577's pair).
Saved small under assets/img/works and written into _data/works.yml as icon / icon2 (the
second version of a pair), with icon_credit saying which of the three it is.

    python tools/build-work-icons.py            # draw / fetch what is missing, update works.yml
    python tools/build-work-icons.py --force    # redo them all
"""
import io
import sys
import time
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "works"
WORKS = ROOT / "_data" / "works.yml"
UA = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com; work icons)"}
SIZE = 96
HOME_ICON = "https://pokeamice.com/game_gallery/icon/HOME_{}_icon.png"
SGDB = "https://cdn2.steamgriddb.com/icon/{}.png"

# name -> file slug (the classic tiles are named after these)
SLUGS = {
    "宝可梦 红·绿": "red-green", "宝可梦 蓝": "blue", "宝可梦 皮卡丘版": "yellow",
    "宝可梦 金·银": "gold-silver", "宝可梦 水晶版": "crystal",
    "宝可梦 红宝石·蓝宝石": "ruby-sapphire", "宝可梦 绿宝石": "emerald", "宝可梦 火红·叶绿": "firered-leafgreen",
    "宝可梦 钻石·珍珠": "diamond-pearl", "宝可梦 白金": "platinum", "宝可梦 心金·魂银": "heartgold-soulsilver",
    "宝可梦 黑·白": "black-white", "宝可梦 黑2·白2": "black2-white2", "宝可梦立体图鉴BW": "black-white",
    "Pokémon GO": "go", "宝可梦 动画系列": "anime", "超梦的逆袭": "mewtwo-strikes-back",
    "宝可梦：超梦的逆袭": "mewtwo-strikes-back", "超梦的诞生": "mewtwo-origin", "超梦！我就在这里": "mewtwo-returns",
    "洛奇亚爆诞": "lugia", "结晶塔的帝王": "crystal-tower", "宝可梦集换式卡牌游戏": "tcg", "宝可梦卡牌": "tcg",
    "宝可梦不可思议迷宫": "mystery-dungeon", "宝可梦竞技场": "stadium", "宝可梦圆形竞技场": "colosseum",
    "宝可梦随乐拍": "snap", "名侦探皮卡丘": "detective-pikachu", "宝可梦打字DS": "typing", "宝可梦乱战": "rumble",
    "超级宝可梦乱战": "rumble", "宝可梦对战革命": "battle-revolution", "宝可梦频道": "channel", "Pokémon mini": "mini",
}

# name -> HOME icon names (one per version), as game_gallery files them
HOME = {
    "宝可梦 X·Y": ["X", "Y"],
    "宝可梦 欧米伽红宝石·阿尔法蓝宝石": ["Omega_Ruby", "Alpha_Sapphire"],
    "宝可梦 太阳·月亮": ["Sun", "Moon"],
    "宝可梦 究极之日·究极之月": ["Ultra_Sun", "Ultra_Moon"],
    "宝可梦 Let's Go！皮卡丘·Let's Go！伊布": ["Let's_Go_Pikachu", "Let's_Go_Eevee"],
    "宝可梦 剑·盾": ["Sword", "Shield"],
    "宝可梦传说 阿尔宙斯": ["Legends_Arceus"],
    "宝可梦 晶灿钻石·明亮珍珠": ["Brilliant_Diamond", "Shining_Pearl"],
    "宝可梦 朱·紫": ["Scarlet", "Violet"],
    "Pokémon LEGENDS Z-A": ["Legends_Z-A"],
    "Pokémon HOME": ["HOME"],
    "Pokémon Champions": ["Champions"],
}

# the official DS icons of Black and White (SteamGridDB, FloweyGaming577)
OFFICIAL = {
    "宝可梦 黑·白": ["8d65294979cf7c59fa43f91f993fb5c2", "5b97f793636f8baec3ff8cd0ebf5c33c"],
    "宝可梦立体图鉴BW": ["8d65294979cf7c59fa43f91f993fb5c2", "5b97f793636f8baec3ff8cd0ebf5c33c"],
}


def fetch(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(rgb, k):
    """the colour mixed towards black (k < 0) or white (k > 0)"""
    t = 255 if k > 0 else 0
    k = abs(k)
    return tuple(int(c + (t - c) * k) for c in rgb)


def ball_tile(color):
    """the classic mark: a rounded tile in the version colour, a darker rim, a Poké Ball"""
    S = SIZE * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rgb = hexrgb(color)
    d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=shade(rgb, -0.28))
    rim = int(S * 0.055)
    d.rounded_rectangle((rim, rim, S - 1 - rim, S - 1 - rim), radius=int(S * 0.17), fill=rgb)
    c = S / 2
    r = S * 0.31
    line = S * 0.045
    red, white, black = (238, 66, 52), (247, 247, 247), (28, 28, 30)
    d.ellipse((c - r, c - r, c + r, c + r), fill=black)
    ri = r - line
    d.pieslice((c - ri, c - ri, c + ri, c + ri), 180, 360, fill=red)
    d.pieslice((c - ri, c - ri, c + ri, c + ri), 0, 180, fill=white)
    d.rectangle((c - ri, c - line / 2, c + ri, c + line / 2), fill=black)
    rb = S * 0.10
    d.ellipse((c - rb, c - rb, c + rb, c + rb), fill=black)
    rb2 = rb - line * 0.9
    d.ellipse((c - rb2, c - rb2, c + rb2, c + rb2), fill=white)
    return im.resize((SIZE, SIZE), Image.LANCZOS)


def save(im, f):
    im = im.copy()
    im.thumbnail((SIZE, SIZE), Image.LANCZOS)
    im.save(f, optimize=True)


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    works = yaml.safe_load(io.open(WORKS, encoding="utf-8")) or []
    wanted = set()
    for w in works:
        name = w["name"]
        files, credit = [], ""
        if name in HOME:
            credit = "Pokémon HOME 的作品图标（pokeamice.com/game_gallery）"
            for v in HOME[name]:
                f = OUT / ("home-" + v.lower().replace("'", "").replace("_", "-") + ".png")
                if not f.exists() or force:
                    save(fetch(HOME_ICON.format(v)), f)
                    print(f"  {f.name:40s} <- HOME {v}")
                    time.sleep(0.2)
                files.append(f)
        elif name in OFFICIAL:
            credit = "官方 DS 图标（SteamGridDB · FloweyGaming577）"
            for i, h in enumerate(OFFICIAL[name]):
                f = OUT / (SLUGS[name] + ("" if i == 0 else "-2") + ".png")
                if not f.exists() or force:
                    save(fetch(SGDB.format(h)), f)
                    print(f"  {f.name:40s} <- SteamGridDB {h[:8]}")
                    time.sleep(0.3)
                files.append(f)
        elif w.get("color"):
            credit = "经典标记：版本色底 + 精灵球（tools/build-work-icons.py 绘制，样式取自 SteamGridDB 49670）"
            colors = [w["color"]] + ([w["color2"]] if w.get("color2") else [])
            for i, col in enumerate(colors):
                f = OUT / ("ball-" + SLUGS[name] + ("" if i == 0 else "-2") + ".png")
                if not f.exists() or force:
                    ball_tile(col).save(f, optimize=True)
                    print(f"  {f.name:40s} <- ball on {col}")
                files.append(f)
        else:
            print(f"  ?? {name}: no HOME icon and no colour"); continue
        wanted.update(f.name for f in files)
        w["icon"] = f"/assets/img/works/{files[0].name}"
        if len(files) > 1:
            w["icon2"] = f"/assets/img/works/{files[1].name}"
        else:
            w.pop("icon2", None)
        w["icon_credit"] = credit
    for f in OUT.glob("*.png"):
        if f.name not in wanted:
            f.unlink(); print(f"  -- {f.name} (no longer used)")
    header = "\n".join([
        "# 作品图标：站内 entities.works 名 → 图标（tools/build-work-icons.py 生成到 assets/img/works）。一条规则：",
        "# HOME 收录的作品用 Pokémon HOME 的作品图标；其余用经典标记——版本色底 + 精灵球（黑·白沿用官方 DS 图标）。",
        "# 双版本作品 icon 在名字前、icon2 在名字后；color / color2 是版本代表色，mascot 是封面宝可梦的 HOME 渲染图（备用）。",
        "",
    ])
    io.open(WORKS, "w", encoding="utf-8", newline="\n").write(header + yaml.safe_dump(works, allow_unicode=True, sort_keys=False, width=1000))
    kinds = {}
    for w in works:
        k = (w.get("icon_credit") or "?")[:6]
        kinds[k] = kinds.get(k, 0) + 1
    print(f"works.yml: {sum(1 for w in works if w.get('icon'))} of {len(works)} with an icon {kinds}")


if __name__ == "__main__":
    main()
