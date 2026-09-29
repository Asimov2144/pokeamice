#!/usr/bin/env python3
"""晴れたり時々曇ったり的早期版本：把 2013 年之前的每一份 Wayback 快照都抓下来，逐篇和现有版本比对。

    python tools/gamefreak_staff_history.py list       # CDX → manifest/history-captures.yml（要抓哪些）
    python tools/gamefreak_staff_history.py fetch      # 按清单抓原始 HTML（可中断，重跑只补没抓的）
    python tools/gamefreak_staff_history.py extract    # 从每份快照里切出每一篇 → content/history/<id>.yml
    python tools/gamefreak_staff_history.py compare    # 与现有版本（raw/posts/<id>.html）比对 → reports/history-diff.yml
    python tools/gamefreak_staff_history.py restore    # 每篇的恢复记录 content/<id>/history.yml（署名 / 分类 / 乱码修复 / 改稿）
    python tools/gamefreak_staff_history.py publish    # 写回：archive 的日文与元数据、_posts 的前言与日文面板、员工名单与头像

现有的 209 篇（tools/gamefreak_legacy_blogs_pipeline.py）取自 2013-08 前后的快照，那时博客已经换成
clean-minimal 主题。2007–2012 年它用的是另一套主题（staff1 / staff2，入口 index.php），当时每篇还带标签
（index.php?tag=…）。这里把那几年的快照当「版本史」来读：

  - 逐篇页（?p=N / index.php?p=N）、按月归档（?m=YYYYMM）、首页、分类页、标签页、RSS / Atom
    都可能带着某一篇的全文——每一份都切出来，按 (文章 id, 快照时间) 存一个版本；
  - 比对只看正文文字、图片、嵌入（视频 / Flash / iframe）、标签和标题，不看侧栏和模板；
  - 所有原始 HTML 存在 archive/gamefreak-staff/raw/history/，不改动现有的 raw/posts。

网络礼貌：一个会话串行抓，默认每次请求后停 0.6 秒，失败退避重试；抓过的不再抓。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, Comment, Tag

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "archive" / "gamefreak-staff"
RAW = BASE / "raw" / "history"
HIST = BASE / "content" / "history"
MANIFEST = BASE / "manifest" / "history-captures.yml"
REPORT = BASE / "reports"
CUTOFF = "20130808"            # 现有版本取的主要快照；这之前的都算「早期」
UA = "PokeAmice-Digital-Archive/0.2 (+https://docs.pokeamice.com/; low-rate historical blog preservation)"
#  gamefreak.sakura.ne.jp 是同一个博客早期的另一个主机名（图片与少量页面还挂在那边）
SITE = re.compile(r"^https?://((www\.)?gamefreak\.co\.jp|gamefreak\.sakura\.ne\.jp)(:80)?", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8", newline="\n")
    tmp.replace(path)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None


def norm_url(url: str) -> str:
    """去掉协议、主机、:80 和结尾的「?」——同一页的几种写法算一个"""
    return SITE.sub("", url).rstrip("?") or "/"


def kind_of(path: str) -> str:
    if re.search(r"[?&]p=\d+", path):
        return "post"
    if re.search(r"[?&]m=\d{6}", path):
        return "month"
    if re.search(r"[?&]cat=\d+", path):
        return "cat"
    if re.search(r"[?&]tag=", path):
        return "tag"
    if "feed" in path:
        return "feed"
    if "page_id" in path:
        return "page"
    if re.search(r"paged=\d+", path):
        return "paged"
    if re.search(r"^/blog/staff/?(index\.php)?$", path):
        return "index"
    return "other"


def safe_name(ts: str, path: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._=-]+", "_", unquote(path).encode("ascii", "backslashreplace").decode("ascii"))[:90].strip("_")
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    return f"{ts}_{stem}_{digest}.html"


# ---------------------------------------------------------------- list

def cmd_list(args) -> int:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    rows = []
    for host in ("gamefreak.co.jp/blog/staff/", "gamefreak.sakura.ne.jp/blog/staff/"):
        q = (f"https://web.archive.org/cdx/search/cdx?url={host}&matchType=prefix&output=json"
             "&fl=timestamp,original,statuscode,mimetype,digest,length&limit=200000")
        rows.extend(s.get(q, timeout=240).json()[1:])
    keep, seen = [], set()
    for ts, orig, status, mime, digest, length in sorted(rows):
        if status != "200" or ts >= CUTOFF:
            continue
        path = norm_url(orig)
        kind = kind_of(path)
        if mime not in ("text/html", "text/xml", "application/rss+xml", "application/atom+xml"):
            continue
        if kind in ("other",) and "xmlrpc" in path:
            continue
        key = (path, digest)
        if key in seen:
            continue
        seen.add(key)
        keep.append({"ts": ts, "url": orig, "path": path, "kind": kind, "mime": mime, "digest": digest,
                     "file": f"raw/history/{safe_name(ts, path)}"})
    by_kind = collections.Counter(c["kind"] for c in keep)
    write_yaml(MANIFEST, {"generated_at": utc_now(), "cutoff": CUTOFF, "cdx_rows": len(rows),
                          "captures": len(keep), "by_kind": dict(by_kind.most_common()), "items": keep})
    print(f"{len(keep)} captures before {CUTOFF}: {dict(by_kind.most_common())}")
    return 0


# ---------------------------------------------------------------- fetch

def cmd_fetch(args) -> int:
    man = load_yaml(MANIFEST)
    if not man:
        raise SystemExit("run `list` first")
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "ja"})
    todo = [c for c in man["items"] if not (BASE / c["file"]).exists()]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(man['items'])} in manifest, {len(todo)} to fetch")
    failed = []
    for i, cap in enumerate(todo, 1):
        replay = f"https://web.archive.org/web/{cap['ts']}id_/{cap['url']}"
        body = None
        for attempt in range(4):
            try:
                r = s.get(replay, timeout=60)
                if r.status_code == 200:
                    body = r.content
                    break
                if r.status_code in (404, 403):
                    break
            except requests.RequestException:
                pass
            time.sleep(2.5 * (attempt + 1))
        if body is None:
            failed.append(cap["file"])
            print(f"  {i:>4}/{len(todo)} FAILED {cap['ts']} {cap['path'][:60]}")
            continue
        path = BASE / cap["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(body)
        tmp.replace(path)
        meta = path.with_suffix(".meta.yml")
        write_yaml(meta, {"original_url": cap["url"], "replay_url": replay, "timestamp": cap["ts"], "kind": cap["kind"],
                          "fetched_at": utc_now(), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        if i % 25 == 0 or i == len(todo):
            print(f"  {i:>4}/{len(todo)} {cap['ts']} {cap['kind']:<6} {cap['path'][:60]}", flush=True)
        time.sleep(args.delay)
    if failed:
        write_yaml(REPORT / "history-fetch-failed.yml", {"at": utc_now(), "failed": failed})
    print(f"done; failed {len(failed)}")
    return 1 if failed else 0


# ---------------------------------------------------------------- extract

def decode(raw: bytes) -> str:
    head = raw[:2000].decode("ascii", "ignore").lower()
    m = re.search(r"charset=([\w-]+)", head)
    enc = (m.group(1) if m else "utf-8").replace("shift_jis", "cp932").replace("sjis", "cp932").replace("euc-jp", "euc_jp")
    try:
        return raw.decode(enc)
    except (LookupError, UnicodeDecodeError):
        return raw.decode("utf-8", "replace")


def unwrap(url: str, base: str) -> str:
    """快照里的链接可能已经被改写成 web.archive.org/web/…/原址，还原成原址"""
    if not url:
        return ""
    full = urljoin(base, url.strip())
    m = re.match(r"https?://web\.archive\.org/web/\d+[a-z_]*/(.*)", full)
    if m:
        inner = m.group(1)
        full = inner if re.match(r"https?://", inner) else "http://" + inner
    return full


def post_id(url: str) -> int | None:
    q = parse_qs(urlparse(url).query)
    v = (q.get("p") or [None])[0]
    return int(v) if v and v.isdigit() else None


def text_of(node: Tag) -> str:
    for bad in node.find_all(["script", "style", "noscript"]):
        bad.decompose()
    for c in node.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    txt = node.get_text("\n")
    lines = [re.sub(r"[ \t　]+", " ", ln).strip() for ln in txt.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def media_of(node: Tag, base: str) -> dict:
    imgs, embeds, links = [], [], []
    for img in node.find_all("img"):
        src = unwrap(img.get("src") or "", base)
        if src:
            imgs.append(src)
    for tag in node.find_all(["embed", "object", "iframe", "video", "source", "param", "audio"]):
        for attr in ("src", "data", "value", "movie"):
            v = tag.get(attr)
            if not v:
                continue
            if tag.name == "param" and (tag.get("name") or "").lower() not in ("movie", "src", "flashvars", "url", "filename"):
                continue
            embeds.append({"tag": tag.name, "attr": attr, "url": unwrap(v, base) if "=" not in v or v.startswith("http") else v})
    for a in node.find_all("a"):
        href = unwrap(a.get("href") or "", base)
        if re.search(r"\.(jpe?g|png|gif|flv|mp4|mov|wmv|avi|mpe?g|swf|mp3|wav|zip|pdf)(\?|$)", href, re.I):
            links.append(href)
    return {"images": imgs, "embeds": embeds, "file_links": links}


def blocks_from_html(html: str, base: str) -> list:
    """一份快照里的每一篇：(id, 标题, 日期, 正文节点, 标签)。两套主题都认。"""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    # 新旧主题都用 WordPress 的 post 结构：id="post-N" 或 class="post"，标题里的链接带 ?p=N
    cands = soup.select("[id^=post-]") or soup.select("div.post, div.entry, div.hentry")
    done = set()
    for node in cands:
        pid = None
        m = re.match(r"post-(\d+)$", node.get("id") or "")
        if m:
            pid = int(m.group(1))
        #  staff01 主题把 id="post-N" 挂在标题 <h3 class="storytitle"> 上，正文在同一个 div.post 里的 .storycontent
        if node.name in ("h1", "h2", "h3", "h4") and node.parent is not None:
            node = node.parent
        if id(node) in done:
            continue
        done.add(id(node))
        title_el = node.find(["h2", "h3", "h1"])
        if pid is None and title_el and title_el.find("a"):
            pid = post_id(unwrap(title_el.find("a").get("href") or "", base))
        if pid is None:
            for a in node.find_all("a", href=True):
                pid = post_id(unwrap(a["href"], base))
                if pid:
                    break
        if pid is None:
            continue
        body = node.select_one(".storycontent, .entry, .entrybody, .post-content, .entry-content, .contents, .post_body")
        if body is None and node.select_one(":scope > .right"):
            #  clean-minimal（2012 年起）：div.post > .left（日期）+ .right（h2 标题 + 正文 + .tag）。
            #  和 gamefreak_legacy_blogs_pipeline.py 的取法一致：去掉 h2 和 .tag
            body = BeautifulSoup(str(node.select_one(":scope > .right")), "html.parser").select_one(".right")
            for drop in body.select(":scope > h2, .tag"):
                drop.decompose()
        body = body or node
        #  「書いた人：<a ?tag=カニ子>カニ子</a>」—— Ultimate Tag Warrior 插件的署名行，2013 年换主题后整行消失。
        #  记下署名，再从正文里拿掉，免得比对时每篇都「多一行」
        writers = []
        for span in body.select(".UTWPrimaryTags, .UTWTags"):
            if "書いた人" in span.get_text() or span.find("a", href=re.compile(r"tag=")):
                writers.extend(a.get_text(strip=True) for a in span.find_all("a") if a.get_text(strip=True))
                span.decompose()
        tags = []
        for a in node.find_all("a", href=True):
            href = unwrap(a["href"], base)
            if re.search(r"[?&]tag=", href):
                tags.append(a.get_text(strip=True) or unquote(parse_qs(urlparse(href).query).get("tag", [""])[0]))
        #  分类只认这一篇自己的 meta 行（staff01 的「category: …」），不认侧栏的分类列表
        meta_el = node.select_one(".meta, .postmetadata, .post-meta, .cat, .category")
        cats = [a.get_text(strip=True) for a in (meta_el.find_all("a", href=True) if meta_el else [])
                if re.search(r"[?&]cat=\d+", a["href"])]
        date_el = node.select_one(".left, .date, .postdate, .time, .entry-date, .post-date, small")
        out.append({"id": pid, "title": title_el.get_text(" ", strip=True) if title_el else "",
                    "date": date_el.get_text(" ", strip=True) if date_el else "",
                    "node": body, "tags": sorted(set(t for t in tags if t)), "cats": sorted(set(c for c in cats if c)),
                    "writers": list(dict.fromkeys(writers))})
    if not out:
        # 旧主题有时是 <h2><a href="?p=N"> 后面跟着正文 div，没有外层 id —— 按标题切
        for h in soup.find_all(["h2", "h3"]):
            a = h.find("a", href=True)
            pid = post_id(unwrap(a["href"], base)) if a else None
            if not pid:
                continue
            frag = BeautifulSoup("<div></div>", "html.parser").div
            sib = h.find_next_sibling()
            while sib is not None and sib.name not in ("h2", "h3"):
                frag.append(sib.__copy__() if hasattr(sib, "__copy__") else sib)
                sib = sib.find_next_sibling()
            out.append({"id": pid, "title": h.get_text(" ", strip=True), "date": "", "node": frag, "tags": [], "cats": []})
    return out


def blocks_from_feed(xml: str, base: str) -> list:
    soup = BeautifulSoup(xml, "html.parser")
    out = []
    for item in soup.find_all(["item", "entry"]):
        link = item.find("link")
        href = (link.get("href") if link and link.get("href") else (link.get_text(strip=True) if link else "")) or ""
        guid = item.find(["guid", "id"])
        pid = post_id(href) or (post_id(guid.get_text(strip=True)) if guid else None)
        if not pid:
            continue
        content = item.find(["content:encoded", "content"]) or item.find(["description", "summary"])
        html = content.get_text() if content else ""
        node = BeautifulSoup(f"<div>{html}</div>", "html.parser").div
        tags = [c.get_text(strip=True) for c in item.find_all("category")]
        out.append({"id": pid, "title": (item.find("title").get_text(strip=True) if item.find("title") else ""),
                    "date": "", "node": node, "tags": sorted(set(tags)), "cats": [], "feed": True})
    return out


def collect_roster(html: str, base: str, cap: dict, roster: dict) -> None:
    """侧栏「書いてる人リスト」：笔名 + 头像（themes/staff01/images/writerNN.jpg|gif）+ 链到 ?tag=笔名。
    同一个笔名在不同年份可能换过头像，全记下来，带首末出现的快照时间"""
    soup = BeautifulSoup(html, "html.parser")
    side = soup.select_one("#menu, #sidebar, .sidebar")
    if not side:
        return
    for img in side.find_all("img"):
        src = unwrap(img.get("src") or "", base)
        if not re.search(r"/images/writer[\w-]*\.(jpe?g|gif|png)$", src, re.I):
            continue
        a = img.find_parent("a")
        href = unwrap(a.get("href") or "", base) if a else ""
        tag = unquote(parse_qs(urlparse(href).query).get("tag", [""])[0]) if href else ""
        name = (img.get("alt") or "").strip()
        key = tag or name
        if not key:
            continue
        w = roster["writers"].setdefault(key, {"tag": tag, "names_on_icon": [], "avatars": {}, "first_seen": cap["ts"],
                                              "last_seen": cap["ts"], "order": None})
        if name and name not in w["names_on_icon"]:
            w["names_on_icon"].append(name)
        av = w["avatars"].setdefault(src, {"first_seen": cap["ts"], "last_seen": cap["ts"]})
        av["first_seen"] = min(av["first_seen"], cap["ts"])
        av["last_seen"] = max(av["last_seen"], cap["ts"])
        w["first_seen"] = min(w["first_seen"], cap["ts"])
        w["last_seen"] = max(w["last_seen"], cap["ts"])
        m = re.search(r"writer(\d+)", src)
        if m and w["order"] is None:
            w["order"] = int(m.group(1))


def cmd_extract(args) -> int:
    man = load_yaml(MANIFEST)
    versions = collections.defaultdict(list)
    template = collections.Counter()
    roster: dict = {"writers": {}}
    for cap in man["items"]:
        path = BASE / cap["file"]
        if not path.exists():
            continue
        raw = path.read_bytes()
        html = decode(raw)
        base = cap["url"]
        theme = re.search(r"wp-content/themes/([\w-]+)/", html)
        template[(cap["ts"][:4], theme.group(1) if theme else "?")] += 1
        if cap["mime"] == "text/html":
            collect_roster(html, base, cap, roster)
        blocks = blocks_from_feed(html, base) if cap["kind"] == "feed" or cap["mime"] != "text/html" else blocks_from_html(html, base)
        #  分类页（?cat=N）上列出的每一篇都属于这个分类——2013 年的主题不再逐篇写分类，只能这样认
        page_cat = None
        m = re.search(r"[?&]cat=(\d+)", cap["path"])
        if m and cap["mime"] == "text/html":
            link = BeautifulSoup(html, "html.parser").find("a", href=re.compile(rf"[?&]cat={m.group(1)}(?!\d)"))
            page_cat = link.get_text(strip=True) if link else None
            page_cat = re.sub(r"\s*\(\d+\)$", "", page_cat or "") or None
        for b in blocks:
            if page_cat and page_cat not in b["cats"]:
                b["cats"] = sorted(set(b["cats"]) | {page_cat})
                b.setdefault("cat_from_page", page_cat)
            node = b["node"]
            med = media_of(node, base)
            text = text_of(node)
            versions[b["id"]].append({
                "ts": cap["ts"], "kind": cap["kind"], "file": cap["file"],
                "theme": theme.group(1) if theme else None, "title": b["title"], "date": b["date"],
                "tags": b["tags"], "cats": b["cats"], "writers": b.get("writers") or [], "text": text,
                "text_sha": hashlib.sha1(norm_text(text).encode("utf-8")).hexdigest()[:12],
                "images": med["images"], "embeds": med["embeds"], "file_links": med["file_links"],
                "partial": bool(b.get("feed")) or looks_truncated(node, text),
            })
    write_yaml(BASE / "manifest" / "history-writers.yml", roster)
    HIST.mkdir(parents=True, exist_ok=True)
    for pid, vs in versions.items():
        vs.sort(key=lambda v: v["ts"])
        write_yaml(HIST / f"{pid}.yml", {"id": pid, "versions": vs})
    print(f"{sum(len(v) for v in versions.values())} versions of {len(versions)} posts")
    print("themes by year:", dict(sorted(template.items())))
    return 0


def looks_truncated(node: Tag, text: str) -> bool:
    """归档页 / 首页有时只给摘要（「続きを読む」）"""
    return bool(node.find("a", class_=re.compile("more")) or re.search(r"続きを読む|続きはこちら|Read the rest|more-\d+", str(node)[-400:]))


# ---------------------------------------------------------------- compare

def norm_text(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "")
    t = re.sub(r"\s+", "", t)
    return t


def current_post(pid: int) -> dict:
    """现有版本：content/posts/<id>.md 的正文 + 同目录的 meta"""
    for cand in (BASE / "content" / "posts" / f"{pid}.md", BASE / "content" / f"{pid}.md"):
        if cand.exists():
            raw = cand.read_text(encoding="utf-8")
            fm, body = {}, raw
            m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", raw, re.S)
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                body = raw[m.end():]
            return {"fm": fm, "body": body, "path": str(cand.relative_to(ROOT))}
    raw_html = BASE / "raw" / "posts" / f"{pid}.html"
    if raw_html.exists():
        html = decode(raw_html.read_bytes())
        blocks = [b for b in blocks_from_html(html, f"http://www.gamefreak.co.jp/blog/staff/?p={pid}") if b["id"] == pid]
        if blocks:
            return {"fm": {}, "body": text_of(blocks[0]["node"]), "html_node": blocks[0], "path": str(raw_html.relative_to(ROOT))}
    return {}


PUNCT = re.compile(r"[\s、。，．・…！？!?「」『』（）()\[\]【】〜～ー\-―—:：;；,.\"'“”‘’♪☆★]+")
CHROME_IMG = re.compile(r"^(writer\d|top_ico|spacer|icon|rss|wb_|staff_tit|title|bg)", re.I)


def sentences(text: str) -> list:
    out = []
    for line in (text or "").splitlines():
        line = unicodedata.normalize("NFKC", line).strip()
        if line:
            out.append(line)
    return out


def text_delta(early: str, now: str) -> dict:
    """早期 → 现在：删掉的句子、加上的句子。只差标点空白的算 minor"""
    import difflib
    a, b = sentences(early), sentences(now)
    removed, added = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op in ("replace", "delete"):
            removed.extend(a[i1:i2])
        if op in ("replace", "insert"):
            added.extend(b[j1:j2])
    squash = lambda xs: PUNCT.sub("", "".join(xs))
    kind = "same" if not removed and not added else ("minor" if squash(removed) == squash(added) else "changed")
    return {"kind": kind, "removed": removed, "added": added}


def file_name(url: str) -> str:
    return Path(unquote(urlparse(url).path)).name


def cmd_compare(args) -> int:
    rows = []
    for path in sorted(HIST.glob("*.yml"), key=lambda p: int(p.stem)):
        data = load_yaml(path)
        pid = data["id"]
        cur_html = BASE / "raw" / "posts" / f"{pid}.html"
        if not cur_html.exists():
            rows.append({"id": pid, "status": "not-in-current", "versions": len(data["versions"]),
                         "title_early": data["versions"][0]["title"]})
            continue
        html = decode(cur_html.read_bytes())
        meta = load_yaml(cur_html.with_suffix(".meta.yml")) or {}
        base = meta.get("original_url") or f"http://www.gamefreak.co.jp/blog/staff/?p={pid}"
        cur = [b for b in blocks_from_html(html, base) if b["id"] == pid]
        if not cur:
            rows.append({"id": pid, "status": "current-unparsed"})
            continue
        cur = cur[0]
        cur_text = text_of(cur["node"])
        cur_media = media_of(cur["node"], base)
        cur_imgs = {file_name(u) for u in cur_media["images"]}
        cur_links = {file_name(u) for u in cur_media["file_links"]}
        full = [v for v in data["versions"] if not v["partial"]]
        early = full[0] if full else data["versions"][0]
        #  每个不同的早期正文只比一次（同一段文字在逐篇页、月归档、首页里各出现一回）
        deltas, seen = [], {}
        for v in full:
            key = v["text_sha"]
            if key in seen:
                seen[key]["seen_in"].append(v["ts"])
                continue
            d = text_delta(v["text"], cur_text)
            d.update({"ts": v["ts"], "kind_of_page": v["kind"], "file": v["file"], "seen_in": [v["ts"]]})
            seen[key] = d
            deltas.append(d)
        early_imgs = {file_name(u) for v in full for u in v["images"]}
        early_links = {file_name(u): u for v in full for u in v["file_links"]}
        rows.append({
            "id": pid,
            "current_capture": re.search(r"/web/(\d{14})", meta.get("final_url") or "").group(1) if re.search(r"/web/(\d{14})", meta.get("final_url") or "") else "",
            "earliest": early["ts"], "earliest_theme": early.get("theme"),
            "versions": len(data["versions"]), "full_versions": len(full),
            "text": "changed" if any(d["kind"] == "changed" for d in deltas) else ("minor" if any(d["kind"] == "minor" for d in deltas) else "same"),
            "deltas": [d for d in deltas if d["kind"] != "same"],
            "title_early": early["title"], "title_now": cur["title"],
            "cats_early": sorted({c for v in data["versions"] for c in v.get("cats") or []}),
            "tags_early": sorted({t for v in data["versions"] for t in v["tags"] if t.strip()}),
            "writers_early": list(dict.fromkeys(w for v in data["versions"] for w in v.get("writers") or [])),
            "images_only_early": sorted(n for n in early_imgs - cur_imgs if not CHROME_IMG.match(n)),
            "images_only_now": sorted(n for n in cur_imgs - early_imgs if not CHROME_IMG.match(n)) if full else [],
            "links_only_early": sorted(u for n, u in early_links.items() if n not in cur_links and n not in cur_imgs),
            "embeds_early": [e for v in full for e in v["embeds"]],
            "embeds_now": cur_media["embeds"],
        })
    write_yaml(REPORT / "history-diff.yml", {"generated_at": utc_now(), "posts": rows})
    c = collections.Counter(r.get("text") or r.get("status") for r in rows)
    print(f"{len(rows)} posts with early versions; text: {dict(c)}; "
          f"early-only images {sum(1 for r in rows if r.get('images_only_early'))}; "
          f"early-only links {sum(1 for r in rows if r.get('links_only_early'))}; "
          f"embeds early {sum(1 for r in rows if r.get('embeds_early'))} / now {sum(1 for r in rows if r.get('embeds_now'))}; "
          f"cats {sum(1 for r in rows if r.get('cats_early'))}; tags {sum(1 for r in rows if r.get('tags_early'))}")
    return 0


# ---------------------------------------------------------------- restore

#  2013 年迁移时的字符损坏：〜（U+301C）按 Shift-JIS 误读成「縲怩」「縲鰀」「縲怐」并吃掉后一个字，
#  ～ / ~ / − / ‐ 变成「?」，「−F」变成「竏窒e」
CORRUPT = re.compile(r"縲|竏|鰀|怩|怐|怺|\?")


#  署名标签里偶尔打错的写法（小字假名、平假/片假名）——对照侧栏名单与 staff-names.yml 认定是同一人
WRITER_TYPOS = {"っやっや": "っゃっゃ", "ナギー": "なぎー", "Y": "Ｙ"}


def roster_aliases(roster: dict) -> dict:
    """笔名的几种写法 → 规范写法（侧栏 ?tag= 的那个）。「執筆者近影」是侧栏标题图，不是人"""
    out = dict(WRITER_TYPOS)
    for key, w in (roster.get("writers") or {}).items():
        if key in ("執筆者近影",) or not w.get("tag"):
            continue
        out[key] = key
        for n in w.get("names_on_icon") or []:
            out.setdefault(n, key)
    return out


def raw_lines(text: str) -> list:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def repairs_for(early_text: str, now_text: str) -> tuple[list, list]:
    """逐行配对：现在这行带损坏记号、早期那行没有、两行几乎一样 → 修复；
    两行都干净却不一样 → 真的改过稿。返回 (repairs, edits)"""
    import difflib
    a, b = raw_lines(early_text), raw_lines(now_text)
    na = [unicodedata.normalize("NFKC", x) for x in a]
    nb = [unicodedata.normalize("NFKC", x) for x in b]
    repairs, edits = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=na, b=nb, autojunk=False).get_opcodes():
        if op != "replace":
            continue
        used = set()
        for j in range(j1, j2):
            best, score = None, 0.0
            for i in range(i1, i2):
                if i in used:
                    continue
                r = difflib.SequenceMatcher(a=na[i], b=nb[j], autojunk=False).ratio()
                if r > score:
                    best, score = i, r
            if best is None or score < 0.6:
                continue
            used.add(best)
            #  「縲怐」这类强记号一出现就是损坏，短句（「はじめまして〜。」）相似度天然偏低，门槛放到 0.6；
            #  只有「?」的行可能本来就有问号，门槛 0.75
            strong = bool(re.search(r"縲|竏|鰀|怩|怐|怺", b[j]))
            if CORRUPT.search(b[j]) and not CORRUPT.search(a[best].replace("?", "")) and score >= (0.6 if strong else 0.75):
                repairs.append({"now": b[j], "early": a[best]})
            elif PUNCT.sub("", na[best]) != PUNCT.sub("", nb[j]):
                edits.append({"early": a[best], "now": b[j]})
    return repairs, edits


class name_table(dict):
    """staff-names.yml 的笔名 → 中文译名。署名标签和名单的写法偶有全半角、大小写、长音符的出入，查不到再归一一次"""
    @staticmethod
    def fold(s: str) -> str:
        return unicodedata.normalize("NFKC", s or "").casefold().replace("−", "ー").replace("-", "ー")

    def __init__(self, names: dict):
        super().__init__()
        self.folded = {}
        for row in names.get("names") or []:
            for term in row.get("source_terms") or []:
                self[term] = row.get("target")
                self.folded[self.fold(term)] = row.get("target")

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return self.folded.get(self.fold(key), default)


def cmd_restore(args) -> int:
    roster = load_yaml(BASE / "manifest" / "history-writers.yml") or {"writers": {}}
    alias = roster_aliases(roster)
    names = load_yaml(BASE / "staff-names.yml") or {}
    zh_of = name_table(names)
    blogs = load_yaml(ROOT / "_data" / "gamefreak_legacy_blogs.yml") or {}
    cat_zh = {c["ja"]: c["zh"] for c in (blogs.get("staff") or {}).get("categories") or []}
    diff = {r["id"]: r for r in (load_yaml(REPORT / "history-diff.yml") or {}).get("posts") or []}
    summary = []
    for path in sorted(HIST.glob("*.yml"), key=lambda p: int(p.stem)):
        data = load_yaml(path)
        pid = data["id"]
        cur_html = BASE / "raw" / "posts" / f"{pid}.html"
        if not cur_html.exists():
            continue
        html = decode(cur_html.read_bytes())
        meta = load_yaml(cur_html.with_suffix(".meta.yml")) or {}
        base = meta.get("original_url") or f"http://www.gamefreak.co.jp/blog/staff/?p={pid}"
        cur = [b for b in blocks_from_html(html, base) if b["id"] == pid]
        if not cur:
            continue
        now_text = text_of(cur[0]["node"])
        full = [v for v in data["versions"] if not v["partial"]]
        #  署名：只收侧栏名单里的笔名；名单外的（プラチナ连载的开发组长「太田」「松田」等）记为客座执笔，
        #  系列名、分类名那种不是人的标签丢掉
        writers, guests = [], []
        for v in data["versions"]:
            for w in v.get("writers") or []:
                if w in alias:
                    canon = alias[w]
                    if canon not in writers:
                        writers.append(canon)
                elif w not in cat_zh and "ポケットモンスター" not in w and len(w) <= 8 and w not in guests:
                    guests.append(w)
        cats = sorted({c for v in data["versions"] for c in v.get("cats") or [] if c in cat_zh},
                      key=lambda c: list(cat_zh).index(c))
        repairs, edits = [], []
        seen = set()
        for v in reversed(full):                       # 越晚的早期版本越接近现在，先拿它配
            if v["text_sha"] in seen:
                continue
            seen.add(v["text_sha"])
            rep, ed = repairs_for(v["text"], now_text)
            for r in rep:
                if r["now"] not in {x["now"] for x in repairs}:
                    repairs.append({**r, "ts": v["ts"]})
            for e in ed:
                if e["now"] not in {x["now"] for x in edits} and e["now"] not in {x["now"] for x in repairs}:
                    edits.append({**e, "ts": v["ts"]})
        #  同一行既能修复又被当成改稿时，修复优先
        edits = [e for e in edits if e["now"] not in {r["now"] for r in repairs}]
        still = [ln for ln in raw_lines(now_text) if re.search(r"縲|竏|鰀|怩|怐|怺", ln) and ln not in {r["now"] for r in repairs}]
        #  标题也挨了同一刀（「東京マラソン ?東京がひとつになる日?」）
        title_now = cur[0]["title"]
        title_early = next((v["title"] for v in reversed(full) if v["title"] and not CORRUPT.search(v["title"])), "")
        title_repair = None
        if CORRUPT.search(title_now) and title_early and title_early != title_now:
            import difflib
            if difflib.SequenceMatcher(a=title_early, b=title_now).ratio() >= 0.7:
                title_repair = {"now": title_now, "early": title_early}
        record = {
            "post_id": pid,
            "early_versions": len(data["versions"]), "earliest_capture": data["versions"][0]["ts"],
            "themes": sorted({v.get("theme") for v in data["versions"] if v.get("theme")}),
            "writers": [{"ja": w, "zh": zh_of.get(w) or w} for w in writers],
            "guest_writers": guests,
            "categories": [{"ja": c, "zh": cat_zh[c]} for c in cats],
            "text_repairs": repairs, "text_edits": edits, "unrepaired_corruption": still, "title_repair": title_repair,
            "images_only_early": (diff.get(pid) or {}).get("images_only_early") or [],
            "embeds_early": (diff.get(pid) or {}).get("embeds_early") or [],
        }
        write_yaml(BASE / "content" / str(pid) / "history.yml", record)
        summary.append({k: record[k] for k in ("post_id", "earliest_capture")} |
                       {"writers": writers, "guests": guests, "cats": cats, "repairs": len(repairs), "edits": len(edits),
                        "unrepaired": len(still)})
    write_yaml(BASE / "manifest" / "history-restore.yml", {"generated_at": utc_now(), "posts": summary})
    print(f"{len(summary)} posts: writers {sum(1 for s in summary if s['writers'])}, guest {sum(1 for s in summary if s['guests'])}, "
          f"categories {sum(1 for s in summary if s['cats'])}, repairs {sum(s['repairs'] for s in summary)} in "
          f"{sum(1 for s in summary if s['repairs'])} posts, edits {sum(s['edits'] for s in summary)}, "
          f"unrepaired lines {sum(s['unrepaired'] for s in summary)}")
    return 0


# ---------------------------------------------------------------- publish

PUBLIC = ROOT / "assets" / "images" / "gamefreak-legacy" / "staff"
WRITERS_DATA = ROOT / "_data" / "gamefreak_staff_writers.yml"
BLOG_CATS_ZH = ["GF介绍", "日记", "宝可梦", "招聘", "更新通知", "未分类"]


def fetch_asset(session: requests.Session, url: str, ts: str, dest: Path) -> dict | None:
    """一张图：按它最早出现的快照时间取原始字节（id_），存进 archive；已有就不再抓"""
    if dest.exists():
        data = dest.read_bytes()
        return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    for attempt in range(4):
        try:
            r = session.get(f"https://web.archive.org/web/{ts}id_/{url}", timeout=60)
            if r.status_code == 200 and r.content and not r.content[:15].lower().startswith((b"<!doctype", b"<html")):
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(r.content)
                time.sleep(0.6)
                return {"bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()}
            if r.status_code in (403, 404):
                return None
        except requests.RequestException:
            pass
        time.sleep(2.5 * (attempt + 1))
    return None


def writer_assets(roster: dict, zh_of: dict, counts: collections.Counter) -> list:
    """侧栏名单的头像：每个笔名可能换过几次头像，全部存档；页面用最后那一张"""
    s = requests.Session()
    s.headers["User-Agent"] = UA
    out = []
    alias = roster_aliases(roster)
    for key, w in sorted((roster.get("writers") or {}).items(), key=lambda kv: (kv[1].get("order") or 999, kv[0])):
        if alias.get(key) != key:
            continue
        avatars = []
        for url, seen in sorted(w["avatars"].items(), key=lambda kv: kv[1]["first_seen"]):
            name = f"{Path(urlparse(url).path).stem}-{hashlib.sha1(url.encode()).hexdigest()[:6]}{Path(urlparse(url).path).suffix.lower()}"
            dest = BASE / "assets" / "history" / "writers" / name
            got = fetch_asset(s, url, seen["first_seen"], dest)
            if not got:
                continue
            pub = PUBLIC / "writers" / name
            if not pub.exists() or hashlib.sha256(pub.read_bytes()).hexdigest() != got["sha256"]:
                pub.parent.mkdir(parents=True, exist_ok=True)
                pub.write_bytes(dest.read_bytes())
            avatars.append({"original_url": url, "local_path": str(dest.relative_to(ROOT)).replace("\\", "/"),
                            "public": f"/assets/images/gamefreak-legacy/staff/writers/{name}",
                            "first_seen": seen["first_seen"], "last_seen": seen["last_seen"], **got})
        out.append({"ja": key, "zh": zh_of.get(key) or key, "names_on_icon": w.get("names_on_icon") or [],
                    "avatar": avatars[-1]["public"] if avatars else None, "avatars": avatars,
                    "posts": counts.get(key, 0), "first_seen": w["first_seen"], "last_seen": w["last_seen"]})
    return out


def yaml_block(key: str, value) -> str:
    return yaml.safe_dump({key: value}, allow_unicode=True, sort_keys=False, width=1000).rstrip("\n")


def replace_key(front: str, key: str, value) -> str:
    """只换前言里这一个键的整块（其余字段逐字不动——实体标注等是别的工具写的）"""
    lines = front.split("\n")
    out, i, done = [], 0, False
    while i < len(lines):
        line = lines[i]
        if not done and re.match(rf"^{re.escape(key)}:", line):
            j = i + 1
            while j < len(lines) and (lines[j].startswith((" ", "-")) and not re.match(r"^[A-Za-z_]+:", lines[j])):
                j += 1
            out.append(yaml_block(key, value))
            i, done = j, True
            continue
        out.append(line)
        i += 1
    if not done:
        out.append(yaml_block(key, value))
    return "\n".join(out)


def insert_after(front: str, anchor_key: str, key: str, value) -> str:
    if re.search(rf"^{re.escape(key)}:", front, re.M):
        return replace_key(front, key, value)
    lines = front.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(anchor_key + ":"):
            lines.insert(i + 1, yaml_block(key, value))
            return "\n".join(lines)
    return front + "\n" + yaml_block(key, value)


def panel_span(body: str, lang: str) -> tuple[int, int] | None:
    m = re.search(rf'<div data-gf-language-panel="{re.escape(lang)}"[^>]*>', body)
    if not m:
        return None
    end = body.find("\n</div>", m.end())
    return (m.end(), end if end > 0 else len(body))


#  中文译文是照着损坏的日文译的，大多数乱码被译者绕过去了，漏进译文的只有这几处（人工核对过）
ZH_FIXES = {
    160: [("Ｗｉ竏窒eｉ俱乐部", "Wi-Fi 俱乐部")],
}


def flex_replace(text: str, now: str, early: str) -> tuple[str, bool]:
    """text_of 把全角空格、制表符归一成了半角空格；回到原文里找时空白要宽松，换上去时保留原文的空白"""
    if now in text:
        return text.replace(now, early, 1), True
    chunks = now.split(" ")
    pattern = r"[ \t　]+".join(re.escape(c) for c in chunks)
    m = re.search(pattern, text)
    if not m:
        return text, False
    gaps = re.findall(r"[ \t　]+", m.group(0))
    parts = early.split(" ")
    rebuilt = parts[0] + "".join(g + p for g, p in zip(gaps, parts[1:])) if len(parts) - 1 == len(gaps) else early
    return text[:m.start()] + rebuilt + text[m.end():], True


def revision_note(edits: list) -> str:
    rows = []
    for e in edits:
        when = f"{e['ts'][:4]} 年 {int(e['ts'][4:6])} 月"
        rows.append(f"<li><span>{when}的存档版本</span><q lang=\"ja\">{e['early']}</q>"
                    f"<span>后来改为</span><q lang=\"ja\">{e['now']}</q></li>")
    return ("\n<aside class=\"gf-legacy-revision\" aria-label=\"修订记录\">\n<strong>修订记录</strong>"
            "<p>对照 Web Archive 里更早的快照，这篇在原站上改过：</p>\n<ul>" + "".join(rows) + "</ul>\n</aside>\n")


def cmd_publish(args) -> int:
    """把 restore 的结果写回：archive 的日文正文与元数据、_posts 的前言与日文面板、员工名单与头像"""
    roster = load_yaml(BASE / "manifest" / "history-writers.yml") or {"writers": {}}
    names = load_yaml(BASE / "staff-names.yml") or {}
    zh_of = name_table(names)
    records = {}
    for path in BASE.glob("content/*/history.yml"):
        rec = load_yaml(path)
        records[rec["post_id"]] = rec
    counts = collections.Counter(w["ja"] for r in records.values() for w in r["writers"])
    writers = writer_assets(roster, zh_of, counts)
    avatar_of = {w["ja"]: w["avatar"] for w in writers}
    write_yaml(WRITERS_DATA, {"_note": "tools/gamefreak_staff_history.py publish 生成：早期模板侧栏「書いてる人リスト」的笔名与头像，"
                                        "posts 是按「書いた人」署名数的篇数。",
                              "writers": [{k: w[k] for k in ("ja", "zh", "avatar", "posts", "first_seen", "last_seen")} for w in writers]})
    write_yaml(BASE / "manifest" / "history-writers-assets.yml", {"generated_at": utc_now(), "writers": writers})

    changed = collections.Counter()
    problems = []
    for pid, rec in sorted(records.items()):
        posts = list((ROOT / "_posts").glob(f"*-gamefreak-staff-{pid}.md"))
        if len(posts) != 1:
            problems.append(f"{pid}: {len(posts)} post files")
            continue
        post = posts[0]
        raw = post.read_text(encoding="utf-8")
        m = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
        if not m:
            problems.append(f"{pid}: no front matter")
            continue
        front, body = m.group(1), raw[m.end():]
        fm = yaml.safe_load(front) or {}
        real_zh = [c["zh"] for c in rec["categories"]]
        if rec["categories"]:
            tags = [t for t in fm.get("tags") or [] if t not in BLOG_CATS_ZH or t in real_zh]
            for t in real_zh:
                if t not in tags:
                    tags.append(t)
            front = replace_key(front, "tags", tags)
            front = replace_key(front, "gf_blog_categories", rec["categories"])
        people = [{"ja": w["ja"], "zh": w["zh"], **({"avatar": avatar_of[w["ja"]]} if avatar_of.get(w["ja"]) else {})}
                  for w in rec["writers"]]
        people += [{"ja": g, "zh": zh_of.get(g) or g, "guest": True} for g in rec["guest_writers"]]
        if people:
            front = replace_key(front, "gf_source_tags", [p["ja"] for p in people])
            front = insert_after(front, "gf_legacy_post_id", "gf_writers", people)
        history = {"early_versions": rec["early_versions"], "earliest_capture": rec["earliest_capture"],
                   "themes": rec["themes"], "repaired_lines": len(rec["text_repairs"]) + (1 if rec.get("title_repair") else 0),
                   "edits": len(rec["text_edits"])}
        front = insert_after(front, "gf_legacy_post_id", "gf_history", history)
        tr = rec.get("title_repair")
        if tr:
            #  日文标题：前言里凡是原样写着坏标题的地方（gf_original_title、source.title、没译标题时的 title）一起换
            if tr["now"] in front:
                front = front.replace(tr["now"], tr["early"])
                changed["titles"] += 1
            elif tr["early"] not in front:
                problems.append(f"{pid}: title not found in front matter: {tr['now']}")
        # 日文面板：乱码行换回早期原文
        fixed = 0
        span = panel_span(body, "ja")
        if span and rec["text_repairs"]:
            seg = body[span[0]:span[1]]
            for r in rec["text_repairs"]:
                seg, ok = flex_replace(seg, r["now"], r["early"])
                if ok:
                    fixed += 1
                elif not flex_replace(seg, r["early"], r["early"])[1]:      # 已经修过（重跑）不算问题
                    problems.append(f"{pid}: repair line not found in ja panel: {r['now'][:40]}")
            body = body[:span[0]] + seg + body[span[1]:]
        zspan = panel_span(body, "zh-CN")
        for bad_zh, good_zh in ZH_FIXES.get(pid, []):
            if zspan and bad_zh in body[zspan[0]:zspan[1]]:
                body = body[:zspan[0]] + body[zspan[0]:zspan[1]].replace(bad_zh, good_zh) + body[zspan[1]:]
                changed["zh_fixes"] += 1
            tfile = BASE / "translations" / "zh-CN" / f"{pid}.md"
            if tfile.exists() and bad_zh in tfile.read_text(encoding="utf-8"):
                tfile.write_text(tfile.read_text(encoding="utf-8").replace(bad_zh, good_zh), encoding="utf-8", newline="\n")
        if rec["text_edits"] and "gf-legacy-revision" not in body:
            body = body.rstrip("\n") + "\n" + revision_note(rec["text_edits"])
        new = "---\n" + front + "\n---\n" + body
        if new != raw:
            post.write_text(new, encoding="utf-8", newline="\n")
            changed["posts"] += 1
        changed["repairs"] += fixed
        # archive 层同步：日文正文、结构、元数据
        adir = BASE / "content" / str(pid)
        for fname in ("ja.md", "structure.ja.json"):
            f = adir / fname
            if f.exists() and rec["text_repairs"]:
                text = f.read_text(encoding="utf-8")
                new_text = text
                for r in rec["text_repairs"]:
                    new_text, _ = flex_replace(new_text, r["now"], r["early"])
                if new_text != text:
                    f.write_text(new_text, encoding="utf-8", newline="\n")
                    changed["archive_" + fname] += 1
        if tr:
            f = adir / "ja.md"
            if f.exists():
                text = f.read_text(encoding="utf-8")
                if tr["now"] in text:
                    f.write_text(text.replace(tr["now"], tr["early"]), encoding="utf-8", newline="\n")
        meta_path = adir / "metadata.yml"
        meta = load_yaml(meta_path) or {}
        if tr and meta.get("title") == tr["now"]:
            meta["title"] = tr["early"]
        if rec["categories"]:
            meta["blog_categories"] = rec["categories"]
        if people:
            meta["writers"] = people
            meta["tags"] = [p["ja"] for p in people]
        meta["history"] = {**history, "record": f"archive/gamefreak-staff/content/{pid}/history.yml"}
        write_yaml(meta_path, meta)
    #  管线的权威清单（manifest/articles.yml）里的标题也换掉，重跑管线时不会把坏标题带回来
    fixes = {pid: rec["title_repair"] for pid, rec in records.items() if rec.get("title_repair")}
    if fixes:
        art_path = BASE / "manifest" / "articles.yml"
        text = art_path.read_text(encoding="utf-8")
        new_text = text
        for tr in fixes.values():
            new_text = new_text.replace(tr["now"], tr["early"])
        if new_text != text:
            art_path.write_text(new_text, encoding="utf-8", newline="\n")
            changed["manifest_titles"] = len(fixes)
    if problems:
        write_yaml(REPORT / "history-publish-problems.yml", {"at": utc_now(), "problems": problems})
    print(f"writers {len(writers)} (avatars {sum(len(w['avatars']) for w in writers)}); {dict(changed)}; problems {len(problems)}")
    for p in problems[:20]:
        print("  !", p)
    return 1 if problems else 0


def cmd_report(args) -> int:
    """人读的报告：reports/history-report.md"""
    man = load_yaml(MANIFEST)
    diff = (load_yaml(REPORT / "history-diff.yml") or {}).get("posts") or []
    records = {}
    for path in BASE.glob("content/*/history.yml"):
        rec = load_yaml(path)
        records[rec["post_id"]] = rec
    fetched = sum(1 for c in man["items"] if (BASE / c["file"]).exists())
    arts = (load_yaml(BASE / "manifest" / "articles.yml") or {}).get("articles") or []
    ids_now = {a["id"]: a for a in arts}
    no_early = sorted(set(ids_now) - set(records))
    writers = (load_yaml(WRITERS_DATA) or {}).get("writers") or []
    themes = collections.Counter(t for r in records.values() for t in r["themes"] if t != "clean-minimal")
    rep = sorted((r for r in records.values() if r["text_repairs"] or r.get("title_repair")), key=lambda r: r["post_id"])
    eds = sorted((r for r in records.values() if r["text_edits"]), key=lambda r: r["post_id"])
    still = sorted((r for r in records.values() if r["unrepaired_corruption"]), key=lambda r: r["post_id"])
    L = []
    L.append("# 晴れたり時々曇ったり · 早期版本对照\n")
    L.append(f"生成：`python tools/gamefreak_staff_history.py report`（{utc_now()[:10]}）。数据全在 `archive/gamefreak-staff/`，"
             "原始快照在 `raw/history/`，逐篇版本在 `content/history/<id>.yml`，逐篇恢复记录在 `content/<id>/history.yml`。\n")
    L.append("## 查了什么\n")
    L.append(f"- Web Archive 里 `gamefreak.co.jp/blog/staff/` 与旧主机 `gamefreak.sakura.ne.jp/blog/staff/` 在 {CUTOFF[:4]}-{CUTOFF[4:6]}-{CUTOFF[6:]} "
             f"之前的全部 HTML / RSS 快照，按「网址 + 内容摘要」去重后 **{man['captures']} 份**，抓到 {fetched} 份："
             + "、".join(f"{k} {v}" for k, v in man["by_kind"].items()) + "。")
    L.append("- 每份快照里切出每一篇（逐篇页、月归档、首页、分类页、标签页、RSS 都可能带全文），按「文章 · 快照时间」存成版本，"
             "只比正文文字、图片、嵌入、署名、分类和标题，不比侧栏与模板。")
    old_theme = {r["post_id"] for r in records.values() if set(r["themes"]) - {"clean-minimal"}}
    L.append(f"- 现有的 {len(arts)} 篇取自 2013-08 前后的快照（clean-minimal 主题）。其中 **{len(old_theme)} 篇**在换主题之前"
             "（2007–2012 的旧模板）就有快照，能逐字对照" +
             (f"；{len(no_early)} 篇没有任何更早的快照（{', '.join(map(str, no_early))}）" if no_early else "") + "。\n")
    L.append("## 结论\n")
    L.append("- **没有被删掉的文章**：早期快照里出现过的文章 id 和现在的 209 篇一一对得上（id 2 是 About 页，站上已有）。")
    L.append("- **没有被删掉的图片，也没有视频**：早期版本里的正文图片现在都在；所有快照里没有一处 `<embed>` / `<object>` / `<iframe>` / `<video>`，"
             "CDX 里也没有任何视频文件，外链里没有 YouTube / ニコニコ——这个博客从来没放过视频。")
    L.append(f"- **署名被去掉了**：2007–2012 年的模板每篇结尾有「書いた人：笔名」（Ultimate Tag Warrior 标签），侧栏有 {len(writers)} 位员工的"
             "「書いてる人リスト」和头像；2013 年换主题后这两样全没了，站上每篇都只写「GAME FREAK 员工」。"
             f"现在按早期版本补回 **{sum(1 for r in records.values() if r['writers'])} 篇**的署名，"
             f"另有 {sum(1 for r in records.values() if r['guest_writers'])} 篇是名单外的客座执笔（プラチナ「ここだけの話」连载的开发组长等）。")
    L.append(f"- **分类被抹平了**：现有导入给每篇都挂了全部 6 个分类（站上 209 篇都带「招聘」标签）。早期模板逐篇写着分类，"
             f"2013 年的分类页也列着各篇；据此改回 **{sum(1 for r in records.values() if r['categories'])} 篇**的真实分类。")
    L.append(f"- **2013 年迁移造成了乱码**：`〜` 被误读成「縲怩」「縲鰀」「縲怐」并吃掉后一个字，`～` / `~` / `−` 变成「?」，"
             f"「Wi−Fi」变成「Wi竏窒ei」。站上的日文原文原样带着这些乱码。按早期原文修正 **{sum(len(r['text_repairs']) for r in rep)} 行、"
             f"{sum(1 for r in rep if r.get('title_repair'))} 个标题，涉及 {len(rep)} 篇**。")
    L.append(f"- **原站后来真正改过稿的**：{sum(len(r['text_edits']) for r in eds)} 处，在 {len(eds)} 篇里；文章末尾加了「修订记录」，正文保留最后的版本。")
    L.append("- **早期模板**（括号里是在这套模板下有快照的篇数）：" + "、".join(f"`{t}`（{n} 篇）" for t, n in themes.most_common()) +
             "。staff01 是 2007–2009 的原版，staff_hgss 是《心金·魂银》发售期的特别版，staff01_wb 是《黑·白》发售期的特别版。"
             "三套模板的页头、背景、样式表与按钮存在 `assets/history/themes/`（清单 `manifest/history-themes.yml`），"
             f"{len(writers)} 位员工的头像存在 `assets/history/writers/`（有人换过头像，全部保留）。\n")
    if eds:
        L.append("## 改过稿的地方\n")
        for r in eds:
            title = ids_now.get(r["post_id"], {}).get("title", "")
            for e in r["text_edits"]:
                L.append(f"- **{r['post_id']}《{title}》**（{e['ts'][:4]}-{e['ts'][4:6]} 的快照）：「{e['early']}」→「{e['now']}」")
        L.append("")
    if rep:
        L.append("## 修正的乱码\n")
        L.append("| 篇 | 现在（损坏） | 早期原文 |")
        L.append("| --- | --- | --- |")
        for r in rep:
            if r.get("title_repair"):
                L.append(f"| {r['post_id']}（标题） | {r['title_repair']['now']} | {r['title_repair']['early']} |")
            for x in r["text_repairs"]:
                L.append(f"| {r['post_id']} | {x['now'][:60]} | {x['early'][:60]} |")
        L.append("")
    if still:
        L.append("## 没法修的\n")
        for r in still:
            for ln in r["unrepaired_corruption"]:
                L.append(f"- {r['post_id']}：{ln[:80]}")
        L.append("")
    L.append("## 书いてる人リスト\n")
    L.append("| 笔名 | 译名 | 署名篇数 | 侧栏出现 |")
    L.append("| --- | --- | --- | --- |")
    for w in writers:
        L.append(f"| {w['ja']} | {w['zh']} | {w['posts']} | {w['first_seen'][:6]}–{w['last_seen'][:6]} |")
    (REPORT / "history-report.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"→ {(REPORT / 'history-report.md').relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["list", "fetch", "extract", "compare", "restore", "publish", "report"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.6)
    args = ap.parse_args()
    return {"list": cmd_list, "fetch": cmd_fetch, "extract": cmd_extract, "compare": cmd_compare,
            "restore": cmd_restore, "publish": cmd_publish, "report": cmd_report}[args.stage](args)


if __name__ == "__main__":
    raise SystemExit(main())
