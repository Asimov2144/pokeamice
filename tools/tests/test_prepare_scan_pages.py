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
    seam_span_of,
    seam_tilt_of,
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


def test_seam_tilt_tracks_the_shadow_not_the_bright_gap():
    """The seam is a dark trough; the pale gap beside it is a decoy.

    Measured on these scans the seam column reads about 110 against a page
    median above 190. Chasing the bright ridge instead reported tilts of several
    degrees on spreads whose binding is in fact vertical.
    """
    width, height = 1200, 800
    canvas = np.full((height, width, 3), 235, dtype=np.uint8)
    canvas[:, 200:560] = 180                # left page body, mid grey
    canvas[:, 660:1000] = 180               # right page body
    canvas[:, 560:600] = 250                # bright gap on one side of the seam
    for y in range(height):                 # dark binding shadow, dead vertical
        x = 610
        canvas[y, x:x + 14] = 40

    seam, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert 0.50 < seam < 0.53, f"seam should sit on the shadow, got {seam}"
    tilt, bands = seam_tilt_of(canvas.astype(np.float32), seam, contrast)
    assert bands >= 15, f"a clean vertical shadow should be found in most bands, got {bands}"
    assert abs(tilt) < 0.3, f"a vertical seam must not report a tilt, got {tilt}"


def test_seam_tilt_is_found_when_the_binding_really_leans():
    width, height = 1200, 800
    canvas = np.full((height, width, 3), 220, dtype=np.uint8)
    for y in range(height):
        x = 560 + round(y * 0.08)           # about 4.6 degrees
        canvas[y, x:x + 14] = 40
    seam, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    tilt, bands = seam_tilt_of(canvas.astype(np.float32), seam, contrast)
    assert bands >= 15
    assert 3.5 < tilt < 5.5, f"expected roughly 4.6 degrees, got {tilt}"


def test_flat_page_reports_no_usable_gutter():
    _, contrast = gutter_of(page(width=1200, height=800).astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert contrast < 35, "a page with no seam must not look splittable"


def test_trim_removes_uniform_dark_bands_within_the_limit():
    array = np.full((400, 300, 3), 240, dtype=np.uint8)
    array[:, :8] = 15           # binding shadow left behind by a split
    array[390:] = 15            # scanner bed along the bottom
    trimmed = trim_dark_edges(Image.fromarray(array), paper_luma=240.0)
    assert trimmed.size == (300 - 8, 400 - 10)

    all_dark = Image.fromarray(np.full((400, 300, 3), 15, dtype=np.uint8))
    kept = trim_dark_edges(all_dark, paper_luma=240.0)
    assert kept.size == (300 - 2 * 12, 400 - 2 * 16), "trimming must stop at the 4% cap"


def test_trim_leaves_a_printed_black_masthead_alone():
    """Ink is dark but structured; a scanner edge is dark and featureless.

    Trimming on brightness alone took the full allowance out of the top of
    DREAM 2008.12 page011, which opens with a full-width black masthead.
    """
    array = np.full((400, 300, 3), 240, dtype=np.uint8)
    array[:40] = 20                       # black masthead band
    array[:40, 20:280:9] = 245            # white type knocked out, on every row
    trimmed = trim_dark_edges(Image.fromarray(array), paper_luma=240.0)
    assert trimmed.size == (300, 400), "a masthead carrying type must survive"


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
    def measurement(paper, luma, black=20.0, cast=0.0):
        return Measurement(
            width=1000, height=1400, aspect=0.71, content_box=[0, 0, 1, 1],
            gutter_x=None, gutter_contrast=0.0, seam_span=[0.5, 0.5], skew_deg=0.0,
            seam_tilt=0.0, seam_bands=0,
            paper_rgb=paper, paper_luma=luma, black_point=black, colour_cast=cast,
        )

    dark = measurement([120.0, 90.0, 60.0], 150.0)
    clean = measurement([255.0, 255.0, 255.0], 255.0, black=3.0, cast=0.0)
    yellowed = measurement([252.0, 249.0, 232.0], 248.0, black=8.0, cast=20.0)
    washed = measurement([255.0, 255.0, 255.0], 255.0, black=95.0, cast=0.0)

    assert tone_policy_for("art", clean) == "preserve", "art is never tone-mapped"
    assert tone_policy_for("single", dark) == "preserve", "a page with no paper white is left alone"
    assert tone_policy_for("single", yellowed) == "paper", "a visible cast is worth removing"
    assert tone_policy_for("single", washed) == "paper", "lifted blacks are worth pulling down"
    # A near-identity stretch still rewrites every pixel and forces a re-encode,
    # which on DREAM 2008.12 turned 59MB of source into 114MB of archive.
    assert tone_policy_for("single", clean) == "already-clean"


def test_split_order_follows_the_binding_side():
    image = Image.fromarray(spread())
    right_bound = split_at(image, (0.48, 0.52), "right")
    left_bound = split_at(image, (0.48, 0.52), "left")
    assert [name for name, _ in right_bound] == ["a", "b"]
    # The first piece of a right-bound title is the right half, and mirrored for left.
    assert right_bound[0][1].size[0] < image.width
    assert left_bound[0][1].size[0] == right_bound[1][1].size[0]


def test_split_cuts_outside_the_shadow_so_neither_half_keeps_it():
    """Both halves must start on their own page, not on the binding.

    Cutting at the seam with a fixed bleed left the shadow on the inner edge of
    both pieces, and it survived the edge trim because a gradient is not flat
    enough to look like a scanner border.
    """
    canvas = spread(gutter_at=0.5, width=1200, height=800)
    seam = round(1200 * 0.5)
    for offset in range(-30, 30):                 # a graded shadow, not a hard band
        fade = 1.0 - abs(offset) / 30.0
        canvas[:, seam + offset] = round(245 - 200 * fade)

    seam_x, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    span = seam_span_of(canvas.astype(np.float32), seam_x, contrast)
    assert span[0] < seam_x < span[1], "the shadow must straddle the seam"

    pieces = dict(split_at(Image.fromarray(canvas), span, "right"))
    right = np.asarray(pieces["a"].convert("L"), dtype=np.float32).mean(axis=0)
    left = np.asarray(pieces["b"].convert("L"), dtype=np.float32).mean(axis=0)
    assert right[0] > 150, f"right page starts inside the shadow: {right[0]:.0f}"
    assert left[-1] > 150, f"left page ends inside the shadow: {left[-1]:.0f}"


def test_encode_flags_when_reencoding_gains_nothing(tmp_path=None):
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "out.jpg"
        image = Image.fromarray(page())
        tight = encode(image, target, 88, None, budget_bytes=10)
        assert tight["over_budget"] is True, "an impossible budget must be reported"
        assert tight["quality"] == 70, "quality should step down to the floor trying to fit"
        assert target.exists() and tight["bytes"] > 0

        roomy = encode(image, target, 88, None, budget_bytes=5_000_000)
        assert roomy["over_budget"] is False
        assert roomy["quality"] == 88, "no need to drop quality when the budget allows it"

        web = encode(image, Path(directory) / "web.jpg", 82, 200, None)
        assert max(web["size"]) == 200, "web profile must respect the long edge"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok  {name}")
    print("scan preparation checks passed")
