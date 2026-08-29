"""Read the entities out of translated posts so the archive can be cross-indexed.

The site already aggregates people, works and organisations into
`_data/resource-index.json`, but only the 16 hand-tagged posts carry an
`entities:` block. The 459 serialised column entries do not, which is exactly
where names appear most densely, so the entity layer covers almost nothing.

This asks DeepSeek to read a post's translated body and name the entities it
actually discusses. Two rules keep the index from fragmenting:

* one canonical form per entity, preferring the name the site already uses, so
  a person is not split between 増田順一 and 增田顺一;
* only entities the text is really about, not every noun that appears once.

Nothing is written into a post until a human has read the sample. Run with
--apply to write, and without it to review.

    python tools/extract_post_entities.py --pattern "*gamefreak-director*" --limit 20
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
KINDS = ("people", "works", "organizations", "events")

# The columnist is the author of every entry in his own series, and the blog is
# Game Freak's. The model only names them when the prose happens to, which put
# 増田順一 on 6 of 20 sample posts instead of all of them. These are facts about
# the series, so they are asserted rather than inferred.
SERIES_FACTS = {
    "gamefreak_director_column": {"people": ["增田顺一"], "organizations": ["Game Freak"]},
    "gamefreak_legacy_blog": {"organizations": ["Game Freak"]},
}

PROMPT = """你在为一个宝可梦资料库建立实体索引。下面是一篇已翻译的文章。

只输出严格 JSON，不要解释、不要代码块：

{
  "people": [], "works": [], "organizations": [], "events": []
}

规则：
- 只收录文章**实质讨论**的实体，不要收录一笔带过的名词。宁少勿多。
- 人物用中文通用译名（增田顺一、杉森建、田尻智）；非日本人保留原名（moog）。
- 作品按**同期发行组**合并成一个条目，用「·」连接，不要拆成单版本：
    正确：宝可梦 红·绿 / 宝可梦 红宝石·蓝宝石 / 宝可梦 火红·叶绿 / 宝可梦 金·银
    错误：把「宝可梦 火红」和「宝可梦 叶绿」分成两条
  单独发行的写单名（宝可梦 绿宝石、宝可梦 水晶版、宝可梦 皮卡丘版）。
  泛指整个系列时不要收进 works，那不是具体作品。
- works **只收电子游戏、影视、书刊**。乐器型号、硬件机型、软件工具不是作品：
    罗兰 SH-2、KORG MS-20、moog IIIc、SUN SPARCstation → 不要收进 works，
    把生产它们的公司收进 organizations 即可。
- 只收**真实存在**的作品名。不确定就不收，不要自己拼组合。
- 组织写正式名（Game Freak、任天堂、Creatures、罗兰、KORG）。
- events 只收有名字的具体事件（发布会、大会、展会），不收日常起居。
- 每类最多 6 项。没有就给空数组。
"""


def front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[: end + 4], text[end + 4:]


def body_excerpt(text: str, limit: int = 3500) -> str:
    """The translated prose, without markup that would distract the model."""
    _, body = front_matter(text)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body[:limit]


def ask(text: str, model: str, api_key: str, base_url: str, retries: int = 2) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的资料编目员，只输出 JSON。"},
            {"role": "user", "content": PROMPT + "\n\n---\n\n" + text},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {k: [str(v).strip() for v in (parsed.get(k) or []) if str(v).strip()]
                    for k in KINDS}
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                pass
            last = f"HTTP {exc.code}: {detail or exc.reason}"
            if exc.code in (401, 402, 403):
                raise RuntimeError(last) from None
        except Exception as exc:  # noqa: BLE001 - reported, then retried
            last = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(last or "extraction failed")


def merge_series_facts(entities: dict, text: str) -> dict:
    """Add what the series guarantees, without duplicating what was extracted."""
    match = re.search(r"^archive_type:\s*(\S+)", text, re.M)
    series = match.group(1).strip("\"'") if match else ""
    facts = SERIES_FACTS.get(series, {})
    for kind, values in facts.items():
        have = entities.setdefault(kind, [])
        for value in values:
            if value not in have:
                have.insert(0, value)
    return entities


def render_block(entities: dict) -> str:
    lines = ["entities:"]
    for kind in KINDS:
        values = entities.get(kind) or []
        if not values:
            continue
        lines.append(f"  {kind}:")
        for value in values:
            safe = value.replace('"', '\\"')
            lines.append(f'    - "{safe}"')
    return "\n".join(lines) + "\n"


def apply_to(path: Path, entities: dict) -> bool:
    text = path.read_text(encoding="utf-8")
    head, body = front_matter(text)
    if not head or "\nentities:" in head:
        return False
    block = render_block(entities)
    if block.strip() == "entities:":
        return False
    updated = head[: head.rfind("\n---")] + "\n" + block + head[head.rfind("\n---"):]
    path.write_text(updated + body, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pattern", default="*.md", help="Glob over _posts.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--base-url", default=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--api-key", default=os.getenv("DEEPSEEK_API_KEY", ""))
    parser.add_argument("--apply", action="store_true", help="Write the block into each post.")
    parser.add_argument("--out", default="", help="Also save the sample as JSON for review.")
    args = parser.parse_args()

    if not args.api_key:
        print("set DEEPSEEK_API_KEY to run extraction")
        return 2

    files = [p for p in sorted(POSTS.glob(args.pattern)) if p.suffix == ".md"]
    files = [p for p in files if "\nentities:" not in p.read_text(encoding="utf-8")[:2000]]
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("nothing to do: every matching post already has entities")
        return 1

    print(f"{len(files)} post(s), model {args.model}, "
          f"{'writing' if args.apply else 'review only'}\n")

    seen = Counter()
    results, failures = [], []
    for index, path in enumerate(files, start=1):
        text = path.read_text(encoding="utf-8")
        excerpt = body_excerpt(text)
        if len(excerpt) < 120:
            print(f"{index:>3}/{len(files)}  {path.name[:44]:<46} too short, skipped")
            continue
        try:
            entities = ask(excerpt, args.model, args.api_key, args.base_url)
        except Exception as exc:  # noqa: BLE001 - reported per file
            failures.append((path.name, str(exc)))
            print(f"{index:>3}/{len(files)}  {path.name[:44]:<46} FAILED {str(exc)[:60]}")
            continue
        entities = merge_series_facts(entities, text)
        for kind in KINDS:
            for value in entities[kind]:
                seen[(kind, value)] += 1
        flat = "; ".join(f"{k[:4]}={'/'.join(v)}" for k, v in entities.items() if v)
        print(f"{index:>3}/{len(files)}  {path.name[:44]:<46} {flat[:96]}")
        results.append({"file": path.name, "entities": entities})
        if args.apply and apply_to(path, entities):
            pass

    print(f"\n{len(results)} extracted, {len(failures)} failed")
    if seen:
        print("\nmost common entities across the sample:")
        for (kind, value), count in seen.most_common(18):
            print(f"  {count:>3}x  {kind:<14} {value}")
    if args.out and results:
        Path(args.out).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nsample written to {args.out}")
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
