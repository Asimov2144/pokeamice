import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "ocr_rework_loop.py"
SPEC = importlib.util.spec_from_file_location("ocr_rework_loop", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OcrReworkLoopTests(unittest.TestCase):
    def test_two_consistent_clean_runs_can_replace_failed_text(self):
        proposal = {"auto_replace_allowed": True, "reason_codes": ["ocr_failed"]}
        result = MODULE.evaluate_replacement("待校对（VLM API 请求失败）", "田尻さんにお話を伺いました。", "田尻さんにお話を伺いました。", proposal)
        self.assertEqual(result["decision"], "auto_replace")

    def test_disagreeing_runs_never_auto_replace(self):
        proposal = {"auto_replace_allowed": True, "reason_codes": ["ocr_failed"]}
        result = MODULE.evaluate_replacement("", "ポケモンの開発について話します。", "まったく別の文章になりました。", proposal)
        self.assertEqual(result["decision"], "human_review")
        self.assertIn("two_runs_disagree", result["gates"])

    def test_boundary_change_requires_human_even_when_consistent(self):
        proposal = {"auto_replace_allowed": False, "reason_codes": ["boundary_uncertain"]}
        result = MODULE.evaluate_replacement("開発について", "ゲーム開発について", "ゲーム開発について", proposal)
        self.assertEqual(result["decision"], "human_review")
        self.assertIn("proposal_requires_human", result["gates"])

    def test_coordinate_candidate_is_blocked(self):
        proposal = {"auto_replace_allowed": True, "reason_codes": ["coordinate_dump"]}
        result = MODULE.evaluate_replacement("本文", "12, 23, 40, 50, 99, 本文です", "12, 23, 40, 50, 99, 本文です", proposal)
        self.assertEqual(result["decision"], "human_review")

    def test_repeated_single_glyph_is_unhealthy(self):
        health = MODULE.text_health("た" * 40 + "ならな")
        self.assertIn("repeated_glyph_pattern", health["blockers"])
        self.assertLess(health["score"], 0.6)

    def test_short_changed_caption_is_not_silently_replaced(self):
        proposal = {"auto_replace_allowed": True, "reason_codes": ["direction_conflict"]}
        result = MODULE.evaluate_replacement("増田順一", "増田順二", "増田順二", proposal)
        self.assertIn("short_text_changed", result["gates"])

    def test_direction_proposal_uses_detected_direction(self):
        item = {"box": [10, 20, 200, 500], "writing_direction": "horizontal"}
        ocr = {"preprocessing": {"effective_direction": "vertical"}}
        proposal = MODULE.build_repair_proposal(item, ocr, [{"code": "direction_conflict"}])
        self.assertEqual(proposal["kind"], "direction_fix")
        self.assertEqual(proposal["writing_direction"], "vertical")

    def test_too_many_columns_proposes_ordered_groups_but_needs_preview(self):
        columns = [[index * 10, 0, index * 10 + 8, 500] for index in range(13)]
        item = {"box": [100, 200, 360, 1200], "writing_direction": "vertical"}
        ocr = {"preprocessing": {"effective_direction": "vertical", "source_size": [130, 500], "detected_columns": columns}}
        proposal = MODULE.build_repair_proposal(item, ocr, [{"code": "multicolumn_exceeds_limit"}])
        self.assertEqual(proposal["kind"], "split_columns")
        self.assertEqual(len(proposal["parts"]), 3)
        self.assertFalse(proposal["auto_replace_allowed"])
        self.assertGreater(proposal["parts"][0]["scan_box"][0], proposal["parts"][-1]["scan_box"][0])


if __name__ == "__main__":
    unittest.main()
