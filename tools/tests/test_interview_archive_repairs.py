"""Regressions for reviewed scan order, anonymous speakers and source links."""
import importlib.util
import json
import re
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("archive_export", ROOT / "tools/export-docs-archive.py")
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class InterviewArchiveRepairs(unittest.TestCase):
    REVIEWED_SCANS = (
        "2003-02-21-scan-ndream-084-ruby-sapphire-interview",
        "2004-03-21-scan-ndream-108-frlg-developer-interview",
        "2005-07-15-scan-corocoro-200508-diamond-pearl-scoop",
        "2010-09-16-scan-famitsu-1137-bw-launch-interview",
        "2010-09-23-scan-famitsu-1138-bw-secrets-interview",
        "2011-01-06-scan-davinci-201102-masuda-comment",
        "2011-01-20-scan-otonafamily-201103-masuda-bw-adults",
        "2012-07-19-scan-famitsu-1233-b2w2-interview",
        "2012-07-21-scan-ndream-221-b2w2-developer-interview",
        "2012-08-21-scan-ndream-222-b2w2-pwt-pokewood",
        "2013-09-21-scan-ndream-235-xy-developer-interview",
    )

    def test_reviewed_scans_keep_reader_order_and_quote_targets(self):
        quotes = yaml.safe_load((ROOT / "_data/quotes.yml").read_text(encoding="utf-8"))["quotes"]
        for stem in self.REVIEWED_SCANS:
            with self.subTest(stem=stem):
                fm = yaml.safe_load((ROOT / "_posts" / f"{stem}.md").read_text(encoding="utf-8").split("---", 2)[1])
                rows = fm["translation_segments"]
                exported = archive.normalize_scan(rows, {}, preserve_order=fm.get("scan_reading_order") == "listed")
                self.assertEqual([r["region_id"] for r in exported], [r["region_id"] for r in rows])
                self.assertEqual(len({r["region_id"] for r in rows}), len(rows))
                for row in rows:
                    if row.get("type") == "table":
                        for text_key, lang in (("original", "ja"), ("translation", "zh")):
                            lines = row[text_key].splitlines()
                            expected = [[cell.strip() for cell in line.split("|")] for line in lines if "|" in line]
                            self.assertEqual(row[f"rows_{lang}"], expected)
                            note = "\n".join(line for line in lines if line.strip() and "|" not in line)
                            self.assertEqual(row.get(f"table_note_{lang}", ""), note)
                for quote in (q for q in quotes if q.get("post") == stem):
                    source = rows[quote["segment"] - 1]
                    self.assertEqual(quote["ja"], source["original"])
                    self.assertEqual(quote["zh"], source["translation"])
                    self.assertEqual(quote["id"], f"{stem}#{quote['segment']}")

    def test_nd84_pokemon_index_matches_corrected_text(self):
        path = ROOT / "_posts/2003-02-21-scan-ndream-084-ruby-sapphire-interview.md"
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        rows = archive.normalize_scan(fm["translation_segments"], {}, preserve_order=True)
        lore = json.loads((ROOT / "data/post_lore/scan-ndream-084-ruby-sapphire-interview.json").read_text(encoding="utf-8"))
        self.assertEqual(lore["body"]["n"], len(rows))
        for pokemon in lore["facets"]["pokemon"]:
            for index in pokemon["seg"]:
                with self.subTest(pokemon=pokemon["name"], index=index):
                    self.assertIn(pokemon["name"], rows[index]["translation"])

    def test_nd84_export_matches_reviewed_transcript(self):
        path = ROOT / "_posts/2003-02-21-scan-ndream-084-ruby-sapphire-interview.md"
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        rows = fm["translation_segments"]
        exported = archive.normalize_scan(rows, {}, preserve_order=fm.get("scan_reading_order") == "listed")
        self.assertEqual([r["region_id"] for r in exported], [r["region_id"] for r in rows])
        self.assertEqual(list(dict.fromkeys(r["scan_page"] for r in exported)), fm["scan_page_order"])

    def test_reviewed_order_survives_upload_leaf_order(self):
        rows = [
            {"type": "paragraph", "scan_page": 4, "order": "20", "region_id": "page120", "original": "first"},
            {"type": "paragraph", "scan_page": 3, "order": "21", "region_id": "page122", "original": "second"},
        ]
        reviewed = archive.normalize_scan(rows, {}, preserve_order=True)
        self.assertEqual([r["original"] for r in reviewed], ["first", "second"])
        self.assertEqual([r["scan_page"] for r in reviewed], [4, 3])
        self.assertEqual([r["region_id"] for r in reviewed], ["page120", "page122"])
        self.assertEqual([r["original"] for r in archive.normalize_scan(rows, {})], ["second", "first"])

    def test_scoped_initials_keep_separate_speaker_ids(self):
        names = {"H.T.": "h-t", "H.T.（2019设计师特写）": "gf-ht-designer-2019",
                 "H.T.（2020程序员特写）": "gf-ht-programmer-2020"}
        rows = [{"speaker": n, "translation": "test"} for n in names if n != "H.T."]
        self.assertEqual([r["speaker_slug"] for r in archive.normalize_parallel(rows, names)],
                         ["gf-ht-designer-2019", "gf-ht-programmer-2020"])

    def test_source_override_and_legacy_metadata(self):
        self.assertEqual(archive.source_url({"original_url": "https://example.org/old"}), "https://example.org/old")
        self.assertEqual(archive.source_url({"source": "https://example.org/scalar"}), "https://example.org/scalar")
        self.assertIsNone(archive.source_url({"source": {"title": "no URL"}}))
        self.assertEqual(archive.source_url({"source": {"url": "https://example.org/original", "archive_url": "https://example.org/archive"}}), "https://example.org/original")
        self.assertEqual(archive.source_url({"original_link": "https://example.org/original", "preferred_source_url": "https://example.org/archive"}), "https://example.org/archive")


class OldScanAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report = (ROOT / "docs/maintenance/old-scan-translation-audit-2026-11-12.md").read_text(encoding="utf-8")
        cls.stems = re.findall(r"\(../../_posts/([^/)]+)\.md\)", report)
        cls.posts = {}
        for stem in cls.stems:
            text = (ROOT / "_posts" / f"{stem}.md").read_text(encoding="utf-8")
            front = re.search(r"(?ms)\A---\n(.*?)^---[ \t]*$", text).group(1)
            cls.posts[stem] = yaml.load(front, Loader=yaml.CSafeLoader)

    def test_source_locations_and_explicit_gaps(self):
        self.assertEqual(len(self.posts), 40)
        gaps = 0
        for stem, fm in self.posts.items():
            with self.subTest(stem=stem):
                rows = fm["translation_segments"]
                self.assertEqual(fm["scan_reading_order"], "listed")
                self.assertEqual(len({r["region_id"] for r in rows}), len(rows))
                pages = {r["scan_page"] for r in rows}
                self.assertTrue(all(isinstance(p, int) and p >= 0 for p in pages))
                self.assertEqual(set(fm["scan_page_order"]), pages)
                self.assertEqual(len(fm["scan_page_order"]), len(pages))
                pending = sum(r.get("review_status") in ("review", "pending", "needs-review") for r in rows)
                self.assertEqual(fm["pending_review_regions"], pending)
                gaps += pending
                self.assertEqual(fm["workflow"]["proofreading"], "source-checked-with-gaps" if pending else "source-checked")
        self.assertEqual(gaps, 11)

    def test_quotes_still_match_source_regions(self):
        quotes = yaml.load((ROOT / "_data/quotes.yml").read_text(encoding="utf-8"), Loader=yaml.CSafeLoader)["quotes"]
        checked = 0
        for q in quotes:
            if q.get("post") not in self.posts:
                continue
            with self.subTest(quote=q["id"]):
                row = self.posts[q["post"]]["translation_segments"][q["segment"] - 1]
                self.assertEqual(q["id"], f"{q['post']}#{q['segment']}")
                self.assertEqual(q["ja"], row["original"])
                self.assertEqual(q["zh"], row["translation"])
                self.assertEqual(q["speaker"], row["speaker"])
                checked += 1
        self.assertEqual(checked, 66)

    def test_web_page_groups_preserve_reviewed_reading_order(self):
        for stem, fm in self.posts.items():
            text_rows = [r for r in fm["translation_segments"] if r.get("original") or r.get("translation")]
            grouped = [r for page in fm["scan_page_order"] for r in text_rows
                       if r.get("reading_page", r["scan_page"]) == page]
            with self.subTest(stem=stem):
                self.assertEqual([r["region_id"] for r in grouped], [r["region_id"] for r in text_rows])

    def test_lore_indices_and_named_pokemon(self):
        for stem, fm in self.posts.items():
            rows = archive.normalize_scan(fm["translation_segments"], {}, preserve_order=True)
            post_id = archive.jekyll_title_slug(archive.DATE_PREFIX.sub("", stem))
            rec = json.loads((ROOT / "data/post_lore" / f"{post_id}.json").read_text(encoding="utf-8"))
            with self.subTest(stem=stem):
                self.assertEqual(rec["body"]["n"], len(rows))
                for items in rec["facets"].values():
                    for item in items:
                        self.assertTrue(all(isinstance(n, int) and 0 <= n < len(rows) for n in item.get("seg", [])))
                for item in rec["observations"]:
                    self.assertTrue(0 <= item["seg"] < len(rows))
                for pokemon in rec["facets"]["pokemon"]:
                    aliases = pokemon.get("as", []) + [pokemon["name"]]
                    for n in pokemon["seg"]:
                        text = rows[n].get("translation") or rows[n].get("original", "")
                        self.assertTrue(any(name in text for name in aliases), (pokemon["name"], n))

    def test_table_cells_match_reviewed_transcript(self):
        count = 0
        for stem, fm in self.posts.items():
            for row in fm["translation_segments"]:
                if row.get("type") != "table":
                    continue
                count += 1
                for text_key, lang in (("original", "ja"), ("translation", "zh")):
                    expected = []
                    notes = []
                    lines = row[text_key].splitlines()
                    outer_pipes = lines[0].strip().startswith("|") and lines[0].strip().endswith("|")
                    for line in lines:
                        if "|" in line:
                            source = line.strip().strip("|") if outer_pipes else line
                            cells = [c.strip() for c in source.split("|")]
                            if not all(re.fullmatch(r"[-: ]+", c) for c in cells):
                                expected.append(cells)
                        elif line.strip():
                            notes.append(line)
                    with self.subTest(stem=stem, region=row["region_id"], lang=lang):
                        self.assertEqual(row[f"rows_{lang}"], expected)
                        self.assertEqual(len({len(cells) for cells in expected}), 1)
                        self.assertEqual(row.get(f"table_note_{lang}", ""), "\n".join(notes))
        self.assertEqual(count, 7)


if __name__ == "__main__":
    unittest.main()
