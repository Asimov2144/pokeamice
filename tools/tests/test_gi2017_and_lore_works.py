"""Regression tests for Game Informer 2017 appendix separation and Pokémon-only post_lore works."""

import importlib.util
import json
import pathlib
import sys
import unittest
from urllib.parse import unquote, urlparse

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_module(rel_path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bpl = _load_module("tools/build-post-lore.py", "build_post_lore")
eda = _load_module("tools/export-docs-archive.py", "export_docs_archive")


def _read_fm(path: pathlib.Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    return yaml.safe_load(txt.split("---", 2)[1]) or {}


GI_ZH_STEMS = [
    "2017-08-09-interview-gameinformer-2017-masuda-ohmori-pokemon-on-nintendo-switch",
    "2017-08-09-interview-game-informer-game-freak-origins-pre-pokemon",
    "2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures",
    "2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging",
    "2017-08-15-interview-gi-2017-spinoffs",
    "2017-08-16-interview-gameinformer-2017-pokemon-early-design-documents-masuda-ohmori",
    "2017-08-17-interview-game-informer-creators-on-pokemon-anime",
    "2017-08-18-interview-gi-2017-usum-mode",
    "2017-09-22-interview-gi-2017-gs-history",
]

GI_JA_STEMS = [
    "2017-08-09-interview-game-informer-game-freak-origins-pre-pokemon",
    "2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures",
    "2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging",
    "2017-08-15-interview-gi-2017-spinoffs",
    "2017-08-17-interview-game-informer-creators-on-pokemon-anime",
    "2017-08-18-interview-gi-2017-usum-mode",
    "2017-09-22-interview-gi-2017-gs-history",
]

BOILERPLATE_PHRASES = (
    "For more on the history of Pokémon",
    "check out the September '17 issue",
    "Our Reddit AMA On Our Trip",
    "Discussing Our In-Depth Tour Of Game Freak",
    "Game Freak On Player Freedom Vs. Story In Pokémon",
)

FORBIDDEN_NON_WORKS = {
    "任天堂 Switch",
    "任天堂 Switch (Nintendo Switch)",
    "Game Informer Issue 293",
    "周刊Fami通",
    "Fami通",
    "CoroCoro Comic",
    "GAME FREAK",
    "宝可梦中心",
    "宝可梦",
    "精灵宝可梦",
    "超梦",
    "梦幻",
    "基拉祈",
    "宝可拍乐乐",
    "阿罗拉摄影俱乐部",
}


class TestGi2017AndLoreWorks(unittest.TestCase):
    def test_gi2017_posts_trimmed_and_tagged(self):
        expected_counts = {
            ("_posts", "2017-09-22-interview-gi-2017-gs-history"): {14},
            ("_ja", "2017-09-22-interview-gi-2017-gs-history"): {14},
            ("_posts", "2017-08-15-interview-gi-2017-spinoffs"): {8},
            ("_ja", "2017-08-15-interview-gi-2017-spinoffs"): {8},
            ("_posts", "2017-08-17-interview-game-informer-creators-on-pokemon-anime"): {13, 17},
            ("_ja", "2017-08-17-interview-game-informer-creators-on-pokemon-anime"): {17},
            ("_posts", "2017-08-09-interview-game-informer-game-freak-origins-pre-pokemon"): {27},
            ("_ja", "2017-08-09-interview-game-informer-game-freak-origins-pre-pokemon"): {27},
        }
        present_zh_stems = [s for s in GI_ZH_STEMS if (ROOT / "_posts" / f"{s}.md").exists()]
        self.assertGreaterEqual(len(present_zh_stems), 7)
        for stem in present_zh_stems:
            fm = _read_fm(ROOT / "_posts" / f"{stem}.md")
            self.assertEqual(fm.get("source_appendix"), "gi_2017_gamefreak_visit", stem)
            items = fm.get("parallel_items") or []
            if ("_posts", stem) in expected_counts:
                self.assertIn(len(items), expected_counts[("_posts", stem)], stem)
            for it in items:
                txt = (it.get("original") or "") + "\n" + (it.get("translation") or "")
                for phrase in BOILERPLATE_PHRASES:
                    self.assertNotIn(phrase, txt, f"{stem}: found footer phrase {phrase!r}")

        present_ja_stems = [s for s in GI_JA_STEMS if (ROOT / "_ja" / f"{s}.md").exists()]
        self.assertGreaterEqual(len(present_ja_stems), 7)
        for stem in present_ja_stems:
            fm = _read_fm(ROOT / "_ja" / f"{stem}.md")
            self.assertEqual(fm.get("source_appendix"), "gi_2017_gamefreak_visit", f"ja/{stem}")
            items = fm.get("parallel_items") or []
            if ("_ja", stem) in expected_counts:
                self.assertIn(len(items), expected_counts[("_ja", stem)], f"ja/{stem}")
            for it in items:
                txt = (it.get("original") or "") + "\n" + (it.get("translation") or "")
                for phrase in BOILERPLATE_PHRASES:
                    self.assertNotIn(phrase, txt, f"ja/{stem}: found footer phrase {phrase!r}")

        switch_path = ROOT / "_posts" / f"{GI_ZH_STEMS[0]}.md"
        if switch_path.exists():
            switch_fm = _read_fm(switch_path)
            self.assertEqual((switch_fm.get("entities") or {}).get("works"), ["宝可梦 剑·盾"])
        rs_fm = _read_fm(ROOT / "_posts" / f"{GI_ZH_STEMS[3]}.md")
        self.assertEqual(
            (rs_fm.get("entities") or {}).get("works"),
            ["宝可梦 红宝石·蓝宝石", "宝可梦 欧米伽红宝石·阿尔法蓝宝石"],
        )
        early_path = ROOT / "_posts" / f"{GI_ZH_STEMS[5]}.md"
        if early_path.exists():
            early_fm = _read_fm(early_path)
            self.assertEqual(
                (early_fm.get("entities") or {}).get("works"),
                ["宝可梦 红·绿", "宝可梦 黑·白", "宝可梦 太阳·月亮"],
            )

    def test_source_appendices_data_and_urls(self):
        data = yaml.safe_load((ROOT / "_data" / "source_appendices.yml").read_text(encoding="utf-8"))
        gi = data["gi_2017_gamefreak_visit"]
        items = gi["items"]
        self.assertEqual(len(items), 13)
        archived_stems = []
        present_zh_stems = [s for s in GI_ZH_STEMS if (ROOT / "_posts" / f"{s}.md").exists()]
        for item in items:
            self.assertTrue(item.get("title_zh"))
            self.assertTrue(item.get("title_ja"))
            self.assertTrue(item.get("title_en"))
            self.assertTrue((item.get("source_url") or "").startswith("https://"))
            stem = item.get("stem")
            if stem:
                archived_stems.append(stem)
                post_path = ROOT / "_posts" / f"{stem}.md"
                if post_path.exists():
                    post_fm = _read_fm(post_path)
                    expected_zh = urlparse(eda.canonical_url(post_fm, stem[11:])).path
                    self.assertEqual(unquote(item["zh_url"]), unquote(expected_zh), stem)
                ja_path = ROOT / "_ja" / f"{stem}.md"
                if item.get("ja_url") and ja_path.exists():
                    self.assertEqual(item["ja_url"], _read_fm(ja_path).get("permalink"), stem)
        self.assertTrue(set(present_zh_stems).issubset(set(archived_stems)))

    def test_quotes_anchors_remain_valid_for_gi2017(self):
        quotes_doc = yaml.safe_load((ROOT / "_data" / "quotes.yml").read_text(encoding="utf-8")) or {}
        gi_stems = {s for s in GI_ZH_STEMS if (ROOT / "_posts" / f"{s}.md").exists()}
        checked = 0
        for q in (quotes_doc.get("quotes") or []):
            stem = q.get("post")
            if stem not in gi_stems:
                continue
            checked += 1
            seg_num = int(q["segment"])
            items = _read_fm(ROOT / "_posts" / f"{stem}.md").get("parallel_items") or []
            self.assertGreaterEqual(seg_num, 1, q)
            self.assertLessEqual(seg_num, len(items), f"{stem} #{seg_num} out of bounds ({len(items)})")
        self.assertGreaterEqual(checked, 13)

    def test_post_lore_works_grounded_and_canonical(self):
        works_idx = bpl.works_index()
        posts_by_id = {p["id"]: p for p in bpl.load_posts()}
        gi_ids = {s[11:] for s in GI_ZH_STEMS}

        for jp in sorted((ROOT / "data" / "post_lore").glob("*.json")):
            blob = json.loads(jp.read_text(encoding="utf-8"))
            pid = blob.get("id")
            segs = posts_by_id[pid]["segs"] if pid in posts_by_id else None
            seen_names = set()
            seen_non_pokemon = False
            for row in (blob.get("facets") or {}).get("works") or []:
                name = row.get("name")
                self.assertNotIn(name, FORBIDDEN_NON_WORKS, f"{pid}: forbidden non-work {name!r}")
                resolved = bpl.resolve_work(name, works_idx)
                self.assertIsNotNone(resolved, f"{pid}: invalid work {name!r}")
                self.assertEqual(resolved["name"], name, f"{pid}: non-canonical work {name!r} -> {resolved['name']!r}")
                self.assertEqual(row.get("slug"), resolved.get("slug"), f"{pid}: slug mismatch for {name!r}")
                self.assertNotIn(name, seen_names, f"{pid}: duplicate work {name!r}")
                seen_names.add(name)
                if resolved.get("pokemon"):
                    self.assertFalse(seen_non_pokemon, f"{pid}: Pokemon work {name!r} appeared after non-Pokemon work")
                else:
                    seen_non_pokemon = True
                if pid in gi_ids and segs is not None:
                    for s in row.get("seg") or []:
                        self.assertIsInstance(s, int, f"{pid}: non-int seg {s!r}")
                        self.assertTrue(0 <= s < len(segs), f"{pid}: out-of-range work seg {s} >= {len(segs)}")

        lore_yml = yaml.safe_load((ROOT / "_data" / "post_lore.yml").read_text(encoding="utf-8")) or {}
        yml_work_counts = {}
        for pid, entry in lore_yml.items():
            for w in (entry.get("facets") or {}).get("works") or []:
                name = w.get("name")
                self.assertNotIn(name, FORBIDDEN_NON_WORKS, f"_data/post_lore.yml {pid}: {name!r}")
                resolved = bpl.resolve_work(name, works_idx)
                self.assertIsNotNone(resolved, f"_data/post_lore.yml {pid}: {name!r}")
                self.assertEqual(resolved["name"], name, f"_data/post_lore.yml {pid}: non-canonical {name!r}")
                yml_work_counts[name] = yml_work_counts.get(name, 0) + 1

        for expected_kept in ("Quinty", "勇者斗恶龙", "塞尔达传说", "塞尔达传说：旷野之息", "MOTHER", "铁板阵", "风来的西林", "接龙赛马"):
            self.assertGreaterEqual(yml_work_counts.get(expected_kept, 0), 1, f"Missing expected work {expected_kept!r}")
        for old_variant in ("昆蒂", "孟德尔宫殿", "パルスマン", "ソリティ馬"):
            self.assertEqual(yml_work_counts.get(old_variant, 0), 0, f"Uncanonicalized variant {old_variant!r}")

        gs_lore = json.loads((ROOT / "data" / "post_lore" / "interview-gi-2017-gs-history.json").read_text(encoding="utf-8"))
        gs_work_names = [w["name"] for w in gs_lore["facets"]["works"]]
        self.assertEqual(set(gs_work_names), {"宝可梦 金·银", "宝可梦 红·绿"})
        self.assertNotIn("使命召唤：二战", gs_work_names)
        self.assertNotIn("Bazaar de Gosāru no Game de Gosāru", gs_work_names)
        self.assertTrue(any(p["name"] == "东寺塔" for p in gs_lore["facets"]["places"]))
        self.assertTrue(any(p["name"] == "岩田聪" for p in gs_lore["facets"]["people"]))
        self.assertGreater(len(gs_lore.get("observations") or []), 0)
        for pkm in gs_lore["facets"].get("pokemon") or []:
            for s in pkm.get("seg") or []:
                self.assertLess(s, 14)

        anime_lore = json.loads((ROOT / "data" / "post_lore" / "interview-game-informer-creators-on-pokemon-anime.json").read_text(encoding="utf-8"))
        anime_works = [w["name"] for w in anime_lore["facets"]["works"]]
        self.assertNotIn("玩具总动员2", anime_works)

        origins_lore = json.loads((ROOT / "data" / "post_lore" / "interview-game-informer-game-freak-origins-pre-pokemon.json").read_text(encoding="utf-8"))
        origins_works = [w["name"] for w in origins_lore["facets"]["works"]]
        for req in ("宝可梦 红·绿", "Quinty", "Jerry Boy", "耀西的蛋", "脉冲超人", "马力欧与瓦力欧", "TEMBO THE BADASS ELEPHANT"):
            self.assertIn(req, origins_works, f"origins missing {req!r}")
        self.assertEqual(origins_works[0], "宝可梦 红·绿")

        gs_items = _read_fm(ROOT / "_posts" / "2017-09-22-interview-gi-2017-gs-history.md")["parallel_items"]
        self.assertEqual(len(eda.normalize_parallel(gs_items, {})), 14)


if __name__ == "__main__":
    unittest.main()
