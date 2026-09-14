import re, html
from pathlib import Path

def parse_taidan_page(filename):
    f = Path("data/cache_nom") / filename
    raw = f.read_bytes().decode("cp932", errors="replace")
    raw = re.sub(r"<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->", "", raw, flags=re.DOTALL | re.I)
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.I)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.I)

    # Title
    m_title = re.search(r"<title>(.*?)</title>", raw, re.I)
    title = m_title.group(1).strip() if m_title else filename

    # Body
    body_m = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.I)
    body = body_m.group(1) if body_m else raw

    # Convert breaks and table cells
    body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
    body = re.sub(r"</?(p|tr|td|div)[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", "", body)

    lines = [html.unescape(l).strip() for l in body.split("\n")]
    lines = [l for l in lines if l and not l.startswith("★") and "ページ" not in l and "N.O.M" not in l and "バックナンバー" not in l]

    dialogues = []
    current_speaker = ""
    current_text = []

    for l in lines:
        m = re.match(r"^([^\s>]{1,10})(&gt;>|>>|>)(.*)$", l)
        if m:
            if current_text:
                dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_text = []
            current_speaker = m.group(1).strip()
            rest = m.group(3).strip()
            if rest:
                current_text.append(rest)
        else:
            if l.endswith("？") or l.endswith("ですか？") or l.endswith("ますか？") or l.endswith("でしょうか？"):
                if not current_speaker or (not l.startswith("そうですね") and not l.startswith("はい")):
                    if current_text:
                        dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})
                        current_text = []
                    current_speaker = "N.O.M 采访者"
                    current_text.append(l)
                    continue
            current_text.append(l)

    if current_text:
        dialogues.append({"speaker": current_speaker, "text": " ".join(current_text)})

    return title, dialogues

for p in range(1, 5):
    t, d = parse_taidan_page(f"nom_0007_taidan1_page0{p}.html")
    print(f"taidan1 p0{p}: {t} -> {len(d)} items, speakers = {set(x['speaker'] for x in d)}")

for p in range(1, 5):
    t, d = parse_taidan_page(f"nom_0007_taidan2_page0{p}.html")
    print(f"taidan2 p0{p}: {t} -> {len(d)} items, speakers = {set(x['speaker'] for x in d)}")
