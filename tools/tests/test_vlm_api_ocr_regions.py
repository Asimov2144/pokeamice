import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "vlm_api_ocr_regions.py"
SPEC = importlib.util.spec_from_file_location("vlm_api_ocr_regions", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VerticalLongStripTests(unittest.TestCase):
    def make_vertical_columns(self, path: Path, columns: int = 3):
        image = Image.new("RGB", (columns * 60 + 40, 520), "white")
        draw = ImageDraw.Draw(image)
        for column in range(columns):
            x = 25 + column * 60
            for y in range(24, 485, 28):
                draw.rectangle((x, y, x + 16, y + 19), fill="black")
        image.save(path)

    def make_horizontal_layout_columns(self, path: Path):
        image = Image.new("RGB", (640, 380), "white")
        draw = ImageDraw.Draw(image)
        for left in (25, 345):
            for y in range(25, 345, 26):
                for x in range(left, left + 265, 20):
                    draw.rectangle((x, y, x + 13, y + 16), fill="black")
        image.save(path)

    def test_vertical_qwen_strip_is_square_padded_without_scaling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "strip.jpg"
            original = Image.new("RGB", (100, 500), "white")
            for y in range(40, 460):
                original.putpixel((50, y), (0, 0, 0))
            original.save(source, quality=100, subsampling=0)

            request_path, metadata = MODULE.prepare_vertical_long_strip(
                source,
                {"writing_direction": "vertical"},
                "qwen-vl-ocr-latest",
                root / "prepared",
                3.0,
                False,
            )

            self.assertNotEqual(request_path, source)
            self.assertEqual(metadata["strategy"], "vertical_long_strip_square_padding")
            with Image.open(source) as source_image, Image.open(request_path) as request_image:
                self.assertEqual(request_image.width, request_image.height)
                x, y = metadata["padding_offset"]
                restored = request_image.crop((x, y, x + source_image.width, y + source_image.height))
                self.assertIsNone(ImageChops.difference(source_image.convert("RGB"), restored.convert("RGB")).getbbox())

    def test_non_vertical_region_is_not_preprocessed(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "strip.jpg"
            Image.new("RGB", (100, 500), "white").save(source)
            request_path, metadata = MODULE.prepare_vertical_long_strip(
                source,
                {"writing_direction": "horizontal"},
                "qwen-vl-ocr-latest",
                Path(temp) / "prepared",
                3.0,
                False,
            )
            self.assertEqual(request_path, source)
            self.assertEqual(metadata, {})

    def test_vertical_columns_are_joined_in_right_to_left_order(self):
        text, metadata = MODULE.reverse_vertical_column_order("左列\n右列", True)
        self.assertEqual(text, "右列左列")
        self.assertEqual(metadata["column_count"], 2)
        self.assertTrue(metadata["reversed"])

    def test_single_vertical_column_chunks_keep_top_to_bottom_order(self):
        text, metadata = MODULE.reverse_vertical_column_order("上の続き\n中央\n下の続き", True, reverse=False)
        self.assertEqual(text, "上の続き中央下の続き")
        self.assertFalse(metadata["reversed"])
        self.assertEqual(metadata["reading_order"], "top_to_bottom")

    def test_image_structure_detects_and_splits_vertical_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "vertical.png"
            self.make_vertical_columns(source, 3)
            orientation = MODULE.detect_text_orientation(source)
            columns = MODULE.detect_physical_columns(source, "vertical", 8)
            self.assertEqual(orientation["direction"], "vertical")
            self.assertGreaterEqual(orientation["confidence"], 0.3)
            self.assertEqual(columns["column_count"], 3)

    def test_horizontal_layout_gutters_are_split_left_to_right(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "horizontal.png"
            self.make_horizontal_layout_columns(source)
            orientation = MODULE.detect_text_orientation(source)
            columns = MODULE.detect_physical_columns(source, "horizontal", 8)
            text, metadata = MODULE.join_column_texts(["左栏", "右栏"], "horizontal")
            self.assertIn(orientation["direction"], {"horizontal", "unknown"})
            self.assertEqual(columns["column_count"], 2)
            self.assertEqual(text, "左栏\n右栏")
            self.assertEqual(metadata["reading_order"], "left_to_right")

    def test_prepare_column_crops_records_direction_override(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "vertical.png"
            self.make_vertical_columns(source, 3)
            paths, metadata = MODULE.prepare_column_crops(
                source,
                {"writing_direction": "horizontal"},
                "qwen-vl-ocr-latest",
                root / "prepared",
                8,
                False,
            )
            self.assertEqual(len(paths), 3)
            self.assertTrue(metadata["direction_overridden"])
            self.assertEqual(metadata["effective_direction"], "vertical")

    def test_narrow_vertical_strip_is_never_split_by_glyph_strokes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "single-column.png"
            image = Image.new("RGB", (72, 720), "white")
            draw = ImageDraw.Draw(image)
            for y in range(20, 690, 24):
                draw.rectangle((26, y, 42, y + 18), fill="black")
            image.save(source)
            paths, metadata = MODULE.prepare_column_crops(
                source,
                {"writing_direction": "vertical", "confidence": 1.0},
                "qwen-vl-ocr-latest",
                root / "prepared",
                8,
                False,
            )
            self.assertEqual(paths, [])
            self.assertTrue(metadata["forced_single_column"])
            self.assertEqual(metadata["detected_column_count"], 1)

    def test_wide_vertical_band_uses_whole_block_ocr(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "wide-band.png"
            image = Image.new("RGB", (900, 420), "white")
            draw = ImageDraw.Draw(image)
            for x in range(70, 860, 45):
                for y in range(30, 390, 28):
                    draw.rectangle((x, y, x + 14, y + 20), fill="black")
            image.save(source)
            paths, metadata = MODULE.prepare_column_crops(
                source,
                {"writing_direction": "vertical", "confidence": 1.0},
                "qwen-vl-ocr-latest",
                root / "prepared",
                16,
                False,
            )
            self.assertEqual(paths, [])
            self.assertEqual(metadata["strategy"], "whole_vertical_block")
            self.assertTrue(metadata["whole_block_selected"])
            self.assertGreaterEqual(metadata["detected_column_count"], 2)

    def test_ocr_similarity_ignores_whitespace_only(self):
        score = MODULE.normalized_ocr_similarity("永田町へ\n行く", "永田町へ 行く")
        self.assertEqual(score, 1.0)

    def test_repeated_line_sequence_is_warned(self):
        warnings = MODULE.quality_warnings("甲\n乙\n丙\n甲\n乙\n丁")
        self.assertIn("repeated_line_sequence", warnings)

    def test_vertical_columns_are_grouped_into_subblocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "band.png"
            Image.new("RGB", (720, 360), "white").save(source)
            boxes = [[x, 20, x + 24, 340] for x in range(20, 620, 40)]
            paths = MODULE.prepare_vertical_subblock_crops(source, boxes, root / "prepared", 6)
            self.assertEqual(len(paths), 3)
            self.assertTrue(all(path.exists() for path in paths))

    def test_wide_high_confidence_heading_suppresses_structure_override(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "heading.png"
            Image.new("RGB", (1000, 120), "white").save(source)
            with patch.object(MODULE, "detect_text_orientation", return_value={
                "direction": "vertical", "confidence": 0.82, "source_size": [1000, 120]
            }), patch.object(MODULE, "detect_physical_columns", return_value={
                "direction": "horizontal", "column_count": 1, "columns": [[0, 0, 1000, 120]],
                "detected_columns": [[0, 0, 1000, 120]], "detected_column_count": 1,
                "too_many_columns": False, "reading_order": "left_to_right", "source_size": [1000, 120]
            }):
                paths, metadata = MODULE.prepare_column_crops(
                    source,
                    {"writing_direction": "horizontal", "confidence": 0.95},
                    "qwen-vl-ocr-latest",
                    root / "prepared",
                    8,
                    False,
                )
            self.assertEqual(paths, [])
            self.assertEqual(metadata["effective_direction"], "horizontal")
            self.assertTrue(metadata["direction_override_suppressed"])
            self.assertFalse(metadata["direction_overridden"])

    def test_physical_vertical_columns_join_right_to_left(self):
        text, metadata = MODULE.join_column_texts(["左", "中", "右"], "vertical")
        self.assertEqual(text, "右中左")
        self.assertEqual(metadata["column_count"], 3)

    def test_long_strip_uses_column_structured_prompt(self):
        prompt = MODULE.prompt_with_region_hint(
            "a longer project-specific prompt",
            {"writing_direction": "vertical"},
            True,
        )
        self.assertEqual(prompt, MODULE.VERTICAL_LONG_STRIP_PROMPT)

    def test_coordinate_only_ocr_output_is_flagged(self):
        text = "\n".join([
            "498,34,11,229,90",
            "516,44,13,201,90",
            "500,112,15,211,90",
            "506,152,15,211,90",
            "500,192,15,211,90",
        ])
        warnings = MODULE.quality_warnings(text)
        self.assertTrue(any(warning.startswith("coordinate_dump") for warning in warnings))

    def test_single_coordinate_row_in_short_output_is_flagged_and_removed(self):
        text = "472,526,429,579,90\n129"
        warnings = MODULE.quality_warnings(text)
        cleaned, detail = MODULE.strip_coordinate_prefixes(text)
        self.assertTrue(any(warning.startswith("coordinate_dump") for warning in warnings))
        self.assertEqual(cleaned, "129")
        self.assertEqual(detail["affected_lines"], 1)

    def test_coordinate_prefixed_text_is_detected_and_cleaned(self):
        text = "\n".join([
            "19,262,323,28,90,はすべて色彩設計により規定されている。",
            "64,262,323,28,90,ピカチュウの黄色やサトシの目の色など",
            "110,262,323,28,90,ペイントのソフトで彩色をしていく。",
            "156,262,323,28,90,作業が終わると色指定に沿って確認する。",
        ])
        warnings = MODULE.quality_warnings(text)
        cleaned, detail = MODULE.strip_coordinate_prefixes(text)
        self.assertTrue(any(warning.startswith("coordinate_dump") for warning in warnings))
        self.assertNotIn("19,262,323,28,90", cleaned)
        self.assertIn("色彩設計", cleaned)
        self.assertEqual(detail["strategy"], "coordinate_prefix_strip")


class ImageAnalysisDependencyTests(unittest.TestCase):
    """numpy/cv2 must fail loudly instead of quietly disabling column detection."""

    def make_crop(self, path: Path):
        Image.new("RGB", (120, 480), "white").save(path)

    def test_missing_packages_are_reported_by_name(self):
        with patch.object(MODULE, "np", None), patch.object(MODULE, "cv2", None):
            self.assertEqual(
                MODULE.missing_image_analysis_packages(),
                ["numpy", "opencv-python-headless"],
            )
        with patch.object(MODULE, "cv2", None):
            self.assertEqual(MODULE.missing_image_analysis_packages(), ["opencv-python-headless"])
        self.assertEqual(MODULE.missing_image_analysis_packages(), [])

    def test_direction_detection_raises_when_numpy_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "crop.png"
            self.make_crop(source)
            with patch.object(MODULE, "np", None):
                with self.assertRaises(RuntimeError) as caught:
                    MODULE.detect_text_orientation(source)
        message = str(caught.exception)
        self.assertIn("numpy", message)
        self.assertNotIn("opencv-python-headless", message)
        self.assertIn("tools/requirements.txt", message)
        self.assertIn("--disable-auto-column-split", message)

    def test_column_detection_raises_when_opencv_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "crop.png"
            self.make_crop(source)
            with patch.object(MODULE, "cv2", None):
                with self.assertRaises(RuntimeError) as caught:
                    MODULE.detect_physical_columns(source, "vertical", 8)
        self.assertIn("opencv-python-headless", str(caught.exception))

    def test_column_crop_preparation_raises_instead_of_skipping_the_split(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "crop.png"
            self.make_crop(source)
            with patch.object(MODULE, "cv2", None), patch.object(MODULE, "np", None):
                with self.assertRaises(RuntimeError):
                    MODULE.prepare_column_crops(
                        source,
                        {"writing_direction": "vertical"},
                        "qwen-vl-ocr-latest",
                        root / "prepared",
                        8,
                        False,
                    )

    def test_disabled_auto_split_stays_a_silent_no_op_without_the_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "crop.png"
            self.make_crop(source)
            stderr = io.StringIO()
            with patch.object(MODULE, "cv2", None), patch.object(MODULE, "np", None):
                with contextlib.redirect_stderr(stderr):
                    paths, metadata = MODULE.prepare_column_crops(
                        source,
                        {"writing_direction": "vertical"},
                        "qwen-vl-ocr-latest",
                        root / "prepared",
                        8,
                        True,
                    )
            self.assertEqual((paths, metadata), ([], {}))
            self.assertEqual(stderr.getvalue(), "")

    def test_missing_pillow_downgrade_prints_a_warning(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "crop.png"
            self.make_crop(source)
            stderr = io.StringIO()
            with patch.object(MODULE, "Image", None):
                with contextlib.redirect_stderr(stderr):
                    paths, metadata = MODULE.prepare_column_crops(
                        source,
                        {"writing_direction": "vertical"},
                        "qwen-vl-ocr-latest",
                        root / "prepared",
                        8,
                        False,
                    )
            self.assertEqual((paths, metadata), ([], {}))
            self.assertIn("WARNING", stderr.getvalue())
            self.assertIn("Pillow is unavailable", stderr.getvalue())

    def test_undecodable_crop_warns_instead_of_claiming_opencv_is_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "not-an-image.png"
            source.write_text("this is not a png", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                orientation = MODULE.detect_text_orientation(source)
            self.assertEqual(orientation["direction"], "unknown")
            self.assertEqual(orientation["reason"], "unreadable_image")
            self.assertIn("could not be decoded", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
