"""Run a tool over posts that someone else is editing, without touching their edits.

    python tools/head-base-run.py --posts _posts/a.md _posts/b.md -- python tools/augment-images.py --all
    python tools/head-base-run.py --posts-file list.txt -- python tools/augment-images.py --all

For each named post the working copy is set aside, HEAD's version is put in its place, the
command runs (and edits the file as it likes), the result is stored as a blob for the commit
(`data/cache_web/pending_blobs.json`, path -> blob id, which the commit step feeds to
`git update-index --cacheinfo`), and the other person's edits are laid back over the result
with `git apply` so their working copy now carries both. When their patch will not apply on
top of the change, their copy is restored untouched and the post is listed for a second,
plain run of the tool (`--only <post> --force`), which lands the same rows in their copy.

Nothing here stages or commits: it prepares blobs and leaves the working tree holding
everyone's work.
"""
import io
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING = os.path.join(ROOT, "data", "cache_web", "pending_blobs.json")
G = ["git", "-c", "core.quotepath=false"]


def git(*args, inp=None, binary=False, check=True):
    r = subprocess.run(G + list(args), cwd=ROOT, capture_output=not binary, stdout=subprocess.PIPE if binary else None,
                       text=not binary, encoding=None if binary else "utf-8", input=inp)
    if check and r.returncode:
        raise RuntimeError(" ".join(args[:3]) + ": " + (r.stderr if not binary else ""))
    return r.stdout


def main():
    argv = sys.argv[1:]
    sep = argv.index("--")
    if "--posts-file" in argv:              # one path per line; a name with spaces or CJK survives that way
        posts = [l.strip().replace("\\", "/") for l in io.open(argv[argv.index("--posts-file") + 1], encoding="utf-8") if l.strip()]
    else:
        posts = [p.replace("\\", "/") for p in argv[argv.index("--posts") + 1:sep]]
    cmd = argv[sep + 1:]
    theirs, backup = {}, {}
    for p in posts:
        patch = git("diff", "--binary", "HEAD", "--", p, binary=True)
        theirs[p] = patch
        backup[p] = io.open(os.path.join(ROOT, p), "rb").read()
        head = git("show", f"HEAD:{p}", binary=True)
        io.open(os.path.join(ROOT, p), "wb").write(head)
    print(f"{len(posts)} posts set to HEAD; running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=ROOT, check=False)
    finally:
        pending = json.load(io.open(PENDING, encoding="utf-8")) if os.path.exists(PENDING) else {}
        redo = []
        for p in posts:
            full = os.path.join(ROOT, p)
            mine = io.open(full, "rb").read()
            head = git("show", f"HEAD:{p}", binary=True)
            if mine != head:
                blob = git("hash-object", "-w", "--", p).strip()
                pending[p] = blob
            if not theirs[p].strip():
                continue                       # nothing of theirs to lay back
            if mine == head:
                io.open(full, "wb").write(backup[p])
                continue
            with tempfile.NamedTemporaryFile("wb", suffix=".patch", delete=False) as tf:
                tf.write(theirs[p])
                pf = tf.name
            r = subprocess.run(G + ["apply", "-C1", "--recount", pf], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            os.unlink(pf)
            if r.returncode:
                io.open(full, "wb").write(backup[p])
                redo.append(p)
                print(f"  their edits do not lay over the change: {p} - restored their copy; run the tool on it again")
            else:
                print(f"  {p}: their edits laid back over the change")
        io.open(PENDING, "w", encoding="utf-8", newline="\n").write(json.dumps(pending, indent=1))
        print(f"{len(pending)} blobs pending for the commit -> {os.path.relpath(PENDING, ROOT)}")
        if redo:
            print("second run needed for:", *redo, sep="\n  ")


if __name__ == "__main__":
    main()
