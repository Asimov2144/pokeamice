"""Checks for the dual-channel publisher's rendering and gating."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from publish_bilingual_article import (  # noqa: E402
    content_hash,
    docs_segments,
    preflight,
    render_docs_markdown,
    render_wordpress_html,
)

ENTRIES = [
    {
        "order": 1, "type": "body", "speaker": "body", "region_id": "r1",
        "page_index": 0, "box": [10, 20, 30, 40], "writing_direction": "horizontal",
        "original_corrected": "長官 こんにちは。", "translation": "长官 你好。",
        "note": "左栏",
    },
    {
        "order": 2, "type": "image", "speaker": "image", "region_id": "r2",
        "page_index": 0, "box": [50, 60, 70, 80], "crop": "missing.jpg",
        "note": "杂志写真",
    },
    {
        "order": 3, "type": "caption", "speaker": "caption", "region_id": "r3",
        "page_index": 0, "box": [50, 82, 70, 90], "image_ref": "r2",
        "original_corrected": "写真キャプション", "translation": "照片说明",
    },
]

META = {
    "article_id": "sample", "slug": "sample", "date": "2008-12-01",
    "title": "[扫描访谈] 样例", "publication": "DREAM", "issue": "2008.12",
    "summary": "样例摘要。",
}


def test_docs_segments_satisfy_both_layouts():
    """scan-translation reads kind/region_type; parallel-translation reads type."""
    segments = docs_segments(ENTRIES, {})
    text = segments[0]
    assert text["type"] == "paragraph", "parallel-translation dispatches on type"
    assert text["kind"] == "text"
    assert text["region_type"] == "body", "scan-translation keeps the real region type"
    assert list(text["scan_box"]) == [10, 20, 30, 40]
    assert text["comment"] == "左栏"


def test_image_regions_are_dropped_without_a_published_asset():
    segments = docs_segments(ENTRIES, {})
    assert [item["region_id"] for item in segments] == ["r1", "r3"]
    assert "caption_for" not in segments[1], "a caption must not point at a dropped figure"


def test_image_regions_render_when_mapped():
    segments = docs_segments(ENTRIES, {"r2": "/assets/img/sample/figure.jpg"})
    figure = segments[1]
    assert figure["type"] == "image" and figure["kind"] == "image"
    assert figure["image"] == "/assets/img/sample/figure.jpg"
    assert segments[2]["caption_for"] == "r2"


def test_preflight_blocks_untranslated_and_flagged_regions():
    assert preflight(ENTRIES, META) == []

    missing = [dict(ENTRIES[0], translation="")]
    assert any("no translation" in problem for problem in preflight(missing, META))

    flagged = [dict(ENTRIES[0], review_flags=["low_confidence"])]
    assert any("review flag" in problem for problem in preflight(flagged, META))

    assert any("article_id" in problem for problem in preflight(ENTRIES, {"slug": "x"}))


def test_rendered_output_is_stable_and_channel_independent():
    first = render_docs_markdown(ENTRIES, META)
    assert content_hash(first) == content_hash(render_docs_markdown(ENTRIES, META))
    assert "layout: parallel-translation" in first
    assert "scan_box: [10, 20, 30, 40]" in first, "boxes stay inline like hand-written posts"

    wordpress = render_wordpress_html(ENTRIES, META, "", (0, 0), {})
    assert content_hash(wordpress) != content_hash(first)
    assert 'lang="ja"' in wordpress and 'lang="zh-CN"' in wordpress
    assert "pm-scan-stage" not in wordpress, "no scan pane without a scan image"


def test_wordpress_attaches_captions_to_their_figure():
    html = render_wordpress_html(ENTRIES, META, "", (100, 100), {"r2": "https://x/y.jpg"})
    assert html.count('<section class="pm-segment"') == 2, "the caption merges into the figure block"
    assert "图注译文" in html and "照片说明" in html


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok  {name}")
    print("publisher checks passed")
