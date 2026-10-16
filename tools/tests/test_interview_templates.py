"""Routing tests; set INTERVIEW_PREVIEW_DIR for Jekyll parity / HTML checks."""
import json
import os
from pathlib import Path
import sys
import unittest
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.audit_interview_templates import audit, features, resolve_template, ROOT, FRONT, LOADER
import yaml
from bs4 import BeautifulSoup


def interview(guests=("A",), questions=1):
    return {"parallel_items": [
        {"role": "question", "speaker": "记者", "translation": "问题"}
        for _ in range(questions)
    ] + [{"role": "answer", "speaker": g, "translation": "回答"} for g in guests]}


class RoutingTests(unittest.TestCase):
    def test_short_and_long(self):
        self.assertEqual(resolve_template(interview()), "conversation")
        self.assertEqual(resolve_template(interview(questions=12)), "longform")
        page = interview()
        page["parallel_items"][-1]["translation"] = "文" * 6000
        self.assertEqual(resolve_template(page), "longform")

    def test_roundtable_without_questions(self):
        self.assertEqual(resolve_template(interview(("A", "B"), 0)), "roundtable")

    def test_crowd_is_not_an_extra_guest(self):
        self.assertEqual(resolve_template(interview(("A", "众人"))), "conversation")

    def test_authored_context_not_a_guest(self):
        page = interview(("A", "Dr. Lava", "编者注"))
        self.assertEqual(features(page)["guests"], ["A"])
        self.assertEqual(resolve_template(page), "annotated")

    def test_explicit_commentary(self):
        page = interview()
        page["parallel_items"].append({"voice": "commentary", "translation": "背景"})
        self.assertEqual(resolve_template(page), "annotated")

    def test_profile_and_narrative(self):
        self.assertEqual(resolve_template(interview(questions=0)), "profile")
        page = interview()
        page["source_kind"] = "corporate_interview"
        self.assertEqual(resolve_template(page), "profile")
        self.assertEqual(resolve_template({"parallel_items": [{"translation": "报道"}]}), "narrative")
        self.assertEqual(resolve_template({}), "narrative")

    def test_prose_override_and_invalid_override(self):
        page = interview()
        page["interview_template"] = "longform"
        self.assertEqual(resolve_template(page), "longform")
        page["interview_template"] = "unknown"
        self.assertEqual(resolve_template(page), "conversation")

    def test_structural_reader_is_protected(self):
        self.assertEqual(resolve_template({"interview_template": "conversation", "source_kind": "lecture_report"}), "technical")
        self.assertEqual(resolve_template({"interview_template": "conversation", "translation_segments": [{"translation": "文字"}], "source_pages": ["p1"]}), "scan")
        self.assertEqual(resolve_template({"source": "a legacy string"}), "narrative")

    def test_registry_and_corpus(self):
        report = audit()
        registry = yaml.safe_load((ROOT / "_data/interview_templates.yml").read_text(encoding="utf-8"))
        self.assertFalse(report["errors"])
        self.assertFalse(report["invalid_overrides"])
        self.assertTrue(set(report["templates"]) <= set(registry))
        self.assertEqual(sum(report["templates"].values()), report["posts"])


@unittest.skipUnless(os.environ.get("INTERVIEW_PREVIEW_DIR"), "Set INTERVIEW_PREVIEW_DIR for rendered checks")
class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(os.environ["INTERVIEW_PREVIEW_DIR"])
        cls.manifest = json.loads((cls.directory / "manifest.json").read_text(encoding="utf-8"))

    def test_every_liquid_route_matches_audit(self):
        actual = {r["file"]: r["template"] for r in self.manifest["routes"]}
        expected = {r["file"]: r["template"] for r in audit()["rows"]}
        self.assertEqual(actual, expected)

    def test_examples_keep_content_and_anchors(self):
        for form, name in self.manifest["examples"].items():
            with self.subTest(form=form):
                soup = BeautifulSoup((self.directory / f"{form}.html").read_text(encoding="utf-8"), "html.parser")
                root = soup.select_one("main[data-interview-template]")
                self.assertIsNotNone(root)
                self.assertEqual(root["data-interview-template"], self.manifest.get("expected_forms", {}).get(form, form))
                body = root.select_one("#parallel-reading")
                self.assertIsNotNone(body)
                for img in root.select("img[src]"):
                    src = urlsplit(img["src"]).path
                    if src.startswith("/assets/"):
                        self.assertTrue((ROOT / unquote(src.lstrip("/"))).is_file(), src)
                ids = [tag["id"] for tag in root.select("[id]")]
                self.assertEqual(len(ids), len(set(ids)), "Duplicate reading IDs")
                for link in root.select('.ed-topic-nav a[href^="#"], .ed-contents a[href^="#"]'):
                    self.assertIn(link["href"][1:], ids)
                if form == "prose-fallback":
                    self.assertIsNotNone(body.select_one(".ed-prose h2, .ed-prose h3"))
                    self.assertTrue(body.select(".ed-prose p"))
                    self.assertFalse(root.select(".ed-epilogue.parallel-translation__note"))
                    self.assertFalse(root.select("[data-view-choice]"), "Unsegmented prose cannot pretend to have parallel mode")
                elif form not in ("scan",):
                    page = yaml.load(FRONT.match((ROOT / "_posts" / name).read_text(encoding="utf-8-sig"))[1], Loader=LOADER)
                    rows = page.get("parallel_items") or []
                    expected_turns = sum(i.get("type", "paragraph") not in ("heading", "header", "image", "hr") for i in rows)
                    self.assertEqual(len(body.select(".ed-trans")), expected_turns)
                    self.assertTrue(all(t.get_text(strip=True) for t in body.select(".ed-trans")))
                    expected_notes = sum(bool(str(i.get("note") or "").strip() or str(i.get("comment") or "").strip()) for i in rows if i.get("type", "paragraph") not in ("heading", "header", "image", "hr"))
                    self.assertEqual(len(body.select("[data-note-toggle]")), expected_notes)
                if form == "annotated":
                    self.assertTrue(body.select(".ed-turn--commentary"))
                    self.assertNotIn("Dr. Lava", [b.get("data-speaker") for b in root.select(".parallel-cast-chip")])


if __name__ == "__main__":
    unittest.main()
