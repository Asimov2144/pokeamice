"""Verify visible profile anchors in final HTML, separately from client card data."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

BASE = 'https://docs.pokeamice.com'
TARGETS = ['masuda-junichi', 'ohmori-shigeru', 'sugimori-ken']
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
SCOPES = {
    'home-featured-people': 'featured people', 'dims__profile': 'home dimensions',
    'people__card': 'people index', 'people__roster': 'people roster',
    'ed-person': 'interview people', 'parallel-topics': 'interview topics',
    'person__co': 'related people', 'person__pub-with': 'co-interviewees',
    'search-result-card__tags': 'static result cards', 'library__entry-who': 'archive rows',
    'lore': 'mentioned people', 'tl-chip': 'timeline', 'wanted-card__people': 'recovery cards',
    'resource-card': 'resource cards',
}


def plain(text):
    return re.sub(r'\s+', ' ', text).strip()


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack, self.links = [], []
        self.canonical, self.lang, self.anchor = None, None, None
        self.nested_anchors = 0
        self.nested_anchor_details = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')
        classes = set(a.get('class', '').split())
        hidden = ('hidden' in a or a.get('aria-hidden') == 'true' or
                  bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden', a.get('style', ''), re.I)))
        state = (tag, classes, hidden)
        ancestors = [*self.stack, state]
        if tag == 'a' and a.get('href'):
            if self.anchor:
                self.nested_anchors += 1
                self.nested_anchor_details.append((self.anchor['href'], a['href']))
            contexts = {SCOPES[c] for _, names, _ in ancestors for c in names if c in SCOPES}
            self.anchor = {'href': a['href'], 'text': [], 'contexts': sorted(contexts),
                           'hidden': any(entry[2] for entry in ancestors)}
        if tag not in VOID: self.stack.append(state)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor:
            self.anchor['text'] = plain(''.join(self.anchor['text']))
            self.links.append(self.anchor)
            self.anchor = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        if self.anchor and not any(tag in ('script', 'style') or hidden for tag, _, hidden in self.stack):
            self.anchor['text'].append(text)


def built_file(root, url):
    path = unquote(urlsplit(url).path)
    return root / path.lstrip('/') / 'index.html' if path.endswith('/') else root / path.lstrip('/')


def check(root, source):
    identities = json.loads((source / '._site-seo-checks/person-identities.json').read_text(encoding='utf8'))
    manifest = json.loads((source / '._site-seo-checks/entity-manifest.json').read_text(encoding='utf8'))
    interviews = {unquote(BASE + row['url']) for row in manifest if row.get('interview')}
    errors, other_anchors, existing_external_nesting = [], [], []
    counts, links = Counter(), defaultdict(list)
    unique_sources = defaultdict(lambda: defaultdict(set))
    checked_targets = set()
    pages = 0
    for path in root.rglob('*.html'):
        pages += 1
        if pages % 1000 == 0: print(f'Scanned {pages} HTML pages', flush=True)
        page = Links(path.read_text(encoding='utf8'))
        if not page.canonical: continue
        canonical = unquote(page.canonical)
        # Redirect copies do not create independent discovery paths.
        if built_file(root, page.canonical).resolve() != path.resolve(): continue
        for link in page.links:
            target = urlsplit(urljoin(page.canonical, link['href']))
            match = re.fullmatch(r'/people/([^/]+)/', target.path)
            if target.netloc != urlsplit(BASE).netloc or not match: continue
            slug = match[1]
            identity = identities.get(slug)
            target_url = BASE + target.path
            if not built_file(root, target_url).is_file():
                errors.append(f'{canonical}: missing profile target {target_url}')
                continue
            if slug not in checked_targets:
                profile = built_file(root, target_url).read_text(encoding='utf8')
                canonical_tag = re.search(r'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"', profile)
                if not canonical_tag or unescape(canonical_tag[1]) != target_url:
                    errors.append(f'{target_url}: non-self profile canonical')
                checked_targets.add(slug)
            contexts = list(link['contexts'])
            if re.fullmatch(r'/credits/[^/]+/', urlsplit(canonical).path): contexts.append('credits / atlas')
            if not identity: continue
            english = identity.get('name_en')
            if contexts and link['text']:
                counts['managed_profile_anchors'] += 1
                counts.update({context: 1 for context in contexts})
                if link['hidden']: errors.append(f'{canonical}: hidden managed profile anchor {slug}')
                if english and english not in link['text']:
                    errors.append(f'{canonical}: missing English alias for {slug}: {link["text"]}')
                if page.lang not in ('en', 'ja') and identity['label'] not in link['text']:
                    errors.append(f'{canonical}: noncanonical display name for {slug}: {link["text"]}')
            if slug not in TARGETS or link['hidden']: continue
            if not english or english not in link['text']:
                if len(other_anchors) < 80:
                    other_anchors.append({'source': page.canonical, 'anchor': link['text'], 'target': target_url, 'contexts': contexts})
                continue
            category = ('home' if canonical == BASE + '/' else 'people' if canonical == BASE + '/people/'
                        else 'credits' if '/credits/' in canonical else 'interview' if canonical in interviews
                        else 'related' if 'related people' in contexts or 'co-interviewees' in contexts else 'other')
            unique_sources[slug][category].add(page.canonical)
            links[slug].append({'source': page.canonical, 'anchor': link['text'], 'target': target_url,
                                'category': category, 'contexts': contexts, 'file': str(path.resolve())})
        for outer, inner in page.nested_anchor_details:
            if '/people/' in outer or '/people/' in inner:
                errors.append(f'{canonical}: nested profile anchors')
            else:
                existing_external_nesting.append({'source': canonical, 'outer': outer, 'inner': inner})

    for slug in TARGETS:
        for category in ('home', 'people', 'interview', 'credits'):
            if not unique_sources[slug][category]: errors.append(f'{slug}: no visible English anchor from {category}')
    client_counts = Counter()
    for row in json.loads((root / 'assets/js/catalogue.json').read_text(encoding='utf8')):
        people, slugs, labels, aliases = [row.get(key, []) for key in ('people', 'slugs', 'people_labels', 'people_aliases')]
        if len({len(people), len(slugs), len(labels), len(aliases)}) != 1:
            errors.append(f'{row["url"]}: misaligned search card identities')
        for slug, label, names in zip(slugs, labels, aliases):
            if not slug: continue
            client_counts['search_person_labels'] += 1
            if slug not in identities or label != identities[slug]['label']:
                errors.append(f'{row["url"]}: search label mismatch {slug}')
            elif any(name not in names for name in identities[slug]['aliases']):
                errors.append(f'{row["url"]}: incomplete search aliases {slug}')
    for slug, row in json.loads((root / 'assets/js/tips.json').read_text(encoding='utf8'))['people'].items():
        client_counts['hover_card_labels'] += 1
        if row['n'] != identities[slug]['label']: errors.append(f'Hover label mismatch {slug}')
    keys = (root / 'keys/index.html').read_text(encoding='utf8')
    featured = re.search(r'<script[^>]*data-feed-people[^>]*>(.*?)</script>', keys, re.S)
    if not featured: errors.append('Missing featured developer data')
    else:
        for row in json.loads(featured[1]):
            client_counts['featured_developer_labels'] += 1
            if row['n'] != identities[row['s']]['label']: errors.append(f'Featured developer mismatch {row["s"]}')
    css = (root / 'assets/css/main.css').read_text(encoding='utf8')
    if not re.search(r'\.search-result-card__tags\s*>\s*span', css):
        errors.append('Built card CSS still styles the nested English alias as a separate chip')
    preferred_interviews = {
        'masuda-junichi': '/developer-interviews/gamefreak-recruit/interview-gamefreak-career-message-masuda/',
        'ohmori-shigeru': '/developer-interviews/gamefreak-recruit/interview-gamefreak-crosstalk-designer/',
        'sugimori-ken': '/developer-interviews/gamefreak-recruit/interview-gamefreak-recruit-3d-graphics-to-fk/',
    }
    samples = []
    for slug in TARGETS:
        for category in ('home', 'people', 'interview', 'credits', 'related'):
            candidates = [row for row in links[slug] if row['category'] == category]
            preferred = BASE + ('/credits/x-y/' if category == 'credits' else preferred_interviews[slug])
            samples.extend(sorted(candidates, key=lambda row: row['source'] != preferred)[:1])
    alias_url = '/访谈翻译/扫描存档/scan-ndream-2009-11-hgss-developer-interview/'
    alias_page = Links(built_file(root, alias_url).read_text(encoding='utf8'))
    if not any('/people/sen-zhang-ren/' == row['href'] and identities['sen-zhang-ren']['label'] in row['text'] for row in alias_page.links):
        errors.append('Registered alias 森昭人 still lacks its canonical, bilingual profile link')
    return {'errors': sorted(set(errors)), 'html_pages_scanned': pages,
            'managed_anchor_counts': dict(counts), 'client_card_counts': dict(client_counts),
            'unique_source_counts': {slug: {group: len(urls) for group, urls in groups.items()} for slug, groups in unique_sources.items()},
            'samples': samples, 'other_target_anchors': other_anchors,
            'existing_external_anchor_nesting': existing_external_nesting,
            'identity_examples': {slug: identities[slug] for slug in TARGETS}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=Path('_site'))
    parser.add_argument('--source', type=Path, default=Path('.'))
    parser.add_argument('--report', type=Path, default=Path('._site-seo-checks/internal-links-validation.json'))
    args = parser.parse_args()
    result = check(args.site.resolve(), args.source.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({key: value for key, value in result.items() if key not in ('samples', 'identity_examples', 'other_target_anchors')}, ensure_ascii=False))
    raise SystemExit(bool(result['errors']))


if __name__ == '__main__': main()
