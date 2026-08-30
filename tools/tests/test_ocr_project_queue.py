import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build_ocr_project_queue.py"
SPEC = importlib.util.spec_from_file_location("build_ocr_project_queue", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OcrProjectQueueTests(unittest.TestCase):
    def test_severe_furigana_lines_are_sent_to_review(self):
        text = "\n".join([
            "一般トレーナーにも工事現場の",
            "さぎょういん",
            "作業員や電気工事にまつわる人がいたり",
            "でんきこうじ",
            "するので大変でしたけど。",
            "たいへん",
            "取材の結果が反映されています。",
            "けっか",
        ])
        warning = MODULE.furigana_contamination(text)
        self.assertEqual(warning["code"], "furigana_contamination")

    def test_single_heading_reading_is_not_severe(self):
        self.assertIsNone(MODULE.furigana_contamination("ひみつ\nデザインの秘密"))

    def test_coordinate_recovery_still_gets_quick_review(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "horizontal"},
            {"quality_warnings": [], "recovery": {"reason": "coordinate_dump", "succeeded": True}},
            "取材で得たイメージを伝えます。",
        )
        self.assertIn("coordinate_dump", [reason["code"] for reason in reasons])
        self.assertEqual(reasons[0]["severity"], "medium")

    def test_auto_direction_and_mixed_content_are_sent_to_review(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "auto", "content_mix": "mixed"},
            {},
            "本文",
        )
        self.assertEqual({reason["code"] for reason in reasons}, {"direction_uncertain", "image_text_mixed"})

    def test_layout_direction_and_boundary_flags_are_preserved(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "horizontal", "review_flags": ["direction_uncertain", "boundary_uncertain"]},
            {},
            "斜めに配置された本文",
        )
        self.assertEqual({reason["code"] for reason in reasons}, {"direction_uncertain", "boundary_uncertain"})

    def test_wide_vertical_strip_returning_one_column_is_reviewed(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {
                "preprocessing": {"strategy": "vertical_long_strip_square_padding", "original_size": [132, 780]},
                "postprocessing": {"strategy": "vertical_column_order", "column_count": 1},
            },
            "複数の縦書き列が一行に連結されたような長い文字列です。",
        )
        self.assertIn("vertical_columns_unstructured", [reason["code"] for reason in reasons])

    def test_narrow_single_vertical_caption_is_not_reviewed(self):
        reasons = MODULE.review_reasons(
            {"type": "caption", "writing_direction": "vertical"},
            {
                "preprocessing": {"strategy": "vertical_long_strip_square_padding", "original_size": [72, 560]},
                "postprocessing": {"strategy": "vertical_column_order", "column_count": 1},
            },
            "杉森建さん",
        )
        self.assertNotIn("vertical_columns_unstructured", [reason["code"] for reason in reasons])

    def test_too_many_detected_columns_are_sent_to_review(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {
                "preprocessing": {
                    "strategy": "column_detection",
                    "detected_column_count": 23,
                    "too_many_columns": True,
                }
            },
            "本文",
        )
        self.assertIn("multicolumn_exceeds_limit", [reason["code"] for reason in reasons])

    def test_successful_physical_split_can_continue_automatically(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "horizontal"},
            {
                "preprocessing": {
                    "strategy": "physical_column_split",
                    "declared_direction": "horizontal",
                    "effective_direction": "vertical",
                    "direction_overridden": True,
                },
                "postprocessing": {
                    "strategy": "physical_column_reading_order",
                    "column_count": 3,
                    "column_text_lengths_visual_left_to_right": [20, 18, 21],
                },
            },
            "右中左",
        )
        self.assertNotIn("direction_conflict", [reason["code"] for reason in reasons])
        self.assertNotIn("column_ocr_incomplete", [reason["code"] for reason in reasons])

    def test_empty_split_column_is_sent_to_review(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {
                "preprocessing": {"strategy": "physical_column_split"},
                "postprocessing": {
                    "column_count": 3,
                    "column_text_lengths_visual_left_to_right": [20, 0, 21],
                },
            },
            "右左",
        )
        self.assertIn("column_ocr_incomplete", [reason["code"] for reason in reasons])

    def test_heterogeneous_vertical_columns_are_sent_to_review(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {
                "preprocessing": {
                    "strategy": "physical_column_split",
                    "effective_direction": "vertical",
                    "columns": [[0, 0, 18, 500], [20, 0, 72, 500], [74, 0, 128, 500]],
                },
                "postprocessing": {
                    "column_count": 3,
                    "column_text_lengths_visual_left_to_right": [20, 60, 58],
                },
            },
            "本文",
        )
        self.assertIn("heterogeneous_vertical_columns", [reason["code"] for reason in reasons])

    def test_page_rotation_uncertainty_is_never_auto_released(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "horizontal", "review_flags": ["page_rotation_uncertain"]},
            {},
            "短い見出し",
        )
        self.assertIn("page_rotation_uncertain", [reason["code"] for reason in reasons])

    def test_suppressed_direction_override_is_reviewed(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "horizontal"},
            {"preprocessing": {"direction_override_suppressed": True, "declared_direction": "horizontal", "orientation": {"direction": "vertical"}}},
            "横長の見出し",
        )
        self.assertIn("direction_conflict_suppressed", [reason["code"] for reason in reasons])

    def test_repeated_glyph_hallucination_is_blocked(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {},
            "た" * 45 + "ならな",
        )
        self.assertIn("ocr_text_repetition", [reason["code"] for reason in reasons])

    def test_long_body_without_kana_is_blocked(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {},
            "財政状況予算編成企画調整行政機関地域振興事業計画" * 4,
        )
        self.assertIn("japanese_text_implausible", [reason["code"] for reason in reasons])

    def test_dual_ocr_disagreement_is_blocked(self):
        reasons = MODULE.review_reasons(
            {"type": "body", "writing_direction": "vertical"},
            {"quality_warnings": ["dual_ocr_disagreement:0.731"]},
            "これは読み取った日本語の本文です。",
        )
        self.assertIn("dual_ocr_disagreement", [reason["code"] for reason in reasons])


if __name__ == "__main__":
    unittest.main()
