"""The works' icons, in this order of preference:

  1. a local file we chose by hand (Pokopia's official logo)
  2. the official system icon from Bulbagarden Archives - the DS / 3DS game icon, a Virtual
     Console or Switch icon for the older games, the app icon for the mobile ones; the anime
     and the films wear their Japanese logos (ARCHIVE below, and CREDITS_ICONS for the games
     that only exist in the staff rolls -> archive/credits/icons.yml)
  3. the Pokémon HOME work icon (the Switch titles)
  4. the classic mark - a tile in its version colour with a Poké Ball on it (SteamGridDB 49670's
     design, drawn here) - for the works nothing official covers

Saved 96x96 under assets/img/works and written into _data/works.yml as icon / icon2 (the
second version of a pair), with icon_credit saying which it is.

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

ARCHIVE_API = "https://archives.bulbagarden.net/w/api.php"

# name -> Bulbagarden Archives file(s): official system icons, VC / Switch icons for the old games, logos for the anime
ARCHIVE = {
    "宝可梦 红·绿": ["Red VC JP icon.png", "Green VC icon.png"],
    "宝可梦 蓝": ["Blue VC JP icon.png"],
    "宝可梦 皮卡丘版": ["Yellow VC JP icon.png"],
    "宝可梦 金·银": ["Gold VC icon.png", "Silver VC icon.png"],
    "宝可梦 水晶版": ["Crystal VC JP icon.png"],
    "宝可梦 火红·叶绿": ["FireRed Icon.jpg", "LeafGreen Icon.jpg"],
    "宝可梦 钻石·珍珠": ["Diamond icon.png", "Pearl icon.png"],
    "宝可梦 白金": ["Platinum icon.png"],
    "宝可梦 心金·魂银": ["HeartGold Icon.png", "SoulSilver Icon.png"],
    "宝可梦 黑·白": ["Black Icon.png", "White Icon.png"],
    "宝可梦 黑2·白2": ["Black 2 Icon.png", "White 2 Icon.png"],
    "宝可梦 X·Y": ["X icon.png", "Y icon.png"],
    "宝可梦 欧米伽红宝石·阿尔法蓝宝石": ["Omega Ruby icon.png", "Alpha Sapphire icon.png"],
    "宝可梦 太阳·月亮": ["Sun icon.png", "Moon icon.png"],
    "宝可梦 究极之日·究极之月": ["Ultra Sun icon.png", "Ultra Moon icon.png"],
    "Pokémon GO": ["Pokémon GO icon.png"],
    "宝可梦 动画系列": ["S01 logo JP.png"],
    "超梦的逆袭": ["Japanese M01 Logo.png"],
    "宝可梦：超梦的逆袭": ["Japanese M01 Logo.png"],
    "洛奇亚爆诞": ["Japanese M02 Logo.png"],
    "结晶塔的帝王": ["Japanese M03 Logo.png"],
    "宝可梦不可思议迷宫": ["PMD Time icon.png"],
    "宝可梦随乐拍": ["PokémonSnapWiiUVCIconE.png"],
    "名侦探皮卡丘": ["Detective Pikachu icon.png"],
    "超级宝可梦乱战": ["Rumble Blast icon.png"],
}

# a file already in assets/img/works, chosen by hand; a pair that is not there yet falls through to the next rule
# (FireRed / LeafGreen: the HOME icons of the October 2026 link-up — drop the two-icon picture in and run
#  `python tools/build-work-icons.py --split <picture> home-firered home-leafgreen`)
LOCAL = {"Pokémon Pokopia": ["pokopia.png"], "宝可梦 火红·叶绿": ["home-firered.png", "home-leafgreen.png"]}
KEEP = {"pokopia-logo.png"}

# credits slug -> Archives file(s), for the games the staff rolls cover but works.yml does not
CREDITS_ICONS = {
    "red-blue": ["Red VC icon.png", "Blue VC icon.png"],
    "detective-pikachu": ["Detective Pikachu icon.png"],
    "detective-pikachu-birth-of-a-new-duo": ["Great Detective Pikachu Birth of a New Duo icon.png"],
    "detective-pikachu-returns": ["Detective Pikachu Returns Icon.jpg"],
    "mystery-dungeon-red-rescue-team-and-blue-rescue-team": ["PMDRRTEVCIcon.png", "PMDBRTEVCIcon.png"],
    "mystery-dungeon-explorers-of-time-and-explorers-of-darkness": ["PMD Time icon.png", "PMD Darkness icon.png"],
    "mystery-dungeon-explorers-of-sky": ["PMD Sky Icon.png"],
    "mystery-dungeon-gates-to-infinity": ["Gates to Infinity icon.png"],
    "super-mystery-dungeon": ["Super Mystery Dungeon icon.png"],
    "mystery-dungeon-rescue-team-dx": ["Mystery Dungeon Rescue Team DX Icon.jpg"],
    "ranger": ["PREVCIcon.png"],
    "ranger-shadows-of-almia": ["PRSOAEVCIcon.png"],
    "ranger-guardian-signs": ["PRGSEIcon.png"],
    "pinball-ruby-sapphire": ["Pinball Ruby and Sapphire VC icon.png"],
    "snap": ["PokémonSnapWiiUVCIconE.png"],
    "new-pokemon-snap": ["New Snap Icon.jpg"],
    "pokepark-wii": ["PokéParkWiieShopIconE.png"],
    "rumble-u": ["Rumble U icon.png"],
    "rumble-blast": ["Rumble Blast icon.png"],
    "rumble-world": ["Rumble World icon.png"],
    "rumble-rush": ["Pokémon Rumble Rush icon.png"],
    "pokken-tournament": ["Pokkén icon.png"],
    "pokken-tournament-dx": ["Pokken Tournament DX Icon.jpg"],
    "shuffle": ["Shuffle 3DS icon.png"],
    "picross": ["Picross icon.png"],
    "art-academy": ["Art Academy icon.png"],
    "battle-trozei": ["Battle Trozei icon.png"],
    "the-thieves-and-the-1000-pokemon": ["The Thieves and the 1000 Pokémon icon.png"],
    "puzzle-challenge": ["Puzzle Challenge VC icon.png"],
    "trading-card-game": ["TCG GB VC icon.png"],
    "magikarp-jump": ["Pokémon Magikarp Jump icon.png"],
    "quest": ["Quest Icon.jpg"],
    "sleep": ["Pokémon Sleep icon.png"],
    "smile": ["Pokémon Smile icon.png"],
    "tcg-card-dex": ["Pokémon TCG Card Dex icon.png"],
    "trading-card-game-pocket": ["Pokémon TCG Pocket icon iOS 1.4.0.png"],
    "friends": ["Friends Icon Switch.jpg"],
    "goita-tutorial-app": ["Pokémon GOITA icon.png"],
    "duel": ["Pokémon Duel icon 7.0.7.png"],
    "cafe-remix": ["Pokémon Café ReMix icon Switch.png"],
    "masters": ["Pokémon Masters EX icon 2.23.0 iOS.png"],
}
CREDITS_ICONS_FILE = ROOT / "archive" / "credits" / "icons.yml"

# the official DS icons of Black and White (SteamGridDB, FloweyGaming577)
OFFICIAL = {
    "宝可梦 黑·白": ["8d65294979cf7c59fa43f91f993fb5c2", "5b97f793636f8baec3ff8cd0ebf5c33c"],
    "宝可梦立体图鉴BW": ["8d65294979cf7c59fa43f91f993fb5c2", "5b97f793636f8baec3ff8cd0ebf5c33c"],
}


def fetch(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def archive_url(title):
    """the download URL of a Bulbagarden Archives file"""
    import json
    import urllib.parse
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + title, "prop": "imageinfo", "iiprop": "url", "format": "json"})
    raw = urllib.request.urlopen(urllib.request.Request(f"{ARCHIVE_API}?{q}", headers=UA), timeout=60).read()
    for page in json.loads(raw)["query"]["pages"].values():
        if page.get("imageinfo"):
            return page["imageinfo"][0]["url"]
    raise KeyError(title)


def tile_from(im):
    """any archive picture → the 96x96 tile: pixel icons (DS 32, 3DS 48) scale by whole steps so they stay
    crisp; big square icons shrink and get the rounded corners the HOME icons have; wide logos sit
    centred on a transparent square"""
    w, h = im.size
    if max(w, h) <= 64:
        k = SIZE // max(w, h)
        im = im.resize((w * k, h * k), Image.NEAREST)
        tile = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        tile.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
        return tile
    if abs(w - h) <= max(w, h) * 0.08:  # square-ish: a system icon
        im = im.resize((SIZE, SIZE), Image.LANCZOS)
        if im.getchannel("A").getpixel((1, 1)) > 200:  # a jpg / opaque png: round the corners
            mask = Image.new("L", (SIZE * 4, SIZE * 4), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), radius=int(SIZE * 4 * 0.18), fill=255)
            im.putalpha(mask.resize((SIZE, SIZE), Image.LANCZOS))
        return im
    bbox = im.getbbox()  # a logo: trim, fit with a margin
    if bbox:
        im = im.crop(bbox)
    m = 4
    im.thumbnail((SIZE - 2 * m, SIZE - 2 * m), Image.LANCZOS)
    tile = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    tile.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
    return tile


def slug_of(title):
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", title.rsplit(".", 1)[0]).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def archive_tile(title, force=False):
    """fetch + tile one Archives file, cached as assets/img/works/bulba-<slug>.png"""
    f = OUT / f"bulba-{slug_of(title)}.png"
    if not f.exists() or force:
        tile_from(fetch(archive_url(title))).save(f, optimize=True)
        print(f"  {f.name:40s} <- Archives {title}")
        time.sleep(0.4)
    return f


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


def split_pair(src, names):
    """a picture with two icons side by side (as the official announcements show them) → two tiles.
    Split at the emptiest column near the middle, trim each half to its content, fit into the tile."""
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    # background = the corner colour; anything close to it counts as empty
    bg = im.getpixel((0, 0))
    def empty(px):
        return px[3] < 16 or all(abs(px[i] - bg[i]) < 28 for i in range(3))
    cols = [sum(0 if empty(im.getpixel((x, y))) else 1 for y in range(h)) for x in range(w)]
    lo, hi = int(w * 0.3), int(w * 0.7)
    cut = min(range(lo, hi), key=lambda x: cols[x])
    out = []
    for i, part in enumerate((im.crop((0, 0, cut, h)), im.crop((cut, 0, w, h)))):
        mask = Image.eval(part.getchannel("A"), lambda a: 255 if a >= 16 else 0)
        # also treat the background colour as transparent so the tile is clean
        px = part.load()
        for y in range(part.height):
            for x in range(part.width):
                if empty(px[x, y]):
                    px[x, y] = (0, 0, 0, 0)
        bbox = part.getbbox()
        part = part.crop(bbox) if bbox else part
        m = 6
        part.thumbnail((SIZE - 2 * m, SIZE - 2 * m), Image.LANCZOS)
        tile = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        tile.paste(part, ((SIZE - part.width) // 2, (SIZE - part.height) // 2), part)
        f = OUT / f"{names[i]}.png"
        tile.save(f, optimize=True)
        out.append(f)
        print(f"  {f.name:40s} <- {Path(src).name} ({'left' if i == 0 else 'right'} of the cut at x={cut})")
    return out


def main():
    if "--split" in sys.argv:
        i = sys.argv.index("--split")
        split_pair(sys.argv[i + 1], sys.argv[i + 2:i + 4])
        sys.argv = [a for a in sys.argv if a not in sys.argv[i:i + 4]]
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    works = yaml.safe_load(io.open(WORKS, encoding="utf-8")) or []
    wanted = set()
    for w in works:
        name = w["name"]
        files, credit = [], ""
        if name in LOCAL and all((OUT / fn).exists() for fn in LOCAL[name]):
            credit = "Pokémon HOME 的作品图标（官方公告图裁切）" if LOCAL[name][0].startswith("home-") else (w.get("icon_credit") or "手选的官方图")
            files = [OUT / fn for fn in LOCAL[name]]
        elif name in ARCHIVE:
            credit = "官方图标 / 标志（Bulbagarden Archives）"
            files = [archive_tile(t, force) for t in ARCHIVE[name]]
        elif name in HOME:
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
    # the games only the staff rolls know: archive/credits/icons.yml, read by tools/build-credits-site.py
    credits_icons = {}
    for slug, titles in CREDITS_ICONS.items():
        fs = [archive_tile(t, force) for t in titles]
        credits_icons[slug] = [f"/assets/img/works/{f.name}" for f in fs]
        wanted.update(f.name for f in fs)
    io.open(CREDITS_ICONS_FILE, "w", encoding="utf-8", newline="\n").write(
        "# 由 tools/build-work-icons.py 生成：制作名单里的作品 → 官方图标（Bulbagarden Archives），works.yml 没有的才用\n"
        + yaml.safe_dump(credits_icons, allow_unicode=True, sort_keys=True, width=200))
    wanted.update(KEEP)
    for f in OUT.glob("*.png"):
        if f.name not in wanted:
            f.unlink(); print(f"  -- {f.name} (no longer used)")
    header = "\n".join([
        "# 作品图标：站内 entities.works 名 → 图标（tools/build-work-icons.py 生成到 assets/img/works）。一条规则：",
        "# 先用官方图标（Bulbagarden Archives：DS / 3DS 游戏图标、VC / Switch 图标、动画与电影的日文标志），Switch 世代用 Pokémon HOME 的作品图标，",
        "# 都没有的用经典标记——版本色底 + 精灵球；Pokopia 用手选的官方标志。",
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
