import json
import csv
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_corpus_audit():
    catalog_path = 'data/pokemon_1000_interviews.json'
    csv_path = 'data/pokemon_1000_interviews.csv'
    posts_dir = '_posts'
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    total_catalog = len(catalog)
    imported = [i for i in catalog if i.get('status') == 'imported' or i.get('imported') is True]
    unimported = [i for i in catalog if not (i.get('status') == 'imported' or i.get('imported') is True)]
    
    # Check link integrity
    broken_links = []
    missing_links = []
    for item in imported:
        pf = item.get('post_file')
        if not pf:
            missing_links.append(item['id'])
        elif not os.path.exists(pf):
            broken_links.append((item['id'], pf))
            
    # Check posts on disk
    all_posts = glob.glob(os.path.join(posts_dir, '*.md')) + glob.glob(os.path.join(posts_dir, '*.markdown'))
    total_posts = len(all_posts)
    
    parallel_posts = 0
    layout_counts = {}
    for pf in all_posts:
        with open(pf, 'r', encoding='utf-8', errors='ignore') as f:
            head = f.read(2500)
        if 'parallel_items:' in head:
            parallel_posts += 1
        for l in ['interview-editorial', 'gamefreak-director', 'gamefreak-legacy-blog', 'single']:
            if f'layout: {l}' in head:
                layout_counts[l] = layout_counts.get(l, 0) + 1
                break
        else:
            layout_counts['other'] = layout_counts.get('other', 0) + 1

    # Check CSV sync
    csv_rows = 0
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            csv_rows = sum(1 for _ in reader) - 1
            
    return {
        'catalog_total': total_catalog,
        'catalog_imported': len(imported),
        'catalog_unimported': len(unimported),
        'imported_percentage': round(len(imported) / total_catalog * 100, 2),
        'unimported_percentage': round(len(unimported) / total_catalog * 100, 2),
        'broken_links_count': len(broken_links),
        'missing_links_count': len(missing_links),
        'total_posts': total_posts,
        'parallel_posts': parallel_posts,
        'parallel_percentage': round(parallel_posts / total_posts * 100, 2),
        'layout_counts': layout_counts,
        'csv_rows': csv_rows,
        'csv_synced': csv_rows == total_catalog,
        'broken_links': broken_links,
        'missing_links': missing_links
    }

if __name__ == '__main__':
    res = run_corpus_audit()
    print(json.dumps(res, ensure_ascii=False, indent=2))
