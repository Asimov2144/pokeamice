"""Regressions for reviewed scan order, anonymous speakers and source links."""
import importlib.util
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("archive_export", ROOT / "tools/export-docs-archive.py")
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class InterviewArchiveRepairs(unittest.TestCase):
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
