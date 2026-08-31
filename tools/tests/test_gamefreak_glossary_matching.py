import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from gamefreak_translate_deepseek import glossary_checks, glossary_matches


class GameFreakGlossaryMatchingTests(unittest.TestCase):
    def setUp(self):
        self.glossary = [
            {"terms": ["Media"], "target": "普通", "category": "system", "source": "test"},
            {"terms": ["Junichi"], "target": "武德", "category": "person", "source": "test"},
            {"terms": ["ピカチュウ"], "target": "皮卡丘", "category": "pokemon", "source": "test"},
        ]

    def targets(self, source):
        return [entry["target"] for entry in glossary_matches(source, self.glossary)]

    def test_ignores_liquid_attributes_html_attributes_urls_and_handles(self):
        source = (
            '<div class="Media">ピカチュウ '
            '{% lineblog_image id="line-1" alt="_var_mobile_Media_DCIM" %} '
            '<a href="https://example.com/Media">Junichi_Masuda</a></div>'
        )
        self.assertEqual(self.targets(source), ["皮卡丘"])

    def test_visible_standalone_latin_term_can_still_match(self):
        self.assertIn("普通", self.targets("Media について書きます。"))

    def test_ignores_known_ambiguous_glossary_terms_in_visible_prose(self):
        self.assertNotIn("武德", self.targets("Junichi MASUDA will attend the event."))

    def test_accepts_official_pokemon_source_form_when_preserved(self):
        matches = [{
            "hits": ["Pokémon"], "target": "宝可梦", "category": "system", "source": "test",
        }]
        checks = glossary_checks(matches, "The Pokémon Company International")
        self.assertEqual(checks[0]["status"], "source-form-preserved")


if __name__ == "__main__":
    unittest.main()
