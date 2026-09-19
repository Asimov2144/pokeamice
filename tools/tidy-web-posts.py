"""What a web page leaves in an imported post, and the headings it lost.

An imported article carries lines the page had around it - a copyright notice,
the share buttons, the Wayback Machine's calendar, the site's own menu - and
sometimes a section title came through as a paragraph. This lists them, post by
post, and takes them out.

    python tools/tidy-web-posts.py                # report: every post with parallel_items
    python tools/tidy-web-posts.py --only glitter # posts whose file name contains this
    python tools/tidy-web-posts.py --fix          # drop the junk, turn the titles into headings
    python tools/tidy-web-posts.py --fix --no-headings
    python tools/tidy-web-posts.py --fix --only pokken --unguarded   # a file git shows modified (by this tool, earlier)

Findings:
  junk      a copyright / share / navigation / Wayback line          -> dropped
  menu      a run of six or more short label-like lines in a row      -> dropped
  tail      the site after the article's last line or last turn       -> dropped
  label     a speaker's name alone on a line before an unmarked turn   -> dropped, the turn gets the role
  heading   a short title-like line before a paragraph or a picture   -> type: heading, level 3

A post another session is editing (modified or untracked in git) is reported but
never written. The edit keeps the file's own formatting: an item is a text block
between "- " lines under parallel_items, and only those blocks change.
"""
import io
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"

JUNK = re.compile(
    r"©|\(c\)\s*(?:19|20)\d\d|\(C\)|Copyright|All [Rr]ights [Rr]eserved|無断転載|転載(?:を)?禁|禁止转载|版权所有|"
    r"^About this capture$|^TIMESTAMPS$|Wayback Machine|^\d{1,2} [A-Z][a-z]{2} \d{4} - \d{1,2} [A-Z][a-z]{2} \d{4}$|"
    r"^(?:[A-Z][a-z]{2} ?){1,3}(?:\d{1,2} )?(?:\d{4} ?){1,3}$|^success fail|"
    r"^Posted [Bb]y .{0,40} (?:at|on) |^Pages?: ?\d|^Return to .* Index|^By AddToAny|^Share (?:this|on)|^Tweet$|^E-?mail$|^电子邮件$|^Print$|"
    r"(?:Facebook|Twitter|Reddit|Pinterest|Tumblr) (?:Twitter|Google|Pinterest|LinkedIn|Reddit|Tumblr|Delicious)|"
    r"^Related (?:Posts?|Articles?|Stories|Reading)|^Leave a (?:Reply|Comment)|^Comments?$|^Tags?[:：]|^Filed under|^Categor(?:y|ies)[:：]|"
    r"^(?:Previous|Next) (?:Post|Page|Article)|^Subscribe|^Sign up|^Newsletter|^Advertisement$|^Sponsored|^Loading\.\.\.|^Skip to |"
    r"^関連記事|^この記事をシェア|^記事をシェア|^シェアする|^ツイート$|^いいね！?$|^あわせて読みたい|^おすすめ記事|^人気記事|^注目度|^前の記事|^次の記事|"
    r"^タグ[:：]|^カテゴリ[:：]|^この記事の写真|^写真ページ|^画像集|^拡大画像|^関連リンク|^公式サイトはこちら|^.{0,20}はこちら$|"
    r"^www\.|^https?://|^Read more|^More (?:from|Great)|^Follow (?:us|@)|^Like us|^Add Us|^Powered by|^Photo(?:s)?: |^Image credit|^Screenshot: |"
    r"^Written by .*\d{4}$|^Ampliar$|^Open Navigation Menu$|^Etiquetas |^Más lanzamientos|^interviewee$|^information$|^目次[＆&]|^目次閉じる|"
    r"^(?:判型|総ページ数|定価|出版社|ISBN|発売日|希望小売価格|対応機種|ジャンル|プレイ人数|CERO)[：:]|^.{0,24}はこちら(?:から)?$|"
    r"^[^\s：:]{1,20}[：:]$",                                   # a speaker label that lost its line
    re.I)
# the line a page ends its article with: what follows is the site, not the text
END = re.compile(r"^Tags?[:：]|^Etiquetas |^Read More|^Read Past|^Related|^Más lanzamientos|^Return to|^Pages?: ?\d|^Videos About|"
                 r"^関連記事|^この記事をシェア|^あわせて読みたい|^おすすめ記事|^人気記事|^Lava’s Latest", re.I)
# a line that names a person or a post, not a section
STRAY_LABEL = re.compile(r"^([^\s：:]{1,20})[：:]$")
ASKERS = {"4gamer", "ファミ通", "週刊ファミ通", "編集部", "記者", "インサイド", "inside", "oricon", "電ファミ", "東洋経済", "cgworld", "聞き手",
          "game informer", "gi", "polygon", "kotaku", "vg247", "nintendo life", "nl", "pokemon.com", "q", "ｑ", "question", "meristation"}
# the page's title, from the source block of the front matter
SRC_TITLE = re.compile(r"^source:[ \t]*\r?\n(?:[ \t]+.*\r?\n)*?[ \t]+title:[ \t]*['\"]?(.+?)['\"]?[ \t]*\r?$", re.M)
# the credits a magazine signs an article with
CREDIT = re.compile(r"^(?:[A-Z]{3,}|文字起こし|取材|文|構成|撮影|編集|写真)[＿_ ／/：:]")
NOT_HEADING = re.compile(r"(?:さん|氏|様)$|^※|株式会社|代表取締役|CEO|取締役|部長|課長|プロデューサー$|ディレクター$|デザイナー$|プログラマー$|プランナー$")
# a copyright line that is also a real sentence is kept: the notice is short
JUNK_MAX = 220
LABEL = re.compile(r"^[^。．.!?！？」』]{1,40}$")
SENT_END = re.compile(r"[。．.!?！？…:;,、，」』)）\"”’']\s*$")
EN_SMALL = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or", "with", "by", "from", "as", "vs", "vs.", "&", "de", "la", "le", "du", "des", "et"}


def parts(text):
    """(head, items, tail): the text before the first item under parallel_items,
    the item blocks, and the text from the next top-level key on. None when the
    post has no parallel_items."""
    m = re.search(r"^parallel_items:[ \t]*\r?\n", text, re.M)
    if not m:
        return None
    start = m.end()
    tail_m = re.compile(r"^(?=[A-Za-z_][\w-]*:|---\r?$)", re.M).search(text, start)
    end = tail_m.start() if tail_m else len(text)
    body = text[start:end]
    items = re.split(r"(?m)^(?=- )", body)
    if items and not items[0].startswith("- "):
        start += len(items[0])
        items = items[1:]
    return text[:start], items, text[end:]


def item_of(block):
    try:
        v = yaml.safe_load(block)
    except yaml.YAMLError:
        return None
    return v[0] if isinstance(v, list) and v and isinstance(v[0], dict) else None


TEXT_TYPES = (None, "paragraph", "narrative", "caption", "note")


def is_junk(it):
    if it.get("type") not in TEXT_TYPES:
        return False
    o = str(it.get("original") or "").strip()
    if not o:
        # an empty turn; a turn whose translation is there but whose original was never
        # brought over is the text, not junk
        return "image" not in it and not str(it.get("translation") or "").strip()
    # a notice that opens with the copyright sign runs long when it lists every licensor
    limit = JUNK_MAX * 2 if re.match(r"^(?:©|\(C\)|Copyright)", o, re.I) else JUNK_MAX
    return len(o) <= limit and bool(JUNK.search(o))


def is_label(it):
    if it.get("type") not in (None, "paragraph") or it.get("role"):
        return False
    o = str(it.get("original") or "").strip()
    return bool(o) and bool(LABEL.match(o)) and not SENT_END.search(o)


def plain(s):
    """Lower case without accents, for comparing a title with itself on another page."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).strip().lower()


def title_like(o, lang):
    """A heading a page set as a paragraph: short, no sentence end, and
    written the way this language writes titles."""
    if not LABEL.match(o) or SENT_END.search(o) or NOT_HEADING.search(o) or not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ぀-ヿ一-鿿]", o):
        return False
    if re.match(r"^[―─—–\-「『“\"(（【]", o):
        return False
    if lang == "ja" or re.search(r"[぀-ヿ一-鿿]", o):
        return bool(re.match(r"^[■◆●▼▲◎☆★【〈《]", o) or re.match(r"^第[0-9０-９一二三四五六七八九十]+[章回話部節]", o)
                    or (len(o) <= 24 and not re.search(r"[はがをにでと]\S{2,}$", o) and not re.search(r"[はがをにで]", o)))
    words = re.findall(r"[A-Za-zÀ-ÿ'’\-]+", o)
    if len(words) < 1 or len(words) > 10:
        return False
    if re.match(r"^\d", o) and not re.match(r"^\d+[.)]", o):
        return False
    caps = [w for w in words if w[0].isupper() or w.lower() in EN_SMALL]
    return len(caps) >= max(1, round(len(words) * 0.75))


def findings(items, lang, src_title=""):
    """[(index, kind)] over the item blocks of a post."""
    return findings_parsed([item_of(b) or {} for b in items], lang, src_title)


def apply(parsed, lang, src_title=""):
    """The parsed items with the findings applied - what an importer calls before writing."""
    found = findings_parsed(parsed, lang, src_title)
    drop = {f[0] for f in found if f[1] in ("junk", "menu", "tail", "label")}
    heads = {f[0] for f in found if f[1] == "heading"}
    marks = {f[0] + 1: f[2] for f in found if f[1] == "label"}
    out = []
    for k, it in enumerate(parsed):
        if k in drop:
            continue
        if k in marks:
            it = {**it, "role": marks[k]["role"], "speaker": marks[k]["speaker"]}
        if k in heads:
            it = {"type": "heading", "level": 3, **{kk: v for kk, v in it.items() if kk in ("original", "translation")}}
        out.append(it)
    return out


def findings_parsed(parsed, lang, src_title=""):
    """[(index, kind)] over the parsed items."""
    out = []
    n = len(parsed)
    # the page's title repeated as the first line: the post has its own
    first = plain(str(parsed[0].get("original") or "")) if n else ""
    if n and parsed[0].get("type") in (None, "paragraph") and src_title and first == plain(src_title):
        out.append((0, "junk"))
    # a menu: a run of label lines with nothing else in it
    i = 0
    while i < n:
        j = i
        while j < n and is_label(parsed[j]) and not is_junk(parsed[j]):
            j += 1
        if j - i >= 6:
            run = [str(parsed[k].get("original") or "").strip() for k in range(i, j)]
            # a credits or spec list ("プログラム：田尻智") is the text, not a menu
            pairs = sum(1 for o in run if re.search(r"\S[：:]\s*\S", o) or re.match(r"^[•・‣▪]", o))
            if pairs < len(run) * 0.5:
                out.extend((k, "menu") for k in range(i, j))
        i = j + 1 if j == i else j
    # the site after the article: from the line the page ends the text with, or, in
    # a dialogue, after the last turn, when nothing that reads like text follows
    def textual(it):
        o = str(it.get("original") or "")
        return bool(it.get("role")) or it.get("type") == "heading" or (len(o) >= 200 and not JUNK.search(o[:30]))
    cuts = []
    for m, it in enumerate(parsed):
        if m >= n * 0.5 and it.get("type") in (None, "paragraph") and END.search(str(it.get("original") or "").strip()):
            if not any(textual(x) for x in parsed[m + 1:]):
                cuts.append(m)
                break
    # after the last turn, or in an article after the last real paragraph: when what is
    # left is labels and junk. A picture, and the label beside it (its caption), and a
    # credit line (TEXT＿…) are not counted - they are the article's
    anchors = [k for k, it in enumerate(parsed) if it.get("role")]
    if not anchors:
        anchors = [k for k, it in enumerate(parsed) if it.get("type") in (None, "paragraph") and len(str(it.get("original") or "")) >= 120 and not is_junk(it)]
    last = max(anchors) if anchors else -1
    rest = []
    for k in range(last + 1, n):
        it = parsed[k]
        beside_image = it.get("type") == "image" or (k and parsed[k - 1].get("type") == "image") or (k + 1 < n and parsed[k + 1].get("type") == "image")
        if beside_image and not is_junk(it):
            continue
        rest.append(it)
    if len(rest) >= 6 and sum(1 for it in rest if (is_label(it) and not CREDIT.match(str(it.get("original") or ""))) or is_junk(it)) >= len(rest) * 0.8:
        # from the first label after the last turn: a closing sentence stays
        cuts.append(next(k for k in range(last + 1, n) if is_label(parsed[k]) or is_junk(parsed[k])))
    if cuts:
        out.extend((k, "tail") for k in range(min(cuts), n))
    seen = set()
    out = [f for f in out if not (f[0] in seen or seen.add(f[0]))]
    flagged = {k for k, _ in out}
    askers = {str(it.get("speaker") or "").strip() for it in parsed if it.get("role") == "question"}
    answerers = {str(it.get("speaker") or "").strip() for it in parsed if it.get("role") == "answer"}
    for k, it in enumerate(parsed):
        if k in flagged:
            continue
        if is_junk(it):
            o = str(it.get("original") or "").strip()
            m = STRAY_LABEL.match(o)
            nxt = parsed[k + 1] if k + 1 < n else None
            if m and nxt is not None and nxt.get("type") in (None, "paragraph") and not nxt.get("role"):
                # a speaker's label on its own line: the paragraph after it is that speaker's turn
                who = m.group(1)
                if who in answerers:
                    out.append((k, "label", {"role": "answer", "speaker": who}))
                    continue
                if who in askers or who.lower() in ASKERS or re.match(r"^[―─—–\-]+$", who):
                    out.append((k, "label", {"role": "question", "speaker": next(iter(askers), who)}))
                    continue
            out.append((k, "junk"))
            continue
        if it.get("type") in (None, "paragraph") and not it.get("role") and not it.get("quote"):
            o = str(it.get("original") or "").strip()
            nxt = parsed[k + 1] if k + 1 < n else None
            # before a paragraph; a label before a picture is more often its caption
            after = nxt is not None and nxt.get("type") in (None, "paragraph") and len(str(nxt.get("original") or "")) >= 80
            prv = parsed[k - 1] if k else None
            # in a Japanese page a label under a picture, or one of a row of labels, is a caption
            before = (prv is None or prv.get("role") or prv.get("type") == "heading"
                      or (prv.get("type") in (None, "paragraph") and len(str(prv.get("original") or "")) >= 80)
                      or (prv.get("type") == "image" and not re.search(r"[぀-ヿ一-鿿]", o)))
            if after and before and title_like(o, lang):
                out.append((k, "heading"))
    return sorted(out, key=lambda f: f[0])


def as_heading(block):
    """The block rewritten as a level-3 heading, keeping original / translation."""
    it = item_of(block) or {}
    keep = {"type": "heading", "level": 3}
    for k in ("original", "translation"):
        if it.get(k):
            keep[k] = it[k]
    nl = "\r\n" if block.endswith("\r\n") else "\n"
    text = yaml.safe_dump([keep], allow_unicode=True, sort_keys=False, width=1000)
    return text.replace("\n", nl)


def with_role(block, mark):
    """The block with the role and speaker a stray label named, after its first line."""
    lines = block.splitlines(keepends=True)
    nl = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    first = lines[0]
    if re.match(r"^- type: paragraph", first):
        first = "- role: " + mark["role"] + nl
        rest = lines[1:]
    else:
        rest = ["  role: " + mark["role"] + nl] + lines[1:]
    return first + "  speaker: " + mark["speaker"] + nl + "".join(rest)


def other_sessions_files():
    out = subprocess.run(["git", "-c", "core.quotepath=false", "status", "--porcelain", "--", "_posts"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return {ln[3:].strip().strip('"') for ln in out.splitlines() if ln[:2] in (" M", "??", "MM", "AM", " D", "A ", "M ")}


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    do_headings = "--no-headings" not in args
    only = [a.split("=", 1)[1] for a in args if a.startswith("--only=")] or ([args[args.index("--only") + 1]] if "--only" in args else [])
    # a file modified in the worktree is taken to be another session's - which, after a
    # first --fix, includes the files this tool wrote; --unguarded writes those too
    busy = set() if "--unguarded" in args else other_sessions_files()
    total = {"junk": 0, "menu": 0, "tail": 0, "label": 0, "heading": 0}
    touched = 0
    for path in sorted(POSTS.glob("*.md")):
        if only and not any(o in path.name for o in only):
            continue
        text = io.open(path, encoding="utf-8", newline="").read()
        p = parts(text)
        if not p:
            continue
        head, items, tail = p
        lang = "ja"
        m = re.search(r"^\s+language:\s*(\w+)", head, re.M)
        if m:
            lang = m.group(1)
        st = re.search(SRC_TITLE, head)
        found = findings(items, lang, st.group(1) if st else "")
        if not do_headings:
            found = [f for f in found if f[1] != "heading"]
        if not found:
            continue
        rel = "_posts/" + path.name
        state = "  (another session's file - not written)" if rel in busy else ""
        print(f"== {path.name}{state}")
        for f in found:
            k, kind = f[0], f[1]
            it = item_of(items[k]) or {}
            o = re.sub(r"\s+", " ", str(it.get("original") or ""))
            extra = f"  -> next: {f[2]['role']} {f[2]['speaker']}" if kind == "label" else ""
            print(f"   {kind:8s} #{k:<4d} {o[:90]}{extra}")
            total[kind] += 1
        if fix and rel not in busy:
            drop = {f[0] for f in found if f[1] in ("junk", "menu", "tail", "label")}
            heads = {f[0] for f in found if f[1] == "heading"}
            marks = {f[0] + 1: f[2] for f in found if f[1] == "label"}
            new_items = []
            for k, b in enumerate(items):
                if k in drop:
                    continue
                if k in marks:
                    b = with_role(b, marks[k])
                new_items.append(as_heading(b) if k in heads else b)
            new = head + "".join(new_items) + tail
            io.open(path, "w", encoding="utf-8", newline="").write(new)
            touched += 1
    print(f"\n{total['junk']} junk, {total['menu']} menu lines, {total['heading']} headings" + (f"; {touched} posts written" if fix else " (report only; --fix to apply)"))


if __name__ == "__main__":
    main()
