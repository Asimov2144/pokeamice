"""Read-only corpus audit; prints JSON, never changes article content."""
import json, re, sys
from pathlib import Path
from collections import Counter
import yaml
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
front = re.compile(r'\A\ufeff?---\s*\n(.*?)\n---\s*(?:\n|$)', re.S)
loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
counts, issues = Counter(), []
def flag(p, category, text, idx=None, line=None):
    issues.append(dict(file=p.name, category=category, item=idx, line=line, text=text[:650]))
for p in sorted((root/'_posts').rglob('*.md')):
    counts['all_posts'] += 1
    raw = p.read_text(encoding='utf-8-sig')
    m = front.match(raw)
    if not m:
        flag(p, 'no_frontmatter', raw[:100]); continue
    try:
        fm = yaml.load(m[1], Loader=loader) or {}
    except Exception as e:
        flag(p, 'yaml_error', str(e)); continue
    rows = fm.get('parallel_items') or fm.get('translation_segments') or fm.get('segments') or []
    interview = 'interview' in p.name or '访谈' in str(fm.get('categories')) or '访谈' in str(fm.get('title'))
    if interview: counts['interview_posts'] += 1
    if not rows:
        if interview: counts['interviews_without_segments'] += 1
        continue
    counts['segmented_posts'] += 1
    tree = yaml.compose(m[1], Loader=loader)
    nodes = next((v.value for k,v in tree.value if k.value in ('parallel_items','translation_segments','segments')), [])
    slug = p.stem[11:]
    cache = root/'data/cache_web/audit'/f'{slug}.html'
    headings = []
    if cache.exists():
        counts['posts_with_cached_source'] += 1
        soup = BeautifulSoup(cache.read_text(encoding='utf-8',errors='replace'), 'html.parser')
        headings = [re.sub(r'\s+', '', h.get_text()) for h in soup.select('h1,h2,h3,h4')]
    seen = set()
    for idx, row in enumerate(rows):
        if not isinstance(row,dict): continue
        counts['segments'] += 1
        typ = row.get('type','paragraph')
        if typ in ('image','hr'): continue
        counts['text_segments'] += 1
        o, t = str(row.get('original') or '').strip(), str(row.get('translation') or '').strip()
        line = nodes[idx].start_mark.line+2 if idx<len(nodes) else None
        def add(cat, txt): flag(p,cat,txt,idx+1,line)
        if o and not t: add('missing_translation',o)
        if t and not o: add('missing_original',t)
        if o == t and len(o)>40: add('identical_translation',o)
        if o and len(o)>180 and len(t)<len(o)*0.15: add('short_translation_candidate',f'{len(o)} -> {len(t)}: {o[:220]} | {t}')
        if len(re.findall(r'[ぁ-ヿ]',t))>12 and len(re.findall(r'[ぁ-ヿ]',t))/max(1,len(t))>.18: add('japanese_in_translation',t)
        if re.search(r'cookie policy|privacy policy|all rights reserved|subscribe to our|sign up for|related articles|share this article|この記事をシェア|関連記事|無断転載|返回顶部|隐私政策|订阅我们的',o+' '+t,re.I): add('noise_candidate',o+' | '+t)
        if typ not in ('heading','header') and len(o)>3 and re.sub(r'\s+','',o) in headings: add('source_heading_as_body',o+' | '+t)
        if typ not in ('heading','header') and re.match(r'^#{1,4}\s',t): add('markdown_heading_in_body',t)
        if re.search(r'(?<!\n)\n(?!\n)',t): add('single_newline',repr(t))
        if '\\n' in t: add('literal_backslash_n',t)
        if re.search(r'[\u4e00-\u9fff] {2,}[\u4e00-\u9fff]',t): add('cjk_spacing_candidate',t)
        if len(o)>100 and o in seen: add('duplicate_original',o)
        seen.add(o)
        if re.search(r'待翻译|TODO|\[TRANSLATE\]',t): add('placeholder',t)
result = {'counts':dict(counts),'issue_counts':dict(Counter(i['category'] for i in issues)), 'affected_posts': {c:len({i['file'] for i in issues if i['category']==c}) for c in sorted({i['category'] for i in issues})},'issues':issues}
if '--compact' in sys.argv:
    result['issues'] = [{**i,'text':i['text'][:180]} for i in issues if i['category'] != 'single_newline']
print(json.dumps(result,ensure_ascii=False,indent=2))
