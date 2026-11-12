"""Guard against merging anonymous initials across unrelated source pages."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def front(path):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", path.read_text(encoding="utf-8"), re.S)
    assert match, f"Missing front matter: {path}"
    return yaml.load(match.group(1), Loader=LOADER) or {}


def main():
    people = yaml.load((ROOT / "_data/people.yml").read_text(encoding="utf-8"), Loader=LOADER)
    by_slug = {p["slug"]: p for p in people}
    assert len(by_slug) == len(people), "Duplicate person slug"
    profiles = yaml.load((ROOT / "_data/people_profiles.yml").read_text(encoding="utf-8"), Loader=LOADER)
    profile_slugs = {p["slug"] for p in profiles}
    posts = {p.stem: front(p) for p in (ROOT / "_posts").glob("*.md")}
    checked = 0
    for legacy in people:
        if legacy.get("kind") != "disambiguation":
            continue
        initial = legacy["name"]
        assert legacy["slug"] not in profile_slugs, f"Merged biography: {initial}"
        assert all(initial not in (p.get("aliases") or []) for p in people), f"Global alias: {initial}"
        old_page = front(ROOT / "_pages/people" / (legacy["slug"] + ".md"))
        assert old_page["layout"] == "person-disambiguation"
        assert old_page["permalink"] == f"/people/{legacy['slug']}/"
        for slug in legacy["disambiguation"]:
            scoped = by_slug[slug]
            scope, name = scoped["identity_scope"], scoped["name"]
            assert not scoped.get("aliases"), f"Unscoped alias: {slug}"
            assert name in (posts[scope].get("entities") or {}).get("people", [])
            assert any(r.get("speaker") == name for r in posts[scope].get("parallel_items", []))
            assert (ROOT / "_pages/people" / (slug + ".md")).exists()
            for stem, post in posts.items():
                if stem != scope:
                    assert name not in (post.get("entities") or {}).get("people", []), (slug, stem)
            checked += 1
        for stem, post in posts.items():
            assert initial not in (post.get("entities") or {}).get("people", []), (initial, stem)
            assert not any(r.get("speaker") == initial for r in post.get("parallel_items", [])), (initial, stem)
    print(f"PASS: {checked} source-scoped identities; legacy URLs retained without merged biographies")


if __name__ == "__main__":
    main()
