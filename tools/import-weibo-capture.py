#!/usr/bin/env python3
"""Append verified logged-in DOM captures without rebuilding historical Weibo data.

Preview: python tools/import-weibo-capture.py tools/data/weibo-captures/2026-11-13.json
Apply after archiving its image_urls to img_new/ and _work/cos/: add --apply.
This does not fetch a timeline, modify articles, upload media, or render the site.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


def source_hash(value):
    """FNV-1a over JS UTF-16 code units, recorded at DOM capture time."""
    result = 2166136261
    encoded = value.encode("utf-16-le")
    for i in range(0, len(encoded), 2):
        result = ((result ^ int.from_bytes(encoded[i:i + 2], "little")) * 16777619) & 0xffffffff
    return f"{result:08x}"


class PostText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "br":
            self.parts.append("\n")
        elif tag == "img":
            self.parts.append(attrs.get("alt", ""))
        elif tag == "a":
            href = attrs.get("href", "")
            self.link = href if urlsplit(href).scheme in ("http", "https") else None
            if self.link:
                self.parts.append("[")

    def handle_endtag(self, tag):
        if tag == "a" and self.link:
            self.parts.append("](" + self.link.replace("(", "%28").replace(")", "%29") + ")")
            self.link = None

    def handle_data(self, value):
        self.parts.append(value)


def post_text(value):
    parser = PostText()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts).strip()


def media_name(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not re.fullmatch(r"wx\d+\.sinaimg\.cn", parsed.netloc)
            or parsed.query or parsed.fragment):
        raise ValueError(f"Unexpected image URL: {url}")
    name = parsed.path.rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9]+\.(?:jpg|png|gif)", name):
        raise ValueError(f"Unexpected image filename: {name}")
    return name


def merge_capture(dataset, capture):
    """Return a new dataset and added MIDs; reject edits to already archived posts."""
    if capture.get("full_text_verified") is not True or capture.get("date_precision") != "minute":
        raise ValueError("Capture must verify full text and declare minute precision")
    display_tz = ZoneInfo(capture["display_timezone"])
    archive_tz = ZoneInfo(capture["archive_timezone"])
    existing = {p["mid"]: p for p in dataset["posts"] if p.get("mid")}
    checkpoint = existing.get(capture["checkpoint_mid"])
    if not checkpoint or checkpoint["d"] != capture["checkpoint_archive_date"]:
        raise ValueError("Checkpoint does not match the existing archive")
    excluded = {p["mid"] for p in capture.get("excluded", [])}
    ids = {p["id"] for p in dataset["posts"]}
    added, seen = [], set()
    for raw in capture["posts"]:
        mid = raw["mid"]
        if not re.fullmatch(r"\d+", mid) or mid in seen or mid in excluded or raw.get("retweeted_status"):
            raise ValueError(f"Duplicate, excluded or non-original MID: {mid}")
        seen.add(mid)
        if raw["source_hash"] != source_hash(raw["html"]):
            raise ValueError(f"Source HTML hash mismatch: {mid}")
        if raw["url"] not in (f"https://m.weibo.cn/status/{mid}", f"https://m.weibo.cn/detail/{mid}"):
            raise ValueError(f"Source URL does not match MID: {mid}")
        date = datetime.strptime(raw["display_date"], "%Y-%m-%d %H:%M")
        date = date.replace(tzinfo=display_tz).astimezone(archive_tz).strftime("%Y-%m-%d %H:%M:%S")
        if date <= checkpoint["d"]:
            raise ValueError(f"Post is not newer than checkpoint: {mid}")
        names = [media_name(url) for url in raw["image_urls"]]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate images in post: {mid}")
        post = dict(id=hashlib.md5((date + mid).encode()).hexdigest()[:8], d=date,
                    src="new", text=post_text(raw["html"]), truncated=False,
                    imgs=["img_new/" + name for name in names],
                    likes=raw["likes"], reposts=raw["reposts"], comments=raw["comments"],
                    video=raw["video"], mid=mid, edited=raw["edited"],
                    date_precision="minute", date_timezone=capture["archive_timezone"],
                    captured_at=capture["captured_at"], source_html_hash=raw["source_hash"])
        if not post["text"] or any(type(post[key]) is not int or post[key] < 0
                                    for key in ("likes", "reposts", "comments")):
            raise ValueError(f"Missing text or invalid counters: {mid}")
        if mid in existing:
            # Counts can change on a later capture; content changes need deliberate review.
            content = ("d", "text", "imgs", "video", "truncated")
            if any(post[k] != existing[mid][k] for k in content):
                raise ValueError(f"Already archived MID has changed; review before replacing: {mid}")
            continue
        if post["id"] in ids:
            raise ValueError(f"Fragment ID collision: {post['id']}")
        ids.add(post["id"])
        added.append(post)
    # Existing objects (including articles) are never edited.
    merged = {**dataset, "posts": sorted(dataset["posts"] + added, key=lambda p: p["d"], reverse=True)}
    return merged, [p["mid"] for p in added]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--dataset", type=Path, default=Path("P:/weibo/_work/dataset.json"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    original = json.loads(args.dataset.read_text(encoding="utf-8"))
    merged, added = merge_capture(original, capture)
    if args.apply and added:
        # A failed image download must not silently remove pictures from the archive.
        work = args.dataset.parent
        for post in merged["posts"]:
            if post.get("mid") in added:
                for rel in post["imgs"]:
                    if not (work.parent / rel).is_file() or not (work / "cos" / Path(rel).name).is_file():
                        raise ValueError(f"Archive source and CDN copy required before applying: {rel}")
        pending = args.dataset.with_suffix(".pending.json")
        pending.write_text(json.dumps(merged, ensure_ascii=False) + "\n", encoding="utf-8")
        pending.replace(args.dataset)
    print(f"{'Applied' if args.apply else 'Preview'}: {len(added)} new posts; "
          f"{len(merged['posts'])} total; {len(capture.get('excluded', []))} excluded")


if __name__ == "__main__":
    main()
