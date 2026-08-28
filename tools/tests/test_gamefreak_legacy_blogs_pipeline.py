import importlib.util
import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


MODULE_PATH = Path(__file__).resolve().parents[1] / "gamefreak_legacy_blogs_pipeline.py"
SPEC = importlib.util.spec_from_file_location("gamefreak_legacy_blogs_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class GameFreakLegacyBlogsPipelineTests(unittest.TestCase):
    def test_parse_staff_post_metadata(self):
        html = """
        <div class="post">
          <div class="left"><h5>29</h5><b>6月</b><br><b>2012</b></div>
          <div class="right">
            <h2><a href="http://www.gamefreak.co.jp/blog/staff/?p=243">発売！</a></h2>
            <p>本文の先頭です。</p>
            <div class="tag">Tags: <a href="?tag=y">Ｙ</a></div>
          </div>
        </div>
        """
        post = BeautifulSoup(html, "html.parser").select_one(".post")
        result = pipeline.parse_post(
            post, pipeline.BLOGS["staff"], pipeline.BLOGS["staff"]["root_url"]
        )
        self.assertEqual(result["id"], 243)
        self.assertEqual(result["date"], "2012-06-29")
        self.assertEqual(result["title"], "発売！")
        self.assertEqual(result["tags"], ["Ｙ"])


    def test_art_zoom_image_is_collected_as_thumbnail_and_full_resolution(self):
        html = """
        <div class="post"><div class="right">
          <div class="comset">
            <div class="com"><div class="zoom"><a href="wp-content/images/full.jpg"><img src="zoom_off.gif"></a></div></div>
            <div class="sm"><a href="wp-content/images/full.jpg"><img src="wp-content/images/s_full.jpg"></a></div>
          </div>
        </div></div>
        """
        post = BeautifulSoup(html, "html.parser").select_one(".post")
        assets = pipeline.collect_article_assets(
            post, pipeline.BLOGS["art"], pipeline.BLOGS["art"]["root_url"]
        )
        full = "http://www.gamefreak.co.jp/blog/art/wp-content/images/full.jpg"
        thumb = "http://www.gamefreak.co.jp/blog/art/wp-content/images/s_full.jpg"
        self.assertEqual(assets[full]["roles"], {"design-full-resolution"})
        self.assertEqual(assets[thumb]["roles"], {"design-thumbnail"})
        self.assertEqual(assets[thumb]["pair_url"], full)
        self.assertFalse(any("zoom_off.gif" in url for url in assets))


    def test_wayback_urls_are_unwrapped_to_original_source(self):
        replay = "https://web.archive.org/web/20130808124032im_/http://www.gamefreak.co.jp/blog/art/a.jpg"
        self.assertEqual(
            pipeline.unwrap_wayback_url(replay, pipeline.BLOGS["art"]["root_url"]),
            "http://www.gamefreak.co.jp/blog/art/a.jpg",
        )
        self.assertEqual(
            pipeline.post_id_from_url("http://www.gamefreak.co.jp/blog/staff/?p=201"),
            201,
        )


if __name__ == "__main__":
    unittest.main()
