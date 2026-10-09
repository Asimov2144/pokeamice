"""Give the recruit posts that are already faithful their `recruit:` block and their date - by editing
lines in place (no YAML round trip), so a parallel session's edits to the same files stay mergeable.

Usage: python design/recruit-archive/scripts/stamp_posts.py [--dry]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POSTS = ROOT / "_posts"

FIRST = "2019 年 12 月招聘站改版时的首批人物页（Wayback 首见 2019-12-11）"
BATCH_2022 = "招聘首页 2021-12-13 的快照还没有、2022-03-11 的已有，与策划对谈（Wayback 首见 2022-01-25）同批"
BATCH_2024 = "页面素材批次 ?20240213；Wayback 首见 2024-02-29，2022-10-15 的招聘首页还没有这一篇"

STAMPS = {
    # stem: (page, version, capture, date, basis)
    "2019-04-01-interview-gamefreak-recruit-pg-yi": ("interview-pg-yi", "2019-12-11", "20191211222205", "2019-12-11",
                                                       FIRST + "；2020-10-24 至 12-16 之间，招聘首页上换成了程序员 H.T. 的页面"),
    "2019-04-01-interview-gamefreak-recruit-pl-my": ("interview-pl-my", "2019-12-11", "20191211222535", "2019-12-11",
                                                       FIRST + "；2021-12-13 至 2022-03-11 之间从招聘首页撤下"),
    "2021-12-27-interview-gamefreak-recruit-concept-artist-fk": ("interview-gr-fk", "2019-12-11", "20191211221312", "2019-12-11", FIRST),
    "2021-12-27-interview-gamefreak-recruit-designer-ek": ("interview-gr-ek", "2019-12-11", "20191211222214", "2019-12-11", FIRST),
    "2021-12-27-interview-gamefreak-recruit-designer-ht": ("interview-gr-ht", "2019-12-11", "20191211225544", "2019-12-11", FIRST),
    "2021-12-27-interview-gamefreak-recruit-designer-kn": ("interview-gr-kn", "2019-12-11", "20191211233647", "2019-12-11", FIRST),
    "2021-12-27-interview-gamefreak-recruit-programmer-km": ("interview-pg-km", "2019-12-11", "20191211215625", "2019-12-11", FIRST),
    "2021-12-27-interview-gamefreak-recruit-programmer-ko": ("interview-pg-ko", "2019-12-11", "20240229104429", "2019-12-11",
                                                               FIRST + "；本篇依据 2024-02-29 的快照，与首版只差个别字句"),
    "2021-12-27-interview-gamefreak-recruit-planner-kf": ("interview-pl-kf", "2019-12-11", "20240229104450", "2019-12-11",
                                                            FIRST + "；本篇依据 2024-02-29 的快照，与首版只差个别字句"),
    "2021-12-27-interview-gamefreak-recruit-programmer-ht": ("interview-pg-ht", "2020-11-13", "20201113062528", "2020-11-13",
                                                               "2020-10-24 的招聘首页还是 Y.I.，2020-12-16 已换成这一页（Wayback 首见 2020-11-13）"),
    "2021-12-27-interview-gamefreak-recruit-designer-mi": ("interview-gr-mi", "2022-06-28", "20220628153440", "2021-12-27", BATCH_2022),
    "2021-12-27-interview-gamefreak-recruit-planner-rm": ("interview-pl-rm", "2022-04-25", "20240229104432", "2021-12-27",
                                                            BATCH_2022 + "；本篇依据 2024-02-29 的快照，与首版只差个别字句"),
    "2021-12-27-interview-gamefreak-recruit-ta-tk": ("interview-ta-tk", "2022-06-28", "20220628160831", "2021-12-27", BATCH_2022),
    "2021-12-27-interview-gamefreak-recruit-programmer-tk": ("interview-pg-tk", "2025-07-14", "20250714164000", "2025-03-28",
                                                               "2024-09-15 的招聘首页还没有这张卡、2025-03-28 的已有（页面首次快照 2025-07-14）"),
    "2021-12-27-interview-gamefreak-crosstalk-planner": ("crosstalk-planner", "2022-01-25", "20220125155308", "2021-12-27", BATCH_2022),
    "2021-12-27-interview-gamefreak-crosstalk-programmer": ("crosstalk-programmer", "2024-02-29", "20240229104525", "2024-02-13",
                                                              "页面素材批次 ?20240213；2022-10-15 的快照仍是旧版（T.T. × K.I.），2024-02-29 已是这一版"),
    "2021-12-27-interview-gamefreak-crosstalk-designer": ("crosstalk-designer", "2022-10-15", "20221015223633", "2022-10-15",
                                                            "2022-04-25 的快照仍是旧版（T.U. × J.K.），2022-10-15 已是这一版"),
    "2021-12-27-interview-gamefreak-crosstalk-scenario": ("crosstalk-scenario", "2025-02-14", "20250214192116", "2024-02-13",
                                                            BATCH_2024 + "；本篇译自 2025-02 起的现行版，首版还有 S.N."),
}

# small field fixes that ride along (exact line -> new line)
LINE_FIXES = {
    "2021-12-27-interview-gamefreak-crosstalk-programmer": [("interviewee: M.O., T.T., 档案", "interviewee: T.T.、M.O.")],
}


def stamp(stem, page, version, capture, date, basis, dry):
    p = POSTS / f"{stem}.md"
    t = p.read_text("utf-8")
    nl = "\r\n" if "\r\n" in t[:2000] else "\n"
    head, sep, rest = t.partition(nl + "---" + nl)
    if "\nrecruit:" in head:
        print(f"skip {stem}: already stamped")
        return
    m = re.search(r"^date: .*$", head, re.M)
    assert m, stem
    time_part = re.search(r"\d{2}:\d{2}:\d{2} \+\d{4}", m.group(0))
    new_date = f"date: {date} {time_part.group(0) if time_part else '10:00:00 +0900'}"
    block = nl.join([new_date, "recruit:", f"  page: {page}", f"  version: '{version}'", f"  capture: '{capture}'", f"  date_basis: {basis}"])
    head = head[:m.start()] + block + head[m.end():]
    for old, new in LINE_FIXES.get(stem, []):
        assert old in head, (stem, old)
        head = head.replace(old, new)
    out = head + sep + rest
    print(f"{'(dry) ' if dry else ''}{stem}: {m.group(0)} -> {new_date}")
    if not dry:
        p.write_text(out, "utf-8", newline="")


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for stem, args in STAMPS.items():
        stamp(stem, *args, dry=dry)
