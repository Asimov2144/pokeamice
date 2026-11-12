import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("weibo_capture", TOOLS / "import-weibo-capture.py")
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)
CAPTURE = json.loads((TOOLS / "data/weibo-captures/2026-11-13.json").read_text(encoding="utf-8"))


class WeiboCaptureTest(unittest.TestCase):
    def setUp(self):
        self.capture = copy.deepcopy(CAPTURE)
        self.dataset = {"posts": [{"mid": CAPTURE["checkpoint_mid"], "id": "cddc81b3",
                                  "d": CAPTURE["checkpoint_archive_date"], "text": "旧存档",
                                  "keep": {"unrecognized": True}}],
                        "articles": [{"id": "existing", "html": "手动修订的长文"}]}

    def test_captured_bodies_and_media_match_source(self):
        for post in self.capture["posts"]:
            self.assertEqual(post["source_hash"], IMPORTER.source_hash(post["html"]))
        self.assertEqual(23, sum(len(p["image_urls"]) for p in self.capture["posts"]))

    def test_timezone_and_minute_precision(self):
        merged, mids = IMPORTER.merge_capture(self.dataset, self.capture)
        self.assertEqual(6, len(mids))
        self.assertEqual(["2026-11-12 21:04:00", "2026-11-11 18:29:00", "2026-11-10 23:03:00",
                          "2026-10-31 22:04:00", "2026-10-31 20:02:00", "2026-10-27 23:04:00"],
                         [p["d"] for p in merged["posts"][:-1]])
        for post in merged["posts"][:-1]:
            self.assertEqual("minute", post["date_precision"])
            self.assertEqual("Asia/Shanghai", post["date_timezone"])

    def test_idempotent_and_historical_objects_preserved(self):
        before = copy.deepcopy(self.dataset)
        merged, _ = IMPORTER.merge_capture(self.dataset, self.capture)
        self.assertEqual(before, self.dataset)
        self.assertIs(merged["posts"][-1], self.dataset["posts"][0])
        self.assertIs(merged["articles"], self.dataset["articles"])
        self.capture["posts"][0]["likes"] += 1
        repeated, added = IMPORTER.merge_capture(merged, self.capture)
        self.assertEqual([], added)
        self.assertEqual(merged, repeated)

    def test_existing_mid_with_edited_content_requires_review(self):
        merged, _ = IMPORTER.merge_capture(self.dataset, self.capture)
        post = self.capture["posts"][0]
        post["html"] += "修订"
        post["source_hash"] = IMPORTER.source_hash(post["html"])
        with self.assertRaisesRegex(ValueError, "has changed"):
            IMPORTER.merge_capture(merged, self.capture)

    def test_reject_unverified_or_corrupted_capture(self):
        self.capture["full_text_verified"] = False
        with self.assertRaisesRegex(ValueError, "verify full text"):
            IMPORTER.merge_capture(self.dataset, self.capture)
        self.capture["full_text_verified"] = True
        self.capture["posts"][0]["html"] += "漏了这一句"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            IMPORTER.merge_capture(self.dataset, self.capture)

    def test_reject_excluded_and_duplicate_mids(self):
        self.capture["posts"].append(copy.deepcopy(self.capture["posts"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate, excluded"):
            IMPORTER.merge_capture(self.dataset, self.capture)
        self.capture["posts"].pop()
        self.capture["excluded"].append({"mid": self.capture["posts"][0]["mid"]})
        with self.assertRaisesRegex(ValueError, "Duplicate, excluded"):
            IMPORTER.merge_capture(self.dataset, self.capture)

    def test_body_preserves_paragraphs_emoji_links_and_original_typos(self):
        merged, _ = IMPORTER.merge_capture(self.dataset, self.capture)
        posts = {p["mid"]: p for p in merged["posts"]}
        halloween = posts["5360202993894895"]["text"]
        self.assertIn("[给你小心心]", halloween)
        self.assertIn("提现调皮", halloween)
        self.assertIn("[网页链接](https://weibo.com/6306512172/5360172279272910)", halloween)
        self.assertNotIn("<img", halloween)
        self.assertIn("\n\n", halloween)
        self.assertIn("组合  时过境迁", posts["5358768718352565"]["text"])
        self.assertIn("https://video.weibo.com/show?fid=1034:5360171908530206",
                      posts["5360172279272910"]["text"])

    def test_apply_without_media_leaves_dataset_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            dataset = Path(folder) / "_work/dataset.json"
            dataset.parent.mkdir()
            dataset.write_text(json.dumps(self.dataset), encoding="utf-8")
            before = dataset.read_bytes()
            args = ["import-weibo-capture.py", str(TOOLS / "data/weibo-captures/2026-11-13.json"),
                    "--dataset", str(dataset), "--apply"]
            with patch.object(sys, "argv", args), self.assertRaisesRegex(ValueError, "copy required"):
                IMPORTER.main()
            self.assertEqual(before, dataset.read_bytes())


if __name__ == "__main__":
    unittest.main()
