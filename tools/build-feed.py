"""The library's own timeline: when each entry came in.

A post's `date` is when the magazine came out or the blog was written; when
the entry joined the library is in git - the commit that first added its
file. That is what the resource hub's feed (/keys/) runs on: the entries
added each day, as a stream of 新收录 posts, and the days the library passed
a round number.

    python tools/build-feed.py            # rewrite _data/feed_log.yml and _data/feed_added.yml

feed_added.yml   stem -> YYYY-MM-DD, every published post still in the tree
feed_log.yml     [{date, count, posts: [stem…]}], newest day first; a day
                 with more than KEEP posts keeps its newest KEEP (by the
                 post's own date) and the count says how many there were

Only files git tracks count; a post staged but not yet committed is dated today.
"""
import io
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
KEEP = 8


def git(*args):
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def front(path):
    """The front matter's flags and the entry's type, by the rule entry-card.html uses;
    None when the post is unpublished or kept out of the catalogue."""
    # the whole file: a scan post's front matter runs to hundreds of KB
    text = io.open(path, encoding="utf-8").read()
    m = re.match(r"^﻿?---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None
    fm = m.group(1)
    if re.search(r"^published:\s*false", fm, re.M) or re.search(r"^search:\s*false", fm, re.M) or re.search(r"^hidden:\s*true", fm, re.M):
        return None
    def field(name):
        mm = re.search(r"^" + name + r":\s*['\"]?([^'\"\n]*)", fm, re.M)
        return mm.group(1).strip() if mm else ""
    archive, layout = field("archive_type"), field("layout")
    cats = re.search(r"^categories:\s*\n((?:\s+- .*\n)+)", fm, re.M)
    cats = cats.group(1) if cats else field("categories")
    if archive == "scan_translation":
        kind = "扫描翻译"
    elif layout in ("interview-editorial", "parallel-translation") or archive == "interview_translation" or "访谈翻译" in cats:
        kind = "访谈翻译"
    elif archive in ("gamefreak_director_column", "gamefreak_masuda_lineblog", "gamefreak_legacy_blog"):
        kind = "Game Freak 博客"
    elif "文档" in cats:
        kind = "文档"
    else:
        kind = "文章"
    return {"kind": kind}


def main():
    # the first commit that added each file: git log lists newest first, so the last date seen wins
    out = git("log", "--diff-filter=A", "--name-only", "--format=%ad", "--date=short", "--", "_posts")
    added = {}
    day = None
    for line in out.splitlines():
        line = line.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            day = line
        elif line.startswith("_posts/") and day:
            added[line[len("_posts/"):]] = day        # overwritten by older commits: the first add
    today = date.today().isoformat()
    # only what git knows: a file another session has not committed yet is not in the
    # library the site builds from, so it is not in the feed either
    tracked = set(git("ls-files", "--", "_posts").splitlines())
    stems, kinds = {}, {}
    for path in sorted(POSTS.glob("*.md")):
        if "_posts/" + path.name not in tracked:
            continue
        info = front(path)
        if not info:
            continue
        if path.name not in added:
            # a file the one pass missed - it came in by a rename, or on a merged branch the
            # path-limited log simplified away: its own history, followed, says when
            own = git("log", "--follow", "--diff-filter=A", "--format=%ad", "--date=short", "--", "_posts/" + path.name).split()
            if own:
                added[path.name] = own[-1]
        stems[path.stem] = added.get(path.name, today)
        kinds[path.stem] = info["kind"]
    by_day = defaultdict(list)
    for stem, d in stems.items():
        by_day[d].append(stem)
    log = []
    for d in sorted(by_day, reverse=True):
        posts = sorted(by_day[d], reverse=True)   # the stems start with the post's date: newest first
        tally = defaultdict(int)
        for p in posts:
            tally[kinds[p]] += 1
        log.append({"date": d, "count": len(posts), "posts": posts[:KEEP], "types": dict(sorted(tally.items(), key=lambda kv: -kv[1]))})
    lines = ["# 由 tools/build-feed.py 生成：每篇条目首次进入 git 的日期，按天分组（新在前）；每天只留最新 %d 篇的 stem，count 是当天总数，types 是当天按类型的篇数" % KEEP]
    for e in log:
        lines.append(f"- date: '{e['date']}'")
        lines.append(f"  count: {e['count']}")
        lines.append("  types:")
        lines.extend(f"    {k}: {v}" for k, v in e["types"].items())
        lines.append("  posts:")
        lines.extend(f"  - {p}" for p in e["posts"])
    (ROOT / "_data" / "feed_log.yml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    lines = ["# 由 tools/build-feed.py 生成：stem → 首次入库日期（git 首次加入该文件的提交；未提交的算今天）"]
    lines.extend(f"{stem}: '{d}'" for stem, d in sorted(stems.items()))
    (ROOT / "_data" / "feed_added.yml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(stems)} posts over {len(log)} days; newest: " + ", ".join(f"{e['date']} {e['count']}" for e in log[:6]))


if __name__ == "__main__":
    main()
