import sys
from pathlib import Path
import yaml
import json

sys.stdout.reconfigure(encoding="utf-8")

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

# build url and title lookup
url_lookup = {}
title_lookup = {}
for it in catalog:
    url = it.get("url")
    title = it.get("title")
    otitle = it.get("original_title")
    if url:
        url_lookup[url] = it
    if title:
        title_lookup[title.lower()] = it
    if otitle:
        title_lookup[otitle.lower()] = it

posts = sorted(Path("_posts").glob("*interview*.md"))
updated_count = 0

for p in posts:
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        continue
    try:
        fm = yaml.safe_load(parts[1])
    except:
        continue

    src = fm.get("source")
    if isinstance(src, dict) and src.get("url"):
        continue  # Already has structured source

    orig_link = fm.get("original_link") or fm.get("source_url")
    source_name = fm.get("source_name")
    post_title = fm.get("title", "")
    
    source_dict = None
    if orig_link:
        # Check if we have an entry in catalog
        cat_entry = url_lookup.get(orig_link)
        title = source_name or (cat_entry.get("original_title") or cat_entry.get("title") if cat_entry else "") or post_title
        source_dict = {
            "title": title,
            "url": orig_link
        }
    else:
        # Match by title or file name
        for it in catalog:
            it_title = it.get("title", "")
            it_otitle = it.get("original_title", "")
            it_url = it.get("url", "")
            if not it_url:
                continue
            if it_title and it_title in post_title:
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            # match by file name keywords
            fn = p.stem.lower()
            if "nom-genesis-gamefreak" in fn and "0007/gfreak" in it_url:
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "g4tv-platinum-masuda-kawachimaru" in fn and "g4tv" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "pokemon-com-hgss-masuda-morimoto" in fn and "pokemon.com" in it_url.lower() and "hgss" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "1up-black-white-how-pokemon-get-made" in fn and "1up" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "onm-xy-sugimori" in fn and "officialnintendomagazine" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "gamefreak-recruit-programmer-tt-mi" in fn and "recruit/programmer" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "tpc-leaders-challenge" in fn and "interview01.html" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "tpc-youth-roundtable" in fn and "roundtable.html" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "pokemon-recruit-business-anatomy" in fn and "business.html" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "pokemon-recruit-world-egami" in fn and "world.html" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "eurogamer-letsgo-masuda" in fn and "eurogamer.net" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "gamefreak-crosstalk-designer" in fn and "crosstalk-designer" in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break
            if "gamefreak-crosstalk-programmer" in fn and "crosstalk-programmer" in it_url.lower() and "game-programmer" not in it_url.lower():
                source_dict = {"title": it_otitle or it_title, "url": it_url}
                break

    if source_dict:
        # Update frontmatter
        fm["source"] = source_dict
        # Rewrite file preserving YAML structure
        new_fm_str = yaml.dump(fm, allow_unicode=True, sort_keys=False)
        new_content = f"---\n{new_fm_str}---\n{parts[2].lstrip()}"
        p.write_text(new_content, encoding="utf-8")
        updated_count += 1
        print(f"Updated {p.name} -> source: {source_dict['url']}")

print(f"\nTotal posts updated with normalized source: {updated_count}")
