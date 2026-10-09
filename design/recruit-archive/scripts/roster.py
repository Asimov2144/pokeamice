"""Fetch Wayback snapshots of the GAME FREAK recruit index and list, per snapshot,
the people-card links (interview-*) and cross-talk links, plus the card captions.

Usage: python roster.py <out.json> ts1 ts2 ...
Raw HTML is cached under ./raw/index-<ts>.html (id_ = original bytes).
"""
import json, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)


def fetch(ts, url):
    p = RAW / (re.sub(r"[^a-z0-9]+", "-", url.split("gamefreak.co.jp")[-1].lower()).strip("-") + f"-{ts}.html")
    if p.exists() and p.stat().st_size > 1000:
        return p.read_text("utf-8", "replace")
    w = f"https://web.archive.org/web/{ts}id_/{url}"
    for i in range(4):
        try:
            req = urllib.request.Request(w, headers={"User-Agent": "Mozilla/5.0 pokeamice-docs research"})
            b = urllib.request.urlopen(req, timeout=90).read()
            t = b.decode("utf-8", "replace")
            p.write_text(t, "utf-8")
            time.sleep(1.5)
            return t
        except Exception as e:  # noqa
            time.sleep(8 * (i + 1))
    return ""


def links(html):
    hrefs = re.findall(r'href="([^"]+)"', html)
    people = []
    talks = []
    for h in hrefs:
        m = re.search(r"/recruit/(interview-[a-z]+-[a-z]+)", h)
        if m and m.group(1) not in people:
            people.append(m.group(1))
        m = re.search(r"/recruit/(crosstalk-[a-z-]+)", h)
        if m and m.group(1).rstrip("-") not in talks:
            talks.append(m.group(1).rstrip("-"))
        m = re.search(r"/recruit/(projectstory-[a-z-]+)", h)
        if m and m.group(1) not in talks:
            talks.append(m.group(1))
    return people, talks


def main():
    out = Path(sys.argv[1])
    res = {}
    for ts in sys.argv[2:]:
        html = fetch(ts, "https://www.gamefreak.co.jp/recruit/")
        p, t = links(html)
        res[ts] = {"people": p, "talks": t, "bytes": len(html)}
        print(ts, len(html), "people", len(p), " ".join(x.replace("interview-", "") for x in p), "| talks", " ".join(x.replace("crosstalk-", "ct:") for x in t))
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
