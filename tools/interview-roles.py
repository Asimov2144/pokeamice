"""Give every interview turn a role, so the editorial layout can build chapters.

    python tools/interview-roles.py _posts/2016-*.md            # report only
    python tools/interview-roles.py _posts/2016-*.md --write    # save

The layout needs `role: question | answer` on dialogue turns. Posts arrive in
three shapes, handled in this order:

1. Structural pseudo-speakers - 【章节导览】, 专栏解说, 档案, 序言 and the
   like - are not people. The speaker is removed and the item stays narrative.
2. A turn that already has a speaker gets a role from who is speaking: the
   interviewer, the outlet, or a generic "提问 / Interviewer / 取材班" is a
   question; anyone else is an answer.
3. A block that holds a whole exchange in one string ("MeriStation: ... Ohmori:
   ...") is split into turns on the post's own speaker set, and kept only when
   the original and the translation yield the same speakers in the same order.
   Anything else is left as it was and reported.

Idempotent: turns that already carry a role are not touched. The layout switch
is separate - this only annotates the data.
"""
import glob
import io
import re
import sys

import yaml

STRUCTURAL = re.compile(r"^[【\[『].*[】\]』]$|^(专栏解说|档案|序言|专家档案|旁白|编者按|注记|任天堂官方注记|body)$")
GENERIC_Q = {"提问", "记者", "问", "q", "interviewer", "采访者", "取材班", "主持人", "现场问答环节",
             "主持人 / 少年提问", "西班牙少年听众", "听众提问", "读者提问", "司会"}
OUTLET_HINT = re.compile(r"(记者|编辑|采访|取材|通信|\.com|tv|magazine|online|news|通$|志$|周刊|周刊|采编|团队|专栏|媒体|站)", re.I)


def norm(name):
    return re.sub(r"\s+", "", str(name or "")).strip().lower()


def question_set(data):
    """Names that ask questions in this post: the declared interviewer, the
    outlet, and the generic labels."""
    names = set(GENERIC_Q)
    for key in ("interviewer", "source_name", "publication"):
        value = data.get(key)
        if value:
            names.add(norm(value))
            # "Salva Fernàndez（MeriStation）" -> both halves
            for part in re.split(r"[（(）)、,/／]", str(value)):
                if part.strip():
                    names.add(norm(part))
    source = data.get("source")
    if isinstance(source, dict) and source.get("title"):
        names.add(norm(source["title"]))
        for part in re.split(r"[（(）)、,/／]", str(source["title"])):
            if part.strip():
                names.add(norm(part))
    return names


def is_question(speaker, qset):
    key = norm(speaker)
    if key in qset:
        return True
    if any(q and len(q) > 2 and q in key for q in qset):
        return True
    return bool(OUTLET_HINT.search(speaker))


ASKS = re.compile(r"[？?]\s*(?:[（(][^（）()]{0,6}[）)])?\s*[」）)]*\s*$")


def median(values):
    values = sorted(values)
    return values[len(values) // 2] if values else 0


def asks_mostly(turns, others_median=0):
    """Does this speaker ask the questions? Measured on the corpus: askers end
    at least a third of their turns in a question mark AND keep them short -
    Inside Games runs 26 characters a turn at a 0.40 ratio, 日経ビジネス 39 at
    0.43, 電玩志 28 at 0.37 - while answerers run 100-300. A romanised
    answerer like "Shigeru" (45 characters, no question marks) stays an
    answerer because the ratio floor holds. The name is not consulted at all."""
    texts = [str(t.get("translation") or "").strip() for t in turns if t.get("translation")]
    if len(texts) < 2:
        return False
    ratio = sum(1 for t in texts if ASKS.search(t)) / len(texts)
    length = median(len(t) for t in texts)
    if ratio >= 0.5:
        return True
    if ratio >= 0.3 and length <= 60:
        return True
    return ratio >= 0.2 and len(texts) >= 5 and others_median and length * 2 <= others_median


def split_block(text, speakers, colon=r"[:：]"):
    """Split one merged exchange on a known speaker set. Returns [(name, text)]
    or None if the text does not open with a speaker."""
    if not speakers:
        return None
    names = "|".join(re.escape(n) for n in sorted(speakers, key=len, reverse=True))
    pattern = re.compile(rf"(?:(?<=[\s。？！」）\.\?!])|^)({names})(?:\s?[（(][^（）()]{{1,12}}[）)])?\s*{colon}\s*")
    pieces = pattern.split(text.strip())
    if len(pieces) < 3 or pieces[0].strip():
        return None
    return [(name, body.strip()) for name, body in zip(pieces[1::2], pieces[2::2]) if body.strip()]


HEAD = re.compile(
    r"(?:^|(?<=[\s。？！」）\.\?!]))"
    r"((?:[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ.'\-]*(?:\s[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ.'\-]*){0,2}|[^\s：:，,。、？?！!（）()\[\]【】]{2,24})"
    r"(?:\s?[（(][^（）()]{1,12}[）)])?)"
    r"\s*[:：]\s*(?=\S)")


def canonical_head(name):
    """'增田顺一（JM）' and 'Junichi Masuda (JM)' -> without the tag."""
    return re.sub(r"\s?[（(][^（）()]{1,12}[）)]\s*$", "", name).strip()


def discovered_heads(items, key):
    """Names that open a turn inside the text, seen at least twice in the
    post. This is how a post with no speaker fields at all - a whole exchange
    per block - tells us who is talking."""
    counts = {}
    for item in items:
        for name in HEAD.findall(str(item.get(key) or "")):
            name = canonical_head(name)
            counts[name] = counts.get(name, 0) + 1
    return {n for n, c in counts.items() if c >= 2 and not re.search(r"^(注|注意|备注|译注|原文|译文|图|图片|来源|Source|Note|序言|はじめに)$", n, re.I)}


def speaker_alias_tables(data, items):
    """Speaker names as they appear at the head of a turn, in each language,
    mapped to a canonical name. Built from the post: canonical names from the
    speaker fields and interviewee; original-language heads guessed from
    romanisations the post declares, when it does."""
    canon = {}
    for item in items:
        if item.get("speaker"):
            canon[str(item["speaker"]).strip()] = str(item["speaker"]).strip()
    for who in re.split(r"[、,，/／]", str(data.get("interviewee") or "")):
        if who.strip():
            canon[who.strip()] = who.strip()
    # short forms used inside prose: 大森滋 -> 大森, 增田顺一 -> 增田
    for full in list(canon):
        if re.fullmatch(r"[一-鿿]{3,4}", full):
            canon[full[:2]] = full
    aliases = data.get("speaker_aliases") or {}   # optional: {"Ohmori": "大森滋", ...}
    orig = {str(k): str(v) for k, v in aliases.items()}
    # heads the text itself repeats - always, not only when the fields are
    # empty: NWR declares its interviewees but writes "NWR：" in the prose
    for name in discovered_heads(items, "translation"):
        canon.setdefault(name, name)
    if not orig:
        found = sorted(discovered_heads(items, "original"))
        trans_heads = sorted(canon)
        # same count, same order of first appearance -> pair them
        # pair by order of first appearance, located with the same head
        # grammar the discovery used (so a tagged name still counts)
        def first_seen(names, key):
            seen = {}
            for index, item in enumerate(items):
                for raw in HEAD.findall(str(item.get(key) or "")):
                    name = canonical_head(raw)
                    if name in names and name not in seen:
                        seen[name] = index
            return seen
        discovered_t = discovered_heads(items, "translation")
        if found and discovered_t and len(found) == len(discovered_t):
            ft, fo = first_seen(discovered_t, "translation"), first_seen(found, "original")
            for o, t in zip(sorted(found, key=lambda n: fo.get(n, 10 ** 6)),
                            sorted(discovered_t, key=lambda n: ft.get(n, 10 ** 6))):
                orig[o] = canon.get(t, t)
    return canon, orig


def process(path, write, debug=False):
    raw = io.open(path, encoding="utf-8").read()
    head, front, body = raw.split("---", 2)
    data = yaml.safe_load(front) or {}
    items = data.get("parallel_items")
    if not isinstance(items, list):
        return f"{path}: no parallel_items"
    stats = {"question": 0, "answer": 0, "structural": 0, "split": 0, "unsplit": 0, "kept": 0}
    canon, orig_alias = speaker_alias_tables(data, items)
    trans_heads = dict(canon)
    # every head the original repeats, as itself; alignment is positional, so
    # they need no mapping to translation names
    orig_heads = {n: n for n in discovered_heads(items, "original")}
    orig_heads.update({n: canon[n] for n in canon if re.search(r"[A-Za-z]", n)})
    orig_heads.update(orig_alias)

    # --- phase 1: expand merged exchanges into turns, roles still unset ---
    turns = []
    for item in items:
        speaker = str(item.get("speaker") or "").strip()
        if item.get("role") or speaker or item.get("type") in ("header", "heading", "image"):
            turns.append(item); continue
        trans = split_block(str(item.get("translation") or ""), trans_heads)
        if not trans or len(trans) < 2:
            turns.append(item); continue
        # The original is split on every head it repeats, unmapped - English
        # writes "Junichi Masuda (JM)" once and "JM" after, so name-for-name
        # mapping never lines up. Alignment is positional instead: same number
        # of turns, and the same question/answer pattern, where a question
        # head is one the translation also uses (NWR, GQ, MeriStation read
        # the same in both) or one that reads as an outlet. Names then come
        # from the translation side.
        orig = split_block(str(item.get("original") or ""), orig_heads) if orig_heads else None
        t_seq = [trans_heads[n] for n, _ in trans]
        base_q = question_set(data)
        t_qheads = {trans_heads[n] for n in trans_heads if is_question(n, base_q)}
        t_pattern = [trans_heads[n] in t_qheads for n, _ in trans]
        o_pattern = [canonical_head(n) in t_qheads or is_question(n, base_q) for n, _ in orig] if orig else None
        if orig and len(orig) == len(trans) and o_pattern == t_pattern:
            for (tn, tt), (_, ot) in zip(trans, orig):
                turns.append({**{k: v for k, v in item.items() if k not in ("original", "translation")},
                              "type": "dialogue", "speaker": trans_heads[tn], "original": ot, "translation": tt})
            stats["split"] += 1
        else:
            stats["unsplit"] += 1
            if debug:
                print(f"    unsplit: trans={t_seq}  orig={[n for n, _ in orig] if orig else None}")
            turns.append(item)

    # --- phase 2: who asks, across the whole post ---
    qset = question_set(data)
    by_speaker = {}
    for t in turns:
        sp = str(t.get("speaker") or "").strip()
        if sp and not STRUCTURAL.match(sp):
            by_speaker.setdefault(sp, []).append(t)
    lengths = {sp: median(len(str(t.get("translation") or "")) for t in group) for sp, group in by_speaker.items()}
    for sp, group in by_speaker.items():
        others = median(v for k, v in lengths.items() if k != sp)
        if is_question(sp, qset) or asks_mostly(group, others):
            qset.add(norm(sp))
    title = str(data.get("title") or "") + str(data.get("original_title") or "")
    if re.search(r"社长问|社長が訊く|Iwata Asks", title, re.I):
        qset.add(norm("岩田聪"))
    interviewer_label = str(data.get("interviewer") or data.get("source_name") or data.get("publication") or "提问").split("（")[0].split("(")[0].strip() or "提问"

    out = []
    for index, item in enumerate(turns):
        if item.get("role"):
            out.append(item); stats["kept"] += 1; continue
        speaker = str(item.get("speaker") or "").strip()
        kind = item.get("type")
        if kind in ("header", "heading", "image") or (kind == "narrative" and speaker):
            out.append(item); continue
        if speaker and STRUCTURAL.match(speaker):
            item = dict(item); item.pop("speaker", None); out.append(item); stats["structural"] += 1; continue
        if speaker:
            item = dict(item)
            item["role"] = "question" if is_question(speaker, qset) else "answer"
            stats[item["role"]] += 1; out.append(item); continue
        # speakerless, reads as a question, and an answer follows
        text = str(item.get("translation") or "").strip()
        nxt = turns[index + 1] if index + 1 < len(turns) else None
        nsp = str(nxt.get("speaker") or "").strip() if nxt else ""
        if text and ASKS.search(text) and len(text) < 400 and nsp and not STRUCTURAL.match(nsp) and not is_question(nsp, qset):
            item = dict(item); item["role"] = "question"; item["speaker"] = interviewer_label
            stats["question"] += 1; out.append(item); continue
        out.append(item)

    line = (f"{path.split('/')[-1].split(chr(92))[-1][:60]:62s} Q {stats['question']:3d}  A {stats['answer']:3d}  "
            f"structural {stats['structural']:2d}  split {stats['split']:2d}  unsplit {stats['unsplit']:2d}"
            + ("  (already done)" if stats["kept"] and not stats["question"] and not stats["answer"] else ""))
    if write and (stats["question"] or stats["answer"] or stats["structural"] or stats["split"]):
        data["parallel_items"] = out
        io.open(path, "w", encoding="utf-8", newline="\n").write(
            "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000) + "---" + body)
        line += "  written"
    return line


if __name__ == "__main__":
    write = "--write" in sys.argv
    debug = "--debug" in sys.argv
    paths = [p for a in sys.argv[1:] if not a.startswith("--") for p in glob.glob(a)]
    for p in sorted(paths):
        print(process(p, write, debug))
