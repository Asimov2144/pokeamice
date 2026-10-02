"""Denfaminico 2016 不思議のダンジョン (re-imported 2026-10-02): the page's notes (div.notes-text: 「※『X』」 + a line of
explanation) come in as two loose items, and the speaker's paragraph after a note loses its speaker. Notes become one item
by 编者注 (the site's convention, as in the 2016 Denfami Morimoto post); the unlabelled paragraphs after a note go back
to whoever was speaking before it. Alignment with data/cache_web/<key>.items.json (same order) gives `_explicit`."""
import json
import re
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "P:/WEBSITE/pokeamice-main (1)/app-data-export/"
key = "denfami-2016-mystery-dungeon-nakamura-nagahata"
p = ROOT + f"_posts/2016-03-07-interview-{key}.md"
fm = yaml.safe_load(open(p, encoding="utf-8").read().split("\n---\n")[0][4:])
items = fm["parallel_items"]
raw = json.load(open(ROOT + f"data/cache_web/{key}.items.json", encoding="utf-8"))
assert len(raw) == len(items), (len(raw), len(items))
NOTE = re.compile(r"^※『[^』]+』$")
out, k, merged, restored = [], 0, 0, 0
last_turn = None          # (role, speaker) of the last labelled turn
while k < len(items):
    x, r = items[k], raw[k]
    o = (x.get("original") or "").strip()
    if NOTE.match(o) and k + 1 < len(items) and items[k + 1].get("type") is None:
        body = items[k + 1]
        out.append({"original": o + (body.get("original") or ""), "translation": (x.get("translation") or o) + (body.get("translation") or ""),
                    "speaker": "编者注", "role": "answer"})
        merged += 1
        k += 2
        # the paragraphs after the note, until the next labelled turn, are the speaker's before it
        while k < len(items) and not raw[k].get("_explicit") and items[k].get("type") is None and last_turn \
                and not NOTE.match((items[k].get("original") or "").strip()):
            items[k]["role"], items[k]["speaker"] = last_turn
            out.append(items[k])
            restored += 1
            k += 1
        continue
    if r.get("_explicit") and x.get("role"):
        last_turn = (x["role"], x.get("speaker", ""))
    elif x.get("type") == "heading":
        last_turn = None
    out.append(x)
    k += 1
fm["parallel_items"] = out
fm["tags"] = [t for t in fm["tags"] if t != "Game Freak"]
open(p, "w", encoding="utf-8", newline="\n").write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n")
print("notes merged", merged, "paragraphs given back", restored, "items", len(out))
