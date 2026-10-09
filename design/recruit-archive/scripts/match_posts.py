"""Which Wayback version of a recruit page did each site post translate?

For every post whose original_url / original_link / source url points at a /recruit/<slug>/ page,
take the post's Japanese `original:` strings (parallel_items) and measure how many of them occur in
each extracted version text (text/<slug>/<ts>.txt, written by versions.py). Prints the best version.

Usage: python match_posts.py <repo>
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
SLUG_OF_POST = {
    "2019-04-01-interview-gamefreak-recruit-pg-yi": "interview-pg-yi",
    "2019-04-01-interview-gamefreak-recruit-pl-my": "interview-pl-my",
    "2021-12-27-interview-gamefreak-crosstalk-designer": "crosstalk-designer",
    "2021-12-27-interview-gamefreak-crosstalk-game-programmer": "crosstalk-game-programmer",
    "2021-12-27-interview-gamefreak-crosstalk-new-graduate": "crosstalk-new-graduate",
    "2021-12-27-interview-gamefreak-crosstalk-planner": "crosstalk-planner",
    "2021-12-27-interview-gamefreak-crosstalk-programmer": "crosstalk-programmer",
    "2021-12-27-interview-gamefreak-crosstalk-scenario": "crosstalk-scenario",
    "2021-12-27-interview-gamefreak-crosstalk-system-programmer": "crosstalk-system-programmer",
    "2021-12-27-interview-gamefreak-recruit-concept-artist-fk": "interview-gr-fk",
    "2021-12-27-interview-gamefreak-recruit-designer-ek": "interview-gr-ek",
    "2021-12-27-interview-gamefreak-recruit-designer-ht": "interview-gr-ht",
    "2021-12-27-interview-gamefreak-recruit-designer-kn": "interview-gr-kn",
    "2021-12-27-interview-gamefreak-recruit-designer-mi": "interview-gr-mi",
    "2021-12-27-interview-gamefreak-recruit-planner-kf": "interview-pl-kf",
    "2021-12-27-interview-gamefreak-recruit-planner-rm": "interview-pl-rm",
    "2021-12-27-interview-gamefreak-recruit-programmer-ht": "interview-pg-ht",
    "2021-12-27-interview-gamefreak-recruit-programmer-km": "interview-pg-km",
    "2021-12-27-interview-gamefreak-recruit-programmer-ko": "interview-pg-ko",
    "2021-12-27-interview-gamefreak-recruit-programmer-tk": "interview-pg-tk",
    "2021-12-27-interview-gamefreak-recruit-ta-tk": "interview-ta-tk",
}


def norm(s):
    return re.sub(r"[\s　「」『』（）()、。，．・！？!?：:“”\"'…―ー〜~]+", "", s)


def post_originals(stem):
    t = subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:_posts/{stem}.md"], capture_output=True).stdout.decode("utf-8", "replace")
    outs = re.findall(r"^\s+original: (.+)$", t, re.M)
    outs = [o.strip().strip('"').strip("'") for o in outs if not o.strip().startswith("/assets")]
    return [norm(o) for o in outs if len(norm(o)) >= 12]


def main():
    vers = json.loads((HERE / "versions.json").read_text("utf-8"))
    res = {}
    for stem, slug in SLUG_OF_POST.items():
        d = HERE / "text" / slug
        if not d.exists():
            print(f"{stem}: no versions for {slug}")
            continue
        origs = post_originals(stem)
        scores = []
        for f in sorted(d.glob("*.txt")):
            body = norm(f.read_text("utf-8"))
            hit = sum(1 for o in origs if o in body)
            scores.append((f.stem, hit))
        best = max(scores, key=lambda x: (x[1], x[0])) if scores else None
        res[stem] = {"slug": slug, "n_orig": len(origs), "scores": scores, "best": best}
        print(f"{stem.split('interview-gamefreak-')[1]:<28} n={len(origs):>3} exact " + "  ".join(f"{ts[:8]}:{h}" for ts, h in scores))
    (HERE / "post-version-match.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
