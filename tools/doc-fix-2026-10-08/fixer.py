"""Line-level fixer for _posts front matter.

Edits only the exact YAML lines it targets (keeps every other byte), then
re-parses the whole front matter and checks that only the intended values changed.
"""
import re, sys, json, yaml, collections
from pathlib import Path
from common import POSTS, read_post, split_fm, load_fm, L

sys.stdout.reconfigure(encoding="utf-8")

def yq(v):
    """YAML scalar for v. Plain text is single-quoted; newlines/backslashes use JSON (valid YAML)."""
    if v == "":
        s = "''"
    elif "\n" in v or "\\" in v or '"' in v:
        s = json.dumps(v, ensure_ascii=False)
    else:
        s = "'" + v.replace("'", "''") + "'"
    assert yaml.safe_load("x: " + s)["x"] == v, ("yq roundtrip failed", v[:60])
    return s

def indent_of(s):
    return len(s) - len(s.lstrip(" "))

# ---------- block location ----------
def top_block(lines, key):
    """(start, end) of a top-level `key:` block, or None. end is exclusive and excludes trailing blanks."""
    for j, l in enumerate(lines):
        if l.startswith(key + ":"):
            k = j + 1
            while k < len(lines) and (lines[k].strip() == "" or lines[k].startswith(" ") or lines[k].startswith("-")):
                k += 1
            while k > j + 1 and lines[k - 1].strip() == "":
                k -= 1
            return j, k
    return None

def parallel_items_range(lines):
    p = next((i for i, l in enumerate(lines) if l.startswith("parallel_items:")), None)
    if p is None:
        return None
    end = len(lines)
    for j in range(p + 1, len(lines)):
        l = lines[j]
        if l.strip() and not (l.startswith(" ") or l.startswith("-")):
            end = j
            break
    return p, end

def item_spans(lines):
    """[(start, end, K)] for each parallel item; K = column of the item's keys."""
    r = parallel_items_range(lines)
    if r is None:
        return []
    p, end = r
    starts, dash = [], None
    for j in range(p + 1, end):
        m = re.match(r"^(\s*)-(\s|$)", lines[j])
        if m:
            col = len(m.group(1))
            if dash is None:
                dash = col
            if col == dash:
                starts.append(j)
    spans = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else end
        spans.append((s, e, dash + 2))
    return spans

def find_key(lines, s, e, K, key):
    """Locate `key` inside item [s,e). Returns (line_idx, block_end, prefix) or None.
    prefix is the text before the key name on its first line (indent, or '  - ' on the dash line)."""
    for j in range(s, e):
        l = lines[j]
        if j == s:
            m = re.match(r"^(\s*-\s+)(\w+):", l)
            if m and m.group(2) == key:
                return j, _block_end(lines, j, e, K), m.group(1)
        else:
            if l.startswith(" " * K + key + ":") and indent_of(l) == K:
                return j, _block_end(lines, j, e, K), " " * K
    return None

def _block_end(lines, j, e, K):
    k = j + 1
    while k < e and (lines[k].strip() == "" or indent_of(lines[k]) > K):
        k += 1
    while k > j + 1 and lines[k - 1].strip() == "":
        k -= 1
    return k

# ---------- note extraction ----------
LABEL = r"(?:译注|译者注|编者注|編者注|编辑注|编注|編集部注|备注|作者注|注)"
OPEN = {"（": "）", "(": ")", "【": "】", "[": "]", "［": "］"}
# bracketed note: opener, then ※n / 注n / 注· / label+colon, then content (balanced brackets allowed inside)
BRACKET_NOTE = re.compile(r"^\s*(?:※\s*\d*\s*[：:]?|注\d+\s*[：:]?|注\s*[·・]|" + LABEL + r"\s*[：:])(.*)$", re.S)
PREF = re.compile(r"(※\s*\d*\s*[：:]?|" + LABEL + r"\s*[：:]|[［\[]注\d+[］\]]\s*)")
DUP_PREF = re.compile(r"((?:备注|译注|译者注|编者注|编辑注|作者注|編者注)\s*[：:])")
NOTE_TRIGGER = re.compile(r"※|译注|译者注|编者注|編者注|编辑注|編集部注|备注[：:]|作者注[：:]|注[：:]|（注|\(注|［注|\[注")
TERM = "。！？!?"

def bracket_notes(t):
    """[(start, end, content)] for label-led bracketed notes, honouring nested brackets."""
    found, i = [], 0
    while i < len(t):
        j = next((k for k in range(i, len(t)) if t[k] in OPEN), None)
        if j is None:
            break
        o, c = t[j], OPEN[t[j]]
        depth, end = 0, -1
        for k in range(j, len(t)):
            if t[k] == o:
                depth += 1
            elif t[k] == c:
                depth -= 1
                if depth == 0:
                    end = k
                    break
        if end == -1:
            i = j + 1
            continue
        m = BRACKET_NOTE.match(t[j + 1:end])
        content = m.group(1).strip() if m else ""
        # （※9，雷吉洛克等）: a reference followed by running text, not a note
        if m and content and not re.fullmatch(r"\d+", content) and content[0] not in "，,、":
            found.append((j, end + 1, content))
            i = end + 1
        else:
            i = j + 1
    return found

def _unb_allowed(t2, idx):
    """An unbracketed ※/注 is a note only at paragraph start, after sentence-final punctuation, or after a space.
    A ※ glued to a word (培育屋※”企划) is a footnote mark inside running text and stays put."""
    if idx == 0 or t2[idx - 1] in " \t　\n":
        return True
    return t2[:idx].rstrip()[-1:] in TERM

def extract_notes(t, dup=False):
    """Split translator notes out of a translation string. Returns (text_without_notes, [notes]).
    dup=True: the item already has a note field, so only label-led notes are taken (bare 注： is not, to keep speaker tags)."""
    spans = bracket_notes(t)
    t2 = t
    for s, e, _ in sorted(spans, reverse=True):
        t2 = t2[:s] + t2[e:]
    notes = [c for _, _, c in spans]
    for m in (DUP_PREF if dup else PREF).finditer(t2):
        if not _unb_allowed(t2, m.start()):
            continue
        content = t2[m.end():].strip()
        if not content or re.fullmatch(r"\d+", content):
            continue
        notes.append(content)
        t2 = t2[:m.start()]
        break
    return t2.rstrip(), [n.replace("\n", " ") for n in notes]

def para_breaks(s):
    """A newline after sentence-final punctuation is a paragraph break; other soft breaks are left alone.
    Idempotent: an existing blank line stays one blank line."""
    if "\n" not in s:
        return s
    parts = s.split("\n")
    res = parts[0]
    for seg in parts[1:]:
        if seg.strip() and not res.endswith("\n") and res.rstrip() and res.rstrip()[-1] in TERM + "」』”）)…":
            res += "\n\n" + seg
        else:
            res += "\n" + seg
    return re.sub(r"\n{3,}", "\n\n", res)

# ---------- per-file planning ----------
def plan_items(lines, d0):
    """Edits for parallel items. Returns (edits, expected, notes_log)."""
    spans = item_spans(lines)
    items = d0.get("parallel_items") or []
    edits, expected, notes_log = [], {}, []
    if len(spans) != len(items):
        raise RuntimeError(f"item span mismatch {len(spans)} vs {len(items)}")
    for i, ((s, e, K), it) in enumerate(zip(spans, items)):
        if not isinstance(it, dict):
            continue
        new = {}
        has_note = bool(it.get("note"))
        tr = it.get("translation")
        if tr is not None and NOTE_TRIGGER.search(str(tr)):
            t2, notes = extract_notes(str(tr), dup=has_note)
            if notes:
                new["translation"] = t2
                added = " ".join(notes)
                new["note"] = (str(it["note"]).strip() + " " + added).strip() if has_note else added
                notes_log.append((i, str(tr), t2, new["note"]))
        for k in ("translation", "original"):
            if it.get(k) is None:
                continue
            base = new.get(k, str(it[k]))
            nb = para_breaks(base)
            if nb != base:
                new[k] = nb
        if not new:
            continue
        expected[i] = new
        for k in ("translation", "original"):
            if k not in new:
                continue
            kidx, kend, prefix = find_key(lines, s, e, K, k)
            add = []
            if k == "translation" and "note" in new:
                if has_note:
                    nidx, nend, nprefix = find_key(lines, s, e, K, "note")
                    edits.append((nidx, nend, [nprefix + "note: " + yq(new["note"])]))
                else:
                    add = [" " * K + "note: " + yq(new["note"])]
            edits.append((kidx, kend, [prefix + f"{k}: " + yq(new[k])] + add))
    return edits, expected, notes_log

def plan_top(lines, d0, name, summary_map, tags_fn):
    edits, exp = [], {}
    if name in summary_map:
        new_s = summary_map[name]
        blk = top_block(lines, "summary")
        if blk:
            j, k = blk
            edits.append((j, k, ["summary: " + yq(new_s)]))
        else:
            t = top_block(lines, "title")
            edits.append((t[1], t[1], ["summary: " + yq(new_s)]))
        exp["summary"] = new_s
    new_tags = tags_fn(d0.get("tags"), name)
    if new_tags is not None:
        blk = top_block(lines, "tags")
        flow = blk and re.match(r"^tags:\s*\[", lines[blk[0]])
        if blk and flow:
            edits.append((blk[0], blk[1], ["tags: " + json.dumps(new_tags, ensure_ascii=False)]))
        elif blk:
            first = next((x for x in lines[blk[0] + 1:blk[1]] if x.strip().startswith("-")), "- x")
            ind = " " * indent_of(first)
            edits.append((blk[0], blk[1], ["tags:"] + [ind + "- " + yq(t) for t in new_tags] if new_tags else ["tags: []"]))
        else:
            t = top_block(lines, "title")
            edits.append((t[1], t[1], ["tags:"] + ["- " + yq(x) for x in new_tags] if new_tags else ["tags: []"]))
        exp["tags"] = new_tags
    return edits, exp

def apply_edits(lines, edits):
    edits = sorted(edits, key=lambda x: (x[0], x[1]), reverse=True)
    prev_start = None
    for s, e, new in edits:
        if prev_start is not None and e > prev_start:
            raise RuntimeError("overlapping edits")
        lines[s:e] = new
        prev_start = s
    return lines

def verify(new_fm, d0, exp_items, exp_top):
    """Re-parse the edited front matter; every item and top-level key must equal the intended value."""
    d1 = yaml.load(new_fm, Loader=L) or {}
    p0, p1 = d0.get("parallel_items") or [], d1.get("parallel_items") or []
    if len(p0) != len(p1):
        raise RuntimeError("item count changed")
    for i, (a, b) in enumerate(zip(p0, p1)):
        if not isinstance(a, dict):
            continue
        want = dict(a)
        want.update(exp_items.get(i, {}))
        if set(want) != set(b):
            raise RuntimeError(f"item {i} key set differs: {set(want) ^ set(b)}")
        for k in want:
            if b[k] != want[k]:
                raise RuntimeError(f"item {i} key {k} mismatch")
    for k in set(d0) | set(d1):
        if k == "parallel_items":
            continue
        want = exp_top[k] if k in exp_top else d0.get(k)
        if d1.get(k) != want:
            raise RuntimeError(f"top-level {k} mismatch")
    return d1
