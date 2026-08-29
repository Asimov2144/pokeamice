import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "gamefreak_staff_names.py"
SPEC = importlib.util.spec_from_file_location("gamefreak_staff_names", MODULE_PATH)
names = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = names
SPEC.loader.exec_module(names)


class GameFreakStaffNamesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = names.load_policy()

    def test_first_occurrence_is_annotated_and_later_ones_keep_kana(self):
        source = "カニ子です。カニ子でした。"
        translated = "我是螃蟹子。后来蟹子又来了。"
        body, annotations = names.normalize_body(source, translated, self.entries, 5)
        self.assertEqual(body, "我是カニ子（蟹子）。后来カニ子又来了。")
        self.assertEqual(annotations, [{"source": "カニ子", "target": "蟹子"}])

    def test_structural_regions_and_longer_katakana_words_are_protected(self):
        source = "ペンギンです。カビゴンもいます。"
        translated = (
            "我是企鹅。卡比兽也在。"
            '{% legacy_image id="ペンギン" alt="企鹅" %}'
        )
        body, _annotations = names.normalize_body(source, translated, self.entries, 173)
        self.assertIn("ペンギン（企鹅）", body)
        self.assertIn("卡比兽", body)
        self.assertIn('id="ペンギン" alt="企鹅"', body)
        self.assertNotIn("ギン（银）", body)

    def test_old_chained_annotations_are_repaired_idempotently(self):
        source = "ペンギンです。"
        broken = "ペンギン（企鹅）（银）（ペンギン）です。"
        once, _annotations = names.normalize_body(source, broken, self.entries, 173)
        twice, _annotations = names.normalize_body(source, once, self.entries, 173)
        self.assertEqual(once, "ペンギン（企鹅）です。")
        self.assertEqual(twice, once)

    def test_article_exclusion_prevents_food_from_becoming_a_person(self):
        source = "冷蔵庫のエノキとイクラを加えます。"
        translated = "加入金针菇和鱼籽。"
        body, annotations = names.normalize_body(source, translated, self.entries, 164)
        self.assertEqual(body, translated)
        self.assertEqual(annotations, [])

    def test_search_card_text_uses_chinese_name_without_annotation(self):
        entry = next(item for item in self.entries if item["source"] == "ペンギン")
        result = names.normalize_card_text("程序员ペンギン回顾求职经历", [entry])
        self.assertEqual(result, "程序员企鹅回顾求职经历")


if __name__ == "__main__":
    unittest.main()
