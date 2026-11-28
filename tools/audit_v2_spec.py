#!/usr/bin/env python3
"""Unified V2 Archive Acceptance Spec auditor (implements V2-G1..V2-G8).

Encodes every check derived from the 2026-10 / 2026-11 zero-fabrication and
translation audits:
  V2-G1  Unified parallel_items / translation_segments schema (no HTML/table body, no text:{zh,en}, no empty originals on body rows)
  V2-G2  Zero fabrication & multi-source 6-gram / OCR / scan JSON fidelity; bans pokeamice.com self-citations & pseudo-essay markers
  V2-G3  Translation faithfulness & anti-padding (JA->ZH median <= 0.90, no >1.15 bloat, no translator-notes in note, no kana leaks, no forbidden terms)
  V2-G4  DOM chrome, ad promo, related-article, newsletter CTA, and footer purity
  V2-G5  Speaker attribution & zero generic '受访嘉宾' check
  V2-G6  Deduplication (URL & retired-draft collision check against catalog + _drafts/retired-*)
  V2-G7  Required metadata (archive_type, source dict, workflow dict, entities dict, interview_id)
  V2-G8  Catalog / CSV parity & link integrity

Usage:
    python tools/audit_v2_spec.py --posts _posts/2026-*.md
    python tools/audit_v2_spec.py --untracked
    python tools/audit_v2_spec.py --all --skip-fidelity --json scratch/v2_audit.json
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_source_fidelity as asf  # noqa: E402

LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

RE_BODY_LEGACY = re.compile(
    r'<div\s+class="(?:parallel-lang-source|parallel-container|lang-ja)"|\|\s*日本語原文\s*\|\s*中文',
    re.I,
)
RE_PSEUDO_ESSAY = re.compile(
    r"^(?:考[証证](?:前言|背景)|本稿は、|文献档案库说明)|(?:学术归档评注|奇迹之作|波澜壮阔|震撼业界)"
)
RE_PSEUDO_ORIGIN_PREFIX = re.compile(r"^(?:考証(?:前言|背景)|本稿は、)")
RE_CN_IN_JA_NOTE = re.compile(r"[（(][\u4e00-\u9fff]{2,12}[)）]")
# Simplified-Chinese-only characters that never appear as standard Japanese Joyo kanji
RE_SIMP_ONLY = re.compile(r"[证说讲请谈观览编辑译该这为专访录实纪构设进历]")
RE_HTML_LEAK = re.compile(r"<(?:div|span|p|br|a\s+href|/div|/p|/a)\b", re.I)
RE_PLACEHOLDER = re.compile(r"\[TODO\]|TODO:|FIXME|待翻译|\[TRANSLATE\]")
RE_FORBIDDEN_TERMS = re.compile(r"宠物小精灵|神奇宝贝|口袋妖怪|口袋魔鬼")
RE_NOTE_WORKLOG = re.compile(r"译注待|TODO|疑似网页|脚本代码|待核|未核实|待补充")
RE_NOISE_CHROME = re.compile(
    r"cookie policy|privacy policy|all rights reserved|subscribe to our|sign up for|"
    r"related articles|share this article|この記事をシェア|関連記事一覧|関連記事：|▼関連記事|［関連記事］|"
    r"Amazon\s*で\s*買う|楽天ブックス\s*で\s*買う|ご購入はお早めに|特別付録|"
    r"無断転載|返回顶部|隐私政策|订阅我们的|Perfume最新情報|バックナンバー一覧|バックナンバーを見る|"
    r"この記事の画像・SNS投稿|■\s*最近のコラム|［\s*HOME\s*］|このブログを購読|"
    r"カテゴリ一覧|この記事にはアフィリエイトリンクが含まれる|GAME Watchホームページ|"
    r"Copyright\s*\(c\)",
    re.I,
)
RE_KANA = re.compile(r"[\u3040-\u309f\u30a0-\u30ff]")
RE_CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
BRACKET_GLOSS = re.compile(r"[（(][^（()）]{0,60}[)）]")
PUFF_WORDS = [
    "淋漓尽致", "叹为观止", "无与伦比", "史无前例", "划时代", "前所未有", "令人震撼", "震撼业界",
    "奇迹般", "翻天覆地", "质的飞跃", "飞跃式", "里程碑式", "登峰造极", "拍案叫绝", "回味无穷",
    "心潮澎湃", "彻底颠覆", "颠覆性", "革命性", "传世", "永垂",
]
RE_PUFF = re.compile("|".join(map(re.escape, PUFF_WORDS)))
CALQUE_JARGON = [
    "过家家共犯", "共犯关系", "营销媒体", "编集部",
    "致死量", "装置机能", "心智占领", "生态闭环", "赋能他人",
    "企画", "出展",
    "史诗长访", "史诗级长访", "史诗座谈", "史诗对谈", "殿堂级",
    "版权裂变", "跨媒体破圈", "破圈生态", "负痛点", "两大狙击点",
    "颗粒度", "社交力拉满",
]
RE_CALQUE = re.compile(
    "|".join(map(re.escape, CALQUE_JARGON))
    + r"|(?:企划人|营销人)(?![员数口物才们类群])|(?:企划阵|制作阵)(?![容营])"
)


def normalize_url(u: str | None) -> str:
    if not u:
        return ""
    s = str(u).strip().rstrip("/")
    s = re.sub(r"^https?://", "https://", s, flags=re.I)
    s = s.replace("https://www.gamasutra.com/", "https://www.gamedeveloper.com/")
    s = s.replace("https://gamasutra.com/", "https://www.gamedeveloper.com/")
    return s


def load_post(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if not raw.startswith("---\n"):
        return None, raw, "missing YAML frontmatter start"
    rest = raw[4:]
    if "\n---\n" not in rest and not rest.endswith("\n---"):
        return None, raw, "unclosed YAML frontmatter"
    fm_text, _, body = rest.partition("\n---\n") if "\n---\n" in rest else (rest[:-4], "", "")
    try:
        fm = yaml.load(fm_text, Loader=LOADER)
    except Exception as exc:
        return None, body, f"YAML parse error: {str(exc)[:100]}"
    if not isinstance(fm, dict):
        return None, body, "frontmatter is not a dict"
    return fm, body, None


def extra_local_source(fm: dict[str, Any], post_path: Path) -> str:
    """Gather additional primary caches ignored by audit_source_fidelity.py:
    scratch/fetched_html/<ID>*.html, scratch/scans/<ID>_source.json, scan-prepared/<scan_set>/
    """
    parts: list[str] = []
    pid = fm.get("interview_id")
    if pid:
        fh_dir = ROOT / "scratch" / "fetched_html"
        if fh_dir.exists():
            for p in sorted(fh_dir.glob(f"{pid}*.html")):
                raw = p.read_bytes()
                parts.append(asf.strip_html(asf.decode(raw)))
        sc_json = ROOT / "scratch" / "scans" / f"{pid}_source.json"
        if sc_json.exists():
            try:
                d = json.loads(sc_json.read_text(encoding="utf-8"))
                for para in d.get("paragraphs", []):
                    t = para.get("text") if isinstance(para, dict) else para
                    if isinstance(t, str):
                        parts.append(t)
            except Exception:
                pass
    scan_set = fm.get("scan_set")
    if scan_set:
        sp = ROOT / "scan-prepared" / str(scan_set)
        if sp.exists():
            for tf in sorted(sp.glob("*.txt")):
                parts.append(tf.read_text(encoding="utf-8", errors="replace"))
            ocr = sp / "ocr_transcriptions"
            if ocr.exists():
                for jf in sorted(ocr.glob("*.json")):
                    try:
                        d = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                        if isinstance(d, dict) and "boxes" in d:
                            parts.append(" ".join(b.get("text", "") for b in d["boxes"] if isinstance(b, dict)))
                    except Exception:
                        pass
    return "\n".join(parts)


def load_origin_main_posts() -> set[str]:
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", "origin/main", "_posts"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        ).stdout
        return set(out.splitlines())
    except Exception:
        return set()


def load_retired_names() -> set[str]:
    drafts = ROOT / "_drafts"
    if not drafts.exists():
        return set()
    return {p.name for p in drafts.rglob("*.md") if "retired-" in p.as_posix()}


def audit_one(
    path: Path,
    cat_by_id: dict[str, dict],
    cat_by_pf: dict[str, dict],
    url_to_posts: dict[str, list[str]],
    retired_names: set[str],
    origin_main_posts: set[str],
    offline: bool,
    skip_fidelity: bool,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    rel = path.relative_to(ROOT).as_posix()
    fm, body, err = load_post(path)
    if err or fm is None:
        return {"post": rel, "status": "FAIL", "failures": [f"V2-G1: {err}"], "warnings": []}

    # V2-G6: Retired shadow collision
    if path.name in retired_names:
        failures.append("V2-G6: file name also exists in _drafts/retired-*")

    # V2-G7: Required metadata
    layout = str(fm.get("layout") or "")
    is_legacy_dir_or_blog = layout in ("gamefreak-director", "gamefreak-legacy-blog", "single") or "-gamefreak-" in path.name or "[站点]" in path.name or "[整理]" in path.name
    is_legacy_workflow = is_legacy_dir_or_blog or (rel in origin_main_posts)
    for k in ("archive_type", "source", "workflow", "entities"):
        if not fm.get(k):
            if k == "workflow" and is_legacy_workflow:
                warnings.append(f"V2-G7: legacy post missing '{k}'")
            else:
                failures.append(f"V2-G7: missing required frontmatter '{k}'")
    src = fm.get("source")
    if src is not None and not isinstance(src, dict):
        failures.append(f"V2-G7: 'source' must be a dict, got {type(src).__name__}")
    wf = fm.get("workflow")
    if wf is not None and not isinstance(wf, dict):
        failures.append("V2-G7: 'workflow' must be a dict")

    # Catalog 1:1 check
    pid = fm.get("interview_id")
    if not pid:
        if not is_legacy_dir_or_blog and fm.get("archive_type") not in ("developer_memoir", "developer_message"):
            warnings.append("V2-G7: missing interview_id")
    else:
        c_row = cat_by_id.get(pid)
        if not c_row:
            failures.append(f"V2-G8: interview_id '{pid}' not found in catalog JSON")
        else:
            if c_row.get("post_file") != rel:
                failures.append(f"V2-G8: catalog post_file mismatch ({c_row.get('post_file')} != {rel})")
            if c_row.get("status") != "imported":
                failures.append(f"V2-G8: catalog status for {pid} is {c_row.get('status')!r}, expected 'imported'")

    # V2-G2 URL validity + V2-G6 dedup
    src_url = (src.get("url") if isinstance(src, dict) else None) or fm.get("source_url") or fm.get("original_link") or fm.get("original_url")
    src_kind = fm.get("source_kind") or (src.get("source_type") if isinstance(src, dict) else None) or ""
    is_offline_print = any(x in str(src_kind) for x in ("scan", "magazine", "print", "book", "site_notice")) or fm.get("scan_set")
    if src_url and str(src_url).strip():
        su = str(src_url).strip()
        if "pokeamice.com" in su.lower() and not is_legacy_dir_or_blog:
            failures.append(f"V2-G2: forbidden self-citation URL {su!r}")
        elif not su.startswith("http"):
            failures.append(f"V2-G2: non-HTTP source URL {su!r}")
        elif not is_legacy_dir_or_blog:
            nu = normalize_url(su)
            dups = [p for p in url_to_posts.get(nu, []) if p != rel]
            if dups:
                failures.append(f"V2-G6: duplicate canonical URL with {dups}")
    elif not is_offline_print and not is_legacy_dir_or_blog:
        failures.append("V2-G2: missing source HTTP URL on web/non-print post")

    # V2-G1 Body legacy & parallel items schema
    if RE_BODY_LEGACY.search(body):
        failures.append("V2-G1: bilingual HTML/table found in Markdown body instead of frontmatter parallel_items")

    rows = fm.get("parallel_items") or fm.get("translation_segments") or []
    if not isinstance(rows, list) or not rows:
        if not is_legacy_dir_or_blog and layout == "interview-editorial":
            failures.append("V2-G1: missing non-empty parallel_items or translation_segments")
        status = "FAIL" if failures else ("WARN" if warnings else "PASS")
        return {"post": rel, "id": pid, "status": status, "failures": failures, "warnings": warnings}

    # Check rows V2-G1..G5
    ja_ratios: list[float] = []
    over_115: list[int] = []
    noise_hits: list[int] = []
    generic_spk = 0
    pseudo_orig = 0
    legacy_text_schema = 0
    empty_nonheading_orig = 0
    empty_tr = 0
    simp_in_ja_orig = 0
    html_leaks = 0
    placeholders = 0
    forbidden_terms = 0
    kana_leaks = 0
    note_worklogs = 0
    calque_hits: list[str] = []
    for meta_k in ("title", "display_title", "dek", "summary", "author", "interviewer"):
        mv = str(fm.get(meta_k) or "")
        if mv and RE_CALQUE.search(mv):
            calque_hits.extend(RE_CALQUE.findall(mv))
    align_mismatches: list[int] = []

    src_lang = str(
        (src.get("language") or src.get("lang") if isinstance(src, dict) else None)
        or fm.get("original_lang")
        or ""
    ).lower()

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        typ = str(row.get("type") or "paragraph")
        if typ in ("image", "hr"):
            continue
        if typ == "table":
            # Scan archive tables use rows_ja / rows_zh rather than original / translation
            if row.get("rows_ja") and row.get("rows_zh"):
                continue
        if "text" in row and isinstance(row.get("text"), dict) and "original" not in row:
            legacy_text_schema += 1
            continue
        o = str(row.get("original") or "").strip()
        t = str(row.get("translation") or "").strip()
        note = str(row.get("note") or "").strip()
        tr_note = str(row.get("translation_note") or "").strip()
        tr_note2 = str(row.get("translator_note") or "").strip()
        spk = str(row.get("speaker") or "").strip()

        # Intentional cross-column / cross-page scan merge stub
        merged_hint = tr_note + " " + tr_note2
        if not o and not t and ("已接回" in merged_hint or "并入前页" in merged_hint or "已并入" in merged_hint or "接回前页" in merged_hint):
            continue

        if spk == "受访嘉宾":
            generic_spk += 1
        if not t:
            empty_tr += 1
        if not o and typ not in ("heading", "header"):
            empty_nonheading_orig += 1
        if o and RE_PSEUDO_ORIGIN_PREFIX.search(o):
            pseudo_orig += 1
        if RE_PSEUDO_ESSAY.search(o) or RE_PSEUDO_ESSAY.search(t):
            if "考証前言" in o or "考証背景" in o or o.startswith("本稿は、"):
                pseudo_orig += 1
        if o and src_lang in ("ja", "jp", "") and RE_KANA.search(o):
            # Simplified-Chinese glyph inside Japanese original (not inside ASCII/EN)
            if RE_SIMP_ONLY.search(o) or RE_CN_IN_JA_NOTE.search(o):
                # Distinguish real Japanese kanji vs simplified-only glyphs (RE_SIMP_ONLY contains JP-absent forms)
                if RE_SIMP_ONLY.search(o):
                    simp_in_ja_orig += 1
        if RE_HTML_LEAK.search(o + " " + t):
            html_leaks += 1
        if RE_PLACEHOLDER.search(o + " " + t + " " + note):
            placeholders += 1
        if RE_FORBIDDEN_TERMS.search(t):
            forbidden_terms += 1
        if RE_CALQUE.search(t):
            calque_hits.extend(RE_CALQUE.findall(t))
        if note and RE_NOTE_WORKLOG.search(note):
            note_worklogs += 1
        if RE_NOISE_CHROME.search(o):
            noise_hits.append(idx)
        kana_chars = sum(len(k) for k in RE_KANA.findall(t))
        if kana_chars > 12 and kana_chars / max(1, len(t)) > 0.18:
            kana_leaks += 1
        if o and t:
            oq = o.startswith(("――", "──"))
            tq = t.startswith(("——", "──", "――", "Q", "●", "▼"))
            ocap = o.startswith("▲")
            tcap = t.startswith("▲")
            if ocap != tcap or (oq and not tq):
                align_mismatches.append(idx)

        # Anti-padding JA -> ZH ratio check (skip headings and image captions)
        if src_lang in ("ja", "jp", "") and RE_KANA.search(o) and typ not in ("heading", "header") and o:
            t_clean = BRACKET_GLOSS.sub("", t)
            oc = len(RE_CJK.findall(o))
            tc = len(RE_CJK.findall(t_clean))
            if oc >= 15:
                r = tc / oc
                ja_ratios.append(r)
                if r > 1.15:
                    over_115.append(idx)

    if legacy_text_schema:
        failures.append(f"V2-G1: {legacy_text_schema} items use legacy 'text:{{zh,en}}' without original/translation")
    if empty_tr:
        failures.append(f"V2-G1: {empty_tr} non-image items have empty translation")
    if empty_nonheading_orig:
        failures.append(f"V2-G1: {empty_nonheading_orig} non-heading items have empty original")
    if pseudo_orig:
        failures.append(f"V2-G2: {pseudo_orig} items contain pseudo-essay prefix ('考証前言'/'考証背景'/'本稿は、')")
    if simp_in_ja_orig:
        failures.append(f"V2-G2: {simp_in_ja_orig} Japanese original items contain Simplified-Chinese-only characters")
    if generic_spk:
        failures.append(f"V2-G5: {generic_spk} items use banned generic speaker '受访嘉宾'")
    if noise_hits:
        failures.append(f"V2-G4: {len(noise_hits)} DOM chrome / ad / related-link items at {noise_hits[:5]}")
    if html_leaks:
        failures.append(f"V2-G7: {html_leaks} items contain raw HTML tag leaks")
    if placeholders:
        failures.append(f"V2-G7: {placeholders} items contain TODO/placeholder markers")
    if forbidden_terms:
        failures.append(f"V2-G7: {forbidden_terms} items contain non-official Pokémon terms")
    if note_worklogs:
        failures.append(f"V2-G3: {note_worklogs} items contain translator worklog text in 'note'")
    if kana_leaks:
        warnings.append(f"V2-G3: {kana_leaks} items have >18% residual kana in translation")
    if calque_hits:
        warnings.append(f"V2-G3: awkward calque/jargon in translation: {sorted(set(calque_hits))}")
    if len(align_mismatches) >= 2:
        warnings.append(f"V2-G5: {len(align_mismatches)} items have marker alignment mismatch at {align_mismatches[:5]}")

    if ja_ratios:
        s_ratios = sorted(ja_ratios)
        med = s_ratios[len(s_ratios) // 2]
        if med > 0.90:
            failures.append(f"V2-G3: JA->ZH median ratio {med:.2f} > 0.90 (translation inflation)")
        if len(over_115) > 0:
            warnings.append(f"V2-G3: {len(over_115)} segments with ratio > 1.15 at {over_115[:5]}")

    # V2-G2 Source Fidelity check (if enabled and not purely offline print without local OCR)
    fidelity_info = None
    if not skip_fidelity:
        res = asf.audit(str(path), hit=0.55, offline=offline, verbose=False)
        verdict = res.get("verdict")
        if verdict not in ("OK", "NOTHING TO CHECK"):
            # Try augmenting with scratch/fetched_html, scratch/scans JSON, or scan-prepared/ OCR!
            extra = extra_local_source(fm, path)
            if extra.strip():
                gs = asf.grams(asf.norm(extra))
                segs = [r for r in rows if isinstance(r, dict) and (r.get("original") or "").strip() and r.get("type") not in ("image", "hr") and r.get("role") != "image" and not str(r.get("original") or "").strip().startswith("/assets/")]
                chk = hits = 0
                for r in segs:
                    n = asf.norm(r.get("original"))
                    if len(n) < 12:
                        continue
                    chk += 1
                    g = asf.grams(n)
                    if (len(g & gs) / max(1, len(g))) >= 0.55:
                        hits += 1
                pct = round(100 * hits / chk, 1) if chk else 100.0
                if pct >= 90.0:
                    verdict = "OK"
                    res["pct"] = pct
                    res["found"], res["checked"] = hits, chk
        fidelity_info = {"verdict": verdict, "pct": res.get("pct"), "found": res.get("found"), "checked": res.get("checked")}
        if verdict in ("NOT IN SOURCE", "PARTLY NOT IN SOURCE"):
            failures.append(f"V2-G2: fidelity check {verdict} ({res.get('pct')}% = {res.get('found')}/{res.get('checked')})")
        elif verdict == "NOTHING TO CHECK":
            failures.append("V2-G2: fidelity returned NOTHING TO CHECK (no verifiable original segments)")
        elif verdict == "UNVERIFIABLE" and not is_offline_print:
            warnings.append("V2-G2: web source UNVERIFIABLE (fetch blocked or offline)")

    status = "FAIL" if failures else ("WARN" if warnings else "PASS")
    return {"post": rel, "id": pid, "status": status, "fidelity": fidelity_info, "failures": failures, "warnings": warnings}


def check_catalog_sync() -> list[str]:
    errs: list[str] = []
    jpath = ROOT / "data" / "pokemon_1000_interviews.json"
    cpath = ROOT / "data" / "pokemon_1000_interviews.csv"
    data = json.loads(jpath.read_text(encoding="utf-8"))
    with cpath.open(encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    if len(data) != len(csv_rows):
        errs.append(f"V2-G8: JSON count ({len(data)}) != CSV rows ({len(csv_rows)})")
    for x in data:
        if x.get("status") == "imported":
            pf = x.get("post_file")
            if not pf or not (ROOT / pf).exists():
                errs.append(f"V2-G8: {x['id']} imported but post_file missing: {pf}")
            u = (x.get("url") or "").strip()
            if u and not u.startswith("http"):
                errs.append(f"V2-G2: {x['id']} non-HTTP catalog url: {u!r}")
        else:
            if not x.get("disposition"):
                errs.append(f"V2-G8: unimported {x['id']} missing disposition")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", nargs="*", default=[])
    ap.add_argument("--untracked", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--skip-fidelity", action="store_true")
    ap.add_argument("--skip-catalog", action="store_true")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    paths: list[Path] = []
    for pat in args.posts:
        paths.extend(Path(p) for p in sorted(glob.glob(pat)))
    if args.untracked:
        out = subprocess.run(["git", "-c", "core.quotePath=false", "status", "--porcelain", "_posts"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
        for l in out.splitlines():
            if l.startswith("?? "):
                paths.append(ROOT / l[3:].strip().strip('"'))
    if args.all:
        paths.extend(sorted((ROOT / "_posts").glob("*.md")))
    paths = list(dict.fromkeys(p.resolve() for p in paths if p.exists()))
    if not paths:
        raise SystemExit("No target posts selected. Use --posts, --untracked, or --all.")

    cat = json.loads((ROOT / "data" / "pokemon_1000_interviews.json").read_text(encoding="utf-8"))
    cat_by_id = {x["id"]: x for x in cat}
    cat_by_pf = {x["post_file"]: x for x in cat if x.get("post_file")}

    # Build canonical URL map across _posts/ (fast header read)
    url_re = re.compile(r'^\s*(?:url|source_url|original_link):\s*["\']?(https?://[^\s"\']+)', re.M)
    url_to_posts: dict[str, list[str]] = {}
    for p in sorted((ROOT / "_posts").glob("*.md")):
        if "Updates" in p.name or "[站点]" in p.name:
            continue
        head = p.open("r", encoding="utf-8-sig", errors="replace").read(4096)
        # Only index canonical source URLs, not secondary 'links:' cross-references
        head_no_links = re.split(r"^links:\s*$", head, maxsplit=1, flags=re.M)[0]
        rel = p.relative_to(ROOT).as_posix()
        for m in url_re.finditer(head_no_links):
            nu = normalize_url(m.group(1))
            if nu and "pokeamice.com" not in nu:
                url_to_posts.setdefault(nu, []).append(rel)

    retired_names = load_retired_names()
    origin_main_posts = load_origin_main_posts()
    results = [
        audit_one(p, cat_by_id, cat_by_pf, url_to_posts, retired_names, origin_main_posts, args.offline, args.skip_fidelity)
        for p in paths
    ]

    cat_errs = [] if args.skip_catalog else check_catalog_sync()
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    passes = [r for r in results if r["status"] == "PASS"]

    print(f"V2 Spec Audit: {len(results)} posts | PASS={len(passes)} WARN={len(warns)} FAIL={len(fails)} | catalog_errors={len(cat_errs)}")
    for ce in cat_errs[:15]:
        print("  [CATALOG FAIL]", ce)
    for r in fails + warns:
        print(f"  [{r['status']}] {r['post']} ({r.get('id')})")
        for f in r["failures"]:
            print(f"      FAIL: {f}")
        for w in r["warnings"]:
            print(f"      WARN: {w}")

    if args.json:
        Path(args.json).write_text(json.dumps({"catalog_errors": cat_errs, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("wrote", args.json)

    if fails or cat_errs:
        sys.exit(1)


if __name__ == "__main__":
    main()
