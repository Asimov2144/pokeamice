"""Create a focused annotation containing selected page/region pairs."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Select regions from a magazine annotation JSON.")
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--select", action="append", required=True, help="page_name::region_id")
    args = parser.parse_args()

    requested = set()
    for value in args.select:
        if "::" not in value:
            raise SystemExit(f"Invalid selection: {value}")
        page_name, region_id = value.rsplit("::", 1)
        requested.add((page_name, region_id))

    source = json.loads(Path(args.annotation).read_text(encoding="utf-8"))
    result = deepcopy(source)
    result["title"] = f"{source.get('title') or 'annotation'}-focused"
    result["pages"] = []
    found = set()
    for page in source.get("pages") or []:
        page_name = str(page.get("name") or "")
        regions = []
        for region in page.get("regions") or []:
            key = (page_name, str(region.get("id") or ""))
            if key in requested:
                regions.append(region)
                found.add(key)
        if regions:
            selected_page = deepcopy(page)
            selected_page["regions"] = regions
            result["pages"].append(selected_page)

    missing = sorted(requested - found)
    if missing:
        raise SystemExit("Missing selections: " + ", ".join(f"{page}::{region}" for page, region in missing))
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Selected {len(found)} region(s) across {len(result['pages'])} page(s): {out_path}")


if __name__ == "__main__":
    main()
