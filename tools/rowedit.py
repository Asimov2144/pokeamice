"""Edit single fields of single rows of a post's parallel_items / translation_segments without
re-dumping the YAML (so the diff is the edit and nothing else).

    from rowedit import Post
    p = Post("_posts/2009-03-23-interview-gamepro-platinum-masuda-kawachimaru.md")
    p.rows[5]["caption"]                      # parsed value
    p.set(5, "caption", "……")                 # replace (or add) one field of row 5
    p.set(5, "caption_original", "……")
    p.drop([0, 1])                            # remove whole rows
    p.meta("author", "McKinley Noble")        # a top-level one-line field of the front matter
    p.save()                                  # writes with the file's own line endings; re-parses to prove it loads

Rows are addressed by their position in the list (the numbers the audits print). Edits are applied
from the bottom up so the numbers stay valid while you queue them.
"""
import json
import re
from pathlib import Path

import yaml

L = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
LISTS = ("parallel_items", "translation_segments")


def _scalar_end(lines, n, m):
    """last line index of the scalar that starts on line n (quoted scalars may run on)"""
    val = m.group(2)
    try:
        yaml.safe_load("v: " + val)
        return n
    except yaml.YAMLError:
        pass
    if val.strip() in ("|", ">", "|-", ">-", "|+", ">+"):
        e = n
        while e + 1 < len(lines) and (lines[e + 1].startswith("    ") or not lines[e + 1].strip()):
            e += 1
        return e
    for e in range(n + 1, min(n + 800, len(lines))):
        try:
            yaml.safe_load("v: " + "\n".join([val] + lines[n + 1:e + 1]))
            return e
        except yaml.YAMLError:
            continue
    return n


class Post:
    def __init__(self, path):
        self.path = Path(path)
        raw = self.path.read_bytes().decode("utf-8-sig")
        self.bom = self.path.read_bytes().startswith(b"\xef\xbb\xbf")
        self.crlf = "\r\n" in raw[:3000]
        self.lines = raw.replace("\r\r\n", "\n").replace("\r\n", "\n").split("\n")
        self.key = None
        self._index()
        self.edits = []       # ("set", row, field, value) | ("drop", row) | ("meta", field, value)

    def _index(self):
        """where the rows are: the list may be written flush left ("- key") or indented ("  - key")"""
        start = None
        for n, l in enumerate(self.lines):
            m = re.match(r"^(parallel_items|translation_segments):\s*$", l)
            if m:
                self.key, start = m.group(1), n
                break
        if start is None:
            raise ValueError("no row list in " + str(self.path))
        self.ind = ""
        for l in self.lines[start + 1:]:
            m = re.match(r"^(\s*)- ", l)
            if m:
                self.ind = m.group(1)
                break
            if l.strip() and not l.startswith(" "):
                break
        dash = self.ind + "- "
        starts, end = [], len(self.lines)
        for n in range(start + 1, len(self.lines)):
            l = self.lines[n]
            if l.startswith(dash):
                starts.append(n)
            elif l.rstrip() == "---" or (l and not l.startswith((" ", "-"))):
                end = n                                   # the closing --- of the front matter, or the next top-level key
                break
        self.starts, self.ends = starts, starts[1:] + [end]
        text = "\n".join(self.lines)
        fm = re.match(r"---\n(.*?)\n---", text, re.S)
        self.data = yaml.load(fm.group(1), Loader=L)
        self.rows = self.data[self.key]

    # ---- queueing
    def set(self, row, field, value):
        self.edits.append(("set", row, field, value))

    def drop(self, rows):
        for r in rows:
            self.edits.append(("drop", r))

    def meta(self, field, value):
        self.edits.append(("meta", field, value))

    # ---- applying
    @staticmethod
    def _dump(field, value, indent):
        if isinstance(value, str):
            return f"{indent}{field}: {json.dumps(value, ensure_ascii=False)}"
        return indent + yaml.safe_dump({field: value}, allow_unicode=True, width=10 ** 6, sort_keys=False).rstrip("\n")

    def _apply_set(self, row, field, value):
        a, b = self.starts[row], self.ends[row]
        for n in range(a, b):
            first = n == a
            pat = r"^" + re.escape(self.ind) + (r"(- )" if first else r"(  )") + re.escape(field) + r": (.*)$"
            m = re.match(pat, self.lines[n])
            if m:
                e = _scalar_end(self.lines, n, m)
                if value is None:                                      # set(row, field, None) removes the field
                    if first:
                        raise ValueError("cannot remove the first key of a row: " + field)
                    del self.lines[n:e + 1]
                    return
                prefix = self.ind + ("- " if first else "  ")
                new = self._dump(field, value, "").rstrip()
                self.lines[n:e + 1] = [prefix + new]
                return
        if value is None:
            return
        # not there: add it after the last line of the row (before any trailing blank)
        last = b
        while last > a + 1 and not self.lines[last - 1].strip():
            last -= 1
        self.lines.insert(last, self._dump(field, value, self.ind + "  "))

    def _apply_drop(self, row):
        del self.lines[self.starts[row]:self.ends[row]]

    def _apply_meta(self, field, value):
        for n, l in enumerate(self.lines):
            if l.startswith("---") and n > 0:
                break
            m = re.match(r"^" + re.escape(field) + r": (.*)$", l)
            if m:
                self.lines[n] = self._dump(field, value, "")
                return
        # add before the row list
        at = next(n for n, l in enumerate(self.lines) if re.match(r"^(parallel_items|translation_segments):\s*$", l))
        self.lines.insert(at, self._dump(field, value, ""))

    def save(self):
        rows_first = sorted([e for e in self.edits if e[0] in ("set", "drop")], key=lambda e: -e[1])
        for e in rows_first:
            if e[0] == "set":
                self._apply_set(e[1], e[2], e[3])
            else:
                self._apply_drop(e[1])
            self._index_keep()
        for e in [e for e in self.edits if e[0] == "meta"]:
            self._apply_meta(e[1], e[2])
        text = "\n".join(self.lines)
        yaml.load(re.match(r"---\n(.*?)\n---", text, re.S).group(1), Loader=L)          # it must still load
        if self.crlf:
            text = text.replace("\n", "\r\n")
        self.path.write_bytes((b"\xef\xbb\xbf" if self.bom else b"") + text.encode("utf-8"))
        self.edits = []

    def _index_keep(self):
        """row spans move when a row is edited or dropped: recompute them (the parsed data is left alone)"""
        keep = (self.data, self.rows)
        self._index()
        self.data, self.rows = keep
