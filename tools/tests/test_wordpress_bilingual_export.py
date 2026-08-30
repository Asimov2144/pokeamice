import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from deepseek_correct_region_ocr import result_verdict, suspicious_correction
from export_workbench_wordpress_case import entry_from_segment
from export_wordpress_bilingual import utterances


class DeepSeekBoundaryTests(unittest.TestCase):
    def test_detects_neighbor_context_copy(self):
        raw = "現在区域の文章です。" * 12
        neighbor = "次の区域から始まる固有の文章です。" * 6
        warnings = suspicious_correction(raw, raw + neighbor, neighbor)
        self.assertIn("neighbor_context_copied", warnings)
        self.assertTrue(any(value.startswith("corrected_text_expanded:") for value in warnings))

    def test_allows_normal_line_break_cleanup(self):
        raw = "蒼井 これは長い\nインタビュー本文です。" * 8
        corrected = raw.replace("\n", "")
        self.assertEqual([], suspicious_correction(raw, corrected, ""))

    def test_blocks_large_semantic_rewrite(self):
        raw = "ゲーム開発について田尻さんに話を聞きました。" * 4
        corrected = "市内農業振興協会は牛の飼料費軽減事業を実施します。" * 4
        warnings = suspicious_correction(raw, corrected, "")
        self.assertTrue(any(value.startswith("corrected_text_changed_too_much:") for value in warnings))

    def test_low_confidence_translation_is_not_usable(self):
        status, _, issues = result_verdict(
            {"verification_status": "usable", "confidence": 0.4, "issues": []},
            "開発について話しました。",
            [],
        )
        self.assertEqual("uncertain", status)
        self.assertTrue(any(value.startswith("verification_confidence_low:") for value in issues))


class InterviewAlignmentTests(unittest.TestCase):
    def test_joins_wrapped_question_before_pairing(self):
        japanese = "——今年で10年なんですけど、\n蒼井さんは思い出がありますか?\n蒼井 兄が遊んでいました。"
        chinese = "——今年已经十周年了，有什么回忆吗？\n苍井：哥哥以前玩过。"
        ja_units = utterances(japanese, "ja")
        zh_units = utterances(chinese, "zh")
        self.assertEqual(2, len(ja_units))
        self.assertEqual(len(ja_units), len(zh_units))
        self.assertIn("蒼井さんは", ja_units[0])

    def test_keeps_non_interview_lead_lines_separate(self):
        self.assertEqual(["一行目", "二行目"], utterances("一行目\n二行目", "ja"))


class WorkbenchCaseExportTests(unittest.TestCase):
    def test_preserves_all_boxes_from_a_merged_region(self):
        entry = entry_from_segment(
            {
                "regionId": "qwen-r4",
                "scanBox": [10, 20, 110, 220],
                "scanBoxes": [[10, 20, 110, 220], [120, 20, 220, 220]],
                "original": "日本語",
                "translation": "中文",
            },
            0,
        )
        self.assertEqual([10, 20, 110, 220], entry["box"])
        self.assertEqual(2, len(entry["members"]))
        self.assertEqual("qwen-r4-box-2", entry["members"][1]["region_id"])


if __name__ == "__main__":
    unittest.main()
