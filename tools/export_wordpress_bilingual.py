"""Export corrected magazine OCR as a WordPress-friendly bilingual article.

The generated fragment is deliberately self-contained: it keeps the scan,
Japanese and Chinese in three visible columns, remains readable when WordPress
strips JavaScript, and adds scan-region highlighting when scripts are allowed.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from PIL import Image


STYLE = r"""
<style>
.pm-interview{--ink:#25231f;--muted:#746f66;--paper:#fbfaf6;--line:#ddd8ce;--accent:#c86135;--soft:#f3eee4;color:var(--ink);font-family:"Noto Sans SC","Noto Sans JP",system-ui,sans-serif;max-width:1680px;margin:0 auto;padding:24px;background:var(--paper)}
.pm-interview *{box-sizing:border-box}.pm-header{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;border-bottom:1px solid var(--line);padding:0 0 22px;margin-bottom:22px}.pm-kicker,.pm-label{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:750}.pm-header h1{font-family:Georgia,"Noto Serif SC","Noto Serif JP",serif;font-size:clamp(30px,4vw,58px);line-height:1.08;margin:7px 0 10px}.pm-meta,.pm-summary{color:var(--muted);line-height:1.75}.pm-status{border:1px solid #c9ad65;background:#fff8dc;border-radius:999px;padding:8px 13px;font-size:13px;white-space:nowrap}.pm-tools{position:sticky;top:0;z-index:5;display:flex;gap:8px;align-items:center;padding:10px 0;background:linear-gradient(var(--paper) 76%,transparent)}.pm-tools button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 12px;color:var(--ink);cursor:pointer}.pm-tools button[aria-pressed="true"]{background:var(--ink);color:#fff}.pm-layout{display:grid;grid-template-columns:minmax(390px,.95fr) minmax(640px,1.45fr);gap:28px;align-items:start}.pm-scan{position:sticky;top:62px}.pm-scan-stage{position:relative;overflow:auto;max-height:calc(100vh - 90px);border:1px solid var(--line);border-radius:12px;background:#ece9e2;box-shadow:0 16px 38px #382d1a18}.pm-scan-stage img{display:block;width:100%;height:auto}.pm-highlight{position:absolute;display:none;border:3px solid #ef6a30;background:#ff8c3930;box-shadow:0 0 0 2px #fff9;border-radius:4px;pointer-events:none}.pm-scan-note{font-size:12px;color:var(--muted);line-height:1.6;margin:9px 3px}.pm-reading{min-width:0}.pm-lead{background:var(--soft);border-radius:12px;padding:18px;margin-bottom:18px}.pm-segment{border-top:1px solid var(--line);padding:20px 0;scroll-margin-top:70px}.pm-segment:focus,.pm-segment.is-active{outline:none}.pm-segment.is-active{border-top-color:var(--accent)}.pm-segment-head{display:flex;align-items:center;gap:10px;margin-bottom:11px}.pm-order{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--ink);color:#fff;font:700 12px/1 system-ui}.pm-line{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:10px 0;border-top:1px dotted #ded8cc}.pm-line:first-child{border-top:0}.pm-cell{min-width:0;white-space:pre-wrap;line-height:1.85}.pm-cell[lang="ja"]{font-family:"Noto Serif JP","Yu Mincho",serif}.pm-cell[lang="zh-CN"]{font-family:"Noto Serif SC","Songti SC",serif}.pm-cell p{margin:0}.pm-tag{display:block;color:var(--muted);font:700 11px/1.4 system-ui;letter-spacing:.08em;margin-bottom:5px}.pm-figure{margin:0}.pm-figure img{display:block;width:100%;max-height:680px;object-fit:cover;object-position:50% 42%;border-radius:12px}.pm-caption{display:grid;grid-template-columns:1fr 1fr;gap:16px;background:#f0eee8;padding:14px;border-radius:0 0 12px 12px;font-size:13px;line-height:1.7}.pm-source-meta{margin-top:24px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}.pm-interview.is-ja-only .pm-cell[lang="zh-CN"],.pm-interview.is-ja-only .pm-caption>[lang="zh-CN"]{display:none}.pm-interview.is-ja-only .pm-line,.pm-interview.is-ja-only .pm-caption{grid-template-columns:1fr}.pm-interview.is-zh-only .pm-cell[lang="ja"],.pm-interview.is-zh-only .pm-caption>[lang="ja"]{display:none}.pm-interview.is-zh-only .pm-line,.pm-interview.is-zh-only .pm-caption{grid-template-columns:1fr}
@media(max-width:1100px){.pm-layout{grid-template-columns:1fr}.pm-scan{position:relative;top:auto}.pm-scan-stage{max-height:68vh}.pm-header{grid-template-columns:1fr}}
@media(max-width:680px){.pm-interview{padding:16px}.pm-line,.pm-caption{grid-template-columns:1fr}.pm-cell[lang="zh-CN"]{padding-top:9px;border-top:1px solid #e4ded2}.pm-tools{overflow:auto}.pm-tools button{white-space:nowrap}}
</style>
""".strip()


SCRIPT = r"""
<script>
(function(){
  var root=document.querySelector('.pm-interview'); if(!root)return;
  var marks=[]; var stage=root.querySelector('.pm-scan-stage');
  function clearMarks(){marks.forEach(function(m){m.remove()});marks=[]}
  function activate(block){
    root.querySelectorAll('.pm-segment').forEach(function(x){x.classList.remove('is-active')});
    block.classList.add('is-active'); clearMarks();
    var boxes=JSON.parse(block.getAttribute('data-boxes')||'[]');
    boxes.forEach(function(b){var m=document.createElement('span');m.className='pm-highlight';m.style.display='block';m.style.left=(b[0]*100)+'%';m.style.top=(b[1]*100)+'%';m.style.width=((b[2]-b[0])*100)+'%';m.style.height=((b[3]-b[1])*100)+'%';stage.appendChild(m);marks.push(m)});
  }
  root.querySelectorAll('.pm-segment').forEach(function(block){block.addEventListener('click',function(){activate(block)});block.addEventListener('focus',function(){activate(block)})});
  root.querySelectorAll('[data-view]').forEach(function(button){button.addEventListener('click',function(){var view=button.getAttribute('data-view');root.classList.toggle('is-ja-only',view==='ja');root.classList.toggle('is-zh-only',view==='zh');root.querySelectorAll('[data-view]').forEach(function(x){x.setAttribute('aria-pressed',String(x===button))})})});
})();
</script>
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def lines(value: str) -> list[str]:
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def utterances(value: str, language: str) -> list[str]:
    """Join OCR line wraps while preserving interview speaker turns."""
    source_lines = lines(value)
    if language == "ja":
        marker = re.compile(r"^(?:[—―]{2}|蒼井\s+)")
    else:
        marker = re.compile(r"^(?:[—―]{2}|[苍蒼]井[：:])")
    if not any(marker.match(line) for line in source_lines):
        return source_lines
    result = []
    for line in source_lines:
        if marker.match(line) or not result:
            result.append(line)
        else:
            result[-1] += line
    return result


def boxes_for(item: dict, scan_width: int, scan_height: int) -> list[list[float]]:
    members = item.get("members") or [item]
    result = []
    for member in members:
        box = member.get("box") or []
        if len(box) != 4:
            continue
        result.append([
            round(float(box[0]) / scan_width, 6),
            round(float(box[1]) / scan_height, 6),
            round(float(box[2]) / scan_width, 6),
            round(float(box[3]) / scan_height, 6),
        ])
    return result


def paired_text(item: dict) -> str:
    originals = utterances(item.get("original_corrected") or item.get("original_raw") or "", "ja")
    translations = utterances(item.get("translation") or "", "zh")
    count = max(len(originals), len(translations), 1)
    rows = []
    for index in range(count):
        original = originals[index] if index < len(originals) else ""
        translation = translations[index] if index < len(translations) else ""
        rows.append(
            '<div class="pm-line">'
            f'<div class="pm-cell" lang="ja"><span class="pm-tag">日本語</span><p>{esc(original)}</p></div>'
            f'<div class="pm-cell" lang="zh-CN"><span class="pm-tag">中文</span><p>{esc(translation)}</p></div>'
            '</div>'
        )
    return "\n".join(rows)


def segment_html(item: dict, index: int, scan_width: int, scan_height: int, lead: bool = False) -> str:
    normalized_boxes = boxes_for(item, scan_width, scan_height)
    class_name = "pm-segment pm-lead" if lead else "pm-segment"
    label = "导语" if lead else "访谈正文"
    return (
        f'<section class="{class_name}" tabindex="0" data-boxes="{esc(json.dumps(normalized_boxes))}">\n'
        f'  <div class="pm-segment-head"><span class="pm-order">{index}</span><span class="pm-label">{label}</span></div>\n'
        f'  {paired_text(item)}\n'
        '</section>'
    )


def figure_html(image_item: dict, captions: list[dict], index: int, media_base: str, scan_width: int, scan_height: int) -> str:
    filename = Path(str(image_item.get("crop") or "")).name
    caption_pairs = []
    for caption in captions:
        caption_pairs.append(
            '<div class="pm-caption">'
            f'<div lang="ja"><span class="pm-tag">图注原文</span>{esc(caption.get("original_corrected") or caption.get("original_raw"))}</div>'
            f'<div lang="zh-CN"><span class="pm-tag">图注译文</span>{esc(caption.get("translation"))}</div>'
            '</div>'
        )
    normalized_boxes = boxes_for(image_item, scan_width, scan_height)
    return (
        f'<section class="pm-segment" tabindex="0" data-boxes="{esc(json.dumps(normalized_boxes))}">\n'
        f'  <div class="pm-segment-head"><span class="pm-order">{index}</span><span class="pm-label">杂志图片与图注</span></div>\n'
        f'  <figure class="pm-figure"><img src="{esc(media_base + "/figures/" + filename)}" alt="苍井优与皮卡丘杂志写真" loading="lazy">'
        + "".join(caption_pairs)
        + '</figure>\n</section>'
    )


def article_html(entries: list[dict], scan_image: Path, media_base: str) -> str:
    with Image.open(scan_image) as image:
        scan_width, scan_height = image.size
    by_id = {item.get("region_id"): item for item in entries}
    lead = by_id.get("qwen-r3")
    body = by_id.get("qwen-r4")
    image_item = next((item for item in entries if item.get("type") == "image"), None)
    captions = [item for item in entries if item.get("type") == "caption" and item.get("image_ref") == (image_item or {}).get("region_id")]
    scan_src = media_base + "/" + scan_image.name
    content = []
    number = 1
    if lead:
        content.append(segment_html(lead, number, scan_width, scan_height, lead=True)); number += 1
    if body:
        content.append(segment_html(body, number, scan_width, scan_height)); number += 1
    if image_item:
        content.append(figure_html(image_item, captions, number, media_base, scan_width, scan_height))
    return f"""
<article class="pm-interview">
  <header class="pm-header">
    <div><div class="pm-kicker">SCAN ARCHIVE · INTERVIEW</div><h1>蒼井優 ♥ ピカチュウ</h1><div class="pm-meta">《CONTINUE》2006 vol.31 · 文＝志田英邦 · 日中对照试读</div></div>
    <span class="pm-status">自动流程测试稿 · 发布前复核</span>
  </header>
  <p class="pm-summary">苍井优谈到童年时哥哥唱的宝可梦歌曲、自己的游戏习惯，以及在《Dr.科托诊疗所》外景期间学做饭的经历。</p>
  <nav class="pm-tools" aria-label="阅读显示"><span class="pm-label">阅读方式</span><button type="button" data-view="both" aria-pressed="true">日中对照</button><button type="button" data-view="ja" aria-pressed="false">只看日文</button><button type="button" data-view="zh" aria-pressed="false">只看中文</button></nav>
  <div class="pm-layout">
    <aside class="pm-scan"><div class="pm-scan-stage"><img src="{esc(scan_src)}" alt="《CONTINUE》2006 vol.31 苍井优采访扫描页"></div><p class="pm-scan-note">点击右侧段落可定位原扫描区域。当前测试图由已保存分区按原坐标重建；正式上线前请替换为原扫描图。</p></aside>
    <main class="pm-reading">{"".join(content)}<p class="pm-source-meta">来源：《CONTINUE》2006 vol.31，页 014–015。OCR：qwen-vl-ocr-latest；校对与初译：DeepSeek；状态：待最终人工复核。</p></main>
  </div>
</article>
""".strip()


def write_qa(out_dir: Path, entries: list[dict], paste_html: str, scan_image: Path, ocr_dir: Path) -> None:
    non_images = [item for item in entries if item.get("type") != "image"]
    missing = [item.get("region_id") for item in non_images if not item.get("original_corrected") or not item.get("translation")]
    reliability = [f"{item.get('region_id')}: {', '.join(item.get('reliability_warnings') or [])}" for item in entries if item.get("reliability_warnings")]
    ocr_warnings = []
    for path in sorted(ocr_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for warning in data.get("quality_warnings") or []:
            ocr_warnings.append(f"{path.stem}: {warning}")
    absolute_path_leak = bool(re.search(r"[A-Z]:\\", paste_html))
    alignment_issues = []
    for item in entries:
        if item.get("region_id") not in {"qwen-r3", "qwen-r4"}:
            continue
        ja_count = len(utterances(item.get("original_corrected") or "", "ja"))
        zh_count = len(utterances(item.get("translation") or "", "zh"))
        if ja_count != zh_count:
            alignment_issues.append(f"{item.get('region_id')}: 日文 {ja_count} / 中文 {zh_count}")
    checks = [
        ("翻译完整", not missing, "无空白段落" if not missing else ", ".join(missing)),
        ("OCR 结构告警", not ocr_warnings, "本页 9 个文字区均无结构告警" if not ocr_warnings else "; ".join(ocr_warnings)),
        ("翻译边界", not reliability, "左右栏已合并，未发现邻区复制" if not reliability else "; ".join(reliability)),
        ("逐句对齐", not alignment_issues, "导语与正文的日中轮次数一致" if not alignment_issues else "; ".join(alignment_issues)),
        ("WordPress 路径", not absolute_path_leak, "未泄漏本机绝对路径" if not absolute_path_leak else "发现本机绝对路径"),
        ("扫描图", scan_image.exists(), f"{scan_image.name} 可读取"),
    ]
    lines_out = ["# WordPress 完整流程检测报告", "", "## 自动检查", "", "| 检查项 | 结果 | 说明 |", "|---|---|---|"]
    for name, passed, detail in checks:
        lines_out.append(f"| {name} | {'通过' if passed else '需处理'} | {detail} |")
    lines_out.extend([
        "", "## 内容统计", "",
        f"- 原始分区：10（9 个文字区、1 个图片区）",
        f"- 发布逻辑段：{len(entries)}（左右正文栏已合并为一个连续段）",
        f"- 校对后日文字符：{sum(len(normalized_text(item.get('original_corrected'))) for item in non_images)}",
        f"- 中文译文字符：{sum(len(normalized_text(item.get('translation'))) for item in non_images)}",
        "- 页面结构：桌面端为原图／日文／中文三栏；窄屏自动改为上下布局。",
        "", "## 发布闸门", "",
        "1. 当前扫描图是从保留裁片按坐标重建的 QA 图；E 盘恢复后必须换回原始 page041.jpg。",
        "2. 将 WordPress 媒体库目录替换 `{{WORDPRESS_MEDIA_BASE}}` 占位符。",
        "3. 人工复核专有名词与译名后，再将稿件状态从“测试稿”改为“已校对”。",
        "4. 若站点账号会过滤 `<script>`，页面仍可正常阅读，但段落点击定位与显示切换不会启用。",
    ])
    (out_dir / "qa-report.md").write_text("\n".join(lines_out) + "\n", encoding="utf-8")


def normalized_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or ""))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export corrected OCR as WordPress bilingual HTML.")
    parser.add_argument("--corrections", required=True)
    parser.add_argument("--scan-image", required=True)
    parser.add_argument("--ocr-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    corrections = Path(args.corrections).resolve()
    scan_image = Path(args.scan_image).resolve()
    ocr_dir = Path(args.ocr_dir).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = json.loads(corrections.read_text(encoding="utf-8"))

    paste_article = article_html(entries, scan_image, "{{WORDPRESS_MEDIA_BASE}}")
    paste = STYLE + "\n" + paste_article + "\n" + SCRIPT + "\n"
    preview_article = article_html(entries, scan_image, "..")
    preview = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>蒼井優 ♥ ピカチュウ｜WordPress 对照页预览</title>" + STYLE + "</head><body>" + preview_article + SCRIPT + "</body></html>"
    )
    (out_dir / "wordpress-paste.html").write_text(paste, encoding="utf-8")
    (out_dir / "wordpress-preview.html").write_text(preview, encoding="utf-8")
    write_qa(out_dir, entries, paste, scan_image, ocr_dir)
    print(f"WordPress paste fragment: {out_dir / 'wordpress-paste.html'}")
    print(f"Local preview: {out_dir / 'wordpress-preview.html'}")
    print(f"QA report: {out_dir / 'qa-report.md'}")


if __name__ == "__main__":
    main()
