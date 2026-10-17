#!/usr/bin/env python3
"""Serve what tools/preview-pages.rb rendered, with the source tree behind it.

A request is answered from .preview-build/pages/ when that file was rendered, otherwise from the
repository itself - images, scripts, fonts and other static files are copied verbatim by a full build,
so the rendered pages look as they will on the site.

    python tools/preview-serve.py                 # http://127.0.0.1:4759/
    python tools/preview-serve.py --port 4760 --dir <another render dir>
"""
import argparse
import functools
import http.server
import os
import posixpath
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, rendered: Path, **kw):
        self.rendered = rendered
        super().__init__(*a, directory=str(rendered), **kw)

    def translate_path(self, path):
        rel = posixpath.normpath(urllib.parse.unquote(urllib.parse.urlsplit(path).path)).lstrip("/")
        for base in (self.rendered, ROOT):
            p = (base / rel).resolve()
            if base not in p.parents and p != base:
                continue                                   # no escaping the two roots
            if p.is_dir() and (p / "index.html").exists():
                return str(p / "index.html")
            if p.is_file():
                return str(p)
        return str(self.rendered / rel)                    # 404 from the rendered dir

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")      # a re-render shows on reload
        super().end_headers()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=4759)
    ap.add_argument("--dir", type=Path, default=ROOT / ".preview-build" / "pages")
    args = ap.parse_args()
    rendered = args.dir.resolve()
    rendered.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), functools.partial(Handler, rendered=rendered))
    print(f"serving {rendered} (falling back to {ROOT}) on http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
