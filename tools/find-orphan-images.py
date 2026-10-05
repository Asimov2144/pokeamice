"""Pictures nothing refers to: in assets/img/interviews and assets/images, the files whose path - or, failing that, whose
bare file name - appears nowhere: not in a tracked text file of this repo (posts, data, layouts, scripts, tools, the
App's data export), not in a built site (--site, which catches a path Liquid puts together), and not in the App's own
source (--app). Most are left over from a post renamed or re-imported under another folder.

    python tools/find-orphan-images.py --site <_site> --app <Pokeamice_app/src> [--list orphans.txt]
"""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRS = ["assets/img/interviews", "assets/images"]
TEXT = (".md", ".markdown", ".html", ".yml", ".yaml", ".json", ".js", ".mjs", ".ts", ".tsx", ".scss", ".css", ".xml", ".txt", ".py", ".rb", ".csv")
NAME = re.compile(r"[\w\-.%~+]+\.(?:png|jpe?g|gif|webp|svg|avif)", re.I)


def corpus_files(args):
    tracked = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
    for p in tracked:
        if p.endswith(TEXT) and not p.startswith(tuple(d + "/" for d in DIRS)):
            yield ROOT / p
    for extra in (args.site, args.app):
        if extra:
            for d, _, fs in os.walk(extra):
                if "node_modules" in d:
                    continue
                for f in fs:
                    if f.endswith(TEXT):
                        yield Path(d) / f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--app")
    ap.add_argument("--list")
    args = ap.parse_args()
    names = set()
    paths = set()
    for f in corpus_files(args):
        try:
            t = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        t2 = urllib.parse.unquote(t) if "%" in t else t
        for text in (t, t2):
            for m in NAME.findall(text):
                names.add(m)
            for m in re.findall(r"(?:assets/)?(?:img/interviews|images)/[^\s'\"()<>\\,]+", text):
                paths.add(m.split("?")[0].split("#")[0].removeprefix("assets/"))
    orphans = []
    for d in DIRS:
        for f in (ROOT / d).rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(ROOT).as_posix()
            if rel.removeprefix("assets/") in paths or f.name in names or urllib.parse.quote(f.name) in names:
                continue
            orphans.append((f.stat().st_size, rel))
    orphans.sort(reverse=True)
    print(f"{len(orphans)} files nothing refers to, {sum(s for s, _ in orphans) / 1e6:.1f} MB")
    if args.list:
        Path(args.list).write_text("\n".join(r for _, r in orphans) + "\n", encoding="utf-8")
    return orphans


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
