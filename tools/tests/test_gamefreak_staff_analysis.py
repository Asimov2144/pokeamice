import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "_data" / "gamefreak_staff_analysis.yml"


class GameFreakStaffAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = yaml.safe_load(REPORT.read_text(encoding="utf-8"))

    def test_complete_archive_and_translation_coverage(self):
        overview = self.report["overview"]
        self.assertEqual(overview["articles"], 209)
        self.assertEqual(overview["translations"], 209)
        self.assertEqual(overview["translation_rate"], 100.0)

    def test_year_distribution_matches_article_total(self):
        self.assertEqual(
            sum(item["count"] for item in self.report["years"]),
            self.report["overview"]["articles"],
        )

    def test_rankings_and_people_point_to_local_entries(self):
        ranked = self.report["longest_articles"] + self.report["most_visual_articles"]
        self.assertTrue(all(item["url"].startswith("/gamefreak-staff/entry-") for item in ranked))
        self.assertEqual(len(self.report["people"]), self.report["overview"]["named_people"])
        self.assertTrue(all(person["first"]["date"] <= person["last"]["date"] for person in self.report["people"]))


if __name__ == "__main__":
    unittest.main()
