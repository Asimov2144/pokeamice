"""retranslate.py <stem>… — every row of a post translated again from its original with import-web's translator
(DeepSeek, the site glossary, the faithful prompt), written back row by row with rowedit (only translation lines change).
For posts whose earlier translation the review found rewritten throughout (more than a third of the rows)."""
import importlib.util
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
sys.path.insert(0, str(DOCS / "tools"))
from rowedit import Post  # noqa: E402

spec = importlib.util.spec_from_file_location("import_web", DOCS / "tools" / "import-web.py")
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
glossary = W.load_glossary()

for stem in sys.argv[1:]:
    path = DOCS / "_posts" / f"{stem}.md"
    p = Post(str(path))
    fm = yaml.safe_load(path.read_text(encoding="utf-8").split("\n---\n")[0].lstrip("\ufeff")[4:])
    lang = (fm.get("original_lang") or (fm.get("source") or {}).get("language") or "ja")[:2]
    target = {"lang": lang, "outlet": fm.get("publication") or fm.get("outlet") or "", "date": str(fm.get("date"))[:10],
              "title": fm.get("original_title") or fm.get("title_ja") or fm.get("title")}
    items = []
    for i, r in enumerate(p.rows):
        if r.get("type") == "image" or not str(r.get("original") or "").strip():
            continue
        items.append({"_row": i, "original": str(r["original"]), "speaker": r.get("speaker", "")})
    W.translate_items(items, target, glossary)
    n = 0
    for x in items:
        if x.get("translation"):
            p.set(x["_row"], "translation", x["translation"])
            n += 1
    p.save()
    print(f"{stem}: {n}/{len(items)} rows translated again")
