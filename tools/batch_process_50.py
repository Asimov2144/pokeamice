"""Batch process and translate web interviews 11 through 50 with DeepSeek and Chrome headless fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
RAW_DIR = ROOT / "archive" / "web-interviews" / "raw"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
GLOSSARY_PATH = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


def load_glossary() -> list[dict]:
    if not GLOSSARY_PATH.exists():
        return []
    try:
        data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
        entries = []
        for item in data.get("entries", []):
            target = item.get("target")
            terms = item.get("terms") or []
            if target and terms:
                entries.append({"target": target, "terms": terms})
        return entries
    except Exception as e:
        print(f"Error loading glossary: {e}")
        return []


def find_glossary_matches(text: str, glossary: list[dict]) -> list[tuple[str, str]]:
    matches = []
    text_lower = text.lower()
    for entry in glossary:
        target = entry["target"]
        for term in entry["terms"]:
            term_clean = term.strip()
            if len(term_clean) < 2:
                continue
            if re.match(r"^[A-Za-z0-9\s\.\-]+$", term_clean):
                if len(term_clean) <= 2:
                    continue
                pattern = r"\b" + re.escape(term_clean.lower()) + r"\b"
                if re.search(pattern, text_lower):
                    matches.append((term_clean, target))
                    break
            else:
                if term_clean.lower() in text_lower:
                    matches.append((term_clean, target))
                    break
    seen = set()
    unique = []
    for term, target in sorted(matches, key=lambda x: -len(x[0])):
        if term not in seen:
            seen.add(term)
            unique.append((term, target))
    return unique[:80]


def call_deepseek(messages: list[dict], max_tokens: int = 4096, temperature: float = 0.3) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"DeepSeek call attempt {attempt+1} failed: {exc}", file=sys.stderr)
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("Unreachable")


class CleanHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.images = []
        self.current = []
        self.in_ignored = False
        self.block_tags = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'br', 'li', 'dt', 'dd', 'blockquote'}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ('script', 'style', 'nav', 'header', 'footer', 'aside'):
            self.in_ignored = True
        elif tag == 'img':
            src = attrs_dict.get('src') or attrs_dict.get('data-src')
            alt = attrs_dict.get('alt', '')
            if src and not any(k in src for k in ['pixel', 'tracking', 'avatar', 'icon', 'button', 'badge', 'banner']):
                self.images.append({'src': src, 'alt': alt})
        elif tag in self.block_tags:
            self._flush()

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'header', 'footer', 'aside'):
            self.in_ignored = False
        elif tag in self.block_tags:
            self._flush()

    def handle_data(self, data):
        if not self.in_ignored:
            t = data.strip()
            if t:
                self.current.append(t)

    def _flush(self):
        if self.current:
            text = " ".join(self.current).strip()
            if text and len(text) > 1:
                self.paragraphs.append(text)
            self.current = []


def fetch_url(url: str) -> tuple[str, list[dict], list[str]]:
    """Fetch URL and return (html, images, paragraphs). Uses fallback to Chrome headless if needed."""
    html = ""
    # 1. Try urllib
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            # Try decodings
            for enc in ["utf-8", "shift_jis", "cp1252", "latin-1"]:
                try:
                    html = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
    except Exception as e:
        print(f"      urllib error ({e}), attempting Chrome headless...")
        if Path(CHROME_PATH).exists():
            try:
                proc = subprocess.run([
                    CHROME_PATH,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-extensions",
                    "--dump-dom",
                    url
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=30)
                html = proc.stdout
            except Exception as ce:
                print(f"      Chrome headless error: {ce}")

    if not html:
        return "", [], []

    parser = CleanHTMLParser()
    parser.feed(html)
    parser._flush()

    # Filter wayback / ads noise
    cleaned_imgs = []
    for img in parser.images:
        src = img['src']
        full_url = urljoin(url, src)
        if not any(k in full_url for k in ['archive.org/_static', 'analytics', 'counter', 'wp-content/themes', 'logo']):
            cleaned_imgs.append({'src': full_url, 'alt': img['alt']})

    return html, cleaned_imgs, parser.paragraphs


def clean_paragraphs(paragraphs: list[str]) -> list[str]:
    cleaned = []
    end_markers_exact = {
        "記事をシェアする", "関連記事", "コメント", "コメント ※", "メールアドレスが公開されることはありません",
        "スポンサーリンク", "Twitter Facebook はてブ LINE", "Comments", "Leave a Reply",
        "Your email address will not be published", "Next Story", "Recommended Posts",
        "Most Popular »", "IGN Logo Recommends", "More from Game Informer", "Legacy Comments",
        "Related Content", "Popular Discussions", "Site Map", "Share this article", "Recommended Stories",
        "Sign in to comment", "About the Author:"
    }

    skip_exact = {
        "Home", "Photos", "Videos", "Specials", "Topics", "Subscribe", "Mobile Apps",
        "Newsletters", "RSS", "NewsFeed", "Print", "Email", "Reprints", "share",
        "LinkedIn", "StumbleUpon", "Reddit", "Digg", "Del.i.cious", "Tweet", "Back Button",
        "COUNTER", "Next", "Previous", "Top", "Menu", "success", "fail", "DS", "ホーム",
        "Focus Reset", "0 comments", "SUBSCRIBE", "Search:", "Twitter", "Facebook",
        "Instagram", "Twitch", "YouTube", "Tiktok", "Close", "Copy Link", "Follow Us",
        "Facebook Post", "Twitter Tweet", "Email Email", "Comment Comment"
    }

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean or len(p_clean) < 2:
            continue
        # Only check end markers after having gathered at least 5 content paragraphs
        if len(cleaned) >= 5 and (p_clean in end_markers_exact or any(p_clean.startswith(marker) for marker in ["© 20", "© 19", "Legacy Comments", "About the Author:"])):
            break
        if p_clean in skip_exact:
            continue
        if p_clean.startswith("Type: - Any -") or p_clean.startswith("Items per page:") or p_clean.startswith("Sort by:"):
            continue
        if any(s in p_clean for s in ["captures", "Wayback Machine", "COLLECTED BY", "Alexa Crawl", "Internet Archive", "Crawl FS", "Focused crawls are"]):
            continue
        if p_clean.startswith("var ") or p_clean.startswith("function("):
            continue
        cleaned.append(p_clean)

    return cleaned


def download_article_image(img_url: str, dest_dir: Path, idx: int) -> str | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(img_url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if not ext or ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        ext = ".jpg"
    
    filename = f"img_{idx:02d}{ext}"
    dest_path = dest_dir / filename
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return f"/assets/img/interviews/{dest_dir.name}/{filename}"

    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if len(data) > 1000: # only download meaningful images > 1KB
                dest_path.write_bytes(data)
                print(f"      [Image Saved] {filename} ({len(data)} bytes)")
                return f"/assets/img/interviews/{dest_dir.name}/{filename}"
    except Exception as e:
        pass
    return None


def translate_chunk(chunk: list[str], interview_meta: dict, glossary_matches: list[tuple[str, str]]) -> list[dict]:
    glossary_str = "\n".join(f"- {src} -> {tgt}" for src, tgt in glossary_matches) or "无特定匹配词条"
    
    prompt = f"""你是精通宝可梦历史考据、游戏史料与专业翻译的专家。
正在整理宝可梦官方与媒体开发者访谈的日中/英中对照档案。

请将以下访谈内容翻译为流畅、准确、忠实原文的简体中文。
如果是对话/采访形式（如“问：... 答：...”或“IGN: ... Masuda: ...”），请识别出说话人(speaker)。
如果段落中有特定的背景设定、行业术语、人名梗或值得注释的地方，请填写在 note 字段中。

【专业术语规范】：
优先遵循以下官方/通行译名：
{glossary_str}

【输出格式要求】：
请输出严格的 JSON 对象：
{{
  "segments": [
    {{
      "speaker": "说话人名字或职务（若无说话人则留空字符串''）",
      "original": "该段对应的原文",
      "translation": "流畅自然的简体中文译文",
      "note": "对原文背景、专有名词或特定事件的译注（若无则留空字符串''）"
    }}
  ]
}}

待翻译原文段落列表：
{json.dumps(chunk, ensure_ascii=False, indent=2)}
"""

    messages = [
        {"role": "system", "content": "你是一位专业的宝可梦游戏历史考据与开发者访谈双语翻译专家。请只输出合法的 JSON 对象。"},
        {"role": "user", "content": prompt}
    ]

    raw_json = call_deepseek(messages)
    try:
        parsed = json.loads(raw_json)
        return parsed.get("segments", [])
    except Exception as e:
        print(f"      Error parsing DeepSeek JSON: {e}", file=sys.stderr)
        return [{"speaker": "", "original": p, "translation": p, "note": ""} for p in chunk]


def build_post(meta: dict, segments: list[dict], images: list[dict] = None) -> str:
    # Build clean tags and people
    tags_raw = meta.get("tags") or ""
    tags = ["Pokemon", "访谈", "开发者访谈"]
    if tags_raw:
        for t in tags_raw.split(","):
            t_clean = t.strip()
            if t_clean and t_clean not in tags:
                tags.append(t_clean)

    front_matter = {
        "layout": "parallel-translation",
        "title": f"[访谈翻译] {meta['name']}",
        "date": meta["date"],
        "toc": True,
        "toc_sticky": True,
        "parallel_view": "translation",
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": tags,
        "archive_type": "interview_translation",
        "source": {
            "title": meta["name"],
            "url": meta["link"],
            "language": "ja" if "JP" in tags else "en",
            "source_type": "web_interview"
        },
        "workflow": {
            "scan": "not_applicable",
            "preprocess": "done",
            "ocr": "not_applicable",
            "translation": "done",
            "proofreading": "pending",
            "published": "done"
        },
        "entities": {
            "people": [t for t in tags if t in ["增田顺一", "杉森建", "田尻智", "森本茂树", "大森滋", "海野隆雄", "石原恒和"]],
            "works": ["宝可梦"],
            "organizations": ["Game Freak", "Nintendo"]
        },
        "original_title": meta["name"],
        "original_link": meta["link"],
        "translator": "Poke Amice Studio",
        "interviewee": ", ".join(t for t in tags if t in ["增田顺一", "杉森建", "田尻智", "森本茂树", "大森滋", "海野隆雄", "石原恒和"]) or "开发团队",
        "parallel_items": []
    }

    # Insert top image if downloaded
    if images and len(images) > 0:
        front_matter["parallel_items"].append({
            "type": "image",
            "image": images[0]["local_path"],
            "caption": images[0].get("alt") or "专访配图"
        })

    for seg in segments:
        orig = seg.get("original", "").strip()
        trans = seg.get("translation", "").strip()
        if not orig and not trans:
            continue
        item = {
            "type": "paragraph",
            "original": orig,
            "translation": trans
        }
        if seg.get("speaker"):
            item["speaker"] = seg["speaker"]
        if seg.get("note"):
            item["note"] = seg["note"]
        front_matter["parallel_items"].append(item)

    # Insert bottom image if more than 1
    if images and len(images) > 1:
        front_matter["parallel_items"].append({
            "type": "image",
            "image": images[1]["local_path"],
            "caption": images[1].get("alt") or "相关资料图"
        })

    yaml_str = yaml.dump(front_matter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{yaml_str}---\n"


def generate_slug(candidate: dict, index: int) -> str:
    path = urllib.parse.urlparse(candidate.get("link", "")).path
    segments = [s for s in path.split("/") if s and not s.endswith(".html") and not s.endswith(".htm")]
    if segments:
        last_seg = segments[-1].replace(".aspx", "").replace(".php", "")
        url_slug = re.sub(r"[^a-zA-Z0-9\-]", "-", last_seg).strip("-").lower()
        url_slug = re.sub(r"-+", "-", url_slug)
        if len(url_slug) >= 5:
            return url_slug[:35].strip("-")

    name_slug = re.sub(r"[^a-zA-Z0-9\-]", "-", candidate["name"]).strip("-").lower()
    name_slug = re.sub(r"-+", "-", name_slug)
    if len(name_slug) >= 4:
        return name_slug[:35].strip("-")

    return f"interview-{index:02d}"


def is_already_completed(candidate: dict) -> Path | None:
    link = candidate.get("link", "").strip()
    if not link:
        return None
    # Check all posts
    for post in POSTS_DIR.glob("*.md"):
        try:
            content = post.read_text(encoding="utf-8")
            if link in content:
                return post
        except Exception:
            pass
    return None


def process_one_interview(candidate: dict, glossary: list[dict], index: int) -> bool:
    completed_file = is_already_completed(candidate)
    if completed_file:
        print(f"[{index:2d}/50] [ALREADY COMPLETED] {completed_file.name}")
        return True

    slug = generate_slug(candidate, index)
    print(f"\n========================================================")
    print(f"[{index:2d}/50] Processing: {candidate['name']} ({candidate['date']})")
    print(f"      URL: {candidate['link']}")
    print(f"      Generated slug: {slug}")

    # Fetch
    t0 = time.time()
    html, raw_images, raw_paragraphs = fetch_url(candidate["link"])
    print(f"      Fetched in {time.time()-t0:.1f}s: {len(raw_paragraphs)} raw paragraphs, {len(raw_images)} images.")
    if not raw_paragraphs:
        print("      [Warning] No content could be extracted from page!")
        return False

    # Clean paragraphs
    paragraphs = clean_paragraphs(raw_paragraphs)
    print(f"      Cleaned paragraphs: {len(paragraphs)}")
    if not paragraphs or len(paragraphs) < 2:
        print("      [Warning] Too few paragraphs left after cleaning!")
        return False

    # Download top images (up to 2)
    saved_images = []
    dest_dir = IMG_DIR / f"{candidate['date']}-{slug}"
    for i, img in enumerate(raw_images[:3], 1):
        local_path = download_article_image(img['src'], dest_dir, i)
        if local_path:
            saved_images.append({"local_path": local_path, "alt": img['alt']})
            if len(saved_images) >= 2:
                break

    # Glossary matches
    full_text = "\n".join(paragraphs)
    glossary_matches = find_glossary_matches(full_text, glossary)
    print(f"      Matched {len(glossary_matches)} glossary terms.")

    # Translate in chunks of 15
    chunk_size = 15
    chunks = [paragraphs[i:i + chunk_size] for i in range(0, len(paragraphs), chunk_size)]
    print(f"      Translating in {len(chunks)} chunk(s)...")

    all_segments = []
    for c_idx, chunk in enumerate(chunks, 1):
        print(f"        Chunk {c_idx}/{len(chunks)} ({len(chunk)} paragraphs)...", end="", flush=True)
        t_chunk = time.time()
        segs = translate_chunk(chunk, candidate, glossary_matches)
        print(f" done in {time.time()-t_chunk:.1f}s, got {len(segs)} segs.")
        all_segments.extend(segs)
        time.sleep(1)

    # Build post and write
    post_content = build_post(candidate, all_segments, saved_images)
    post_filename = f"{candidate['date']}-interview-{slug}.md"
    post_path = POSTS_DIR / post_filename
    post_path.write_text(post_content, encoding="utf-8")
    
    # Run noise cleanup on the just-written post
    import importlib.util
    _noise_spec = importlib.util.spec_from_file_location("clean_interview_noise", ROOT / "tools" / "clean_interview_noise.py")
    _noise_mod = importlib.util.module_from_spec(_noise_spec)
    _noise_spec.loader.exec_module(_noise_mod)
    _noise_mod.clean_post(post_path)
    
    print(f"      -> SUCCESS: Written to {post_path.name} ({len(post_content)} bytes)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Batch process interviews 11 to 50")
    parser.add_argument("--start", type=int, default=11, help="Start index (1-based)")
    parser.add_argument("--end", type=int, default=50, help="End index (inclusive)")
    args = parser.parse_args()

    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries.")

    # Load candidate list
    with open(ROOT / "_data" / "notion_interviews.json", "r", encoding="utf-8") as f:
        d = json.load(f)

    rows = d['rows']
    valid = [r for r in rows if (r.get('Name') or '') not in ('', '1111', 'Untitled')]

    def extract_date(r):
        d_val = r.get('Date')
        if d_val: return d_val
        link = r.get('Links') or ''
        title = r.get('Name') or ''
        if 'POKEMON/INTER' in link: return '1997-10-16'
        if 'content.time.com' in link: return '1999-11-22'
        if 'nom/0007' in link: return '2000-07-01'
        if 'sunanohi.web.fc2.com' in link: return '2000-01-01'
        if 'pokemon_site.htm' in link: return '2000-05-01'
        if '2004/05/13' in link or 'E3 2004' in title: return '2004-05-13'
        m = re.search(r'/(20\d\d)[/-](\d{1,2})[/-](\d{1,2})', link)
        if m: return f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
        m2 = re.search(r'/(20\d\d)(\d{2})(\d{2})', link)
        if m2: return f'{m2.group(1)}-{m2.group(2)}-{m2.group(3)}'
        m3 = re.search(r'/(20\d\d)[/-](\d{1,2})/', link)
        if m3: return f'{m3.group(1)}-{int(m3.group(2)):02d}-01'
        m4 = re.search(r'\b(20\d\d)[年\.-](\d{1,2})[月\.-](\d{1,2})', title)
        if m4: return f'{m4.group(1)}-{int(m4.group(2)):02d}-{int(m4.group(3)):02d}'
        m5 = re.search(r'\b(20\d\d)\b', title)
        if m5: return f'{m5.group(1)}-01-01'
        return '9999-99-99'

    web_interviews = []
    for r in valid:
        link = (r.get('Links') or '').strip()
        name = (r.get('Name') or '').strip()
        tags = r.get('Tags') or ''
        if not link: continue
        if any(k in link for k in ['youtube.com', 'twitter.com', 'canuch.com', 'twisave.com', 'bwhuman2', 'atwiki.jp', 'gff.jp/internship']):
            continue
        if 'corocoro.jp/news/49271' in link or link.endswith('/blog/art') or link.endswith('/blog/dir_english/'):
            continue
        est_date = extract_date(r)
        web_interviews.append({
            'name': name,
            'date': est_date,
            'link': link,
            'tags': tags,
            'id': r.get('_id')
        })

    seen = set()
    unique = []
    for item in web_interviews:
        if item['link'] not in seen:
            seen.add(item['link'])
            unique.append(item)

    unique.sort(key=lambda x: (x['date'], x['name']))

    print(f"Target range: [{args.start} to {args.end}] of {len(unique)} total candidates.")

    success_count = 0
    for idx in range(args.start, min(args.end + 1, len(unique) + 1)):
        candidate = unique[idx - 1]
        try:
            ok = process_one_interview(candidate, glossary, idx)
            if ok:
                success_count += 1
        except Exception as e:
            print(f"[{idx:2d}/50] ERROR processing {candidate['name']}: {e}", file=sys.stderr)

    print(f"\n========================================================")
    print(f"Batch completed! Processed {success_count} interview(s) successfully.")


if __name__ == "__main__":
    main()
