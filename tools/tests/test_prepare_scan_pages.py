"""Checks for scan page measurement and repair, using synthetic pages only."""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prepare_scan_pages import (  # noqa: E402
    Measurement,
    content_box_of,
    encode,
    gutter_of,
    normalise_tone,
    split_at,
    tone_policy_for,
    trim_dark_edges,
)


def page(width=600, height=800, paper=245, margin=40, border=None):
    """A pale page with a darker text block, optionally on a dark scanner bed."""
    canvas = np.full((height, width, 3), border if border is not None else paper, dtype=np.uint8)
    canvas[margin:height - margin, margin:width - margin] = paper
    canvas[margin * 3:height - margin * 3, margin * 2:width - margin * 2] = 60
    return canvas


def spread(gutter_at=0.47, width=1200, height=800):
    left = page(round(width * gutter_at), height)
    right = page(width - round(width * gutter_at) - 12, height)
    canvas = np.full((height, width, 3), 245, dtype=np.uint8)
    canvas[:, :left.shape[1]] = left
    canvas[:, left.shape[1] + 12:] = right
    canvas[:, left.shape[1]:left.shape[1] + 12] = 30      # binding shadow
    return canvas


def test_content_box_finds_the_page_inside_a_dark_bed():
    box = content_box_of(page(border=20).astype(np.float32))
    assert 0.02 < box[0] < 0.10 and 0.02 < box[1] < 0.10
    assert 0.90 < box[2] <= 1.0 and 0.90 < box[3] <= 1.0


def test_content_box_is_full_frame_when_the_page_already_fills_it():
    assert content_box_of(page().astype(np.float32)) == [0.0, 0.0, 1.0, 1.0]


def test_gutter_is_found_off_centre_with_usable_contrast():
    position, contrast = gutter_of(spread(gutter_at=0.42).astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert 0.40 < position < 0.45, f"seam should follow the shadow, got {position}"
    assert contrast > 35, "a real binding shadow must clear the confidence bar"


def test_dark_photo_page_does_not_steal_the_seam():
    """A full-page photo is a broad dark step, not a binding shadow.

    Taking the darkest column alone put the cut at the photo's edge, 333px off
    the real seam on Continue vol.31 page050, which sliced a margin off the
    facing page.
    """
    canvas = spread(gutter_at=0.5, width=1200, height=800)
    canvas[:, 620:] = 70                                  # dark photo fills the right page
    canvas[:, round(1200 * 0.5):round(1200 * 0.5) + 12] = 30   # the actual seam
    position, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert 0.48 < position < 0.53, f"seam should beat the photo edge, got {position}"
    assert contrast > 35


def test_flat_page_reports_no_usable_gutter():
    _, contrast = gutter_of(page(width=1200, height=800).astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert contrast < 35, "a page with no seam must not look splittable"


def test_trim_removes_dark_bands_but_respects_the_limit():
    array = np.full((400, 300, 3), 240, dtype=np.uint8)
    array[:, :18] = 15          # binding shadow left behind by a split
    array[380:] = 15            # scanner bed along the bottom
    trimmed = trim_dark_edges(Image.fromarray(array), paper_luma=240.0)
    assert trimmed.size[0] == 300 - 18
    assert trimmed.size[1] == 400 - 20

    all_dark = Image.fromarray(np.full((400, 300, 3), 15, dtype=np.uint8))
    kept = trim_dark_edges(all_dark, paper_luma=240.0)
    assert kept.size == (300 - 2 * 24, 400 - 2 * 32), "trimming must stop at the 8% cap"


def test_tone_normalisation_whitens_paper_and_removes_cast():
    array = np.full((100, 100, 3), 0, dtype=np.uint8)
    array[:, :] = (238, 232, 205)          # yellowed paper
    array[40:60] = (70, 68, 60)            # ink
    result = np.asarray(normalise_tone(Image.fromarray(array), 66.0, [238.0, 232.0, 205.0]))
    paper = result[0, 0]
    assert paper.min() >= 250, f"paper should reach white, got {paper}"
    assert int(paper.max()) - int(paper.min()) <= 2, "per-channel mapping should clear the cast"
    assert result[50, 50].max() < 40, "ink should come down toward the target black"


def test_art_pages_keep_their_colour():
    dark = Measurement(1000, 1400, 0.71, [0, 0, 1, 1], None, 0.0, 0.0,
                       [120.0, 90.0, 60.0], 150.0, 20.0, 60.0)
    bright = Measurement(1000, 1400, 0.71, [0, 0, 1, 1], None, 0.0, 0.0,
                         [250.0, 248.0, 240.0], 248.0, 20.0, 10.0)
    assert tone_policy_for("art", bright) == "preserve", "art is never tone-mapped"
    assert tone_policy_for("single", dark) == "preserve", "a page with no paper white is left alone"
    assert tone_policy_for("single", bright) == "paper"


def test_split_order_follows_the_binding_side():
    image = Image.fromarray(spread())
    right_bound = split_at(image, 0.5, "right")
    left_bound = split_at(image, 0.5, "left")
    assert [name for name, _ in right_bound] == ["a", "b"]
    # The first piece of a right-bound title is the right half, and mirrored for left.
    assert right_bound[0][1].size[0] < image.width
    assert left_bound[0][1].size[0] == right_bound[1][1].size[0]


def test_encode_flags_when_reencoding_gains_nothing(tmp_path=None):
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "out.jpg"
        image = Image.fromarray(page())
        gained = encode(image, target, 88, None, original_bytes=10)
        assert gained["reencode_gained_nothing"] is True
        assert target.exists() and gained["bytes"] > 0

        honest = encode(image, target, 88, None, original_bytes=5_000_000)
        assert honest["reencode_gained_nothing"] is False

        web = encode(image, Path(directory) / "web.jpg", 82, 200, None)
        assert max(web["size"]) == 200, "web profile must respect the long edge"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok  {name}")
    print("scan preparation checks passed")
