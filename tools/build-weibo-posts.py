#!/usr/bin/env python3
"""Turn 2144jx's Weibo long articles (头条文章) into regular site posts.

    python tools/build-weibo-posts.py [--include-existing]

Reads P:/weibo/_work/dataset.json (articles) + fetched/art2_<id>.json (styled capture) and
writes _posts/<date>-<slug>.md. Dates are the article's first Weibo appearance (later
re-shares do not count). The 2024-10-24 article is already on the site as
_posts/2024-10-24-[长文]-拨云见日-从百代市到水脉图书馆.md, so it is skipped unless asked for.
Re-running rewrites only the files this script owns (marked by `weibo_article:` in the front matter).
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from weibo_common import WORK, CDN, article_html, esc_liquid  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
EXISTING = "2309405092965491015837"

SLUGS = {
    "2309404844134379946082": "model-study-part-2-3",
    "2309405329430427074632": "jleague-pokemon-prototypes-j1",
    "2309405272565131640835": "wind-and-wave-pv1-frame-analysis",
    "2309405191972716675358": "za-pv4-frame-analysis",
    "2309405139243294130232": "za-pv2-frame-analysis",
    "2309405138641998446823": "kanto-trip-game-freak-pilgrimage",
    "2309405109495591469119": "ptcg-terastal-festival-card-art",
    "2309405067522750677101": "ptcg-wcs-2024-virtual-prep",
    "2309404932874397680024": "sv-indigo-disk-pv3-frame-analysis",
    "2309404836130188296928": "model-study-part-1",
    "2309404820913207246885": "pokeamice-progress-report-2022-10",
    "2309404792238671790223": "tajiri-sugimori-endo-2016-interview-review",
    "2309404815182722630326": "live-a-pokemon-explorers-reflection",
    "2309404730351963734122": "swsh-legendary-design-analysis-2",
    "2309404799099588444854": "sv-pv3-frame-analysis",
    "2309404775939119644801": "sv-pv2-frame-analysis",
    "2309404754928244752721": "pla-gameplay-revisited",
    "2309404730353314038057": "swsh-legendary-design-analysis-1",
    "2309404672026815103417": "pla-pv2-frame-analysis",
    "2309404647313862951516": "pla-first-reveal-analysis",
    "2309404609394460721197": "pla-first-reveal-frame-notes",
    EXISTING: "mythology-from-gendai-to-library",
}

TAG_RULES = [
    (r"阿尔宙斯|传说 ?阿尔宙斯|\bLA\b", "宝可梦传说 阿尔宙斯"),
    (r"朱[＆&/ ]*紫|零之秘宝|SV", "宝可梦 朱/紫"),
    (r"剑[＆&/ ]*盾", "宝可梦 剑/盾"),
    (r"Z-A|ZA", "宝可梦传说 Z-A"),
    (r"风与波", "宝可梦 风与波"),
    (r"逐帧|PV", "逐帧分析"),
    (r"模型", "模型"),
    (r"访谈回顾|采访", "访谈回顾"),
    (r"J联赛", "J联赛"),
    (r"卡图|卡牌|PTCG|世界锦标赛", "宝可梦卡牌"),
    (r"建设进展|Pokeamice|站点", "站点"),
    (r"游记|巡礼", "巡礼"),
    (r"设定分析|传说宝可梦", "设定分析"),
]


def best_cover(urls):
    """The first landscape picture among the first few (a card cover is wide), else the first one."""
    from PIL import Image
    first = None
    for u in urls[:8]:
        name = u.rsplit("/", 1)[-1]
        try:
            with Image.open(WORK / "cos" / name) as im:
                w, h = im.size
        except Exception:
            continue
        if first is None:
            first = u
        if w / h >= 1.3:
            return u
    return first or (urls[0] if urls else "")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-existing", action="store_true")
    args = ap.parse_args()
    data = json.load(open(WORK / "dataset.json", encoding="utf-8"))
    first = {}
    for a in json.load(open(WORK / "articles.json", encoding="utf-8")):
        first[a["id"]] = min(first.get(a["id"], "9"), a["d"])
    for f in POSTS.glob("*.md"):
        if "weibo_article:" in f.read_text(encoding="utf-8", errors="ignore")[:1500]:
            f.unlink()
    n = 0
    # Keep intrinsic dimensions beside the posts: the reader can reserve image
    # space without rewriting the preserved article HTML or fetching the CDN.
    image_index = ROOT / "_data" / "weibo_article_images.json"
    dimensions = json.loads(image_index.read_text(encoding="utf-8")) if image_index.exists() else {}
    for a in sorted(data["articles"], key=lambda x: first[x["id"]]):
        if a["id"] == EXISTING and not args.include_existing:
            continue
        date = first[a["id"]][:10]
        slug = SLUGS[a["id"]]
        title = a["title"].strip()
        hay = title + " " + (a.get("preface") or "")
        tags = []
        for pat, tag in TAG_RULES:
            if re.search(pat, hay) and tag not in tags:
                tags.append(tag)
        body = article_html(a)
        imgs = re.findall(r'src="(%s[^"]+)"' % re.escape(CDN), body)
        from PIL import Image
        for url in imgs:
            image_file = WORK / "cos" / url.rsplit("/", 1)[-1]
            try:
                with Image.open(image_file) as image:
                    dimensions[url] = {"width": image.width, "height": image.height}
            except (OSError, ValueError):
                pass  # Missing archived images retain their existing metadata.
        pre = (a.get("preface") or "").strip().replace("\n", " ")
        text = re.sub(r"<[^>]+>", "", body)
        summary = pre or re.sub(r"\s+", " ", text)[:110]
        fm = [
            "---", "layout: original-article", f"title: {q(title)}", f"date: '{date}'",
            "categories: [长文分析, 宝可梦友会]",
            "tags: [" + ", ".join(q(t) for t in (tags + ["PokeAmice"])) + "]",
        ]
        if imgs:
            cover = best_cover(imgs)
            fm.append(f"image: {cover}")
            fm.append(f"card_image: {cover}")
        fm += [
            "author: 2144jx", "author_profile: false", 'archive_type: "article"',
            "publication: 微博头条文章 · 宝可梦友会", "weibo_article: " + a["id"],
            f"summary: {q(summary[:140])}",
            "source:", '  title: "微博头条文章"', f"  url: {a['url']}", '  source_type: "social"',
            "links:", '  - title: "微博头条文章原文"', f"    url: {a['url']}", '    domain: "weibo.com"', '    type: "social"',
            "workflow:", '  scan: "pending"', '  preprocess: "pending"', '  ocr: "pending"',
            '  translation: "pending"', '  proofreading: "done"', '  published: "done"',
            "entities:", "  organizations:", "  - Poke Amice Docs",
            "---", "",
        ]
        foot = (f'<p class="wbn-note">本文原发布于微博头条文章（专栏：宝可梦友会），{date}。图片已转存；'
                f'文中引用的微博保留为引用块，视频未收录。<a href="{a["url"]}" target="_blank" rel="nofollow noopener">微博原文</a>'
                f' · <a href="/notes/weibo/">更多随手发的碎片 →</a></p>')
        out = "\n".join(fm) + '\n<link rel="stylesheet" href="/assets/css/notes-archive.css">\n<div class="wbn-article">\n' + body + "\n</div>\n" + foot + "\n"
        (POSTS / f"{date}-{slug}.md").write_text(out, encoding="utf-8", newline="\n")
        n += 1
    image_index.write_text(json.dumps(dimensions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{n} posts written to {POSTS}")


if __name__ == "__main__":
    main()
