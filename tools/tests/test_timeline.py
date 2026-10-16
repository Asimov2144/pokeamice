"""Check real timeline HTML, counts, dates, links and local images."""
import json
import os
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = Path(os.environ.get("TIMELINE_PREVIEW_DIR", ROOT / ".preview-build/timeline"))


class TimelineRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((PREVIEW / "manifest.json").read_text(encoding="utf-8"))

    def page(self, route):
        path = PREVIEW / route.lstrip("/") / "index.html"
        return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    def test_current_corpus_counts_match_overview_and_all_years(self):
        overview = self.page("/timeline/")
        totals = Counter(p["kind"] for p in self.manifest["posts"])
        self.assertEqual(int(overview.select_one("[data-tl-total-docs]").text), len(self.manifest["posts"]) - totals["stream"])
        self.assertEqual(int(overview.select_one("[data-tl-total-stream]").text), totals["stream"])
        for column in overview.select("[data-tl-chart-year]"):
            year = column["data-tl-chart-year"]
            counts = self.manifest["years"].get(year, {"docs": 0, "stream": 0})
            self.assertEqual(int(column["data-docs"]), counts["docs"])
            self.assertEqual(int(column["data-stream"]), counts["stream"])
            if counts["docs"] or counts["stream"]:
                self.assertIn(f"/timeline/{year}/", self.manifest["routes"])
            else:
                self.assertEqual(column.name, "span")

    def test_every_visible_post_is_rendered_once_in_its_year(self):
        baseurl = self.manifest.get("baseurl") or ""
        for year, counts in self.manifest["years"].items():
            page = self.page(f"/timeline/{year}/")
            self.assertEqual(int(page.select_one("[data-tl-year-docs]").text), counts["docs"])
            self.assertEqual(int(page.select_one("[data-tl-year-stream]").text), counts["stream"])
            items = page.select(".tl--year .tl-item")
            self.assertEqual(len(items), counts["docs"] + counts["stream"], year)
            expected = Counter(unquote(p["url"]) for p in self.manifest["posts"] if p["year"] == int(year))
            actual = Counter(unquote(item.select_one("a")["href"].removeprefix(baseurl)) for item in items)
            self.assertEqual(actual, expected, year)
            kind_counts = Counter(item["data-kind"] for item in items)
            for button in page.select("[data-tl-filter]"):
                count = int(button.select_one("span").text)
                self.assertEqual(count, len(items) if button["data-tl-filter"] == "all" else kind_counts[button["data-tl-filter"]])

    def test_months_dates_and_blog_dates_are_ordered(self):
        for route in self.manifest["routes"]:
            if route == "/timeline/":
                continue
            page = self.page(route)
            month_ids = [m["id"] for m in page.select("[data-tl-month]")]
            self.assertEqual(month_ids, sorted(month_ids))
            for group in page.select("[data-tl-month], .tl-stream__list"):
                dates = [t["datetime"] for t in group.select("time")]
                self.assertEqual(dates, sorted(dates), route)
                if group.has_attr("data-tl-month"):
                    self.assertEqual(int(group.select_one("[data-tl-count]").text), len(dates))

    def test_anchor_ids_are_unique_and_local_navigation_resolves(self):
        for route in self.manifest["routes"]:
            page = self.page(route)
            root = page.select_one("[data-tl-root]")
            ids = [e["id"] for e in root.select("[id]")]
            self.assertEqual(len(ids), len(set(ids)), route)
            for a in root.select("a[href^='#']"):
                self.assertIn(a["href"][1:], ids, route)
            self.assertEqual(len(root.select("h1")), 1)
            self.assertFalse(root.select("[data-card-grid], .search-result-card"))

    def test_enhanced_controls_have_static_fallback(self):
        for route in self.manifest["routes"]:
            page = self.page(route)
            for controls in page.select(".tl-enhance"):
                self.assertTrue(controls.has_attr("hidden"))
            for field in page.select("input[id], select[id]"):
                self.assertIsNotNone(page.find("label", attrs={"for": field["id"]}))
            self.assertIsNotNone(page.select_one("noscript"))

    def test_timeline_media_exist_locally(self):
        for route in self.manifest["routes"]:
            for image in self.page(route).select("[data-tl-root] img[src]"):
                source = urlsplit(image["src"])
                self.assertFalse(source.netloc, (route, image["src"]))
                asset = unquote(source.path).removeprefix(self.manifest.get("baseurl") or "").lstrip("/")
                self.assertTrue((ROOT / asset).is_file(), (route, asset))

    def test_featured_interview_is_navigable_in_preview(self):
        url = self.manifest["preview_article"]
        page = self.page(unquote(url))
        reader = page.select_one("main[data-interview-template]")
        self.assertIsNotNone(reader)
        self.assertEqual(reader["data-interview-template"], "longform")
        featured = self.page("/timeline/").select_one(".tl-feature")
        self.assertEqual(unquote(featured["href"]), unquote(url))


if __name__ == "__main__":
    unittest.main()
