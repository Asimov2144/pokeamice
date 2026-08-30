import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "publish_scan_archive_docs.py"
SPEC = importlib.util.spec_from_file_location("publish_scan_archive_docs", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublishScanArchiveDocsTests(unittest.TestCase):
    def build(self, entry, queue_status="ready"):
        with tempfile.TemporaryDirectory() as tmp:
            queue = {
                (entry["page_name"], entry["region_id"]): {
                    "status": queue_status,
                    "reasons": [{"code": "direction_uncertain"}] if queue_status == "review" else [],
                }
            }
            return MODULE.build_segments([entry], Path(tmp), queue)[0]

    def test_verified_ready_text_can_publish(self):
        item = {
            "page_index": 0,
            "page_name": "page001.jpg",
            "region_id": "r1",
            "order": 1,
            "type": "body",
            "original_raw": "開発について話しました。",
            "original_corrected": "開発について話しました。",
            "translation": "谈到了开发。",
            "verification_status": "usable",
            "writing_direction": "vertical",
        }
        self.assertEqual("ready", self.build(item)["review_status"])

    def test_review_queue_text_is_never_ready(self):
        item = {
            "page_index": 0,
            "page_name": "page001.jpg",
            "region_id": "r1",
            "order": 1,
            "type": "body",
            "original_raw": "た" * 30,
            "translation": "错误译文",
            "verification_status": "usable",
            "writing_direction": "vertical",
        }
        self.assertEqual("review", self.build(item, "review")["review_status"])

    def test_legacy_translation_without_verdict_is_blocked(self):
        item = {
            "page_index": 0,
            "page_name": "page001.jpg",
            "region_id": "r1",
            "order": 1,
            "type": "body",
            "original_raw": "本文です。",
            "translation": "这是正文。",
            "writing_direction": "vertical",
        }
        self.assertEqual("review", self.build(item)["review_status"])


if __name__ == "__main__":
    unittest.main()
