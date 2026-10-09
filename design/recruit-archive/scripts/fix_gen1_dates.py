"""Dates of the 2013-2019 numbered recruit pages, from the recruit index snapshots (run once after import)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
IDX15 = "招聘首页 2015-09-15 的快照还没有编号访谈、2015-10-21 的已有"
FIX = {
    # stem: (date, basis)  - for posts the importer wrote (recruit block present)
    "2015-08-01-interview-gamefreak-gear-tembo-turner": ("2015-10-12", IDX15 + "（这一页 Wayback 首见 2015-10-12）；2017-01 起同一网址换成《GIGA WRECKER》的访谈"),
    "2015-10-01-interview-gamefreak-recruit-designers": ("2015-10-21", IDX15 + "；2017-03 起同一网址换成另一组设计师"),
    "2015-10-01-interview-gamefreak-recruit-planners": ("2015-10-21", IDX15),
    "2015-10-01-interview-gamefreak-recruit-programmers": ("2015-10-21", IDX15),
    "2017-03-01-interview-gamefreak-gear-gigawrecker": ("2017-01-28", "同一网址 2016-11-22 的快照仍是《TEMBO》的访谈，2017-01-28 已是这一篇"),
    "2017-06-01-interview-gamefreak-rnd-ta-taya-kk": ("2017-03-29", "同一网址 2016-03-30 的快照仍是 2015 年的研究开发部访谈，2017-03-29 已是这一篇"),
    "2017-09-01-interview-gamefreak-recruit-cross-industry": ("2017-01-19", "招聘首页 2016-11-20 的快照还没有、2017-01-19 的已有（这一页 Wayback 首见 2017-02-12）"),
    "2017-03-29-interview-gamefreak-recruit-designers-2017": ("2017-03-29", "同一网址 2016-03-02 的快照仍是 2015 年那组设计师，2017-03-29 已换成这一篇"),
    "2019-10-19-interview-gamefreak-rnd-2019": ("2017-04-01", "同一网址的上一份快照（2017-03-29）还是 TA 篇，下一份（2019-10-19）已是这一篇；正文说研究开发部「设立第 3 年」（2015 年 4 月成立），推定写于 2017 年 4 月之后"),
}
# faithful posts with no recruit block yet: (page, version, capture, date, basis)
STAMP = {
    "2015-09-01-interview-gamefreak-rnd-launch-taya-mi": ("interview_02", "2015-10-26", "20151026024157", "2015-10-21", IDX15 + "；2017-03 起同一网址换成 TA 篇"),
    "2013-11-01-interview-gamefreak-recruit-3d-graphics-to-fk": ("interview_1", "2013-10-22", "20131022004448", "2013-10-20", "招聘首页 2013-04-03 的快照还没有、2013-10-20 的已有；2016-11 至 2017-01 之间撤下"),
    "2013-11-01-interview-gamefreak-recruit-programmer-tt-mi": ("interview_2", "2013-12-28", "20131228170851", "2013-10-20", "招聘首页 2013-04-03 的快照还没有、2013-10-20 的已有（这一页 Wayback 首见 2013-12-28）；2016-11 至 2017-01 之间撤下"),
}

for stem, (date, basis) in FIX.items():
    p = ROOT / "_posts" / f"{stem}.md"
    t = p.read_text("utf-8")
    t, n1 = re.subn(r"^date: \S+", f"date: {date}", t, count=1, flags=re.M)
    t, n2 = re.subn(r"^  date_basis: .*$", lambda m: f"  date_basis: {basis}", t, count=1, flags=re.M)
    t, n3 = re.subn(r"^era: '?\d{4}'?$", f"era: '{date[:4]}'", t, count=1, flags=re.M)
    assert n1 and n2, stem
    p.write_text(t, "utf-8", newline="")
    print("fixed", stem, date)

for stem, (page, ver, cap, date, basis) in STAMP.items():
    p = ROOT / "_posts" / f"{stem}.md"
    t = p.read_text("utf-8")
    if "\nrecruit:" in t[:5000]:
        continue
    nl = "\r\n" if "\r\n" in t[:2000] else "\n"
    m = re.search(r"^date: .*$", t, re.M)
    tm = re.search(r"\d{2}:\d{2}:\d{2} \+\d{4}", m.group(0))
    block = nl.join([f"date: {date} {tm.group(0) if tm else '10:00:00 +0900'}", "recruit:", f"  page: {page}", f"  version: '{ver}'",
                     f"  capture: '{cap}'", f"  date_basis: {basis}"])
    t = t[:m.start()] + block + t[m.end():]
    t = re.sub(r"^era: '?\d{4}'?$", f"era: '{date[:4]}'", t, count=1, flags=re.M)
    p.write_text(t, "utf-8", newline="")
    print("stamped", stem, date)
