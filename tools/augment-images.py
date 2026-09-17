"""Give a web-imported interview the pictures its page carries and the post lacks.

    python tools/augment-images.py --dry-run                 # every post the audit found short of pictures
    python tools/augment-images.py --dry-run --only famitsu  # posts whose file name contains this
    python tools/augment-images.py --only 2009-09-04         # write the pictures and the post
    python tools/augment-images.py --all                     # every short post (clean ones; dirty are skipped)
    python tools/augment-images.py --all --upgrade           # also swap thumbnails the post shows for the page's full-size files

The audit (tools/audit-web-imports.py -> design/web_import_audit.json) says which posts hold
fewer pictures than their page; this tool reads the page copy the audit cached
(data/cache_web/audit/), cuts the article out the way import-web.py does and walks it in
reading order. Each picture is placed after the post item whose `original` is the paragraph
the page prints before the picture (the audit's prefix match, speaker label removed), so it
lands where the page had it. A picture the post already carries is recognised by a
perceptual hash of the downloaded file against the files under the post's picture folder,
whatever their names or sizes. Tiny pictures, banners and the site's chrome are dropped.
Files over 300 KB are brought down to 1280 px JPEG, as the import does. Nothing is
translated: alt and caption stay in the page's language, as import-web.py leaves them.

A post with uncommitted changes from someone else is skipped (say --force to touch it).
Downloads are cached under data/cache_web/images/ (ignored by git), so a dry run followed
by the real run fetches nothing twice. The run is summarised in
design/augment_images_2026-09.json (one row per post: what was added, what was skipped
and why), which the next run reads to leave finished posts alone unless --redo.
"""
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "design" / "web_import_audit.json"
REPORT = ROOT / "design" / "augment_images_2026-09.json"
CACHE_HTML = ROOT / "data" / "cache_web" / "audit"
DL = ROOT / "data" / "cache_web" / "images"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8,zh;q=0.6"}
MIN_SIDE = 120          # a picture narrower or shorter than this is an icon (Iwata Asks sets its photos at 250x150)
MAX_ASPECT = 4.0        # wider than this is a banner
DUP_BITS = 12           # of 144: perceptual-hash distance under which two files are the same picture
BIG = 300 * 1024


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


importweb = _load("importweb", ROOT / "tools" / "import-web.py")
auditweb = _load("auditweb", ROOT / "tools" / "audit-web-imports.py")


# ---------------------------------------------------------------- the page
def cached_page(stem, target_key=None):
    """the copy import-web.py worked from when the post has a target (the Wayback copy it names,
    with the article's own pictures), else the copy the audit fetched"""
    if target_key:
        own = CACHE_HTML.parent / f"{target_key}.html"
        if own.exists() and own.stat().st_size >= 3000:
            return own.read_bytes()
    key = re.sub(r"[^a-z0-9]+", "-", stem[11:].lower()).strip("-")[:80]
    f = CACHE_HTML / (key + ".html")
    return f.read_bytes() if f.exists() and f.stat().st_size >= 3000 else None


def page_blocks(raw, target):
    soup = importweb.parse(raw)
    importweb.strip_noise(soup)
    box = importweb.find_container(soup, target or {})
    return importweb.extract_blocks(box, bool(target and target.get("join_br")))


def page_year(raw):
    """the year the page says it was published (structured data, Open Graph, a <time>), else None"""
    head = raw[:200000].decode("utf-8", "replace")
    for pat in (r'"datePublished"\s*:\s*"(\d{4})', r'article:published_time"\s+content="(\d{4})', r'property="article:published_time"[^>]*content="(\d{4})',
                r'<time[^>]+datetime="(\d{4})', r'"uploadDate"\s*:\s*"(\d{4})', r'"dateModified"\s*:\s*"(\d{4})'):
        m = re.search(pat, head)
        if m and 1995 <= int(m.group(1)) <= 2030:
            return int(m.group(1))
    return None


def align(blocks, items):
    """each picture of the page with the index of the post item it follows (-1: before all)"""
    sq = [None if it.get("type") == "image" else auditweb.squash(str(it.get("original") or "")) for it in items]
    pos, out, tried, matched = -1, [], 0, 0
    for b in blocks:
        if b["t"] in ("text", "h"):
            core = auditweb.SPEAKER.sub("", auditweb.squash(b["x"]), count=1)
            if len(core) < 12:
                continue
            hit = _find(sq, core, pos)
            if len(core) >= 20:               # a dialogue line split at <br> can be short; a footnote is long
                tried += 1
            if hit is not None:
                pos = hit
                if len(core) >= 20:
                    matched += 1
        elif b["t"] == "img":
            out.append((b, pos))
    return out, tried, matched


def _find(sq, core, pos):
    keys = [k for k in (core[:24], core[6:30], core[14:38]) if len(k) >= 12] if len(core) >= 24 else [core]
    order = list(range(pos + 1, len(sq))) + list(range(max(0, pos - 3), pos + 1))
    for i in order:
        t = sq[i]
        if not t:
            continue
        if any(k in t for k in keys) or (len(t) >= 24 and t[:24] in core):
            return i
    return None


# ---------------------------------------------------------------- pictures
def dhash(im, size=12):
    g = im.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | int(px[r * (size + 1) + c] > px[r * (size + 1) + c + 1])
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def open_image(data):
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        return im
    except Exception:
        return None


def existing_hashes(stem, fm):
    """perceptual hashes of the pictures the post shows (its image rows, its cover), and of the
    files under its folder that no row shows - an earlier import fetched them and never placed
    them; a page picture that matches one of those is placed by reusing the file"""
    shown, remote = set(), set()
    rows = [it for it in fm.get("parallel_items") or [] if isinstance(it, dict) and it.get("type") == "image"]
    rows += [{"image": fm[k]} for k in ("image", "featured_image") if isinstance(fm.get(k), str)]
    for it in rows:
        v = it.get("image") or it.get("src") or it.get("original") or ""
        if not isinstance(v, str):
            continue
        if v.startswith("/"):
            shown.add(ROOT / v.lstrip("/"))
        elif v.startswith("http"):
            remote.add(v)               # a picture the post hotlinks (an older import)
    folder = IMG_DIR / stem
    spare = [p for p in folder.iterdir() if p.is_file() and p not in shown] if folder.exists() else []
    have, unplaced, shown_files = [], [], []
    for p in shown:
        if p.exists():
            try:
                im = Image.open(p)
                have.append(dhash(im))
                shown_files.append((have[-1], p, im.size))
            except Exception:
                pass
    for p in spare:
        try:
            unplaced.append((dhash(Image.open(p)), p))
        except Exception:
            pass
    for url in remote:
        data, _ = download(url, url, None, True)
        im = open_image(data) if data else None
        if im is not None:
            have.append(dhash(im))
    return have, unplaced, {u.split("?")[0] for u in remote}, shown_files


_failed = None


def failed_set():
    global _failed
    if _failed is None:
        f = DL / "failed.json"
        _failed = set(json.load(io.open(f, encoding="utf-8"))) if f.exists() else set()
    return _failed


def remember_failed(url):
    failed_set().add(url)
    io.open(DL / "failed.json", "w", encoding="utf-8").write(json.dumps(sorted(failed_set()), indent=0))


def download(src, page_url, wayback, images_live):
    """the picture's bytes and the address they came from; cached by address under DL/.
    The full-size address is tried before the one the page shows."""
    m = re.match(r"^(?:https?://web\.archive\.org)?/web/\d+[a-z_]*/(.*)$", src)
    if m:
        src = m.group(1)
    absolute = urllib.parse.urljoin(page_url, src)
    DL.mkdir(parents=True, exist_ok=True)
    # WordPress serves the article a resized copy (DSC1553-600x400.jpg); the original is beside it,
    # and some sites keep the full-size file at a sibling address (gamer.ne.jp /m/ -> /o/)
    full = re.sub(r"-\d{2,4}x\d{2,4}(\.(?:jpe?g|png|webp|gif))$", r"\g<1>", absolute, flags=re.I)
    for pat, rep in importweb.FULLSIZE:
        full = re.sub(pat, rep, full)
    addresses = [full, absolute] if full != absolute else [absolute]
    for a in addresses:
        hit = next(DL.glob(hashlib.md5(a.encode("utf-8")).hexdigest() + ".*"), None)
        if hit and hit.suffix != ".json":
            return hit.read_bytes(), a
        if a in failed_set():
            continue
        tries = []
        if wayback and not images_live:
            ts = re.search(r"/web/(\d+)", wayback).group(1)
            tries.append(f"https://web.archive.org/web/{ts}im_/{a}")
        tries += [a, f"https://web.archive.org/web/2024im_/{a}"]
        for url in tries:
            try:
                req = urllib.request.Request(url, headers={**UA, "Referer": page_url})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                time.sleep(0.4)
                if len(data) < 3000:
                    continue
                im = open_image(data)
                if im is None:
                    continue
                ext = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", "WEBP": ".webp"}.get(im.format, ".jpg")
                (DL / (hashlib.md5(a.encode("utf-8")).hexdigest() + ext)).write_bytes(data)
                return data, a
            except Exception:
                continue
        remember_failed(a)
    return None, absolute


TEXT_IMG = re.compile(r"[/_-](?:text|txt|serif|ttl|heading|btn|bg|line|dot|bar|hr)\d*(?:[_-]\d+)*\.(?:gif|png|jpe?g|webp)$", re.I)


def judge(data, url=""):
    """why a downloaded picture is not one for the post, or None with the opened image"""
    if TEXT_IMG.search(url):
        return "text as a picture", None       # a pull-quote or a heading set in a picture file
    if re.search(r"thumb(?:nail)?[_\-./]", url, re.I):
        return "thumbnail", None               # the strip of other articles under the piece (電撃's thumbnail_*.jpg)
    im = open_image(data)
    if im is None:
        return "unreadable", None
    w, h = im.size
    if w < MIN_SIDE or h < MIN_SIDE:
        return f"tiny {w}x{h}", None
    if max(w, h) / max(1, min(w, h)) > MAX_ASPECT:
        return f"banner {w}x{h}", None
    return None, im


def next_index(folder):
    n = 0
    if folder.exists():
        for p in folder.iterdir():
            m = re.match(r"^(\d{3})\.[a-z]+$", p.name.lower())
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


def save_picture(data, im, folder, index):
    """the file under the post's folder, brought down to 1280 px JPEG when it is over 300 KB"""
    folder.mkdir(parents=True, exist_ok=True)
    fmt = im.format or "JPEG"
    animated = fmt == "GIF" and getattr(im, "n_frames", 1) > 1
    ext = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", "WEBP": ".webp"}.get(fmt, ".jpg")
    if len(data) > BIG and not animated:
        transparent = False
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            transparent = im.convert("RGBA").getextrema()[3][0] < 255
        work = im.copy()
        work.thumbnail((1280, 1280), Image.LANCZOS)
        buf = io.BytesIO()
        if transparent:
            work.save(buf, "PNG", optimize=True)
            ext = ".png"
        else:
            work = work.convert("RGB")
            work.save(buf, "JPEG", quality=85, optimize=True, progressive=True)
            if buf.tell() > BIG:
                buf = io.BytesIO()
                work.save(buf, "JPEG", quality=75, optimize=True, progressive=True)
            ext = ".jpg"
        data = buf.getvalue()
    elif fmt == "WEBP" and not animated:
        # the site serves WebP; the post keeps the picture as JPEG/PNG like the rest of its folder
        buf = io.BytesIO()
        if im.mode in ("RGBA", "LA"):
            im.save(buf, "PNG", optimize=True)
            ext = ".png"
        else:
            im.convert("RGB").save(buf, "JPEG", quality=88, optimize=True)
            ext = ".jpg"
        data = buf.getvalue()
    out = folder / f"{index:03d}{ext}"
    while out.exists():
        index += 1
        out = folder / f"{index:03d}{ext}"
    out.write_bytes(data)
    return "/" + out.relative_to(ROOT).as_posix(), index


# ---------------------------------------------------------------- the post
def insert_rows(text, n_items, inserts):
    """`inserts` are (after_item_index, row_dict); the rows are written into the front matter's
    parallel_items after that item (and after any picture rows already following it), in order"""
    m = FRONT.match(text)
    prefix, head, rest = text[:m.start(1)], m.group(1), text[m.end(1):]
    nl = "\r\n" if "\r\n" in head else "\n"
    lines = head.split(nl)
    start = next(i for i, l in enumerate(lines) if l.rstrip() == "parallel_items:")
    indent = ""
    for i in range(start + 1, len(lines)):
        mm = re.match(r"^(\s*)- ", lines[i])
        if mm:
            indent = mm.group(1)
            break
    end = len(lines)
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if not l.strip() or l.startswith(indent + "- "):
            continue
        if len(l) - len(l.lstrip(" ")) > len(indent):
            continue                      # a row's own lines sit deeper than the dash
        end = i                           # the next key of the front matter
        break
    starts = [i for i in range(start + 1, end) if lines[i].startswith(indent + "- ")]
    if len(starts) != n_items:
        raise RuntimeError(f"parallel_items has {n_items} rows but {len(starts)} list lines were found")
    at = {}
    for after, row in inserts:
        k = after + 1
        line = starts[k] if k < len(starts) else end
        dumped = yaml.safe_dump([row], allow_unicode=True, sort_keys=False, width=1000).rstrip("\n").split("\n")
        at.setdefault(line, []).extend(indent + d for d in dumped)
    for line in sorted(at, reverse=True):
        lines[line:line] = at[line]
    return prefix + nl.join(lines) + rest


def same_page(a, b):
    """two addresses of one page: Wayback prefix, scheme, www. and a trailing slash aside"""
    def norm(u):
        u = re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", str(u or ""))
        return re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()
    return bool(a) and bool(b) and norm(a) == norm(b)


def dirty_posts():
    out = set()
    # quotepath off: a file name with CJK in it would otherwise come back octal-escaped and never match;
    # `diff HEAD` rather than `status`, which flags an LF file under autocrlf as modified with no change in it
    res = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--name-only", "HEAD", "--", "_posts"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    for l in res.stdout.splitlines():
        if l.strip():
            out.add(l.strip().strip('"').replace("_posts/", ""))
    return out


def skip_following_pictures(items, after):
    """the index of the last picture row directly after item `after`, so a new one goes behind them"""
    k = after
    while k + 1 < len(items) and items[k + 1].get("type") == "image":
        k += 1
    return k


def run(row, target, target_key, dry, cap, dirty, force, report_rows, upgrade=False):
    name = row["post"]
    stem = name[:-3]
    path = ROOT / "_posts" / name
    if not path.exists():
        return
    if name in dirty and not force:
        print(f"  ~~ {name[:70]}  has uncommitted changes from elsewhere - skipped")
        return
    text = io.open(path, encoding="utf-8").read()
    fm = yaml.safe_load(FRONT.match(text).group(1))
    items = fm.get("parallel_items")
    if not isinstance(items, list):
        print(f"  ~~ {name[:70]}  no parallel_items - skipped")
        return
    raw = cached_page(stem, target_key)
    if raw is None:
        print(f"  ~~ {name[:70]}  no cached page")
        return
    url = row["url"]
    wayback = url if "web.archive.org" in url else (target or {}).get("wayback")
    page_url = re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", url)
    blocks = page_blocks(raw, target)
    placed, tried, matched = align(blocks, items)
    if tried >= 4 and matched < max(3, 0.25 * tried):
        # the post does not hold the page's text (a paraphrase, a translation only): nothing to
        # hang the pictures on - that post wants a re-import, not pictures piled at its top
        print(f"  ~~ {name[:66]:66s} page text not in the post ({matched}/{tried} paragraphs found) - re-import it instead")
        report_rows[name] = {"post": name, "unalignable": [matched, tried], "dry": dry}
        return
    have, unplaced, remote_paths, shown_files = existing_hashes(stem, fm)
    upgrades = []
    folder = IMG_DIR / stem
    idx = next_index(folder)
    title = fm.get("original_title") or fm.get("title") or stem
    added, skipped, seen_urls, new_hashes = [], [], set(), []
    pyear = page_year(raw)
    year = max(int(stem[:4]), pyear) if pyear else None     # a page with no date (a scan blog) is not judged by upload year
    for b, after in placed:
        if len(added) >= cap:
            skipped.append([b["src"][:100], "over the cap"])
            continue
        m = re.search(r"/(20\d\d)/(?:\d\d/)?[^/]*$", b["src"])
        if year and m and int(m.group(1)) > year + 1:
            # uploaded years after the piece: the site's "more stories" strip, not the article
            skipped.append([b["src"][:120], f"uploaded {m.group(1)}"])
            continue
        data, absolute = download(b["src"], page_url, wayback, bool((target or {}).get("images_live")))
        if absolute in seen_urls:
            continue
        seen_urls.add(absolute)
        if absolute.split("?")[0] in remote_paths:
            skipped.append([absolute[:120], "already in the post"])
            continue
        if data is None:
            skipped.append([absolute[:120], "not fetched"])
            continue
        why, im = judge(data, absolute)
        if why:
            skipped.append([absolute[:120], why])
            continue
        h = dhash(im)
        if any(hamming(h, x) <= DUP_BITS for x in have) or any(hamming(h, x) <= DUP_BITS for x in new_hashes):
            small = next(((pth, sz) for x, pth, sz in shown_files if hamming(h, x) <= DUP_BITS and im.size[0] >= 1.5 * sz[0]), None)
            if upgrade and small and not any(u["old"] == small[0] for u in upgrades):
                upgrades.append({"old": small[0], "old_size": list(small[1]), "size": list(im.size), "src": absolute, "data": data, "im": im})
                continue
            skipped.append([absolute[:120], "already in the post"])
            continue
        new_hashes.append(h)
        reuse = next((p for x, p in unplaced if hamming(h, x) <= DUP_BITS), None)
        anchor = items[after]["original"][:28] if after >= 0 and items[after].get("original") else ("(top)" if after < 0 else items[after].get("type", "?"))
        added.append({"src": absolute, "after": after, "anchor": anchor, "alt": b["alt"], "caption": b["cap"], "size": list(im.size), "bytes": len(data), "data": data, "im": im,
                      "reuse": "/" + reuse.relative_to(ROOT).as_posix() if reuse else None})
    last = max((i for i, it in enumerate(items) if it.get("type") != "image"), default=-1)
    tail = [a for a in added if a["after"] >= last and a["size"][0] == a["size"][1]]
    if len(tail) >= 5:
        for a in tail:                         # square, uniform, after the last paragraph: "more stories"
            added.remove(a)
            skipped.append([a["src"][:120], "card grid after the piece"])
    n_dup = sum(1 for s in skipped if s[1] == "already in the post")
    n_fail = sum(1 for s in skipped if s[1] == "not fetched")
    print(f"  {'--' if dry else '++'} {name[:66]:66s} page {len(placed):3d} pics: +{len(added):3d} new, {n_dup:3d} held, {n_fail:2d} unfetched, {len(skipped) - n_dup - n_fail:2d} dropped")
    if dry:
        for a in added[:60]:
            print(f"        after #{a['after']:3d} {a['anchor'][:26]:26s} {a['size'][0]:4d}x{a['size'][1]:<4d} {'(file in folder) ' if a['reuse'] else ''}{a['caption'][:30] or a['alt'][:30]}  {a['src'][-48:]}")
        for s in skipped:
            if s[1] not in ("already in the post",):
                print(f"        skip {s[1]:18s} {s[0][-60:]}")
    if upgrades:
        print(f"        {len(upgrades)} shown at thumbnail size, the page has them bigger: " + ", ".join(f"{u['old'].name} {u['old_size'][0]}->{u['size'][0]}px" for u in upgrades[:6]) + (" …" if len(upgrades) > 6 else ""))
    out_row = {"post": name, "page_pictures": len(placed), "added": [], "skipped": skipped, "dry": dry}
    if not dry and upgrades:
        # the bigger file takes a fresh number; the row is repointed; the thumbnail goes
        for u in upgrades:
            local, idx = save_picture(u["data"], u["im"], folder, idx)
            idx += 1
            old_rel = "/" + u["old"].relative_to(ROOT).as_posix()
            if text.count(old_rel) == 0:
                (ROOT / local.lstrip("/")).unlink()
                continue
            text = text.replace(old_rel, local)
            u["old"].unlink()
            out_row.setdefault("upgraded", []).append({"from": old_rel, "to": local, "size": u["size"]})
        io.open(path, "w", encoding="utf-8", newline="").write(text)
        fm = yaml.safe_load(FRONT.match(text).group(1))
        items = fm["parallel_items"]
    for u in upgrades:
        u.pop("data", None)
        u.pop("im", None)
        u["old"] = str(u["old"])
    if not dry and added:
        inserts = []
        for a in added:
            if a["reuse"] and (ROOT / a["reuse"].lstrip("/")).stat().st_size <= BIG:
                local = a["reuse"]          # the file an earlier import left in the folder
            elif a["reuse"]:
                # left there at full size: it is brought down like a fresh download, the big file goes
                old = ROOT / a["reuse"].lstrip("/")
                local, idx = save_picture(old.read_bytes(), Image.open(old), folder, idx)
                idx += 1
                old.unlink()
            else:
                local, idx = save_picture(a["data"], a["im"], folder, idx)
                idx += 1
            it = {"type": "image", "image": local, "alt": (a["alt"] or f"{title}_{Path(local).stem}")[:200]}
            if a["caption"] and a["caption"] != a["alt"]:
                it["caption"] = a["caption"][:300]
            inserts.append((skip_following_pictures(items, a["after"]), it))
            out_row["added"].append({"image": local, "src": a["src"], "after": a["after"], "size": a["size"], "reused": bool(a["reuse"])})
        new_text = insert_rows(text, len(items), inserts)
        # the file must still parse, and hold exactly the rows it had plus the new pictures
        fm2 = yaml.safe_load(FRONT.match(new_text).group(1))
        if len(fm2["parallel_items"]) != len(items) + len(inserts):
            raise RuntimeError(f"{name}: rewrite lost rows ({len(fm2['parallel_items'])} vs {len(items) + len(inserts)})")
        io.open(path, "w", encoding="utf-8", newline="").write(new_text)
    for a in added:
        a.pop("data", None)
        a.pop("im", None)
    if dry and report_rows.get(name, {}).get("dry") is False:
        return                          # a dry look never overwrites the record of what was written
    report_rows[name] = out_row


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    force = "--force" in argv
    upgrade = "--upgrade" in argv
    redo = "--redo" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv else ""
    cap = int(argv[argv.index("--max") + 1]) if "--max" in argv else 80
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 10 ** 6
    if not only and "--all" not in argv and not dry:
        print(__doc__)
        return
    audit = json.load(io.open(AUDIT, encoding="utf-8"))
    targets = auditweb.load_targets()
    report = json.load(io.open(REPORT, encoding="utf-8")) if REPORT.exists() else {}
    dirty = dirty_posts()
    rows = [r for r in audit if r.get("cached") and (upgrade or r.get("page_images", 0) > r.get("post_images", 0))]
    if only:
        rows = [r for r in rows if only in r["post"]]
    rows.sort(key=lambda r: r["post"])
    done = 0
    for r in rows:
        if done >= limit:
            break
        prev = report.get(r["post"], {})
        if not redo and not dry and not upgrade and prev.get("dry") is False and "added" in prev:
            continue          # written in an earlier run
        slug = r["post"][11:-3]
        tkey = next((k for k, t in targets.items() if isinstance(t, dict) and (same_page(t.get("url"), r["url"]) or same_page(t.get("wayback"), r["url"]) or t.get("slug") == slug)), None)
        try:
            run(r, targets.get(tkey) if tkey else None, tkey, dry, cap, dirty, force, report, upgrade)
            done += 1
        except Exception as e:
            print(f"  !! {r['post'][:70]}  {e}")
            report[r["post"]] = {"post": r["post"], "error": str(e)[:200], "dry": dry}
    REPORT.parent.mkdir(exist_ok=True)
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write(json.dumps(report, ensure_ascii=False, indent=1))
    n_add = sum(len(v.get("added", [])) for v in report.values() if v.get("dry") is False)
    print(f"\n{done} posts handled; {n_add} pictures written so far -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
