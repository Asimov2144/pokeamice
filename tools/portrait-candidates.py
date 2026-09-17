"""After importing interviews: which of their pictures show an interviewee and are not yet in
build-people.py's PORTRAITS? Every picture whose caption names a registry person (running titles
that repeat across a post's pictures do not count), skipping the ones PORTRAITS already uses.
Writes data/portrait-review/candidates.json and contact sheets sheet-NN.jpg (4 x 3, index / name /
entry / caption) to look through, then add the good ones to PORTRAITS (region="left"/"right"/
"left3"/"mid3"/"right3" for a group photo, post=<entry stem>) and run `build-people.py harvest`.

    python tools/portrait-candidates.py            # all interview entries
    python tools/portrait-candidates.py --only 2026-07   # entries whose file name contains this
"""
import glob, io, json, os, re, sys
from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont
try:
    FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    FONT_S = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 12)
except OSError:
    FONT = FONT_S = ImageFont.load_default()

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "portrait-review"
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
OUT.mkdir(parents=True, exist_ok=True)
FRONT = re.compile(r"\A\ufeff?---\r?\n(.*?)\r?\n---\r?\n", re.S)

reg = {e["name"]: e for e in yaml.safe_load(open(ROOT / "_data" / "people.yml", encoding="utf-8"))}
posts = []
for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
    if ONLY and ONLY not in Path(f).name:
        continue
    t = io.open(f, encoding="utf-8", errors="replace").read()
    m = FRONT.match(t)
    if not m:
        continue
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        continue
    if fm.get("layout") not in ("interview-editorial", "parallel-translation"):
        continue
    if "首藤刚志手记" in (fm.get("categories") or []):
        continue
    people = [p for p in ((fm.get("entities") or {}).get("people") or []) if reg.get(p, {}).get("kind") in (None, "staff")]
    imgs = []
    for it in (fm.get("parallel_items") or []) + (fm.get("translation_segments") or []):
        if isinstance(it, dict) and it.get("type") == "image" and it.get("image"):
            imgs.append({"src": it["image"], "cap": " ".join(str(it.get(k) or "") for k in ("caption", "alt", "translation", "original", "text"))[:200]})
    for k in ("image", "featured_image"):
        v = fm.get(k)
        if isinstance(v, str) and v and not any(i["src"] == v for i in imgs):
            imgs.insert(0, {"src": v, "cap": "(front matter image)"})
    for src in re.findall(r'<img[^>]+src="([^"]+)"', t):
        if not any(i["src"] == src for i in imgs):
            imgs.append({"src": src, "cap": "(body img)"})
    # a caption repeated across the pictures is the article's running title, not a caption
    import collections as _c
    freq = _c.Counter(re.sub(r"_\d+", "", i["cap"][:60]) for i in imgs)
    for i in imgs:
        if freq[re.sub(r"_\d+", "", i["cap"][:60])] > 2:
            i["cap"] = ""
    posts.append({"file": Path(f).stem, "people": people, "imgs": imgs, "title": fm.get("title", "")[:60]})

want = [n for n, e in reg.items() if e.get("kind") is None and not re.match(r"^[A-Z]\.[A-Z]\.$", n)]
used = set()
for e in reg.values():
    for ph in e.get("portraits") or []:
        used.add(ph.get("source", ""))
bp = io.open(ROOT / "tools" / "build-people.py", encoding="utf-8").read()
used_src = set(re.findall(r'src=_IA \+ "([^"]+)"', bp))
cands = []
for n in want:
    e = reg[n]
    aliases = [n] + (e.get("aliases") or [])
    for p in posts:
        if n not in p["people"]:
            continue
        for i, im in enumerate(p["imgs"]):
            capn = re.sub(r"[\s　]+", "", im["cap"])
            named = any(a and re.sub(r"[\s　]+", "", a) in capn for a in aliases)
            if not named:
                continue  # only pictures whose caption names the person
            if im["src"].replace("/assets/img/interviews/", "") in used_src:
                continue  # PORTRAITS already has it
            score = 2 + (1 if len(p["people"]) == 1 else 0)
            cands.append({"name": n, "post": p["file"], "src": im["src"], "cap": im["cap"][:90], "score": score, "n_people": len(p["people"]), "title": p["title"]})
cands.sort(key=lambda c: (c["name"], -c["score"]))
print(len(want), "registry people considered;", len(cands), "captioned pictures not yet in PORTRAITS, for", len({c["name"] for c in cands}), "of them")
json.dump(cands, open(OUT / "candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# contact sheets: 4 x 3 thumbs of 260px, label = index / name / caption
TH, COLS, ROWS = 260, 4, 3
sheet_no = 0
for start in range(0, len(cands), COLS * ROWS):
    batch = cands[start:start + COLS * ROWS]
    sheet = Image.new("RGB", (COLS * (TH + 10) + 10, ROWS * (TH + 54) + 10), (240, 240, 240))
    d = ImageDraw.Draw(sheet)
    for k, c in enumerate(batch):
        x = 10 + (k % COLS) * (TH + 10)
        y = 10 + (k // COLS) * (TH + 54)
        try:
            src = c["src"]
            im = Image.open(ROOT / src.lstrip("/")).convert("RGB") if not src.startswith("http") else None
            if im is None:
                raise FileNotFoundError(src)
            im.thumbnail((TH, TH))
            sheet.paste(im, (x + (TH - im.width) // 2, y + (TH - im.height) // 2))
        except Exception as ex:
            d.rectangle((x, y, x + TH, y + TH), outline=(200, 80, 80))
            d.text((x + 6, y + 6), "missing", fill=(200, 80, 80))
        d.text((x, y + TH + 2), f"#{start + k}  {c['name']}  s{c['score']}", fill=(20, 20, 20), font=FONT)
        d.text((x, y + TH + 21), c["post"][:34], fill=(90, 90, 90), font=FONT_S)
        d.text((x, y + TH + 36), c["cap"][:22], fill=(90, 90, 90), font=FONT_S)
    sheet.save(OUT / f"sheet-{sheet_no:02d}.jpg", quality=82)
    sheet_no += 1
print("sheets:", sheet_no, "->", OUT)
