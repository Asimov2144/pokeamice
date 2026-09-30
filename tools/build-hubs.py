"""The two cross-cutting hubs: 海外媒体专访 (/overseas/) and 按游戏 (/games/).

    python tools/build-hubs.py            # write _data/hubs.yml
    python tools/build-hubs.py --tag      # also put/remove the 海外媒体专访 topic on the posts

Both pages are hand-written Liquid over _data/hubs.yml (_pages/overseas.md, _pages/games.md) in the
timeline's layout and stylesheet. Like the timeline, the numbers come from the posts of the last
commit (git cat-file, not the working copy), so a post another session is still writing is not counted.

海外媒体专访 - interviews that a media outlet outside Japan ran: the US and UK games press, the
Spanish, French and Italian press, the Pokemon company's own overseas sites. Membership is decided
by the outlet named in the publication / title / source (OUTLETS below), not by language: some of
these are Spanish or French originals, some are English, and a few carry no language at all. What is
left out on purpose: GlitterBerri (English fan translations of Japanese magazines - a second-hand
copy, not an interview the outlet ran) and interviews that only *cite* a foreign site.

按游戏 - the works of _data/works.yml in the order they came out, by generation, each with how many
documents mention it, what kind, and three to read first. Blog posts are counted apart (they name
games in passing, hundreds of them). A game family with aliases (the Mewtwo film has four names in
the data) is counted as the union of its posts.
"""
import collections
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
L = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

spec = importlib.util.spec_from_file_location("bt", ROOT / "tools" / "build-timeline.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
xp = bt.xp

TAG = "海外媒体专访"

# key, name on the page, region, pattern in publication / title / source
OUTLETS = [
    ("gi", "Game Informer", "美国", r"Game Informer"),
    ("np", "Nintendo Power", "美国", r"Nintendo Power|任天堂力量"),
    ("ign", "IGN", "美国", r"\bIGN\b"),
    ("gamepro", "GamePro", "美国", r"GamePro"),
    ("1up", "1UP.com", "美国", r"1UP"),
    ("g4", "G4TV", "美国", r"G4TV|G4tv"),
    ("polygon", "Polygon", "美国", r"Polygon"),
    ("gamespot", "GameSpot", "美国", r"GameSpot"),
    ("gamasutra", "Gamasutra", "美国", r"Gamasutra"),
    ("time", "《时代周刊》", "美国", r"时代周刊|TIME Magazine"),
    ("nwr", "Nintendo World Report", "美国", r"Nintendo World Report"),
    ("siliconera", "Siliconera", "美国", r"Siliconera"),
    ("eurogamer", "Eurogamer", "英国", r"Eurogamer"),
    ("cvg", "CVG", "英国", r"\bCVG\b"),
    ("onm", "ONM", "英国", r"(?<![A-Za-z])ONM(?![A-Za-z])|Official Nintendo Magazine"),
    ("spong", "SPOnG", "英国", r"SPOnG"),
    ("nlife", "Nintendo Life", "英国", r"Nintendo Life"),
    ("vgc", "VGC", "英国", r"\bVGC\b"),
    ("vg247", "VG247", "英国", r"VG247"),
    ("guardian", "The Guardian", "英国", r"Guardian"),
    ("accion", "Nintendo Acción", "西班牙语", r"Nintendo Acci"),
    ("hobby", "Hobby Consolas", "西班牙语", r"Hobby Consolas"),
    ("elpais", "《国家报》", "西班牙语", r"国家报|El Pa[ií]s"),
    ("gq", "GQ 西班牙", "西班牙语", r"\bGQ\b"),
    ("meri", "MeriStation", "西班牙语", r"MeriStation"),
    ("topo", "Topo Gamer", "西班牙语", r"Topo Gamer"),
    ("jv", "jeuxvideo.com", "法语·意大利语", r"jeuxvideo"),
    ("dordogne", "法国地方报", "法语·意大利语", r"Dordogne|Enqu[eê]te"),
    ("multi", "Multiplayer.it", "法语·意大利语", r"Multiplayer\.it"),
    ("pcom", "Pokémon.com", "官方海外站", r"Pok[eé]mon\.com"),
    ("pmnet", "PocketMonsters.net", "官方海外站", r"PocketMonsters"),
    ("bahamut", "巴哈姆特 GNN", "中文（台湾）", r"巴哈姆特"),
]
REGIONS = [
    ("美国", "美国的游戏媒体", "Game Informer 一家就占了大半，其余是任天堂的官方杂志和一批门户站。"),
    ("英国", "英国的游戏媒体", "多在欧洲发售前的伦敦、巴黎场合采访。"),
    ("西班牙语", "西班牙语媒体", "西班牙的杂志、报纸和游戏站；原文是西班牙语，本站译成中文。"),
    ("法语·意大利语", "法语·意大利语媒体", "法国、意大利的游戏站和一家地方报。"),
    ("官方海外站", "宝可梦官方海外站", "Pokémon.com 和 PocketMonsters.net：公司自己面向海外的站点。"),
    ("中文（台湾）", "中文媒体（台湾）", "巴哈姆特 GNN 在东京的圆桌采访。"),
]
# ids (the part of the file name after the date) that match an outlet by accident, or are second-hand copies
NOT_OVERSEAS = ("glitterberri", "yomiuri", "读卖")
# the outlet by the id, when nothing in the front matter names it
OUTLET_BY_ID = {
    "interview-pokemon-com-": "pcom",
}
CITES = re.compile(r"^\s*(?:[\[［【][^\]］】]*[\]］】]\s*)*")

# ---- games ---------------------------------------------------------------------------------
GROUPS = [
    ("g1", "第一世代", "红·绿·蓝·皮卡丘", ["宝可梦 红·绿", "宝可梦 蓝", "宝可梦 皮卡丘版"]),
    ("g2", "第二世代", "金·银·水晶", ["宝可梦 金·银", "宝可梦 水晶版"]),
    ("g3", "第三世代", "宝石与火红叶绿", ["宝可梦 红宝石·蓝宝石", "宝可梦 绿宝石", "宝可梦 火红·叶绿"]),
    ("g4", "第四世代", "钻石·珍珠到心金·魂银", ["宝可梦 钻石·珍珠", "宝可梦 白金", "宝可梦 心金·魂银"]),
    ("g5", "第五世代", "黑·白与续篇", ["宝可梦 黑·白", "宝可梦 黑2·白2"]),
    ("g6", "第六世代", "3D 化的 X·Y", ["宝可梦 X·Y", "宝可梦 欧米伽红宝石·阿尔法蓝宝石"]),
    ("g7", "第七世代", "太阳·月亮与 Let's Go", ["宝可梦 太阳·月亮", "宝可梦 究极之日·究极之月", "宝可梦 Let's Go！皮卡丘·Let's Go！伊布"]),
    ("g8", "第八世代", "Switch 上的剑·盾与重制", ["宝可梦 剑·盾", "宝可梦 晶灿钻石·明亮珍珠", "宝可梦传说 阿尔宙斯"]),
    ("g9", "第九世代", "朱·紫与 Z-A", ["宝可梦 朱·紫", "Pokémon LEGENDS Z-A"]),
    ("mobile", "手机与卡牌", "Pokémon GO、集换式卡牌、HOME", ["Pokémon GO", ("宝可梦集换式卡牌游戏", "宝可梦卡牌"), "Pokémon HOME"]),
    ("spin", "外传作品", "迷宫、竞技场、乱战和其他", [
        "宝可梦不可思议迷宫", "宝可梦竞技场", "宝可梦圆形竞技场", "宝可梦随乐拍", "宝可梦立体图鉴BW", "宝可梦乱战", "超级宝可梦乱战",
        "宝可梦对战革命", "宝可梦频道", "宝可梦打字DS", "Pokémon mini", "名侦探皮卡丘"]),
    ("anime", "动画与电影", "电视动画与剧场版", ["宝可梦 动画系列", ("超梦的逆袭", "宝可梦：超梦的逆袭", "超梦的诞生", "超梦！我就在这里"), "洛奇亚爆诞", "结晶塔的帝王"]),
]
# first release in Japan, for what has no staff-roll entry in credits_games.yml
RELEASE = {"宝可梦 红·绿": 1996, "宝可梦 蓝": 1996, "Pokémon GO": 2016, "宝可梦集换式卡牌游戏": 1996, "Pokémon HOME": 2020, "Pokémon mini": 2001,
           "宝可梦 动画系列": 1997, "超梦的逆袭": 1998, "洛奇亚爆诞": 1999, "结晶塔的帝王": 2000}
DOC_KIND_NAMES = {"interview": "访谈", "scan": "扫描", "topic": "专题", "article": "文章"}


def text_of(value):
    if isinstance(value, dict):
        value = value.get("title") or value.get("name") or ""
    return str(value or "")


def pick_score(p, freq):
    fm = p["fm"]
    s = (2 if fm.get("image") or fm.get("featured_image") else 0) + (1 if fm.get("publication") else 0) + min(2, len(p["people"])) + (1 if fm.get("summary") else 0)
    s += {"interview": 1, "scan": 1, "topic": 0, "article": 0}[p["kind"]]
    s -= min(3, freq[series_key(fm)] - 1)
    s -= min(3, max(0, len(p["works"]) - 2))       # a page that names ten games is not about this one
    return s


def series_key(fm):
    return re.sub(r"\s+", "", bt.plain(fm.get("publication") or fm.get("display_title") or fm.get("title"), 200))[:11]


def url_of(p):
    return xp.canonical_url(p["fm"], p["id"]).replace(xp.SITE, "")


def cover_row(p, covers):
    fm = bt.read_post(p["rel"], full=True) or p["fm"]
    cover = bt.cover_of(fm)
    row = {}
    if cover:
        row["cover"] = cover
        if covers.get(cover):
            row["cover_size"] = list(covers[cover])
    return row, fm


def outlet_of(p):
    fm = p["fm"]
    hay = " ".join([text_of(fm.get("publication")), text_of(fm.get("title")), text_of(fm.get("display_title")), text_of(fm.get("source")), text_of(fm.get("original_title"))])
    src = fm.get("source_url") or fm.get("original_link") or ""
    if isinstance(fm.get("source"), dict):
        src = src or fm["source"].get("url") or ""
    hay += " " + str(src)
    low = hay.lower()
    if any(k in low for k in NOT_OVERSEAS) or "glitterberri" in p["id"]:
        return None
    for frag, key in OUTLET_BY_ID.items():
        if frag in p["id"]:
            return next(o for o in OUTLETS if o[0] == key)
    for o in OUTLETS:
        if re.search(o[3], hay):
            return o
    if "pokemon.com" in str(src).lower():
        return next(o for o in OUTLETS if o[0] == "pcom")
    return None


def clean_overseas_title(title, outlet):
    """Drop 'Game Informer 2019：' from the front of a title - the card already says where it ran."""
    t = bt.clean_title(title, 300)
    m = re.match(r"^(?:%s)[^：:]{0,16}[：:]\s*(.+)$" % outlet[3], t, re.I)
    if m and len(m.group(1)) >= 8:
        t = m.group(1)
    return t if len(t) <= 64 else t[:64].rstrip("，、；：,;: ") + "…"


def main():
    tag_mode = "--tag" in sys.argv
    works_list = yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8"))
    works = {w["name"]: w for w in works_list}
    games = yaml.safe_load(io.open(ROOT / "_data" / "credits_games.yml", encoding="utf-8"))
    people = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8"))
    slug_of = {p["name"]: p["slug"] for p in people if p.get("slug") and p.get("kind") not in ("character", "figure")}
    covers = yaml.load(io.open(ROOT / "_data" / "covers.yml", encoding="utf-8").read(), Loader=L) or {}
    by_work_game = {}
    for g in games:
        if g.get("work") and g["work"] not in by_work_game:
            by_work_game[g["work"]] = g

    files = bt.git_files()
    bt.load_head(files)
    posts = []
    for rel in files:
        fm = bt.read_post(rel)
        if fm is None or fm.get("date") is None or (fm.get("search") is False and fm.get("archive_type") not in bt.STREAMS):
            continue
        stem = Path(rel).name[:-3]
        ent = fm.get("entities") or {}
        posts.append({
            "rel": rel, "stem": stem, "id": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem), "fm": fm, "date": str(fm["date"])[:10],
            "kind": bt.kind_of(fm),
            "people": [x for x in (ent.get("people") or []) if isinstance(x, str)],
            "works": [x for x in (ent.get("works") or []) if isinstance(x, str)],
        })
    print(len(posts), "tracked posts")

    # ---------------------------------------------------------------- overseas
    members = []
    for p in posts:
        if p["kind"] not in ("interview", "scan", "article"):
            continue
        o = outlet_of(p)
        if o:
            members.append((p, o))
    members.sort(key=lambda t: (t[0]["date"], t[0]["id"]))
    print("overseas members:", len(members))
    outlet_n = collections.Counter(o[0] for _, o in members)
    region_rows = []
    for rkey, label, note in REGIONS:
        items = []
        for p, o in members:
            if o[2] != rkey:
                continue
            row, fm = cover_row(p, covers)
            item = {
                "title": clean_overseas_title(fm.get("display_title") or fm.get("title"), o),
                "url": url_of(p),
                "date": p["date"],
                "outlet": o[0],
                "outlet_name": o[1],
                "kind": p["kind"],
                "people": [n for n in p["people"]][:3],
                "works": [dict({"name": w}, **{k: works[w][k] for k in ("icon", "icon2") if works.get(w, {}).get(k)}) for w in p["works"][:2] if w in works],
                **row,
            }
            blurb = bt.plain(fm.get("dek") or fm.get("summary"), 88)
            if blurb:
                item["blurb"] = blurb
            items.append(item)
        if not items:
            continue
        outs = collections.Counter(i["outlet"] for i in items)
        yrs = [int(i["date"][:4]) for i in items]
        region_rows.append({
            "key": rkey, "label": label, "note": note, "n": len(items), "from": min(yrs), "to": max(yrs),
            "outlets": [{"key": k, "name": next(o[1] for o in OUTLETS if o[0] == k), "n": n} for k, n in outs.most_common()],
            "items": items,
        })
    yc = collections.Counter(int(p["date"][:4]) for p, _ in members)
    pc = collections.Counter(n for p, _ in members for n in set(p["people"]) if n in slug_of)
    wc = collections.Counter(n for p, _ in members for n in set(p["works"]) if n in works)
    overseas = {
        "total": len(members),
        "from": min(yc), "to": max(yc),
        "outlets": [{"key": k, "name": next(o[1] for o in OUTLETS if o[0] == k), "n": n} for k, n in outlet_n.most_common()],
        "years": [{"year": y, "n": yc.get(y, 0)} for y in range(min(yc), max(yc) + 1)],
        "max_year": max(yc.values()),
        "people": [{"name": n, "slug": slug_of[n], "n": c} for n, c in pc.most_common(8)],
        "works": [dict({"name": n, "n": c}, **{k: works[n][k] for k in ("icon", "icon2") if works[n].get(k)}) for n, c in wc.most_common(8)],
        "regions": region_rows,
    }

    # ------------------------------------------------------------------- games
    group_rows = []
    all_docs = 0
    for gkey, glabel, gsub, entries in GROUPS:
        cards = []
        gdocs = {}
        for entry in entries:
            names = list(entry) if isinstance(entry, tuple) else [entry]
            primary = names[0]
            w = works.get(primary)
            if not w:
                continue
            mine = [p for p in posts if any(n in p["works"] for n in names)]
            docs = [p for p in mine if p["kind"] != "stream"]
            blogs = [p for p in mine if p["kind"] == "stream"]
            if not docs and not blogs:
                continue
            g = by_work_game.get(primary)
            year = g.get("year") if g else RELEASE.get(primary)
            if not year:
                for n in names:
                    wg = by_work_game.get(n)
                    if wg:
                        year = wg.get("year")
                        break
            kinds = {k: sum(1 for p in docs if p["kind"] == k) for k in bt.DOC_KINDS}
            freq = collections.Counter(series_key(p["fm"]) for p in docs)
            scored = sorted(((pick_score(p, freq), p["date"], p) for p in docs), key=lambda t: (-t[0], t[1]))
            picks, seen, taken = [], set(), collections.Counter()
            for strict in (True, False):
                for s, d, p in scored:
                    if p in picks or len(picks) == 3:
                        continue
                    k = series_key(p["fm"])
                    if strict and (k in seen or taken[p["kind"]] >= 2 and len(docs) > 3):
                        continue
                    picks.append(p)
                    seen.add(k)
                    taken[p["kind"]] += 1
            picks.sort(key=lambda p: p["date"])
            pcnt = collections.Counter(n for p in docs for n in set(p["people"]) if n in slug_of)
            card = {
                "name": primary,
                "aliases": names[1:],
                "docs": len(docs),
                "blogs": len(blogs),
                "kinds": kinds,
                "picks": [{"title": bt.clean_title(p["fm"].get("display_title") or p["fm"].get("title"), 56), "kind": p["kind"], "date": p["date"], "url": url_of(p), "pub": bt.plain(re.sub(r"\s*[（(].*$", "", text_of(p["fm"].get("publication"))), 24)} for p in picks],
                "people": [{"name": n, "slug": slug_of[n], "n": c} for n, c in pcnt.most_common(3)],
            }
            if year:
                card["year"] = year
            if docs:
                yrs = sorted(int(p["date"][:4]) for p in docs)
                card["span"] = [yrs[0], yrs[-1]]
            for k in ("icon", "icon2", "color", "color2"):
                if w.get(k):
                    card[k] = w[k]
            if g:
                card["credits"] = g["slug"]
                card["title_zh"] = g.get("title_zh") or g.get("title")
            cards.append(card)
            for p in docs:
                gdocs[p["rel"]] = p
        if not cards:
            continue
        cards.sort(key=lambda c: (c.get("year") or 9999, -c["docs"]))
        for i, c in enumerate(cards):
            c["id"] = f"{gkey}-{i + 1}"
        gp = collections.Counter(n for p in gdocs.values() for n in set(p["people"]) if n in slug_of)
        yrs = [c["year"] for c in cards if c.get("year")]
        group_rows.append({
            "key": gkey, "label": glabel, "sub": gsub, "docs": len(gdocs),
            "from": min(yrs) if yrs and gkey[0] == "g" else None, "to": max(yrs) if yrs and gkey[0] == "g" else None,
            "people": [{"name": n, "slug": slug_of[n], "n": c} for n, c in gp.most_common(4)],
            "games": cards,
        })
        all_docs += len(gdocs)
    top = sorted((c for g in group_rows for c in g["games"]), key=lambda c: -c["docs"])[:8]
    games_out = {
        "docs": all_docs,
        "n": sum(len(g["games"]) for g in group_rows),
        "top": [{k: c[k] for k in ("id", "name", "docs", "icon", "icon2") if k in c} for c in top],
        "groups": group_rows,
    }

    out = {"overseas": overseas, "games": games_out}
    text = "# 由 tools/build-hubs.py 生成：海外媒体专访（/overseas/）和按游戏（/games/）两个横切专题页的数据。\n" + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000)
    io.open(ROOT / "_data" / "hubs.yml", "w", encoding="utf-8", newline="\n").write(text)
    print("hubs.yml:", "overseas", overseas["total"], "|", len(overseas["outlets"]), "outlets | games", games_out["n"], "in", len(group_rows), "groups,", games_out["docs"], "documents")
    for r in region_rows:
        print("  ", r["label"], r["n"], [(o["name"], o["n"]) for o in r["outlets"]])

    if tag_mode:
        tag_posts({p["rel"] for p, _ in members})


def _front_matter_end(lines):
    for n in range(1, len(lines)):
        if lines[n].rstrip() == "---":
            return n
    raise ValueError("no closing ---")


def set_tag(path, want):
    """Add TAG as the first of a post's topics (want=True) or take it off (want=False), editing only the
    topics lines: the block list where it already is (front matter has it either before the rows or after
    them), or a new one in front of the row list. Returns True when the file changed."""
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text[:3000]
    lines = text.replace("\r\r\n", "\n").replace("\r\n", "\n").split("\n")
    end = _front_matter_end(lines)
    before = yaml.load("\n".join(lines[1:end]), Loader=L)
    at = [n for n in range(1, end) if re.match(r"^topics:", lines[n])]
    if len(at) > 1:
        raise ValueError("two topics keys in " + str(path))
    if at:
        n = at[0]
        if lines[n].rstrip() == "topics:":
            m = n + 1
            while m < end and re.match(r"^\s*- ", lines[m]):
                m += 1
            items = lines[n + 1:m]
        else:                                                  # topics: [a, b] on one line
            got = yaml.safe_load(lines[n]).get("topics") or []
            m = n + 1
            items = ['- ' + json.dumps(t, ensure_ascii=False) for t in got]
        names = [yaml.safe_load(i.strip()[2:]) for i in items]
        if want and TAG in names:
            return False
        if not want and TAG not in names:
            return False
        quote = bool(items) and re.match(r'^\s*- "', items[0]) is not None
        if want:
            items = ['- "%s"' % TAG if quote else "- " + TAG] + items
        else:
            items = [i for i, nm in zip(items, names) if nm != TAG]
        lines[n:m] = (["topics:"] + items) if items else []
    else:
        if not want:
            return False
        row = next(n for n in range(1, end) if re.match(r"^(parallel_items|translation_segments):\s*$", lines[n]))
        lines[row:row] = ["topics:", "- " + TAG]
    end = _front_matter_end(lines)
    after = yaml.load("\n".join(lines[1:end]), Loader=L)
    expect = dict(before)
    names_after = after.get("topics") or []
    expect.pop("topics", None)
    got = dict(after)
    got.pop("topics", None)
    if got != expect or (want and names_after[:1] != [TAG]) or (not want and TAG in names_after):
        raise ValueError("the edit changed more than topics in " + str(path))
    out = "\n".join(lines)
    if crlf:
        out = out.replace("\n", "\r\n")
    Path(path).write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    return True


def tag_posts(member_rels):
    """TAG first in the topics of every member; off any post that carries it and is no longer a member."""
    added = removed = 0
    for rel in bt.git_files():
        if rel in member_rels:
            if set_tag(ROOT / rel, True):
                added += 1
        elif TAG in bt._BLOBS.get(rel, "")[:bt._BLOBS.get(rel, "").find("\n---", 4)]:
            if set_tag(ROOT / rel, False):
                removed += 1
    print("topic", TAG, "- added to", added, "posts, removed from", removed)


if __name__ == "__main__":
    main()
