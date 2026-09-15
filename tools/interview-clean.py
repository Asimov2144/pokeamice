"""Source cleaning for interview posts: the language they are in, and the
website chrome that came in with them.

    python tools/interview-clean.py _posts/*.md            # report
    python tools/interview-clean.py _posts/*.md --write    # save

Two faults, both found on the live pages:

- English pieces showed "JA" beside English text. The layout used to fall
  back to Japanese when a post declared nothing, and several posts declared
  the wrong thing outright - five Spanish sources marked `en`. The language
  is read off the original text: kana is Japanese, hangul Korean, Latin with
  Spanish or French function words is that, Latin otherwise English, han
  alone means the source itself was Chinese. A declared value that
  disagrees with the text is reported and, with --write, replaced.

- "Sign In or Register" and "Search For: Search" reached the article body
  and were translated as prose. Segments that are nothing but navigation,
  sign-in, search, share, cookie, newsletter or copyright lines are removed.
  The match is on the whole segment, short ones only, so a sentence that
  happens to contain "search" is untouched.

Also drops `note: ""` / `comment: ""` fields - pipeline residue that reads
as a note to Liquid and drew a mark that opened onto nothing.

Idempotent; the report names every change so it can be read before --write.
"""
import glob
import io
import re
import sys

import yaml

KANA = re.compile(r"[぀-ヿ]")
HANGUL = re.compile(r"[가-힯]")
HAN = re.compile(r"[一-鿿]")
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
SPANISH = re.compile(r"\b(que|los|las|para|con|una|del|por|como|más|también|pero|sobre|desde)\b", re.I)
FRENCH = re.compile(r"\b(les|des|est|une|pour|dans|avec|sur|nous|vous|pas|être|c'est)\b", re.I)

BOILERPLATE = re.compile(
    r"^(sign in|sign up|log ?in|register|sign in or register|search( for)?:?( search)?|subscribe|newsletter|"
    r"share( this)?|tweet|facebook|twitter|reddit|advertisement|advertising|cookie|accept( all)?|"
    r"related( stories| articles)?|read more|more from|load more|comments?|leave a comment|"
    r"menu|navigation|skip to (main )?content|home|back to top|privacy( policy)?|terms( of (use|service))?|"
    r"copyright.*|©.*|all rights reserved\.?|"
    r"登录|注册|登录或注册|搜索[:：]?\s*搜索|订阅|分享|广告|相关文章|阅读更多|评论|菜单|返回顶部|隐私政策|使用条款)$",
    re.I)


def detect_language(text):
    """The language of a piece of source text, or None if it cannot say."""
    sample = text[:3000]
    if KANA.search(sample):
        return "ja"
    if HANGUL.search(sample):
        return "ko"
    latin, han = len(LATIN.findall(sample)), len(HAN.findall(sample))
    if latin > han * 2 and latin > 40:
        if len(SPANISH.findall(sample)) >= 6:
            return "es"
        if len(FRENCH.findall(sample)) >= 6:
            return "fr"
        return "en"
    if han > latin and han > 40:
        return "zh"
    return None


def is_boilerplate(item):
    for key in ("original", "translation"):
        text = str(item.get(key) or "").strip()
        if text and len(text) <= 60 and BOILERPLATE.match(text.strip(" .!?。！？")):
            return True
    return False


def process(path, write):
    raw = io.open(path, encoding="utf-8").read()
    head, front, body = raw.split("---", 2)
    try:
        data = yaml.safe_load(front) or {}
    except yaml.YAMLError as exc:
        # a post the parser cannot read is itself a finding; say so and go on
        mark = getattr(exc, "problem_mark", None)
        where = f" line {mark.line + 1}" if mark else ""
        return f"{path.split('/')[-1].split(chr(92))[-1][:58]:60s} UNREADABLE front matter{where}: {str(exc).splitlines()[0][:60]}"
    items = data.get("parallel_items")
    if not isinstance(items, list) or not items:
        return None
    notes, changed = [], False

    # language
    declared = data.get("original_lang")
    if not declared and isinstance(data.get("source"), dict):
        declared = data["source"].get("language")
    declared = str(declared).lower() if declared else None
    detected = detect_language(" ".join(str(i.get("original") or "") for i in items if isinstance(i, dict)))
    if detected and detected != declared:
        notes.append(f"lang {declared or '(none)'} -> {detected}")
        if write:
            data["original_lang"] = detected
            changed = True

    # empty annotations: `note: ""` on every turn is pipeline residue, and an
    # empty string is truthy to Liquid, so it used to draw a note mark that
    # opened onto nothing
    empties = 0
    for item in items:
        if isinstance(item, dict):
            for key in ("note", "comment", "comments"):
                if key in item and (item[key] is None or str(item[key]).strip() == ""):
                    empties += 1
                    if write:
                        del item[key]
    if empties:
        notes.append(f"empty note fields: {empties}")
        if write:
            changed = True

    # boilerplate
    kept, dropped = [], []
    for item in items:
        if isinstance(item, dict) and item.get("type") != "image" and is_boilerplate(item):
            dropped.append(str(item.get("original") or item.get("translation") or "").strip()[:40])
        else:
            kept.append(item)
    if dropped:
        notes.append(f"dropped {len(dropped)}: " + " | ".join(dropped))
        if write:
            data["parallel_items"] = kept
            changed = True

    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(
            "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000) + "---" + body)
    if notes:
        name = path.split("/")[-1].split(chr(92))[-1][:58]
        return f"{name:60s} {'; '.join(notes)}" + ("  written" if changed else "")
    return None


if __name__ == "__main__":
    # the report quotes the segments it drops, which include ©; a GBK console
    # would fail on the first one
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    write = "--write" in sys.argv
    paths = [p for a in sys.argv[1:] if not a.startswith("--") for p in glob.glob(a)]
    lines = [line for line in (process(p, write) for p in sorted(paths)) if line]
    print("\n".join(lines))
    print(f"\n{len(lines)} post(s) with changes{' written' if write else ' (dry run)'}")
