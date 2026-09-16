"""The works' icons: the SteamGridDB "Pokemon Games" icon collection (12146) - the box-art
mascot of each version cut square, one style across every generation - saved small under
assets/img/works and written into _data/works.yml as icon / icon2 (the second version of
a pair). Games the collection has not got keep their cover-legendary render and colours.

    python tools/build-work-icons.py            # download the missing ones, update works.yml
    python tools/build-work-icons.py --force    # redo them all
"""
import io
import sys
import time
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "works"
WORKS = ROOT / "_data" / "works.yml"
CDN = "https://cdn2.steamgriddb.com/icon/"
UA = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com; work icons)"}
SIZE = 96

# site name -> (file slug, [SteamGridDB icon hashes], authors) - the chickenish set where it
# exists (one hand across the generations), Lunecho / Skully / Julia / Varimarthas for the rest
ICONS = {
    "宝可梦 红·绿": ("red-green", ["e64860da9a6248363a016357d47bd65f", "5a0de25c4bcaa248ec1765bcb0863712"], "chickenish"),
    "宝可梦 蓝": ("blue", ["ad59ae2c6077196b68ff0c94a09fed73"], "chickenish"),
    "宝可梦 皮卡丘版": ("yellow", ["d8bc5c8da5d7b391e11ab6e14b1df1e5"], "chickenish"),
    "宝可梦 金·银": ("gold-silver", ["409cc060198690137a12782c09282608", "15b16cf1aa29a55a67eeeb7dc6e5f686"], "chickenish"),
    "宝可梦 水晶版": ("crystal", ["9bd96e176bbedf4d017f4b438bd613e3"], "chickenish"),
    "宝可梦 红宝石·蓝宝石": ("ruby-sapphire", ["6f240678a0a4b55d7f4046426b637fec", "283062995206f8cbf7c0b50216b9623e"], "chickenish"),
    "宝可梦 绿宝石": ("emerald", ["e4ad3061dc592b68a36c62b7681e2e0e"], "chickenish"),
    "宝可梦 火红·叶绿": ("firered-leafgreen", ["d902c3ce47124c66ce615d5ad9ba304f", "8708cc4b4fd657032eddc86555279921"], "Lunecho, chickenish"),
    "宝可梦 钻石·珍珠": ("diamond-pearl", ["a5a922ea078f7e063b2fde0fc5cd3e08", "a2729b7746a7f069a1d87a2141cf6aee"], "chickenish"),
    "宝可梦 白金": ("platinum", ["10caad252666c9992275b6be2555dc6e"], "chickenish"),
    "宝可梦 心金·魂银": ("heartgold-soulsilver", ["0ace141f8779c77b60cdc66fa22da900", "11b4076afd563b2612049c2c77465b32"], "chickenish"),
    "宝可梦 黑·白": ("black-white", ["f0d78b7cc5bda890fe64cdbe4fe573d7", "d52d7aeaf42820be2cc18dd7915e3a2b"], "chickenish"),
    "宝可梦 黑2·白2": ("black2-white2", ["9bd90fed98b9f7f1e9024b13e758c45a", "2d9a3e519c394e52e45c7dab97557ccc"], "chickenish"),
    "宝可梦立体图鉴BW": ("black-white", ["f0d78b7cc5bda890fe64cdbe4fe573d7", "d52d7aeaf42820be2cc18dd7915e3a2b"], "chickenish"),
    "宝可梦 X·Y": ("x-y", ["241bf752bca8e0f0cd7ed4c68b791c55", "7f0c1838d4c84c1f022d0776ce925ace"], "chickenish"),
    "宝可梦 欧米伽红宝石·阿尔法蓝宝石": ("omega-ruby-alpha-sapphire", ["0ec15baa9437436fff3e5fdbb4a7cae3", "0dc8732a8ba6b3b578c1e891a9eb6aa3"], "chickenish"),
    "宝可梦 太阳·月亮": ("sun-moon", ["18f4af2e90e7feea928965095fbd4d31", "1f79b53a859b13a6579670b4574a5892"], "chickenish"),
    "宝可梦 究极之日·究极之月": ("ultra-sun-ultra-moon", ["e2b55042866db16f336e911d6e05a45b", "4fefed995eb187fe7d0c0e4e2351f82a"], "chickenish"),
    "宝可梦 Let's Go！皮卡丘·Let's Go！伊布": ("lets-go", ["c7529b8e425f81f2d9b65a162002f19d", "0415089c6d09cb4eccd7a314f9610301"], "chickenish"),
    "宝可梦 Let's Go！皮卡丘/伊布": ("lets-go", ["c7529b8e425f81f2d9b65a162002f19d", "0415089c6d09cb4eccd7a314f9610301"], "chickenish"),
    "宝可梦 剑·盾": ("sword-shield", ["98ed037c165c8ff9f4afefbe86f08c84", "d6ea02b23d9ba70ecc548116b406c851"], "chickenish"),
    "宝可梦传说 阿尔宙斯": ("legends-arceus", ["21ddd604f061d571546dcffc82e7143a"], "Skully"),
    "宝可梦 晶灿钻石·明亮珍珠": ("brilliant-diamond-shining-pearl", ["cba4fab5fe82032158186944374bf5c0", "e1a0d53a534014217b7961d1870ee76b"], "Julia"),
    "宝可梦 朱·紫": ("scarlet-violet", ["c6c477a7ecc421032cbb009a28f1daf9", "f9e036c34e550a09edf738196fa2e49a"], "Skully"),
    "Pokémon LEGENDS Z-A": ("legends-z-a", ["1278fc97734f54ce31d4b69fd9b07221"], "Skully"),
    "Pokémon HOME": ("home", ["b5cda4dd4e87e6b77a676fc545f325dd"], "Varimarthas"),
}


def fetch(h):
    raw = urllib.request.urlopen(urllib.request.Request(CDN + h + ".png", headers=UA), timeout=120).read()
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    works = yaml.safe_load(io.open(WORKS, encoding="utf-8")) or []
    by_name = {w["name"]: w for w in works}
    done = {}
    for name, (slug, hashes, author) in ICONS.items():
        files = []
        for i, h in enumerate(hashes):
            f = OUT / (slug + ("" if i == 0 else "-2") + ".png")
            if not f.exists() or force:
                if h in done:
                    f.write_bytes(done[h])
                else:
                    im = fetch(h)
                    im.thumbnail((SIZE, SIZE), Image.LANCZOS)
                    im.save(f, optimize=True)
                    done[h] = f.read_bytes()
                    time.sleep(0.3)
                print(f"  {slug:34s} <- {h[:8]} ({author})")
            files.append(f"/assets/img/works/{f.name}")
        w = by_name.get(name)
        if not w:
            print(f"  ?? {name} is not in works.yml"); continue
        w["icon"] = files[0]
        if len(files) > 1:
            w["icon2"] = files[1]
        else:
            w.pop("icon2", None)
        w["icon_credit"] = f"SteamGridDB collection 12146 · {author}"
    header = "\n".join([
        "# 作品图标：站内 entities.works 名 → 图标。icon / icon2 是 SteamGridDB「Pokemon Games」图标集（collection 12146）里各版本的",
        "# 封面主角方形图（tools/build-work-icons.py 抓到 assets/img/works），双版本作品 icon 在名字前、icon2 在名字后；",
        "# 图标集没有的作品用 color / color2（版本代表色）和 mascot（代表宝可梦的 HOME 渲染图）。",
        "",
    ])
    io.open(WORKS, "w", encoding="utf-8", newline="\n").write(header + yaml.safe_dump(works, allow_unicode=True, sort_keys=False, width=1000))
    print(f"works.yml: {sum(1 for w in works if w.get('icon'))} of {len(works)} with an icon")


if __name__ == "__main__":
    main()
