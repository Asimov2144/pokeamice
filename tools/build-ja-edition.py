"""The Japanese edition: one page per Western interview the site has translated into Japanese.

    python tools/build-ja-edition.py [--src ../ja-trial]

Reads the translation work outside the repo (ja-trial/: <stem>-full.json holds the checked Japanese
body, ja-meta/<stem>.json the title, dek, summary, captions and speaker names, ja-stems.txt which
posts go up) and the Chinese post itself, and writes

  _ja/<stem>.md            the Japanese page: the Chinese post's parallel_items with the Japanese in
                           `translation`, the original kept in `original`; rendered by the same
                           interview-editorial layout, which switches its labels on `lang: ja`
  _data/ja_edition.yml     stem -> Japanese URL, so the Chinese post can link to its Japanese page

Only interviews published in a language other than Japanese go here: a Japanese original is not
re-published as a Japanese page. The six whose source is itself an English translation of a
Japanese original (retrans) are left out. Every page says it is an AI translation.
"""
import argparse
import io
import json
import re
import urllib.parse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# outlet shown on the page, by the domain of the original link (inside a Wayback link, the archived domain)
OUTLETS = {
    "content.time.com": "TIME", "ign.com": "IGN", "gameinformer.com": "Game Informer", "eurogamer.net": "Eurogamer",
    "eurogamer.es": "Eurogamer.es", "eurogamer.de": "Eurogamer.de", "spong.com": "SPOnG", "1up.com": "1UP.com",
    "pokemon.com": "Pokemon.com", "jeuxvideo.com": "jeuxvideo.com", "multiplayer.it": "Multiplayer.it",
    "nintendolife.com": "Nintendo Life", "nintendoworldreport.com": "Nintendo World Report", "gamedeveloper.com": "Gamasutra",
    "hobbyconsolas.com": "Hobby Consolas", "elpais.com": "El País", "topofarmer.com": "Topofarmer",
    "pocketmonsters.net": "PocketMonsters.net", "gnn.gamer.com.tw": "巴哈姆特 GNN", "revistagq.com": "GQ España",
    "as.com": "MeriStation", "pokemontrash.com": "Pokémon Trash", "polygon.com": "Polygon", "gamespot.com": "GameSpot",
    "videogameschronicle.com": "VGC", "vg247.com": "VG247", "theguardian.com": "The Guardian",
    "drpez12.substack.com": "Dr. Pez", "lavacutcontent.com": "Nintendo Power", "archive.org": "Nintendo Acción",
    "computerandvideogames.com": "CVG", "gamepro.com": "GamePro", "g4tv.com": "G4", "officialnintendomagazine.co.uk": "Official Nintendo Magazine",
}
# the post's language field is wrong for these two (a French and a German site)
LANG_BY_DOMAIN = {"pokemontrash.com": "fr", "eurogamer.de": "de", "topofarmer.com": "es"}
LANG_NAMES = {"en": "英語", "es": "スペイン語", "fr": "フランス語", "it": "イタリア語", "de": "ドイツ語", "zh": "中国語"}
# Chinese prefixes the engine carried over into a title
TITLE_PREFIX = re.compile(r"^【(?:インタビュー翻訳|インタビュー|翻訳)】\s*")
# a caption that is only the photo's file name
FILENAME_CAPTION = re.compile(r"^[\w .\-]*\d[\w .\-]*$")
HAN_SIMPLIFIED = re.compile("[们这说话时对为个发开现还过进动问题读听让认识关东车门长间见觉线级经结给红绿蓝银钻铁龙鸟风飞马鱼页头买卖乐书习华单历压县变吗员园团处备复够奖实宫尔层岁岛师带帮广应张弹录归忆态总惊战户执扩拥择换摄敌无显术杀杂权极构标树样档桥检欢汉汤泽测济满灭灵热爱猎环电疗盖确种积稳竞笔签简类紧纪约纯纳纸练组细织终绍绘络绝统继续维综编缘缩网罗职联脑脸艺节苏范荐获虽补观规视览计订讨训议记讲许论设访证评词译试诚该详语误请课谁调谈谢谱贝负财责败货质购贯贵费资赏赛赞跃转轮软轻载较辆边达运远违连迟适选递遗释钟钱链销锁错键镇闪闭闻阅阶际陆陈险隐难韩顶项顺须顾预领频颜额饭饮馆鸣务濑刚国报专]")
# lines the archive itself wrote in Chinese, with no original to translate from
ARCHIVE_LINES = {
    "转载来源网站的导语": "転載元サイトによる前書き",
    "转载者补充：人物简介（资料截至2019年）": "転載者による補足：人物紹介（2019年時点の情報）",
}
# fields of the Chinese post that carry over unchanged
KEEP = ("date", "era_skin", "era", "source_kind", "archive_type", "original_link", "source_url", "interview_id")


def front_matter(path: Path) -> dict:
    m = re.search(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", path.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(m.group(1)) or {}


def domain(url: str) -> str:
    url = re.sub(r"^https?://web\.archive\.org/web/[^/]+/", "", url or "")
    return re.sub(r"^(https?://)?(www\.)?", "", url).split("/")[0].lower()


def zh_url(fm: dict, stem: str) -> str:
    """the Chinese post's URL under `permalink: /:categories/:title/` (checked against the built site by --check)"""
    if fm.get("permalink"):
        return fm["permalink"]
    cats = list(dict.fromkeys(str(c).lower() for c in fm.get("categories") or []))
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    return "/" + "/".join(cats + [slug]) + "/"


def clean_source_title(title: str, outlet: str) -> str:
    """the original article's title, without the Chinese notes the archive added to it"""
    t = re.sub(r"[（(][^（）()]*[一-鿿][^（）()]*[）)]", "", str(title or "")).strip()
    if re.search(r"[A-Za-z]", t):
        t = re.split(r"\s+(?=[一-鿿])", t)[0].strip()
    if not t or HAN_SIMPLIFIED.search(t):
        return outlet
    return t


def description(meta: dict) -> str:
    text = meta.get("dek") or meta.get("summary") or ""
    if len(text) <= 120:
        return text
    cut = text[:120]
    end = cut.rfind("。")
    return cut[: end + 1] if end >= 40 else cut.rstrip() + "…"


def build(src: Path) -> dict:
    stems = (src / "ja-stems.txt").read_text(encoding="utf-8").split()
    people = yaml.safe_load((ROOT / "_data" / "people.yml").read_text(encoding="utf-8"))
    by_name = {e["name"]: e for e in people if e.get("name")}
    out_dir = ROOT / "_ja"
    out_dir.mkdir(exist_ok=True)
    pairs, slugs = {}, set()
    for stem in stems:
        post = next(ROOT.glob(f"_posts/**/{stem}.md"))
        fm = front_matter(post)
        r = json.loads((src / f"{stem}-full.json").read_text(encoding="utf-8"))
        meta = json.loads((src / "ja-meta" / f"{stem}.json").read_text(encoding="utf-8"))
        assert not r.get("retrans"), stem
        source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
        link = fm.get("original_link") or fm.get("source_url") or source.get("url") or ""
        dom = domain(link)
        outlet = OUTLETS[dom]
        lang = LANG_BY_DOMAIN.get(dom) or fm.get("original_lang") or source.get("language") or fm.get("source_language")
        assert lang in LANG_NAMES and lang != "ja", (stem, lang)

        # the body: every non-image item with an original takes the next Japanese paragraph, in order
        final = iter(r["final"])
        sources = iter(r["original"])
        caps = iter(meta.get("captions") or [])
        chapters = iter(meta.get("chapters") or [])
        items, dropped = [], 0
        for it in fm.get("parallel_items") or []:
            if not isinstance(it, dict):
                continue
            it = dict(it)
            if it.get("type") != "image" and not it.get("original"):
                if it.get("translation") in ARCHIVE_LINES:  # the archive's own section heads, written in Chinese
                    it["translation"] = ARCHIVE_LINES[it["translation"]]
                    items.append(it)
                else:
                    dropped += 1  # nothing to translate from: a Chinese-only line of the archive's
                continue
            # translator's notes and pull quotes are written for the Chinese page
            for k in ("note", "comment", "pull"):
                it.pop(k, None)
            if it.get("chapter"):
                it["chapter"] = next(chapters)
            if it.get("type") == "image":
                if it.get("caption"):
                    cap = next(caps)
                    if FILENAME_CAPTION.match(str(it["caption"])):
                        it.pop("caption")
                    else:
                        it["caption"] = cap
                it.pop("alt", None)
                for k in ("original", "translation"):
                    if k in it and not str(it[k]).startswith(("/", "http")):
                        it.pop(k)
            else:
                it["translation"] = next(final)
                # the paragraph the translation was made from; a post re-imported since then must not be
                # paired with a translation of its old text (differences in punctuation only - mojibake quotes - are fine,
                # and the clean text the translation used is kept)
                used = next(sources)
                here = re.sub(r"\s+", " ", str(it["original"])).strip()
                if here != used:
                    same = re.sub(r"[\W_]", "", here) == re.sub(r"[\W_]", "", used)  # letters and digits alike
                    assert same, f"{stem}: the post changed since it was translated"
                    it["original"] = used
            if it.get("speaker"):
                it["speaker"] = meta["speakers"].get(it["speaker"], it["speaker"])
            items.append(it)
        assert next(final, None) is None and next(caps, None) is None and next(chapters, None) is None, f"{stem}: left over"
        if dropped:
            print(f"  {stem}: {dropped} item(s) without an original left out")

        # people on the cover keep their portraits and pages: the layout looks them up by the Chinese name
        speaker_zh = {ja: zh for zh, ja in meta["speakers"].items() if ja != zh and zh in by_name}
        people_ja = []
        for zh in (fm.get("entities") or {}).get("people") or []:
            e = by_name.get(zh)
            if e and e.get("kind") != "character":
                ja = meta["speakers"].get(zh) or next((a for a in e.get("aliases") or [] if re.search(r"[぀-ヿ一-鿿]", a)), None)
                people_ja.append(ja or next((a for a in e.get("aliases") or [] if re.fullmatch(r"[A-Za-z .'\-]+", a)), zh))

        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
        assert slug not in slugs, slug
        slugs.add(slug)
        url = f"/ja/{slug}/"
        page = {
            "layout": "interview-editorial", "lang": "ja",
            "title": TITLE_PREFIX.sub("", meta["title"]).strip(),
        }
        if meta.get("display_title"):
            page["display_title"] = meta["display_title"]
        for k in ("dek", "summary", "intro"):
            if meta.get(k):
                page[k] = meta[k]
        page["description"] = description(meta)
        page.update({k: fm[k] for k in KEEP if fm.get(k)})
        page.update({
            "permalink": url, "search": False, "zh_url": zh_url(fm, stem), "zh_stem": stem,
            "source_name": outlet,
            "source": {"title": clean_source_title(source.get("title") or fm.get("publication") or "", outlet), "url": link, "language": lang},
            "original_lang": lang, "original_lang_name": LANG_NAMES[lang], "translation_lang": "ja",
            "translation_status": "ai-machine-translated",
            "interviewee": meta.get("interviewee") or "、".join(people_ja),
            "people_ja": people_ja,
            "speaker_zh": speaker_zh,
            "parallel_items": items,
        })
        text = yaml.safe_dump(page, allow_unicode=True, sort_keys=False, width=10**6)
        io.open(out_dir / f"{stem}.md", "w", encoding="utf-8", newline="\n").write("---\n" + text + "---\n")
        pairs[stem] = url
    stale = [p for p in out_dir.glob("*.md") if p.stem not in pairs]
    for p in stale:
        p.unlink()
    io.open(ROOT / "_data" / "ja_edition.yml", "w", encoding="utf-8", newline="\n").write(
        "# 日文版：中文帖（文件名）→ 日文页网址。tools/build-ja-edition.py 生成，别手改。\n"
        + yaml.safe_dump(pairs, allow_unicode=True, sort_keys=True, width=10**6))
    print(f"{len(pairs)} Japanese pages; removed {len(stale)} stale")
    return pairs


def check(site: Path) -> int:
    """after a build: every Japanese page exists and links to a Chinese page that exists and links back"""
    bad = 0
    for p in sorted((ROOT / "_ja").glob("*.md")):
        fm = front_matter(p)
        ja = site / fm["permalink"].strip("/") / "index.html"
        zh = site / fm["zh_url"].strip("/") / "index.html"
        if not ja.exists() or not zh.exists():
            print("missing", p.stem, ja.exists(), zh.exists())
            bad += 1
            continue
        # relative_url percent-encodes the Chinese category names in a URL
        zh_href = urllib.parse.quote(fm["zh_url"], safe="/")
        if f'href="{fm["permalink"]}"' not in zh.read_text(encoding="utf-8") or f'href="{zh_href}"' not in ja.read_text(encoding="utf-8"):
            print("no cross link", p.stem)
            bad += 1
    print(f"checked {len(list((ROOT / '_ja').glob('*.md')))} pairs, {bad} bad")
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT.parent / "ja-trial"))
    ap.add_argument("--check", metavar="SITE_DIR", help="check a built _site instead of generating")
    args = ap.parse_args()
    raise SystemExit(check(Path(args.check)) if args.check else (build(Path(args.src)) and 0))
