"""Give the older interview posts the summary / dek / topics the newer imports carry.

    python tools/enrich-posts.py --list            # the posts that still lack a summary
    python tools/enrich-posts.py --dry-run         # ask the model, print, write nothing
    python tools/enrich-posts.py [--only slug…] [--workers 4]
    python tools/enrich-posts.py --people [--dry-run]   # entities.people from the transcript's speakers, where a post has none

The same questions the scan importer asks (import-scan-set.py enrich): from the
whole Chinese translation, a 140–200 字 factual summary, a one-line dek, 3–6
topic tags, plus the works and people the piece discusses. What is written:
`summary`, `dek`, `topics`, `mentions` (what the model listed), and
`entities.people` / `entities.works` only where the post has none - people
from the speakers of the transcript first, checked against _data/people.yml,
works checked against _data/works.yml. Nothing that is already there is
changed, and the front matter is edited in place, not re-serialised.
"""
import argparse
import concurrent.futures
import glob
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("import_nom", ROOT / "tools" / "import-nom.py")
_nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nom)
deepseek = _nom.deepseek

SYSTEM = "你是宝可梦开发史料的编辑。只输出合法 JSON；提要平实、具体，不评价、不加感叹号。"
CROWD = {"众人", "全员", "一同", "全体", "众人（笑）", "Everyone", "All", "──", "――"}
ORGS = {"Game Freak", "任天堂", "株式会社ポケモン", "The Pokémon Company", "Creatures", "Niantic", "小学馆", "OLM", "Spike Chunsoft", "Ambrella"}


def front_matter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---(\r?\n)", text, re.S)
    if not m:
        return None, None
    return yaml.safe_load(m.group(1)) or {}, m


def candidates(only=None):
    out = []
    for p in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        if only and not any(o in p for o in only):
            continue
        text = io.open(p, encoding="utf-8", newline="").read()
        try:
            fm, m = front_matter(text)
        except yaml.YAMLError:
            continue
        if not fm or fm.get("layout") not in ("interview-editorial", "parallel-translation"):
            continue
        if fm.get("summary") or not fm.get("parallel_items"):
            continue
        out.append((p, text, fm, m))
    return out


def transcript(fm):
    body, speakers = [], []
    for it in fm["parallel_items"]:
        if not isinstance(it, dict) or it.get("type") == "image":
            continue
        if it.get("type") == "heading":
            body.append("## " + (it.get("translation") or it.get("original") or ""))
            continue
        who = (it.get("speaker") or "").strip()
        if it.get("role") == "answer" and who and who not in CROWD and who not in speakers:
            speakers.append(who)
        body.append((who + "：" if who else "") + (it.get("translation") or ""))
    return "\n".join(body), speakers


def ask(fm, text):
    title = fm.get("title") or ""
    source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
    src = fm.get("publication") or source.get("title") or fm.get("source_name") or ""
    year = str(fm.get("date") or "")[:4]
    prompt = (f"下面是《{title}》（{src} {year} 年）的中文译文。请给出用于站内检索与数据分析的元数据，JSON：\n"
              "{\"summary\": \"140–200 字的内容提要：写清谁在谈什么、有哪些具体的事实与数字（作品、年份、机制、人名），平实，不评价\", "
              "\"dek\": \"一句导语，40 字以内\", "
              "\"topics\": [\"3–6 个主题标签，短语，如 角色设计 / 音乐制作 / 地区设定 / 开发流程 / 系统设计 / 通信功能 / 传说宝可梦 / 动画制作 / 媒体组合 / 卡牌 / 海外展开\"], "
              "\"works\": [\"文中实际讨论到的宝可梦作品，用站内写法：宝可梦 红·绿 / 宝可梦 金·银 / 宝可梦 红宝石·蓝宝石 / 宝可梦 钻石·珍珠 / 宝可梦 黑·白 / 宝可梦 X·Y / 宝可梦 太阳·月亮 / 宝可梦 剑·盾 / 宝可梦 朱·紫 / Pokémon GO / 宝可梦 动画系列 / 宝可梦：超梦的逆袭 等\"], "
              "\"organizations\": [\"受访者所属或作为主体出现的公司：Game Freak / 任天堂 / 株式会社ポケモン / Creatures / Niantic / 小学馆 等\"], "
              "\"people\": [\"文中发言或被专门介绍的开发者，用站内通行中文名，如 增田顺一、杉森建、石原恒和、田尻智、大森滋、岩田聪、久保雅一、汤山邦彦\"]}\n\n" + text[:24000])
    raw = deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1200)
    return json.loads(raw)


def yaml_line(key, value, indent=""):
    return f"{indent}{key}: " + json.dumps(str(value).strip(), ensure_ascii=False)


def yaml_list(key, values, indent=""):
    if not values:
        return [f"{indent}{key}: []"]
    return [f"{indent}{key}:"] + [f"{indent}- " + json.dumps(str(v).strip(), ensure_ascii=False) for v in values]


def apply(path, text, fm, m, got, people_ok, works_ok):
    """The new fields, appended to the front matter; entities added only where missing."""
    nl = m.group(2)
    lines = []
    lines.append(yaml_line("summary", got.get("summary") or ""))
    if got.get("dek") and not fm.get("dek"):
        lines.append(yaml_line("dek", got["dek"]))
    topics = [str(x).strip() for x in (got.get("topics") or []) if str(x).strip()][:5]
    lines += yaml_list("topics", topics)
    m_people = [str(x).strip() for x in (got.get("people") or []) if str(x).strip()]
    m_works = [str(x).strip() for x in (got.get("works") or []) if str(x).strip()]
    _, speakers = transcript(fm)
    ent = fm.get("entities") if isinstance(fm.get("entities"), dict) else None
    if ent is None:
        people = [s for s in speakers if s in people_ok] or [x for x in m_people if x in people_ok]
        works = [w for w in m_works if w in works_ok]
        orgs = [o for o in (got.get("organizations") or []) if o in ORGS]
        lines.append("entities:")
        lines += yaml_list("people", list(dict.fromkeys(people)), "  ")
        lines += yaml_list("works", list(dict.fromkeys(works)), "  ")
        if orgs:
            lines += yaml_list("organizations", list(dict.fromkeys(orgs)), "  ")
        have_people, have_works = people, works
    else:
        have_people, have_works = ent.get("people") or [], ent.get("works") or []
    lines.append("mentions:")
    lines += yaml_list("people", [x for x in dict.fromkeys(m_people) if x not in have_people and re.match(r"^[一-鿿·]{2,6}$", x)], "  ")
    lines += yaml_list("works", [x for x in dict.fromkeys(m_works) if x not in have_works and x.startswith(("宝可梦", "Pokémon"))], "  ")
    block = nl.join(lines) + nl
    # in front of the closing --- of the front matter
    new = text[:m.end(1)] + nl + block.rstrip("\r\n") + text[m.end(1):]
    io.open(path, "w", encoding="utf-8", newline="").write(new)
    yaml.safe_load(front_matter(new)[1].group(1))    # it must still parse


NOT_PEOPLE = {"引言", "履历档案", "4Gamer", "Dwango独立游戏负责人", "编辑部", "记者", "主持人", "旁白"}


def people_from_speakers(fm, people_ok):
    """entities.people for a post that has none: whoever answers in the transcript, when the
    name is a full one (surname and given name, or the initials Game Freak's recruit pages
    use) - a bare surname or a nickname is not a person the library can file."""
    _, speakers = transcript(fm)
    out = []
    for s in speakers:
        n = re.sub(r"[ 　]+", "", s)
        if n in NOT_PEOPLE or n in out:
            continue
        if n in people_ok or re.match(r"^[A-Z]\.[A-Z]\.$", n) or (re.match(r"^[一-鿿぀-ヿ·]{3,8}$", n) and not re.search(r"[・、/]", n)):
            out.append(n)
    return out


def fill_people(only=None, dry=False):
    people_ok = {e["name"] for e in yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) if e.get("kind") not in ("character", "figure")}
    n_done = 0
    for p in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        if only and not any(o in p for o in only):
            continue
        text = io.open(p, encoding="utf-8", newline="").read()
        try:
            fm, m = front_matter(text)
        except yaml.YAMLError:
            continue
        if not fm or fm.get("layout") not in ("interview-editorial", "parallel-translation") or not fm.get("parallel_items"):
            continue
        ent = fm.get("entities") if isinstance(fm.get("entities"), dict) else None
        if ent and ent.get("people"):
            continue
        people = people_from_speakers(fm, people_ok)
        if not people:
            continue
        nl = m.group(2)
        block = nl.join(yaml_list("people", people, "  "))
        head = text[:m.end(1)]
        if ent is not None and re.search(r"(?m)^entities:[ \t]*\r?$", head):
            if re.search(r"(?m)^  people: \[\][ \t]*\r?$", head):        # an empty list left by an earlier pass
                head = re.sub(r"(?m)^  people: \[\][ \t]*\r?$", lambda mm: block, head, count=1)
            else:
                head = re.sub(r"(?m)^entities:[ \t]*\r?$", lambda mm: "entities:" + nl + block, head, count=1)
        else:
            head = head + nl + "entities:" + nl + block
        new = head + text[m.end(1):]
        yaml.safe_load(front_matter(new)[1].group(1))
        print(f"  {Path(p).name[:60]:60s} {people}")
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(new)
        n_done += 1
    print(f"people: {n_done} posts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--people", action="store_true", help="fill entities.people from the transcript's speakers where a post has none")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.people:
        fill_people(a.only, a.dry_run)
        return
    todo = candidates(a.only)
    print(f"{len(todo)} posts without a summary")
    if a.list:
        for p, _, fm, _ in todo:
            print("  ", Path(p).name, "| entities" if fm.get("entities") else "| no entities", "|", len(fm["parallel_items"]), "items")
        return
    people_ok = {e["name"] for e in yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) if e.get("kind") not in ("character", "figure")}
    works_ok = {w["name"] for w in yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8"))}

    def one(job):
        p, text, fm, m = job
        body, speakers = transcript(fm)
        try:
            got = ask(fm, body)
        except Exception as exc:
            return Path(p).name, f"!! {exc}"
        if a.dry_run:
            return Path(p).name, f"{(got.get('summary') or '')[:80]}… | {got.get('dek')} | {got.get('topics')} | people {got.get('people')} | speakers {speakers}"
        apply(p, text, fm, m, got, people_ok, works_ok)
        return Path(p).name, f"ok | {got.get('dek')} | {got.get('topics')}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for name, msg in ex.map(one, todo):
            print(f"  {name[:60]:60s} {msg}")


if __name__ == "__main__":
    main()
