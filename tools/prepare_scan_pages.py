"""Turn raw magazine scans into clean, OCR-ready pages plus web derivatives.

The stages are split by what each technique is actually good at. Measurement is
done with OpenCV and numpy, which give exact pixel coordinates. Judgement is
left to a Qwen VL model, which reads a page's meaning but does not measure: in
testing it reported a gutter at exactly 0.500 for every spread, including ones
whose real seam sat at 0.545, and it invented plausible content boxes for pages
that already filled the frame. So the model decides *whether* to split and what
kind of page this is, and the projection profile decides *where*.

    inventory -> measure (cv) -> classify (cv, vlm when unsure)
              -> split / crop / deskew / tone -> encode -> manifest

Originals are never modified. Re-encoding is skipped whenever it would produce a
larger file than the source, because many of these scans are already compressed
and a second pass would only add generation loss.

    python tools/prepare_scan_pages.py --source "E:/Pokeamice/scan/Continue Vol.31" --out out/
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

try:
    import cv2
except ImportError:  # pragma: no cover - guarded in main()
    cv2 = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Image.MAX_IMAGE_PIXELS = None

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
WORK_WIDTH = 1200          # analysis resolution; decisions scale back to full size
SPREAD_ASPECT = 1.15       # wider than this and the page might be two pages
GUTTER_CONFIDENT = 35.0    # projection contrast above which cv alone may decide
PAPER_LUMA_CLEAR = 235.0   # brighter highlights than this means a paper page
PAPER_LUMA_DARK = 200.0    # dimmer than this means full-bleed art, leave colour alone
MIN_DESKEW_DEG = 0.50      # below this, rotating costs more detail than it recovers
MIN_SEAM_TILT_DEG = 0.30   # below this, a vertical cut is already on the seam
MAX_SEAM_TILT_DEG = 2.00   # ScanTailor caps spine tilt here; measured spreads agree
TONE_BLACK_OK = 25.0       # blacks at or under this need no pulling down
TONE_CAST_OK = 8.0         # channel spread at or under this is not a visible cast
TONE_PAPER_OK = 245.0      # highlights at or above this are already paper white


# --------------------------------------------------------------------------- #
# Measurement
# --------------------------------------------------------------------------- #

@dataclass
class Measurement:
    width: int
    height: int
    aspect: float
    content_box: list[float]
    gutter_x: float | None
    gutter_contrast: float
    seam_span: list[float]
    outer_edges: list[float]
    page_boxes: dict[str, list[float]]
    skew_deg: float | None
    seam_tilt: float
    seam_bands: int
    paper_rgb: list[float]
    paper_luma: float
    black_point: float
    colour_cast: float


def upright_image(opened: Image.Image) -> Image.Image:
    """Materialise the display orientation recorded by the scanner/camera.

    Pillow deliberately exposes JPEG pixels as stored.  Several pokepia scans
    store their pixels upside down and rely on EXIF orientation 3, so ignoring
    metadata makes an apparently successful preparation unusable for OCR.
    ``exif_transpose`` handles all mirrored/rotated EXIF variants and removes
    the tag from the returned image so downstream encoders cannot apply it a
    second time.
    """
    return ImageOps.exif_transpose(opened).convert("RGB")


def working_copy(path: Path) -> tuple[np.ndarray, tuple[int, int]]:
    with Image.open(path) as opened:
        image = upright_image(opened)
        full = image.size
        scale = WORK_WIDTH / image.width
        if scale < 1:
            image = image.resize(
                (WORK_WIDTH, max(1, round(image.height * scale))), Image.BILINEAR
            )
        return np.asarray(image, dtype=np.float32), full


def luma_of(rgb: np.ndarray) -> np.ndarray:
    return rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)


def content_box_of(rgb: np.ndarray) -> list[float]:
    """Bounds of the page sitting on a scanner bed.

    Only a bed that is clearly not paper is worth cropping to. When the frame
    edge is already paper-bright the scan has been trimmed already, and treating
    the white margin as background would crop away the page's own margins along
    with the folios printed in them.
    """
    gray = luma_of(rgb)
    border = np.concatenate([
        gray[:8].ravel(), gray[-8:].ravel(), gray[:, :8].ravel(), gray[:, -8:].ravel(),
    ])
    background = float(np.median(border))
    if background > 200.0:
        return [0.0, 0.0, 1.0, 1.0]
    mask = np.abs(gray - background) > 28
    rows = np.where(mask.mean(axis=1) > 0.02)[0]
    cols = np.where(mask.mean(axis=0) > 0.02)[0]
    height, width = gray.shape
    if not len(rows) or not len(cols):
        return [0.0, 0.0, 1.0, 1.0]
    return [
        round(float(cols[0]) / width, 5), round(float(rows[0]) / height, 5),
        round(float(cols[-1] + 1) / width, 5), round(float(rows[-1] + 1) / height, 5),
    ]


def gutter_of(rgb: np.ndarray, box: list[float]) -> tuple[float, float]:
    """Darkest sustained vertical band near the middle: the binding shadow.

    Returns the seam position over the whole image and how far it stands out
    from the surrounding page, which is the signal used to decide whether this
    measurement can be trusted without asking the model.
    """
    height, width = luma_of(rgb).shape
    x0, x1 = int(box[0] * width), int(box[2] * width)
    y0, y1 = int(box[1] * height), int(box[3] * height)
    inner = luma_of(rgb)[y0:y1, x0:x1]
    if inner.size == 0 or inner.shape[1] < 32:
        return 0.5, 0.0
    column = inner.mean(axis=0)
    span = len(column)

    # Vertical persistence, the gate ScanTailor's spine search uses: a binding
    # runs the whole height, so nearly every row of its column is dark, while a
    # photograph is dark only across the rows it occupies. Scoring on this as
    # well as on local darkness stops a picture edge from ever looking like a
    # seam, rather than relying on the blur difference alone to cancel it.
    ink = max(40.0, float(np.percentile(inner, 85)) * 0.72)
    persistence = (inner < ink).mean(axis=0)

    def blur(width_px: int) -> np.ndarray:
        size = max(3, width_px | 1)
        return np.convolve(column, np.ones(size, dtype=np.float32) / size, mode="same")

    # A binding shadow is a narrow local trough. A page carrying a large dark
    # photograph is a broad step, and plain "darkest column" picks the edge of
    # that step instead of the seam. Subtracting a wide blur from a narrow one
    # leaves only dips that are dark *relative to their own neighbourhood*, so
    # the broad step cancels out and the seam survives.
    narrow, wide = blur(9), blur(int(span * 0.06))
    valley = wide - narrow

    lo, hi = int(span * 0.35), int(span * 0.65)
    window = slice(lo, hi)
    scored = valley[window] * np.clip(persistence[window], 0.0, 1.0)
    index = int(np.argmax(scored)) + lo
    contrast = float(valley[index])
    absolute = (x0 + index) / width
    return round(absolute, 5), round(contrast, 2)


def seam_span_of(rgb: np.ndarray, seam_x: float, contrast: float) -> tuple[float, float]:
    """Width of the binding shadow, as the fractions of image width it covers.

    Cutting at the seam with a fixed bleed leaves the shadow on the inner edge
    of both halves, and the generic edge trim cannot take it off: the shadow is
    a gradient, not a uniform band, so it fails the flatness test that protects
    printed ink. Measured on Continue vol.31 page041 the inner columns climb
    184, 199, 210, 218 before reaching the page, and nothing was removed at all.

    Walking out from the seam until the valley response has decayed gives the
    real extent, so each half can be cut outside the shadow instead of through
    it, which also drops the sliver of the facing page that came with it.
    """
    if contrast <= 0:
        return seam_x, seam_x
    gray = luma_of(rgb)
    width = gray.shape[1]
    column = gray.mean(axis=0)

    def blur(size: int) -> np.ndarray:
        size = max(3, size | 1)
        return np.convolve(column, np.ones(size, dtype=np.float32) / size, mode="same")

    valley = blur(int(width * 0.06)) - blur(9)
    centre = int(round(seam_x * width))
    centre = max(1, min(width - 2, centre))
    floor = valley[centre] * 0.2
    cap = int(width * 0.05)

    left = centre
    while left > 0 and centre - left < cap and valley[left - 1] > floor:
        left -= 1
    right = centre
    while right < width - 1 and right - centre < cap and valley[right + 1] > floor:
        right += 1
    return round(left / width, 5), round((right + 1) / width, 5)


def seam_tilt_of(rgb: np.ndarray, seam_x: float, contrast: float,
                 bands: int = 20, window: float = 0.03) -> tuple[float, int]:
    """Fit a line to the seam and return its tilt in degrees, plus bands used.

    A book does not always sit square on the platen, and the gap between two
    facing pages can run several degrees off vertical: on Continue vol.31
    page052 it travels 409px across the page height, so a vertical cut clips the
    right page at the top and the left page at the bottom.

    Each horizontal band is searched only near the global seam, because a whole
    page of column rules and photo edges offers plenty of darker verticals to
    lock onto by mistake. Bands that disagree with the fit are dropped once and
    the line refitted, and a tilt is only reported when enough bands survive.
    """
    gray = luma_of(rgb)
    height, width = gray.shape
    centre, half = seam_x * width, window * width
    lo, hi = max(0, int(centre - half)), min(width, int(centre + half))
    if hi - lo < 8 or contrast <= 0:
        return 0.0, 0

    wide = max(3, int(width * 0.06) | 1)
    narrow = np.ones(9, dtype=np.float32) / 9
    broad = np.ones(wide, dtype=np.float32) / wide
    edges = np.linspace(0, height, bands + 1).astype(int)

    ys, xs = [], []
    for index in range(bands):
        slab = gray[edges[index]:edges[index + 1]]
        if slab.shape[0] < 4:
            continue
        column = slab.mean(axis=0)
        # Same polarity as `gutter_of`: the seam is a dark trough, so the wide
        # blur sits above the narrow one there. Measured on these scans the seam
        # column reads 107-114 against a page median of 194-225, and the bright
        # page gap beside it scores less than half as strongly.
        response = (np.convolve(column, broad, mode="same")
                    - np.convolve(column, narrow, mode="same"))[lo:hi]
        best = int(np.argmax(response))
        if float(response[best]) <= contrast * 0.35:
            continue
        ys.append((edges[index] + edges[index + 1]) / 2.0)
        xs.append(best + lo)
    if len(ys) < 8:
        return 0.0, len(ys)

    ys_arr, xs_arr = np.array(ys), np.array(xs, dtype=np.float32)
    slope, intercept = np.polyfit(ys_arr, xs_arr, 1)
    residual = np.abs(xs_arr - (slope * ys_arr + intercept))
    keep = residual <= max(2.5 * float(np.median(residual)), 2.0)
    if keep.sum() >= 8:
        ys_arr, xs_arr = ys_arr[keep], xs_arr[keep]
        slope, intercept = np.polyfit(ys_arr, xs_arr, 1)

    tilt = float(np.degrees(np.arctan(slope)))
    if abs(tilt) > MAX_SEAM_TILT_DEG:
        return 0.0, int(len(ys_arr))       # implausible for a bound page
    return round(tilt, 3), int(len(ys_arr))


def skew_of(rgb: np.ndarray) -> float | None:
    """Median tilt of near-horizontal edges, in degrees."""
    if cv2 is None:
        return None
    gray = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLines(edges, 1, np.pi / 1440, threshold=160)
    if lines is None:
        return None
    angles = [
        float(np.degrees(entry[0][1]) - 90.0)
        for entry in lines[:200]
        if abs(np.degrees(entry[0][1]) - 90.0) <= 6
    ]
    return round(float(np.median(angles)), 3) if angles else None


def tone_reference_of(rgb: np.ndarray) -> tuple[list[float], float, float, float, bool]:
    """Estimate a neutral white reference, darkest ink, and colour cast.

    The brightest pixels are not necessarily paper: on the Aoi Yu photo pages
    the cyan backdrop occupies most of the upper histogram. Treating it as
    paper made the tone pass nearly invisible and reinforced the cast. Prefer
    bright *low-chroma* pixels (paper, white type, clothing, page edges).  When
    no trustworthy neutral exists, return a neutral scalar estimate and mark
    it unreliable.  A caller may still use its luminance for classification,
    but must not perform per-channel white balance from a coloured highlight.
    """
    gray = luma_of(rgb)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    bright_cut = float(np.percentile(gray, 65))
    neutral = rgb[(gray >= bright_cut) & (chroma <= 24.0)]
    minimum = max(64, round(gray.size * 0.002))
    if len(neutral) >= minimum:
        paper = np.percentile(neutral, 90, axis=0)
        reliable = True
    else:
        # A yellow illustration can have RGB 246/231/65 at the top of its
        # histogram.  Treating that as paper sends the blue channel through a
        # radically different curve and destroys the artwork.  Preserve hue by
        # exposing only a neutral luminance estimate to the rest of the pass.
        level = float(np.percentile(gray, 95))
        paper = np.array([level, level, level], dtype=np.float32)
        reliable = False
    paper_luma = float(paper @ np.array([0.299, 0.587, 0.114], dtype=np.float32))
    black = float(np.percentile(gray, 2))
    cast = float(paper.max() - paper.min())
    return ([round(float(v), 2) for v in paper], round(paper_luma, 2),
            round(black, 2), round(cast, 2), reliable)


def tone_of(rgb: np.ndarray) -> tuple[list[float], float, float, float]:
    """Compatibility wrapper for callers that only need tone measurements."""
    return tone_reference_of(rgb)[:4]


def _local_stats(gray: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    window = max(3, window | 1)
    mean = cv2.boxFilter(gray, cv2.CV_32F, (window, window))
    squared = cv2.boxFilter(gray * gray, cv2.CV_32F, (window, window))
    return mean, np.sqrt(np.maximum(squared - mean * mean, 0.0))


def binarize_variants(gray: np.ndarray) -> dict[str, np.ndarray]:
    """Several thresholds of the same page, each True where the page is.

    No single threshold survives this corpus: a yellow spread, a full-bleed
    photograph and a white text page each defeat a different one. ScanTailor
    answers that by running peak, Otsu, Mokji, Sauvola and Wolf and keeping
    whichever result best matches the page size it expects, so the choice is
    made by evidence instead of by a constant. The same idea is used here with
    the thresholds that are cheap to compute.
    """
    u8 = np.clip(gray, 0, 255).astype(np.uint8)
    window = max(15, (min(gray.shape) // 8) | 1)
    mean, std = _local_stats(gray, window)
    variants: dict[str, np.ndarray] = {}

    _, otsu = cv2.threshold(u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants["otsu"] = otsu > 0

    # Sauvola: a local threshold that tolerates uneven illumination.
    variants["sauvola"] = gray > mean * (1.0 + 0.2 * (std / 128.0 - 1.0))

    # Wolf: Sauvola anchored to the darkest ink, which suits low-contrast scans.
    darkest, spread = float(gray.min()), float(std.max()) or 1.0
    variants["wolf"] = gray > (mean - 0.5 * (1.0 - std / spread) * (mean - darkest))

    # A plain percentile split, the one that copes with a full-bleed page whose
    # "paper" is a photograph rather than white.
    variants["percentile"] = gray > float(np.percentile(gray, 35))
    return variants


def page_box_from_mask(mask: np.ndarray, min_page: float = 0.5,
                       limit: float = 0.2) -> list[float] | None:
    """Scan inward from each side to where the page reliably begins.

    On a binary image the platen and the book block read as not-page and the
    sheet reads as page, so the boundary is a clean transition instead of the
    ambiguous brightness ramp it is in greyscale.
    """
    height, width = mask.shape
    rows, cols = mask.mean(axis=1), mask.mean(axis=0)

    def first_page_line(profile: np.ndarray, cap: int) -> int:
        """Where the page's own plateau starts, not merely where it looks bright.

        Taking the first line above a fixed level stops at the rim, because the
        top sheet of the book block catches the light: on Continue vol.31
        page041 the outermost columns binarise at 0.79 and 0.89 before the block
        itself dips to 0.28 and the page settles at a steady 0.93. So the page
        begins at the first line from which the profile *stays* near its own
        plateau, which is the same idea as ScanTailor pushing a corner inward
        until it reaches white and holds.
        """
        span = len(profile)
        plateau = float(np.median(profile[int(span * 0.25):int(span * 0.75)]))
        if plateau <= 0.05:
            return 0
        floor = max(min_page, plateau * 0.85)
        hold = max(3, int(span * 0.02))
        for index in range(min(cap, span - hold)):
            if profile[index] >= floor and (profile[index:index + hold] >= floor).all():
                return index
        return 0

    top = first_page_line(rows, int(height * limit))
    bottom = first_page_line(rows[::-1], int(height * limit))
    left = first_page_line(cols, int(width * limit))
    right = first_page_line(cols[::-1], int(width * limit))
    if width - left - right < width * 0.4 or height - top - bottom < height * 0.4:
        return None
    return [round(left / width, 5), round(top / height, 5),
            round((width - right) / width, 5), round((height - bottom) / height, 5)]


def page_box_candidates(rgb: np.ndarray) -> dict[str, list[float]]:
    if cv2 is None:
        return {}
    gray = luma_of(rgb)
    found = {}
    for name, mask in binarize_variants(gray).items():
        box = page_box_from_mask(mask)
        if box is not None:
            found[name] = box
    return found


def choose_page_box(candidates: dict[str, list[float]],
                    expected: tuple[float, float] | None) -> list[float] | None:
    """Pick the candidate closest to the size this title's pages actually are.

    Every scan in a folder came off the same platen at the same setting, so the
    page occupies nearly the same fraction of every frame. That prior is what
    makes the choice safe: a candidate pulled inside the page by a photo card,
    which is how the greyscale attempt failed on 金银攻略 4.png, is simply the
    wrong size and loses.
    """
    if not candidates:
        return None
    if expected is None:
        widths = sorted(box[2] - box[0] for box in candidates.values())
        heights = sorted(box[3] - box[1] for box in candidates.values())
        expected = (widths[len(widths) // 2], heights[len(heights) // 2])

    def error(box: list[float]) -> float:
        return (abs((box[2] - box[0]) - expected[0]) / max(expected[0], 1e-6)
                + abs((box[3] - box[1]) - expected[1]) / max(expected[1], 1e-6))

    best = min(candidates.values(), key=error)
    width_error = abs((best[2] - best[0]) - expected[0]) / max(expected[0], 1e-6)
    height_error = abs((best[3] - best[1]) - expected[1]) / max(expected[1], 1e-6)
    # A summed 15% error is too forgiving: page040's 93.9% wide candidate
    # differed by only 5.3% on one axis and was actually an internal layout
    # edge.  The scanner geometry is stable per folder, so either axis moving
    # more than 3.5% is enough to reject the candidate.
    return best if max(width_error, height_error) <= 0.035 else None


def consensus_page_size(measurements: list[Measurement]) -> dict[bool, tuple[float, float]]:
    """Median page size per layout, so spreads and single pages vote separately."""
    buckets: dict[bool, list[tuple[float, float]]] = {True: [], False: []}
    for item in measurements:
        for box in item.page_boxes.values():
            buckets[item.aspect >= SPREAD_ASPECT].append((box[2] - box[0], box[3] - box[1]))
    result = {}
    for is_spread, sizes in buckets.items():
        if len(sizes) >= 3:
            widths = sorted(size[0] for size in sizes)
            heights = sorted(size[1] for size in sizes)
            result[is_spread] = (widths[len(widths) // 2], heights[len(heights) // 2])
    return result


def measure(path: Path) -> Measurement:
    rgb, full = working_copy(path)
    box = content_box_of(rgb)
    gutter, contrast = gutter_of(rgb, box)
    paper, paper_luma, black, cast = tone_of(rgb)
    aspect = full[0] / full[1]
    if aspect >= SPREAD_ASPECT:
        tilt, bands = seam_tilt_of(rgb, gutter, contrast)
        span = seam_span_of(rgb, gutter, contrast)
    else:
        tilt, bands, span = 0.0, 0, (gutter, gutter)
    outer = outer_page_edges(rgb)
    boxes = page_box_candidates(rgb)
    return Measurement(
        width=full[0], height=full[1], aspect=round(aspect, 4),
        content_box=box,
        gutter_x=gutter if aspect >= SPREAD_ASPECT else None,
        gutter_contrast=contrast,
        seam_span=list(span),
        outer_edges=list(outer),
        page_boxes=boxes,
        skew_deg=skew_of(rgb),
        seam_tilt=tilt, seam_bands=bands,
        paper_rgb=paper, paper_luma=paper_luma, black_point=black, colour_cast=cast,
    )


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #

@dataclass
class Decision:
    kind: str                  # single | spread | art | unknown
    split: bool
    tone_policy: str           # paper | preserve
    decided_by: str            # cv | vlm | vlm-failed
    confidence: float
    reason: str


VLM_PROMPT = """You are preparing scanned magazine pages for an archive.

Answer with STRICT JSON only. No prose, no code fences.

{
  "kind": "spread" | "single" | "foldout" | "art",
  "split_advised": true | false,
  "confidence": <0..1>,
  "reason": "<one short sentence>"
}

- "spread": two facing pages photographed together, separated by a binding seam.
  Facing page numbers in the outer corners are the strongest evidence.
- "single": one printed page.
- "foldout": one continuous layout or illustration that merely happens to be wide.
- "art": a page whose printed area is a full-bleed photograph or illustration
  rather than text on paper.
- split_advised: true only for "spread". Never true when cutting the image in two
  would run through one continuous picture or headline.

Do not report coordinates. Position is measured separately and your numbers are
not used.
"""


def ask_model(path: Path, model: str, timeout: int) -> dict:
    api_url = (os.getenv("VLM_OCR_API_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
    api_key = os.getenv("VLM_OCR_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if not api_key:
        raise RuntimeError("set VLM_OCR_API_KEY or DASHSCOPE_API_KEY to classify pages")
    with Image.open(path) as opened:
        image = upright_image(opened)
        scale = 1024 / max(image.size)
        if scale < 1:
            image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
    url = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": url}},
            {"type": "text", "text": VLM_PROMPT},
        ]}],
        "temperature": 0,
        "max_tokens": 400,
    }
    request = urllib.request.Request(
        f"{api_url}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = payload["choices"][0]["message"]["content"].strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def tone_policy_for(kind: str, measurement: Measurement) -> str:
    """Only normalise pages whose highlights really are paper, and only when it helps.

    A full-bleed illustration has no paper white to align, and stretching it to
    one would rewrite the artwork's colours.

    A page that already has clean blacks, neutral paper and full white is left
    alone as well. The transform would be near-identity, but it still rewrites
    every pixel, which forces a full re-encode and denies the size guard its
    chance to keep the smaller original. On DREAM 2008.12, whose blacks already
    sit at 1-15 and whose paper is often exactly 255, normalising everything
    turned 59MB of source into 114MB of archive.
    """
    if kind == "art" or measurement.paper_luma < PAPER_LUMA_DARK:
        return "preserve"
    if (measurement.black_point <= TONE_BLACK_OK
            and measurement.colour_cast <= TONE_CAST_OK
            and measurement.paper_luma >= TONE_PAPER_OK):
        return "already-clean"
    return "paper"


def classify(path: Path, measurement: Measurement, mode: str, model: str, timeout: int) -> Decision:
    portrait = measurement.aspect < SPREAD_ASPECT
    confident_seam = measurement.gutter_contrast >= GUTTER_CONFIDENT

    if mode == "never" or (mode == "auto" and portrait and measurement.paper_luma >= PAPER_LUMA_CLEAR):
        kind = "single" if portrait else ("spread" if confident_seam else "unknown")
        return Decision(
            kind=kind,
            split=not portrait and confident_seam,
            tone_policy=tone_policy_for(kind, measurement),
            decided_by="cv",
            confidence=(0.9 if portrait else min(
                0.95,
                0.65 + max(0.0, measurement.gutter_contrast - GUTTER_CONFIDENT) / 100,
            )),
            reason=(
                "portrait page with paper highlights" if portrait
                else f"seam contrast {measurement.gutter_contrast}"
            ),
        )

    try:
        answer = ask_model(path, model, timeout)
    except Exception as exc:
        kind = "single" if portrait else "unknown"
        return Decision(
            kind=kind, split=False, tone_policy=tone_policy_for(kind, measurement),
            decided_by="vlm-failed", confidence=0.0,
            reason=f"{type(exc).__name__}: {str(exc)[:120]}",
        )

    kind = str(answer.get("kind") or "unknown")
    split = bool(answer.get("split_advised")) and kind == "spread" and not portrait
    if split and not confident_seam:
        # The model says two pages but the projection found no seam to cut on.
        split = False
        kind = "unknown"
    return Decision(
        kind=kind, split=split, tone_policy=tone_policy_for(kind, measurement),
        decided_by="vlm", confidence=float(answer.get("confidence") or 0.0),
        reason=str(answer.get("reason") or "")[:160],
    )


# --------------------------------------------------------------------------- #
# Processing
# --------------------------------------------------------------------------- #

def straighten_seam(image: Image.Image, tilt: float,
                    fill: tuple[int, int, int]) -> tuple[Image.Image, float, float]:
    """Rotate a spread until its binding runs vertically, then re-locate it.

    Turning the page before cutting costs one resample and makes the slanted
    seam a plain vertical crop, which keeps every later step working on
    rectangles. As in `deskew`, the sign convention is not trusted: both
    directions are measured and the rotation is kept only if the seam ends up
    straighter than it started.
    """
    if abs(tilt) < MIN_SEAM_TILT_DEG:
        return image, 0.0, 0.0
    for candidate in (tilt, -tilt):
        rotated = image.rotate(candidate, resample=Image.BICUBIC, expand=True, fillcolor=fill)
        preview = rotated.resize(
            (WORK_WIDTH, max(1, round(rotated.height * WORK_WIDTH / rotated.width))), Image.BILINEAR)
        array = np.asarray(preview, dtype=np.float32)
        seam, contrast = gutter_of(array, [0.0, 0.0, 1.0, 1.0])
        after, bands = seam_tilt_of(array, seam, contrast)
        if bands >= 8 and abs(after) < abs(tilt) - 0.2:
            return rotated, candidate, seam
    return image, 0.0, 0.0


def split_at(image: Image.Image, span: tuple[float, float], binding: str) -> list[tuple[str, Image.Image]]:
    """Cut a spread into two pages, named in reading order.

    Japanese magazines bind on the right, so the right half carries the earlier
    page and becomes "a"; a left-bound title reverses that. `span` is the
    measured extent of the binding shadow, so each page is cut outside it rather
    than through it and neither half keeps the shadow or a strip of its
    neighbour.
    """
    start, end = span
    cut_left = max(0, min(image.width, round(start * image.width)))
    cut_right = max(cut_left, min(image.width, round(end * image.width)))
    right = image.crop((cut_right, 0, image.width, image.height))
    left = image.crop((0, 0, cut_left, image.height))
    return [("a", right), ("b", left)] if binding == "right" else [("a", left), ("b", right)]


def crop_content(image: Image.Image, box: list[float], margin: float = 0.004) -> Image.Image:
    if box == [0.0, 0.0, 1.0, 1.0]:
        return image
    width, height = image.size
    pad_x, pad_y = margin * width, margin * height
    return image.crop((
        max(0, round(box[0] * width - pad_x)), max(0, round(box[1] * height - pad_y)),
        min(width, round(box[2] * width + pad_x)), min(height, round(box[3] * height + pad_y)),
    ))


def outer_page_edges(rgb: np.ndarray, zone: float = 0.12,
                     min_step: float = 40.0) -> tuple[float, float]:
    """Fractions of width the book block covers at each outer edge of a spread.

    Beyond the printed page a scan often shows the book block, the stack of page
    edges of everything still closed. It cannot be found by consuming dark
    columns from the rim: on Continue vol.31 page041 the outer columns read 211,
    213, 206, 190, 158, 150 before jumping to the page at 220, so the rim itself
    is as bright as paper and the dark part sits further in.

    What is reliable is the step where the page begins, and its direction is not
    fixed. That same edge steps up 150 to 220, while page050 steps *down* 208 to
    130 into a dark page. Both are large; a scan without a visible block, such
    as catelog, drifts 181, 180, 178, 175 with no step at all. So the largest
    step in the outer zone is taken only when it clearly beats the page's own
    texture, and otherwise nothing is trimmed rather than guessing.
    """
    gray = luma_of(rgb)
    width = gray.shape[1]
    column = gray.mean(axis=0)
    span = max(12, int(width * zone))
    reach = max(4, span // 6)          # a page edge is a step across several columns

    col_std = gray.std(axis=0)
    paper = float(np.percentile(gray, 85))

    def edge_at(side: str) -> float:
        window = column[:span + reach] if side == "left" else column[-(span + reach):][::-1]
        spreads = col_std[:span + reach] if side == "left" else col_std[-(span + reach):][::-1]
        best, best_step = 0, 0.0
        for index in range(reach, span):
            step = abs(float(window[index:index + reach].mean())
                       - float(window[index - reach:index].mean()))
            if step > best_step:
                best, best_step = index, step
        if best_step < min_step:
            return 0.0
        # The strongest step in the margin is not always the page edge. On
        # 金银攻略 4.png the leading photo card outscored the block and the cut
        # landed 288px inside the page. What separates the two is that a page's
        # own margin is clean paper, while a book block never is, so a candidate
        # is dropped when everything outside it still looks like paper.
        outer_mean = float(window[:best].mean())
        outer_std = float(spreads[:best].mean())
        if outer_mean >= paper * 0.9 and outer_std < 25.0:
            return 0.0
        return best / width

    return round(edge_at("left"), 5), round(edge_at("right"), 5)


def resolve_outer_trim(setting: str, measurement: Measurement,
                       expected: tuple[float, float] | None = None) -> tuple[float, float]:
    """Turn the --outer-trim setting into fractions of width for each outer side.

    Detection is offered but not trusted by default. Across the pilot folders it
    found the page edge on Continue vol.31 page041 and one side of page050, was
    talked into cutting 288px inside the page by a photo card on 金银攻略 4.png,
    and correctly reported nothing for catelog and fossil, which have no visible
    block. Because the scanner setup is fixed within a folder, one calibrated
    number is both safer and less work than a detector that is right most of the
    time.
    """
    value = str(setting or "off").strip().lower()
    if value in ("", "off", "none", "0"):
        return 0.0, 0.0
    if value == "auto":
        # Prefer the binarised page box: it is chosen against the size the rest
        # of the folder agrees on, which is what finally stopped a photo card on
        # 金银攻略 4.png from pulling the cut 351px inside the page.
        box = choose_page_box(measurement.page_boxes, expected)
        if box is not None:
            return round(box[0], 5), round(1.0 - box[2], 5)
        return tuple(measurement.outer_edges)
    if value.endswith("%"):
        fraction = float(value[:-1]) / 100.0
        return fraction, fraction
    fraction = float(value) / max(measurement.width, 1)
    return fraction, fraction


def trim_outer(image: Image.Image, edges: tuple[float, float]) -> tuple[Image.Image, tuple[int, int]]:
    """Crop the measured book block off the two outer sides of a spread."""
    left = min(round(edges[0] * image.width), image.width // 8)
    right = min(round(edges[1] * image.width), image.width // 8)
    if not (left or right):
        return image, (0, 0)
    return image.crop((left, 0, image.width - right, image.height)), (left, right)


def trim_dark_edges(image: Image.Image, paper_luma: float, limit: float = 0.09) -> Image.Image:
    """Shave the binding shadow and scanner borders off each side.

    Splitting a spread leaves the gutter shadow on the inner edge of both
    halves, and these scans often carry a dark strip along the outside where the
    book block or the scanner bed shows.

    Darkness alone is not enough to identify them. DREAM 2008.12 page011 opens
    with a full-width black masthead, and trimming on brightness took the whole
    8% allowance out of the top of the page. A scanner edge is dark *and*
    featureless, while printed ink carries type and artwork, so a line is only
    eaten when it is both below the paper threshold and nearly uniform.
    """
    array = np.asarray(image.convert("RGB"), dtype=np.float32)
    gray = luma_of(array)
    height, width = gray.shape
    threshold = max(40.0, paper_luma * 0.72)

    def eat(means: np.ndarray, cap: int) -> int:
        """Length of a dark band that visibly ends before the allowance runs out.

        Only a band that stops is treated as an edge. A run still dark when the
        allowance is exhausted is far more likely to be the page itself, so
        nothing is taken and the page keeps whatever it is.
        """
        count = 0
        while count < cap and means[count] < threshold:
            count += 1
        return count if count < cap else 0

    col_mean = gray.mean(axis=0)
    row_mean = gray.mean(axis=1)
    left = eat(col_mean, int(width * limit))
    right = eat(col_mean[::-1], int(width * limit))
    top = eat(row_mean, int(height * limit))
    bottom = eat(row_mean[::-1], int(height * limit))
    if not (left or right or top or bottom):
        return image
    return image.crop((left, top, width - right, height - bottom))


def trim_scanner_frame(image: Image.Image, limit: float = 0.06,
                       min_step: float = 9.0) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Crop the scanner bed or book block around a rectangular printed page.

    `trim_dark_edges` intentionally only removes bands that are uniformly dark.
    Real scans also have a mid-grey platen, pale page stacks, and graded shadows.
    Those are better identified by the first sustained luminance *step* where
    the physical sheet begins. Median row/column profiles ignore most text and
    photographs.  The search is restricted to the outer 6%, and no automatic
    cut may consume more than 5% of a side: a larger candidate is more likely a
    masthead or a layout edge and must be left for review.

    The returned tuple is left, top, right, bottom pixels removed.
    """
    original_width, original_height = image.size
    scale = min(1.0, WORK_WIDTH / max(original_width, original_height))
    if scale < 1.0:
        preview = image.resize(
            (max(1, round(original_width * scale)), max(1, round(original_height * scale))),
            Image.BILINEAR,
        )
    else:
        preview = image
    preview_rgb = np.asarray(preview.convert("RGB"), dtype=np.float32)
    gray = luma_of(preview_rgb)

    def boundary(profile: np.ndarray, colours: np.ndarray) -> int:
        length = len(profile)
        cap = max(8, min(length // 4, round(length * limit)))
        bridge = max(2, round(length * 0.004))
        blur = max(3, round(length * 0.006) | 1)
        pad = blur // 2
        smooth = np.convolve(
            np.pad(profile, (pad, pad), mode="edge"),
            np.ones(blur, dtype=np.float32) / blur,
            mode="valid",
        )
        response = np.abs(smooth[bridge:] - smooth[:-bridge])
        lo = 1
        hi = max(lo + 1, min(cap, len(response)))
        # The strongest edge is often not the sheet edge.  On pokepia page019
        # the grey platen ended around 1% from the side, but the cover headline
        # at 6% produced the largest response and ate visible lettering.  Walk
        # in from the rim and take the first sustained response cluster.
        candidates = np.flatnonzero(response[lo:hi] >= min_step) + lo
        if not len(candidates):
            return 0
        runs = np.split(candidates, np.where(np.diff(candidates) > 1)[0] + 1)
        run = next((part for part in runs if len(part) >= 2), None)
        if run is None:
            return 0
        index = int(run[np.argmax(response[run])])
        step = float(response[index])
        outside = profile[max(0, index - bridge * 3):index]
        inside = profile[index + bridge:index + bridge * 4]
        contrast = (abs(float(np.median(inside)) - float(np.median(outside)))
                    if len(outside) and len(inside) else 0.0)
        if max(step, contrast) < min_step:
            return 0
        if (index + bridge) / length > 0.05:
            return 0
        # Scanner platens and page-stack shadows are neutral.  A coloured strip
        # at the rim is normally printed design: pokepia page063 has a yellow
        # frame whose inner edge looked exactly like a paper boundary in luma,
        # and cropping it removed the first interview column.
        outside_colours = colours[:max(index, 1)]
        outside_colour = np.median(outside_colours, axis=0)
        if float(outside_colour.max() - outside_colour.min()) > 28.0:
            return 0
        # Land just inside the sheet rather than on the anti-aliased boundary.
        return min(cap, index + bridge)

    row_colours = np.median(preview_rgb, axis=1)
    column_colours = np.median(preview_rgb, axis=0)
    top_small = boundary(np.median(gray, axis=1), row_colours)
    bottom_small = boundary(np.median(gray, axis=1)[::-1], row_colours[::-1])
    left_small = boundary(np.median(gray, axis=0), column_colours)
    right_small = boundary(np.median(gray, axis=0)[::-1], column_colours[::-1])

    inverse = 1.0 / scale
    left = round(left_small * inverse)
    top = round(top_small * inverse)
    right = round(right_small * inverse)
    bottom = round(bottom_small * inverse)
    # The detected step sits on an anti-aliased physical edge. Move a few
    # pixels further inward on detected sides so a one-pixel platen hairline
    # does not survive in the OCR derivative.
    safety_x = max(1, round(original_width * 0.0015))
    safety_y = max(1, round(original_height * 0.0015))
    if left:
        left += safety_x
    if right:
        right += safety_x
    if top:
        top += safety_y
    if bottom:
        bottom += safety_y
    if original_width - left - right < original_width * 0.72:
        left = right = 0
    if original_height - top - bottom < original_height * 0.72:
        top = bottom = 0
    if not (left or top or right or bottom):
        return image, (0, 0, 0, 0)
    return image.crop((left, top, original_width - right, original_height - bottom)), (left, top, right, bottom)


def deskew(image: Image.Image, angle: float | None, fill: tuple[int, int, int]) -> tuple[Image.Image, float]:
    """Straighten the page, keeping the result only if it measurably improved.

    Rotation direction depends on how the angle was derived, so rather than
    trusting a sign convention the result is re-measured and discarded when it
    is not flatter than the input.
    """
    if angle is None or abs(angle) < MIN_DESKEW_DEG:
        return image, 0.0
    for candidate in (-angle, angle):
        rotated = image.rotate(candidate, resample=Image.BICUBIC, expand=True, fillcolor=fill)
        # Re-measure on the middle of the page. `expand` leaves wedges of fill in
        # the corners whose edges lie at exactly the rotation angle, and Hough
        # scores them so strongly that a rotation the wrong way still reported a
        # flat page: DREAM 2008.12 page011 came out visibly more crooked than it
        # went in while the check reported 0.00 degrees.
        inset = rotated.crop((round(rotated.width * 0.12), round(rotated.height * 0.12),
                              round(rotated.width * 0.88), round(rotated.height * 0.88)))
        preview = inset.resize(
            (WORK_WIDTH, max(1, round(inset.height * WORK_WIDTH / inset.width))), Image.BILINEAR)
        after = skew_of(np.asarray(preview, dtype=np.float32))
        if after is not None and abs(after) <= abs(angle) * 0.5:
            return rotated, candidate
    return image, 0.0


def normalise_tone(image: Image.Image, black_point: float, paper_rgb: list[float],
                   target_black: float = 6.0) -> Image.Image:
    """Pull each channel's paper value to white and its darkest ink down.

    Doing it per channel removes the yellow cast of aged paper in the same pass
    that restores contrast, which matters here because measured black points sat
    as high as 120 of 255 on some sets.
    """
    array = np.asarray(image, dtype=np.float32)
    output = np.empty_like(array)
    for channel in range(3):
        white = max(paper_rgb[channel], black_point + 1.0)
        scale = (255.0 - target_black) / (white - black_point)
        output[..., channel] = (array[..., channel] - black_point) * scale + target_black
    return Image.fromarray(np.clip(output, 0, 255).astype(np.uint8), "RGB")


def encode(image: Image.Image, destination: Path, quality: int, long_edge: int | None,
           budget_bytes: int | None) -> dict:
    """Write one derivative, never spending more bytes than the source did.

    A fixed quality assumes the source was encoded at a comparable one. These
    scans are not: DREAM 2008.12 pages carry about 0.5 bits per pixel, so
    encoding them at 88 targets a bitrate the original never had and mostly
    preserves its compression artefacts, doubling the file. When a budget is
    given the quality steps down until the result fits, and if even the floor
    cannot fit, the caller is told so it can keep the original bytes instead.
    """
    working = image
    if long_edge and max(image.size) > long_edge:
        scale = long_edge / max(image.size)
        working = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)

    subsampling = 0 if long_edge is None else 2
    attempts = [quality]
    if budget_bytes:
        attempts += [step for step in (82, 76, 70) if step < quality]

    data, used = b"", quality
    for candidate in attempts:
        buffer = io.BytesIO()
        working.save(buffer, format="JPEG", quality=candidate,
                     subsampling=subsampling, optimize=True, progressive=True)
        data, used = buffer.getvalue(), candidate
        if not budget_bytes or len(data) <= budget_bytes:
            break

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {
        "path": destination.name,
        "bytes": len(data),
        "size": list(working.size),
        "quality": used,
        "over_budget": bool(budget_bytes and len(data) > budget_bytes),
    }


# --------------------------------------------------------------------------- #

@dataclass
class PageResult:
    source: str
    source_bytes: int
    measurement: dict
    decision: dict
    outputs: list[dict] = field(default_factory=list)
    deskewed_by: float = 0.0
    seam_straightened_by: float = 0.0
    outer_trimmed: list[int] = field(default_factory=lambda: [0, 0])
    page_trims: list[dict] = field(default_factory=list)
    tone_applied: bool = False
    source_orientation: int | None = None
    orientation_normalized: bool = False
    orientation_transform: str = "none"
    workflow_status: str = "ready"
    review_reasons: list[str] = field(default_factory=list)
    note: str = ""


def review_reasons_for(result: PageResult) -> list[str]:
    """Return page-level gates before a prepared page moves on to OCR.

    This is deliberately conservative: preprocessing may propose a split or a
    colour repair, but an uncertain wide page must remain visible to a person
    instead of silently becoming OCR input.
    """
    decision = result.decision
    measurement = result.measurement
    reasons = []
    if decision.get("kind") == "unknown":
        reasons.append("page_kind_uncertain")
    if decision.get("decided_by") == "vlm-failed":
        reasons.append("page_model_failed")
    if float(decision.get("confidence") or 0) < 0.65:
        reasons.append("page_confidence_low")
    if (float(measurement.get("aspect") or 0) >= SPREAD_ASPECT
            and not decision.get("split")
            and decision.get("kind") not in {"art", "foldout"}):
        reasons.append("wide_page_not_split")
    if (abs(float(measurement.get("seam_tilt") or 0)) >= MIN_SEAM_TILT_DEG
            and decision.get("split") and not result.seam_straightened_by):
        reasons.append("seam_tilt_unresolved")
    if (any(float(value or 0) > 0 for value in measurement.get("outer_edges") or [])
            and not any(result.outer_trimmed)
            and not any(any(trim.get("removed") or []) for trim in result.page_trims)):
        reasons.append("outer_edge_detected_not_trimmed")
    return list(dict.fromkeys(reasons))


def process(path: Path, out_dir: Path, args, source_root: Path | None = None,
            measurement: Measurement | None = None,
            expected: tuple[float, float] | None = None) -> PageResult:
    with Image.open(path) as source_probe:
        source_orientation = source_probe.getexif().get(274)
    orientation_names = {
        2: "mirror-horizontal", 3: "rotate-180", 4: "mirror-vertical",
        5: "transpose", 6: "rotate-90-cw", 7: "transverse", 8: "rotate-270-cw",
    }
    measurement = measurement or measure(path)
    decision = classify(path, measurement, args.vlm, args.model, args.timeout)
    source_root = source_root or path.parent
    try:
        source_relative = path.relative_to(source_root)
    except ValueError:
        source_relative = Path(path.name)
    result = PageResult(
        source=source_relative.as_posix(), source_bytes=path.stat().st_size,
        measurement=asdict(measurement), decision=asdict(decision),
        source_orientation=source_orientation,
        orientation_normalized=source_orientation in orientation_names,
        orientation_transform=orientation_names.get(source_orientation, "none"),
    )
    if args.dry_run:
        result.review_reasons = review_reasons_for(result)
        result.workflow_status = "review" if result.review_reasons else "ready"
        return result

    with Image.open(path) as opened:
        full = upright_image(opened)
        fill = tuple(int(round(v)) for v in measurement.paper_rgb)
        outer = resolve_outer_trim(args.outer_trim, measurement, expected)
        if outer != (0.0, 0.0):
            full, removed = trim_outer(full, outer)
            result.outer_trimmed = list(removed)
        seam = measurement.gutter_x
        span = tuple(measurement.seam_span)
        if any(result.outer_trimmed) and decision.split:
            # Every horizontal fraction moved, so find the seam again rather
            # than trying to rescale the old one.
            small = np.asarray(full.resize(
                (WORK_WIDTH, max(1, round(full.height * WORK_WIDTH / full.width))),
                Image.BILINEAR), dtype=np.float32)
            seam, contrast = gutter_of(small, [0.0, 0.0, 1.0, 1.0])
            span = seam_span_of(small, seam, contrast)
        if decision.split and seam and not args.no_straighten:
            full, turned, moved = straighten_seam(full, measurement.seam_tilt, fill)
            if turned:
                half = (span[1] - span[0]) / 2
                seam, span = moved, (moved - half, moved + half)
                result.seam_straightened_by = round(turned, 3)
        pieces = (split_at(full, span, args.binding)
                  if decision.split and seam else [("", full)])
        # The binarised page box, chosen against the folder's agreed size, is a
        # useful first boundary, but it is not a replacement for scanner-frame
        # cleanup.  A binary mask can stop at a printed colour panel and leave
        # the real grey platen behind, so every single-page crop still passes
        # through the neutral-frame and dark-edge safety checks below.
        single_box = None
        if not decision.split:
            single_box = choose_page_box(measurement.page_boxes, expected)
        for suffix, piece in pieces:
            frame_removed = (0, 0, 0, 0)
            if single_box is not None:
                piece = crop_content(piece, single_box)
                trim_basis = piece.size
                piece, frame_removed = trim_scanner_frame(piece)
                piece = trim_dark_edges(piece, measurement.paper_luma)
            else:
                piece = crop_content(piece, measurement.content_box if not suffix else [0.0, 0.0, 1.0, 1.0])
                trim_basis = piece.size
                piece, frame_removed = trim_scanner_frame(piece)
                piece = trim_dark_edges(piece, measurement.paper_luma)
            piece, rotated = deskew(piece, measurement.skew_deg, fill)
            if rotated:
                rotated_piece = piece
                trimmed_piece, after_rotation = trim_scanner_frame(rotated_piece)
                combined = tuple(a + b for a, b in zip(frame_removed, after_rotation))
                max_x = round(trim_basis[0] * 0.055)
                max_y = round(trim_basis[1] * 0.055)
                if (combined[0] <= max_x and combined[2] <= max_x
                        and combined[1] <= max_y and combined[3] <= max_y):
                    piece = trimmed_piece
                    frame_removed = combined
            result.deskewed_by = rotated
            if decision.tone_policy == "paper" and not args.no_tone:
                preview = piece
                if max(piece.size) > WORK_WIDTH:
                    ratio = WORK_WIDTH / max(piece.size)
                    preview = piece.resize(
                        (round(piece.width * ratio), round(piece.height * ratio)),
                        Image.BILINEAR,
                    )
                piece_paper, piece_luma, piece_black, piece_cast, tone_reliable = tone_reference_of(
                    np.asarray(preview.convert("RGB"), dtype=np.float32)
                )
                if tone_reliable:
                    piece = normalise_tone(piece, piece_black, piece_paper)
                    result.tone_applied = True
            else:
                piece_paper = measurement.paper_rgb
                piece_luma = measurement.paper_luma
                piece_black = measurement.black_point
                piece_cast = measurement.colour_cast
                tone_reliable = decision.tone_policy != "paper"
            result.page_trims.append({
                "piece": suffix or "single",
                "removed": list(frame_removed),
                "tone_reference": {
                    "white_rgb": piece_paper,
                    "white_luma": piece_luma,
                    "black_point": piece_black,
                    "colour_cast": piece_cast,
                    "reliable": tone_reliable,
                },
            })
            stem = path.stem + (f"-{suffix}" if suffix else "")
            relative_parent = source_relative.parent
            untouched = (not suffix and not rotated
                         and not result.seam_straightened_by and not result.tone_applied
                         and not result.orientation_normalized
                         and piece.size == (measurement.width, measurement.height))
            # Half a spread should not be measured against the whole source file.
            budget = round(result.source_bytes / len(pieces))

            if "archive" in args.profiles:
                target = out_dir / "archive" / relative_parent / f"{stem}.jpg"
                written = encode(piece, target, args.archive_quality, None, budget)
                if written["over_budget"] and untouched and path.suffix.lower() in {".jpg", ".jpeg"}:
                    # Nothing was changed and every quality overshot: the source
                    # is already the smallest honest version of this page.
                    target.write_bytes(path.read_bytes())
                    written = {"path": target.name, "bytes": result.source_bytes,
                               "size": [measurement.width, measurement.height],
                               "quality": None, "copied_source": True}
                    result.note = "archive copied from source; re-encoding could not beat it"
                written["profile"] = "archive"
                written["relative_path"] = target.relative_to(out_dir).as_posix()
                result.outputs.append(written)
            if "web" in args.profiles:
                target = out_dir / "web" / relative_parent / f"{stem}.jpg"
                written = encode(piece, target, args.web_quality, args.web_long_edge, None)
                written["profile"] = "web"
                written["relative_path"] = target.relative_to(out_dir).as_posix()
                result.outputs.append(written)
    result.review_reasons = review_reasons_for(result)
    result.workflow_status = "review" if result.review_reasons else "ready"
    return result


def discover(source: Path) -> list[Path]:
    return sorted(
        p for p in source.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="Folder of raw scans; searched recursively.")
    parser.add_argument("--out", required=True, help="Destination folder; originals are never touched.")
    parser.add_argument("--vlm", default="auto", choices=["auto", "always", "never"],
                        help="When to ask the model: auto skips clear portrait paper pages.")
    parser.add_argument("--model", default=os.getenv("VLM_PAGE_MODEL", "qwen3-vl-flash"))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--binding", default="right", choices=["right", "left"],
                        help="Right-bound Japanese titles read right page first; left for Western ones.")
    parser.add_argument("--profiles", default="archive,web", help="Comma separated: archive, web.")
    parser.add_argument("--archive-quality", type=int, default=88)
    parser.add_argument("--web-quality", type=int, default=82)
    parser.add_argument("--web-long-edge", type=int, default=2048)
    parser.add_argument("--no-tone", action="store_true", help="Skip colour normalisation entirely.")
    parser.add_argument("--outer-trim", default="off",
                        help="Book block removal: 'off' (default), 'auto' to use the measured "
                             "page edge where one is found, or a pixel count applied to both "
                             "outer sides. Detection is unreliable across titles, so a folder is "
                             "best calibrated once from the outer_edges values in the manifest.")
    parser.add_argument("--no-straighten", action="store_true",
                        help="Always cut spreads on a vertical line, ignoring seam tilt.")
    parser.add_argument("--limit", type=int, default=0, help="Process at most this many pages.")
    parser.add_argument("--dry-run", action="store_true", help="Measure and classify without writing.")
    args = parser.parse_args()
    args.profiles = {part.strip() for part in args.profiles.split(",") if part.strip()}

    if cv2 is None:
        print("opencv is required for skew and structure analysis; see tools/requirements.txt")
        return 1

    source, out_dir = Path(args.source).resolve(), Path(args.out).resolve()
    if not source.is_dir():
        # Worth separating from an empty folder: these scans live on an external
        # drive that is not always mounted, and a whole batch once reported
        # "no images found" for every title when the volume had simply dropped.
        print(f"source folder is not available: {source}")
        if not source.drive or not Path(source.drive + "/").exists():
            print(f"drive {source.drive or '?'} is not mounted; reconnect it and run again")
        return 2
    files = discover(source)
    if args.limit:
        files = files[: args.limit]
    if not files:
        print(f"{source} exists but holds no images this tool can read")
        return 1
    print(f"{len(files)} images under {source.name}\n")

    # Measure everything before cropping anything. The page box is chosen
    # against the size the rest of the folder agrees on, and a single scan
    # cannot supply that prior.
    measured: dict[Path, Measurement] = {}
    for path in files:
        try:
            measured[path] = measure(path)
        except Exception as exc:
            print(f"      measure failed for {path.name}: {type(exc).__name__}: {str(exc)[:80]}")
    consensus = consensus_page_size(list(measured.values()))
    for is_spread, size in sorted(consensus.items()):
        print(f"page size consensus ({'spread' if is_spread else 'single'}): "
              f"{size[0]:.3f} x {size[1]:.3f} of frame")
    if consensus:
        print()

    results, errors, calls = [], [], 0
    for index, path in enumerate(files, start=1):
        try:
            result = process(path, out_dir, args, source,
                             measurement=measured.get(path),
                             expected=consensus.get(
                                 measured[path].aspect >= SPREAD_ASPECT)
                             if path in measured else None)
        except Exception as exc:
            print(f"{index:>4}/{len(files)}  {path.name[:34]:<34} ERROR {type(exc).__name__}: {str(exc)[:90]}")
            errors.append({
                "source": path.relative_to(source).as_posix(),
                "error_type": type(exc).__name__,
                "message": str(exc)[:500],
            })
            continue
        calls += 1 if result.decision["decided_by"].startswith("vlm") else 0
        results.append(result)
        produced = sum(item["bytes"] for item in result.outputs)
        print(f"{index:>4}/{len(files)}  {path.name[:34]:<34} "
              f"{result.decision['kind']:<8} split={str(result.decision['split']):<5} "
              f"tone={result.decision['tone_policy']:<8} "
              f"{result.source_bytes/1048576:>6.1f}M -> {produced/1048576:>6.1f}M "
              f"({len(result.outputs)} files, {result.decision['decided_by']})")

    if not args.dry_run and (results or errors):
        out_dir.mkdir(parents=True, exist_ok=True)
        review = sum(item.workflow_status == "review" for item in results)
        manifest = {
            "source": str(source),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "settings": {k: (sorted(v) if isinstance(v, set) else v) for k, v in vars(args).items()},
            "summary": {
                "input_count": len(files),
                "processed_count": len(results),
                "error_count": len(errors),
                "ready_count": len(results) - review,
                "review_count": review,
                "split_count": sum(1 for item in results if item.decision["split"]),
                "tone_count": sum(1 for item in results if item.tone_applied),
                "model_call_count": calls,
            },
            "errors": errors,
            "pages": [asdict(item) for item in results],
        }
        (out_dir / "scan-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    original = sum(item.source_bytes for item in results)
    produced = sum(entry["bytes"] for item in results for entry in item.outputs)
    splits = sum(1 for item in results if item.decision["split"])
    toned = sum(1 for item in results if item.tone_applied)
    review = sum(item.workflow_status == "review" for item in results)
    print(f"\n{len(results)} pages | {splits} split | {toned} tone-normalised | "
          f"{review} review | {len(errors)} errors | {calls} model calls")
    if original and not args.dry_run:
        print(f"{original/1048576:.1f} MB in -> {produced/1048576:.1f} MB out "
              f"({100*produced/original:.0f}%), manifest at {out_dir / 'scan-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
