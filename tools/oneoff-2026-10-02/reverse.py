"""reverse.py <post> <url>... — which runs of the source pages are missing from the post.
Source text is cut into 30-char windows (after the audit tool's normalisation); a window is "carried" when ≥ 60% of its
6-grams are in the post's originals. Prints the coverage and the longest missing stretches (to tell chrome from text)."""
import sys
from pathlib import Path

DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
sys.path.insert(0, "P:/WEBSITE/pokeamice-main (1)/pokeamice-main/tools")
import audit_source_fidelity as A  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
post, urls = sys.argv[1], sys.argv[2:]
d, _ = A.front_matter(str(DOCS / post))
P = set()
for x in A.segments(d):
    if isinstance(x, dict):
        P |= A.grams(A.norm(x.get("original")))
src = "".join(A.norm(A.fetch(u)[0]) for u in urls)
W = 30
marks = []
for i in range(0, len(src) - W, W):
    w = src[i:i + W]
    g = A.grams(w)
    marks.append(len(g & P) / max(1, len(g)) >= 0.6)
print(f"{post[7:70]}: {sum(marks)}/{len(marks)} windows carried ({100 * sum(marks) // max(1, len(marks))}%)")
# missing stretches
runs, start = [], None
for k, m in enumerate(marks + [True]):
    if not m and start is None:
        start = k
    elif m and start is not None:
        runs.append((k - start, start))
        start = None
for n, s in sorted(runs, reverse=True)[:8]:
    print(f"   missing {n * W:>5} chars: {src[s * W:s * W + (min(n * W, 400) if n * W > 1000 else 110)]}")
