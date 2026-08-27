"""Checks for scan page measurement and repair, using synthetic pages only."""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prepare_scan_pages import (  # noqa: E402
    Measurement,
    PageResult,
    content_box_of,
    classify,
    encode,
    gutter_of,
    normalise_tone,
    outer_page_edges,
    resolve_outer_trim,
    review_reasons_for,
    seam_span_of,
    seam_tilt_of,
    split_at,
    tone_policy_for,
    tone_of,
    tone_reference_of,
    trim_dark_edges,
    trim_scanner_frame,
    upright_image,
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
        x = 580 + round(y * 0.025)          # about 1.4 degrees
        canvas[y, x:x + 14] = 40
    seam, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    tilt, bands = seam_tilt_of(canvas.astype(np.float32), seam, contrast)
    assert bands >= 15
    assert 1.0 < tilt < 1.9, f"expected roughly 1.4 degrees, got {tilt}"


def test_implausible_seam_tilt_is_refused():
    """A bound page does not lean far. ScanTailor caps its spine search at 2
    degrees and the measured spreads here sit inside +/-0.75, so a larger fit is
    evidence the wrong feature was tracked, not a crooked book."""
    width, height = 1200, 800
    canvas = np.full((height, width, 3), 220, dtype=np.uint8)
    for y in range(height):
        x = 520 + round(y * 0.14)           # about 8 degrees
        canvas[y, x:x + 14] = 40
    seam, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    tilt, _ = seam_tilt_of(canvas.astype(np.float32), seam, contrast)
    assert tilt == 0.0, f"a wild tilt must fall back to a vertical cut, got {tilt}"


def test_a_tall_photo_edge_does_not_outscore_the_binding():
    """Persistence is what tells a spine from a picture edge.

    ScanTailor gates its spine search on the fraction of rows that are dark in
    a column. A binding runs the whole height; a photograph is dark only over
    the rows it covers.
    """
    width, height = 1200, 900
    canvas = np.full((height, width, 3), 240, dtype=np.uint8)
    canvas[:520, 470:520] = 25              # a tall, very dark picture edge
    canvas[:, 620:632] = 70                 # the real seam, weaker but full height
    seam, contrast = gutter_of(canvas.astype(np.float32), [0.0, 0.0, 1.0, 1.0])
    assert 0.50 < seam < 0.54, f"the full-height seam should win, got {seam}"
    assert contrast > 35


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
    assert kept.size == (300, 400), "a band that never ends is the page, not a border"


def test_trim_leaves_a_printed_black_masthead_alone():
    """A band that outlasts the allowance is the page, so it is left alone.

    Row deviation cannot tell ink from platen: measured on these scans the
    scanner band spans 2 to 62 and printed masthead rows span 4 to 96. Whether
    the band ends can, and DREAM 2008.12 page011 keeps its masthead because it
    does not.
    """
    array = np.full((400, 300, 3), 240, dtype=np.uint8)
    array[:60] = 20                       # a masthead deeper than the allowance
    trimmed = trim_dark_edges(Image.fromarray(array), paper_luma=240.0)
    assert trimmed.size == (300, 400), "a masthead deeper than the allowance must survive"


def test_scanner_frame_trim_removes_mid_grey_bed_around_a_page():
    array = np.full((600, 420, 3), 145, dtype=np.uint8)
    array[24:574, 18:402] = (232, 238, 240)
    array[120:500, 70:350] = (70, 75, 78)
    trimmed, removed = trim_scanner_frame(Image.fromarray(array))
    assert removed[0] >= 12 and removed[1] >= 18
    assert removed[2] >= 12 and removed[3] >= 18
    assert trimmed.width < 400 and trimmed.height < 570


def test_scanner_frame_uses_first_page_edge_not_stronger_internal_art():
    array = np.full((600, 420, 3), 180, dtype=np.uint8)
    array[18:582, 14:406] = (225, 218, 190)  # subtle paper/platen boundary
    array[70:145, 14:406] = 15               # much stronger full-width masthead
    trimmed, removed = trim_scanner_frame(Image.fromarray(array))
    assert 10 <= removed[0] <= 30
    assert 12 <= removed[1] <= 36, f"must stop at the sheet edge, got {removed}"
    assert removed[1] < 50, "the masthead must not be mistaken for the top of the page"


def test_scanner_frame_never_auto_crops_deep_inside_a_page():
    array = np.full((600, 420, 3), 240, dtype=np.uint8)
    array[:, :35] = 30                        # printed sidebar at 8.3% of width
    trimmed, removed = trim_scanner_frame(Image.fromarray(array))
    assert removed[0] == 0, "an edge deeper than the 5% safety gate needs review"
    assert trimmed.width == 420


def test_coloured_printed_frame_is_not_a_scanner_edge():
    array = np.full((600, 420, 3), (245, 205, 25), dtype=np.uint8)
    array[20:580, 20:400] = (245, 245, 240)
    trimmed, removed = trim_scanner_frame(Image.fromarray(array))
    assert removed == (0, 0, 0, 0), "a yellow magazine frame is printed content"
    assert trimmed.size == (420, 600)


def test_scanner_frame_trim_does_not_chase_an_internal_masthead():
    array = np.full((600, 420, 3), 240, dtype=np.uint8)
    array[90:190] = 20
    trimmed, removed = trim_scanner_frame(Image.fromarray(array))
    assert removed == (0, 0, 0, 0)
    assert trimmed.size == (420, 600)


def test_tone_normalisation_whitens_paper_and_removes_cast():
    array = np.full((100, 100, 3), 0, dtype=np.uint8)
    array[:, :] = (238, 232, 205)          # yellowed paper
    array[40:60] = (70, 68, 60)            # ink
    result = np.asarray(normalise_tone(Image.fromarray(array), 66.0, [238.0, 232.0, 205.0]))
    paper = result[0, 0]
    assert paper.min() >= 250, f"paper should reach white, got {paper}"
    assert int(paper.max()) - int(paper.min()) <= 2, "per-channel mapping should clear the cast"
    assert result[50, 50].max() < 40, "ink should come down toward the target black"


def test_tone_measurement_prefers_neutral_white_over_cyan_photo_background():
    array = np.full((200, 300, 3), (165, 225, 232), dtype=np.uint8)
    array[145:195, 20:280] = (236, 233, 230)
    array[60:110, 100:200] = (20, 30, 32)
    paper, paper_luma, _, cast = tone_of(array.astype(np.float32))
    assert min(paper) >= 228, f"white clothing or paper should win, got {paper}"
    assert paper_luma >= 230
    assert cast <= 10, f"cyan background must not become the white reference: {cast}"


def test_coloured_highlight_is_never_used_as_a_white_balance_reference():
    array = np.full((200, 300, 3), (246, 231, 65), dtype=np.uint8)
    array[60:140, 80:220] = (35, 32, 15)
    paper, _, _, cast, reliable = tone_reference_of(array.astype(np.float32))
    assert reliable is False, "a yellow illustration has no measured paper white"
    assert max(paper) - min(paper) == 0, "fallback must preserve hue, not invent a cast correction"
    assert cast == 0


def test_exif_orientation_is_materialised_before_processing(tmp_path=None):
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "upside-down.jpg"
        array = np.zeros((80, 60, 3), dtype=np.uint8)
        array[:20] = (250, 20, 20)
        exif = Image.Exif()
        exif[274] = 3
        Image.fromarray(array).save(source, exif=exif, quality=100)
        with Image.open(source) as opened:
            upright = np.asarray(upright_image(opened))
        assert upright[-10:, :, 0].mean() > 220, "EXIF 3 must move the stored top edge to the bottom"
        assert upright[:10, :, 0].mean() < 40


def test_art_pages_keep_their_colour():
    def measurement(paper, luma, black=20.0, cast=0.0):
        return Measurement(
            width=1000, height=1400, aspect=0.71, content_box=[0, 0, 1, 1],
            gutter_x=None, gutter_contrast=0.0, seam_span=[0.5, 0.5],
            outer_edges=[0.0, 0.0], skew_deg=0.0,
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


def test_outer_trim_setting_is_explicit_about_what_it_does():
    """Detection is opt-in; a calibrated number is the reliable path.

    On the pilot folders the detector found the page edge on Continue vol.31
    page041 but was pulled 288px inside the page by a photo card on 金银攻略
    4.png, so nothing is trimmed unless it is asked for.
    """
    m = Measurement(
        width=1000, height=1400, aspect=0.71, content_box=[0, 0, 1, 1],
        gutter_x=None, gutter_contrast=0.0, seam_span=[0.5, 0.5],
        outer_edges=[0.03, 0.04], skew_deg=0.0, seam_tilt=0.0, seam_bands=0,
        paper_rgb=[255.0, 255.0, 255.0], paper_luma=255.0, black_point=3.0, colour_cast=0.0,
    )
    assert resolve_outer_trim("off", m) == (0.0, 0.0)
    assert resolve_outer_trim("", m) == (0.0, 0.0), "the default must never crop"
    assert resolve_outer_trim("auto", m) == (0.03, 0.04)
    assert resolve_outer_trim("50", m) == (0.05, 0.05), "a pixel count is per side"
    assert resolve_outer_trim("2%", m) == (0.02, 0.02)


def test_outer_edges_report_nothing_without_a_clear_step():
    """A page with no book block must not invent one."""
    canvas = np.full((800, 1200, 3), 235, dtype=np.uint8)
    canvas[100:700, 300:900] = 90             # text well clear of the outer zone
    assert outer_page_edges(canvas.astype(np.float32)) == (0.0, 0.0)


def test_outer_edges_find_a_block_that_is_darker_and_busier():
    canvas = np.full((800, 1200, 3), 240, dtype=np.uint8)
    canvas[100:700, 300:900] = 120                       # page content
    rng = np.random.default_rng(7)
    block = rng.integers(60, 190, size=(800, 70, 3), dtype=np.uint8)
    canvas[:, :70] = block                               # book block at the left rim
    left, right = outer_page_edges(canvas.astype(np.float32))
    assert 0.045 < left < 0.075, f"edge should land near the block boundary, got {left}"
    assert right == 0.0, "the clean side must stay untouched"


def test_uncertain_wide_page_is_gated_before_ocr():
    result = PageResult(
        source="nested/page001.jpg",
        source_bytes=100,
        measurement={"aspect": 1.45, "seam_tilt": 0.0, "outer_edges": [0.0, 0.0]},
        decision={
            "kind": "unknown", "split": False, "decided_by": "vlm-failed",
            "confidence": 0.0,
        },
    )
    reasons = review_reasons_for(result)
    assert "page_kind_uncertain" in reasons
    assert "page_model_failed" in reasons
    assert "wide_page_not_split" in reasons


def test_confident_single_page_can_continue_to_ocr():
    result = PageResult(
        source="page001.jpg",
        source_bytes=100,
        measurement={"aspect": 0.71, "seam_tilt": 0.0, "outer_edges": [0.0, 0.0]},
        decision={
            "kind": "single", "split": False, "decided_by": "cv",
            "confidence": 0.9,
        },
    )
    assert review_reasons_for(result) == []


def test_successful_piece_trim_resolves_detected_outer_edge_gate():
    result = PageResult(
        source="page001.jpg",
        source_bytes=100,
        measurement={"aspect": 0.71, "seam_tilt": 0.0, "outer_edges": [0.03, 0.0]},
        decision={
            "kind": "single", "split": False, "decided_by": "cv",
            "confidence": 0.9,
        },
        page_trims=[{"piece": "single", "removed": [20, 0, 0, 0]}],
    )
    assert review_reasons_for(result) == []


def test_cv_seam_threshold_maps_to_workflow_confidence(tmp_path=None):
    measurement = Measurement(
        width=1400, height=900, aspect=1.55, content_box=[0, 0, 1, 1],
        gutter_x=0.5, gutter_contrast=49.0, seam_span=[0.49, 0.51],
        outer_edges=[0.0, 0.0], skew_deg=0.0, seam_tilt=0.0, seam_bands=20,
        paper_rgb=[245.0, 245.0, 245.0], paper_luma=245.0,
        black_point=10.0, colour_cast=0.0,
    )
    decision = classify(Path("unused.jpg"), measurement, "never", "unused", 1)
    assert decision.split is True
    assert decision.confidence >= 0.65


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok  {name}")
    print("scan preparation checks passed")
