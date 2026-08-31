import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


MODULE_PATH = Path(__file__).resolve().parents[1] / "gamefreak_lineblog_pipeline.py"
SPEC = importlib.util.spec_from_file_location("gamefreak_lineblog_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class GameFreakLineBlogPipelineTests(unittest.TestCase):
    def test_numeric_article_urls_only(self):
        self.assertEqual(pipeline.article_id_from_url("https://lineblog.me/masudajunichi/archives/9302351.html"), 9302351)
        self.assertIsNone(pipeline.article_id_from_url("https://lineblog.me/masudajunichi/archives/cat_105167.html"))

    def test_wayback_urls_are_unwrapped(self):
        value = "https://web.archive.org/web/20171024121940im_/https://obs.line-scdn.net/example/small"
        self.assertEqual(pipeline.unwrap_wayback_url(value, pipeline.ROOT_URL), "https://obs.line-scdn.net/example/small")

    def test_extract_preserves_alignment_tags_and_image_position(self):
        html = """
        <article>
          <header class="article-header"><h1 class="article-title">夏の思い出</h1><p class="article-date"><time datetime="2017-10-09T16:57:11+0900">2017/10/9</time></p></header>
          <div class="article-body-inner"><div style="text-align:center">一行目<br><a href="https://obs.line-scdn.net/full"><img src="https://obs.line-scdn.net/full/small" alt="写真"></a></div><div id="ad2"></div></div>
          <footer><dl class="article-tags"><dd><a>ポケモン</a></dd></dl><li class="article-category"><dl><dd><a>日記</a></dd></dl></li></footer>
        </article>
        """
        assets = {"https://obs.line-scdn.net/full": {"id": "line-1-001"}}
        meta, body, blocks = pipeline.extract_article(html.encode(), {"id": 1, "source_url": pipeline.ROOT_URL}, assets)
        self.assertEqual(meta["date"], "2017-10-09")
        self.assertEqual(meta["tags"], ["ポケモン"])
        self.assertEqual(meta["categories"], ["日記"])
        self.assertIn("gf-lineblog-line--center", body)
        self.assertIn('lineblog_image id="line-1-001"', body)
        self.assertEqual(blocks[0]["alignment"], "center")

    def test_links_inside_source_divs_render_as_html(self):
        node = BeautifulSoup('<div style="text-align:center"><a href="https://example.com/a?x=1&y=2">公式</a></div>', "html.parser").div
        rendered = pipeline.inline_html(node, {}, pipeline.ROOT_URL)
        self.assertIn('class="gf-lineblog-source-link"', rendered)
        self.assertIn('href="https://example.com/a?x=1&amp;y=2"', rendered)
        self.assertNotIn("[公式]", rendered)

    def test_public_images_are_resized_and_encoded_as_webp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            Image.new("RGB", (2000, 1000), "#d33").save(source)
            destination, width, height, changed = pipeline.publish_image(source, root / "public")
            self.assertTrue(changed)
            self.assertEqual(destination.suffix, ".webp")
            self.assertEqual((width, height), (1600, 800))
            self.assertLess(destination.stat().st_size, source.stat().st_size)


if __name__ == "__main__":
    unittest.main()
