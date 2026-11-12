"""Regressions for reviewed scan order, anonymous speakers and source links."""
import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
