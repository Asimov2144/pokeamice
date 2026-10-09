"""Version history of GAME FREAK recruit pages from the Wayback Machine.

For every page slug: list captures (collapse=digest, 200 only), fetch each capture's original
bytes (id_), cut out the member block and the body, hash them, and group consecutive captures
whose body text is identical into one version. A change of body is classified by how much text
survives (difflib ratio) so a full replacement and a one-paragraph insert look different.

Writes:
  raw/<slug>-<ts>.html           cached captures
  text/<slug>/<ts>.txt           extracted text (member block + body) of the first capture of each version
  versions.json                  {slug: [{from, to, n_captures, members, assets, body_sha, ratio_prev, added, removed}]}

Usage: python versions.py slug1 slug2 ...   (slug = path under /recruit/, e.g. crosstalk-programmer)
"""
import difflib, hashlib, html as htmllib, json, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"; RAW.mkdir(exist_ok=True)
TEXT = HERE / "text"; TEXT.mkdir(exist_ok=True)
import os
OUT = HERE / os.environ.get("VERSIONS_OUT", "versions.json")
UA = {"User-Agent": "Mozilla/5.0 pokeamice-docs research (archive reconstruction)"}


def get(url, tries=5):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            time.sleep(10 * (i + 1))
    return ""


def captures(slug):
    url = f"https://web.archive.org/cdx/search/cdx?url=www.gamefreak.co.jp/recruit/{slug}/&fl=timestamp,statuscode,digest&collapse=digest"
    t = get(url)
    rows = [l.split() for l in t.splitlines() if l and l[0].isdigit()]
    return [r[0] for r in rows if len(r) >= 2 and r[1] == "200"]


def fetch(slug, ts):
    p = RAW / f"{slug.replace('/', '__')}-{ts}.html"
    if p.exists() and p.stat().st_size > 2000:
        return p.read_text("utf-8", "replace")
    t = get(f"https://web.archive.org/web/{ts}id_/https://www.gamefreak.co.jp/recruit/{slug}/")
    if t:
        p.write_text(t, "utf-8")
    time.sleep(1.2)
    return t


def plain(fragment):
    f = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "", fragment)
    f = re.sub(r"(?i)<br\s*/?>", "\n", f)
    f = re.sub(r"(?i)</(p|h\d|li|dt|dd|div|figcaption|tr)>", "\n", f)
    f = re.sub(r"<[^>]+>", "", f)
    f = htmllib.unescape(f)
    lines = [re.sub(r"[ \t　]+", " ", l).strip() for l in f.splitlines()]
    return [l for l in lines if l]


def cut(h):
    """member block, body block, asset tags"""
    start = h.find('class="st-contents')
    if start < 0:
        start = h.find("<main")
    end = len(h)
    for mark in ('class="cp-projectstory', 'class="cp-people', 'class="cp-crosstalk', 'class="cp-entry', "<footer"):
        i = h.find(mark, start + 1)
        if i > 0:
            end = min(end, i)
    main = h[start:end] if start >= 0 else h
    m0 = main.find('class="member')
    c0 = main.find('class="contents')
    if m0 >= 0 and c0 > m0:
        member, body = main[m0:c0], main[c0:]
    else:
        member, body = "", main
    assets = sorted(set(re.findall(r"\?(20\d{6})=?", h)))
    return plain(member), plain(body), assets


def initials(lines):
    return sorted(set(re.findall(r"\b([A-Z]\.[A-Z]\.)", " ".join(lines))))


def main():
    data = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {}
    for slug in sys.argv[1:]:
        caps = captures(slug)
        print(f"== {slug}: {len(caps)} distinct captures", flush=True)
        versions = []
        prev_body = None
        for ts in caps:
            h = fetch(slug, ts)
            if not h or len(h) < 2000:
                continue
            member, body, assets = cut(h)
            sha = hashlib.sha1("\n".join(body).encode()).hexdigest()[:10]
            if versions and versions[-1]["body_sha"] == sha:
                v = versions[-1]
                v["to"] = ts
                v["n_captures"] += 1
                v["assets"] = sorted(set(v["assets"]) | set(assets))
                if member and initials(member) != v["members"]:
                    v.setdefault("member_changes", []).append({"at": ts, "members": initials(member), "member_text": member[:12]})
                continue
            ratio = None; added = []; removed = []
            if prev_body is not None:
                sm = difflib.SequenceMatcher(None, prev_body, body, autojunk=False)
                ratio = round(sm.ratio(), 3)
                for op, a1, a2, b1, b2 in sm.get_opcodes():
                    if op in ("replace", "delete"):
                        removed += prev_body[a1:a2]
                    if op in ("replace", "insert"):
                        added += body[b1:b2]
            d = TEXT / slug.replace("/", "__"); d.mkdir(exist_ok=True)
            (d / f"{ts}.txt").write_text("## MEMBER\n" + "\n".join(member) + "\n\n## BODY\n" + "\n".join(body) + "\n", "utf-8")
            versions.append({
                "from": ts, "to": ts, "n_captures": 1, "body_sha": sha, "members": initials(member or body[:40]),
                "member_text": member[:12], "assets": assets, "body_lines": len(body), "body_chars": sum(map(len, body)),
                "ratio_prev": ratio, "added": [a[:160] for a in added[:30]], "removed": [r[:160] for r in removed[:30]],
                "n_added": len(added), "n_removed": len(removed),
            })
            prev_body = body
            print(f"  v{len(versions)} {ts} members={versions[-1]['members']} lines={len(body)} ratio_prev={ratio} +{len(added)} -{len(removed)} assets={assets}", flush=True)
        data[slug] = versions
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
