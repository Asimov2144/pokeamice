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
from PIL import Image

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
MIN_DESKEW_DEG = 0.15      # below this, rotating costs more detail than it recovers


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
    skew_deg: float | None
    paper_rgb: list[float]
    paper_luma: float
    black_point: float
    colour_cast: float


def working_copy(path: Path) -> tuple[np.ndarray, tuple[int, int]]:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
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
    index = int(np.argmax(valley[lo:hi])) + lo
    contrast = float(valley[index])
    absolute = (x0 + index) / width
    return round(absolute, 5), round(contrast, 2)


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


def tone_of(rgb: np.ndarray) -> tuple[list[float], float, float, float]:
    """Colour of the page's highlights, its darkest ink, and the colour cast."""
    gray = luma_of(rgb)
    highlight_cut = float(np.percentile(gray, 85))
    highlights = rgb[gray >= highlight_cut]
    paper = highlights.mean(axis=0) if len(highlights) else np.array([255.0, 255.0, 255.0])
    black = float(np.percentile(gray, 2))
    cast = float(paper.max() - paper.min())
    return [round(float(v), 2) for v in paper], round(highlight_cut, 2), round(black, 2), round(cast, 2)


def measure(path: Path) -> Measurement:
    rgb, full = working_copy(path)
    box = content_box_of(rgb)
    gutter, contrast = gutter_of(rgb, box)
    paper, paper_luma, black, cast = tone_of(rgb)
    aspect = full[0] / full[1]
    return Measurement(
        width=full[0], height=full[1], aspect=round(aspect, 4),
        content_box=box,
        gutter_x=gutter if aspect >= SPREAD_ASPECT else None,
        gutter_contrast=contrast,
        skew_deg=skew_of(rgb),
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
        image = opened.convert("RGB")
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
    """Only normalise pages whose highlights really are paper.

    A full-bleed illustration has no paper white to align, and stretching it to
    one would rewrite the artwork's colours.
    """
    if kind == "art" or measurement.paper_luma < PAPER_LUMA_DARK:
        return "preserve"
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
            confidence=0.9 if portrait else min(0.9, measurement.gutter_contrast / 100),
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

def split_at(image: Image.Image, gutter_x: float, binding: str) -> list[tuple[str, Image.Image]]:
    """Cut a spread into two pages, named in reading order.

    Japanese magazines bind on the right, so the right half carries the earlier
    page and becomes "a"; a left-bound title reverses that. Each half keeps a
    sliver past the seam so no edge glyph is lost to an off-by-one, and the dark
    binding shadow that sliver brings with it is removed later by
    `trim_dark_edges`.
    """
    seam = round(gutter_x * image.width)
    bleed = round(image.width * 0.004)
    right = image.crop((min(seam + bleed, image.width), 0, image.width, image.height))
    left = image.crop((0, 0, max(seam - bleed, 0), image.height))
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


def trim_dark_edges(image: Image.Image, paper_luma: float, limit: float = 0.08) -> Image.Image:
    """Shave the binding shadow and scanner borders off each side.

    Splitting a spread leaves the gutter shadow on the inner edge of both
    halves, and these scans often carry a dark strip along the outside where the
    book block or the scanner bed shows. Both are darker than any printed
    margin, so edges are eaten inward while they stay well below the page's own
    paper level, and never past `limit` of the dimension so a dark headline
    bleeding to the trim cannot cost real content.
    """
    array = np.asarray(image.convert("RGB"), dtype=np.float32)
    gray = luma_of(array)
    height, width = gray.shape
    threshold = max(40.0, paper_luma * 0.72)

    def eat(profile: np.ndarray, cap: int) -> int:
        count = 0
        while count < cap and profile[count] < threshold:
            count += 1
        return count

    columns, rows = gray.mean(axis=0), gray.mean(axis=1)
    left = eat(columns, int(width * limit))
    right = eat(columns[::-1], int(width * limit))
    top = eat(rows, int(height * limit))
    bottom = eat(rows[::-1], int(height * limit))
    if not (left or right or top or bottom):
        return image
    return image.crop((left, top, width - right, height - bottom))


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
        preview = rotated.resize(
            (WORK_WIDTH, max(1, round(rotated.height * WORK_WIDTH / rotated.width))), Image.BILINEAR)
        after = skew_of(np.asarray(preview, dtype=np.float32))
        if after is not None and abs(after) < abs(angle) - 0.05:
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
           original_bytes: int | None) -> dict:
    """Write one derivative, preferring the original bytes when smaller."""
    working = image
    if long_edge and max(image.size) > long_edge:
        scale = long_edge / max(image.size)
        working = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    buffer = io.BytesIO()
    working.save(buffer, format="JPEG", quality=quality,
                 subsampling=0 if long_edge is None else 2,
                 optimize=True, progressive=True)
    data = buffer.getvalue()
    reused = False
    if original_bytes is not None and len(data) >= original_bytes * 0.9:
        reused = True
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {
        "path": destination.name,
        "bytes": len(data),
        "size": list(working.size),
        "reencode_gained_nothing": reused,
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
    tone_applied: bool = False
    note: str = ""


def process(path: Path, out_dir: Path, args) -> PageResult:
    measurement = measure(path)
    decision = classify(path, measurement, args.vlm, args.model, args.timeout)
    result = PageResult(
        source=path.name, source_bytes=path.stat().st_size,
        measurement=asdict(measurement), decision=asdict(decision),
    )
    if args.dry_run:
        return result

    with Image.open(path) as opened:
        full = opened.convert("RGB")
        pieces = (split_at(full, measurement.gutter_x, args.binding)
                  if decision.split and measurement.gutter_x else [("", full)])
        fill = tuple(int(round(v)) for v in measurement.paper_rgb)
        for suffix, piece in pieces:
            piece = crop_content(piece, measurement.content_box if not suffix else [0.0, 0.0, 1.0, 1.0])
            piece = trim_dark_edges(piece, measurement.paper_luma)
            piece, rotated = deskew(piece, measurement.skew_deg, fill)
            result.deskewed_by = rotated
            if decision.tone_policy == "paper" and not args.no_tone:
                piece = normalise_tone(piece, measurement.black_point, measurement.paper_rgb)
                result.tone_applied = True
            stem = path.stem + (f"-{suffix}" if suffix else "")
            # Only a single untouched, unsplit page can honestly reuse source bytes.
            comparable = (result.source_bytes
                          if not suffix and not rotated and not result.tone_applied else None)
            if "archive" in args.profiles:
                result.outputs.append(encode(
                    piece, out_dir / "archive" / f"{stem}.jpg",
                    args.archive_quality, None, comparable))
            if "web" in args.profiles:
                result.outputs.append(encode(
                    piece, out_dir / "web" / f"{stem}.jpg",
                    args.web_quality, args.web_long_edge, None))
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
    parser.add_argument("--limit", type=int, default=0, help="Process at most this many pages.")
    parser.add_argument("--dry-run", action="store_true", help="Measure and classify without writing.")
    args = parser.parse_args()
    args.profiles = {part.strip() for part in args.profiles.split(",") if part.strip()}

    if cv2 is None:
        print("opencv is required for skew and structure analysis; see tools/requirements.txt")
        return 1

    source, out_dir = Path(args.source).resolve(), Path(args.out).resolve()
    files = discover(source)
    if args.limit:
        files = files[: args.limit]
    if not files:
        print(f"no images found under {source}")
        return 1
    print(f"{len(files)} images under {source.name}\n")

    results, calls = [], 0
    for index, path in enumerate(files, start=1):
        try:
            result = process(path, out_dir, args)
        except Exception as exc:
            print(f"{index:>4}/{len(files)}  {path.name[:34]:<34} ERROR {type(exc).__name__}: {str(exc)[:90]}")
            continue
        calls += 1 if result.decision["decided_by"].startswith("vlm") else 0
        results.append(result)
        produced = sum(item["bytes"] for item in result.outputs)
        print(f"{index:>4}/{len(files)}  {path.name[:34]:<34} "
              f"{result.decision['kind']:<8} split={str(result.decision['split']):<5} "
              f"tone={result.decision['tone_policy']:<8} "
              f"{result.source_bytes/1048576:>6.1f}M -> {produced/1048576:>6.1f}M "
              f"({len(result.outputs)} files, {result.decision['decided_by']})")

    if not args.dry_run and results:
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "source": str(source),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "settings": {k: (sorted(v) if isinstance(v, set) else v) for k, v in vars(args).items()},
            "pages": [asdict(item) for item in results],
        }
        (out_dir / "scan-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    original = sum(item.source_bytes for item in results)
    produced = sum(entry["bytes"] for item in results for entry in item.outputs)
    splits = sum(1 for item in results if item.decision["split"])
    toned = sum(1 for item in results if item.tone_applied)
    print(f"\n{len(results)} pages | {splits} split | {toned} tone-normalised | {calls} model calls")
    if original and not args.dry_run:
        print(f"{original/1048576:.1f} MB in -> {produced/1048576:.1f} MB out "
              f"({100*produced/original:.0f}%), manifest at {out_dir / 'scan-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
