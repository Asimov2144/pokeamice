import re, sys, yaml
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path("P:/WEBSITE/pokeamice-main (1)/pokeamice-main")
POSTS = ROOT / "_posts"
SCR = Path("C:/Users/2144j/AppData/Local/Temp/claude/P--WEBSITE-pokeamice/7afd9ba7-f41b-4a1f-8271-385fc41af425/scratchpad")
FM = re.compile(r"\A\ufeff?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.S)
L = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")

def read_post(path):
    """Return (text_with_LF, eol) so edits can be done on LF and written back with the original eol."""
    raw = Path(path).read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol

def write_post(path, text_lf, eol):
    out = text_lf.replace("\n", eol) if eol == "\r\n" else text_lf
    Path(path).write_bytes(out.encode("utf-8"))

def split_fm(text_lf):
    m = re.match(r"\A\ufeff?---\n(.*?)\n---\n", text_lf, re.S)
    if not m: return None, None, text_lf
    return m.group(1), text_lf[m.end():], text_lf[:m.end()]

def load_fm(fm_text):
    try:
        return yaml.load(fm_text, Loader=L) or {}
    except Exception:
        return None
