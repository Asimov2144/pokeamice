import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "gamefreak_archive_pipeline.py"
SPEC = importlib.util.spec_from_file_location("gamefreak_archive_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class GameFreakArchivePipelineTests(unittest.TestCase):
    def test_normalize_full_width_japanese_number(self):
        self.assertEqual(pipeline.normalize_number("・第２４４回・ 2015.09.11"), 244)

    def test_normalize_english_number(self):
        self.assertEqual(pipeline.normalize_number("No. 73 01.26.2007"), 73)

    def test_official_unknown_archive_link_is_recognized_as_malformed(self):
        url = "https://www.gamefreak.co.jp/blog/dir_english/2006/07/HPC-index.UNKNOWN.UNKNOWN"
        self.assertTrue(pipeline.is_malformed_archive_url(url))
        self.assertFalse(
            pipeline.is_malformed_archive_url(
                "https://www.gamefreak.co.jp/blog/dir_english/2007/01/index.html"
            )
        )

    def test_full_coverage_reports_japanese_language_gaps(self):
        manifest = {
            "articles": [
                {"number": number, "languages": {"ja": {}}}
                for number in range(1, 245)
            ]
        }
        self.assertEqual(pipeline.missing_japanese_article_numbers(manifest), [])
        manifest["articles"][56]["languages"] = {"en": {}}
        self.assertEqual(pipeline.missing_japanese_article_numbers(manifest), [57])

    def test_resolve_scheme_less_absolute_asset_url(self):
        raw = "www.gamefreak.co.jp/blog/dir/wp-content/uploads/2012/03/33.jpg"
        self.assertEqual(
            pipeline.resolve_source_url("https://www.gamefreak.co.jp/blog/dir/2012/03/", raw),
            "https://www.gamefreak.co.jp/blog/dir/wp-content/uploads/2012/03/33.jpg",
        )
        legacy = "gamefreak.sakura.ne.jp/blog/dir/wp-content/uploads/2007/07/ny001.jpg"
        self.assertEqual(
            pipeline.resolve_source_url("https://www.gamefreak.co.jp/blog/dir/2007/07/", legacy),
            "http://gamefreak.sakura.ne.jp/blog/dir/wp-content/uploads/2007/07/ny001.jpg",
        )

    def test_parse_article_and_preserve_breaks_and_image_marker(self):
        html = """
        <div class="main"><div class="article">
          <div class="article-header"><h2 class="article-header-title">
            ・第１回・
            <span class="article-date">2004.08.01</span>
          </h2></div>
          <div class="article-detail"><p>line one<br>line two<img src="/a.jpg"></p><p></p></div>
          <div class="article-footer"><span class="article-footer-category-name">日記</span></div>
        </div></div>
        """.encode("utf-8")
        parsed = pipeline.parse_articles(html, "ja", "https://example.com/month/")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["number"], 1)
        self.assertEqual(parsed[0]["categories"], ["日記"])
        assets = {"https://example.com/a.jpg": {"id": "001-a"}}
        blocks, markdown = pipeline.detail_to_structure(
            parsed[0]["detail_html"], parsed[0]["page_url"], assets
        )
        self.assertIn("line one", markdown)
        self.assertIn("line two", markdown)
        self.assertIn('{% image id="001-a" %}', markdown)
        self.assertTrue(any(block["type"] == "spacer" for block in blocks))


if __name__ == "__main__":
    unittest.main()
