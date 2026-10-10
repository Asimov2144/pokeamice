"""Check rendered discovery pages and crawlable bilingual profile anchors."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, urljoin
from xml.etree import ElementTree

BASE = 'https://docs.pokeamice.com'
EN_URLS = ['/en/', '/en/interviews/', '/en/people/', '/en/credits/', '/en/archive/']
PEOPLE = {'masuda-junichi': 'Junichi Masuda', 'ohmori-shigeru': 'Shigeru Ohmori', 'sugimori-ken': 'Ken Sugimori'}


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.canonical, self.hreflang, self.description, self.links = [], {}, '', []
        self.robots = []
        self.scripts, self.title, self.h1, self.text = [], '', '', []
        self._script = None
        self._skip = 0
        self._title = self._h1 = False
        self._anchor = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a['href'])
        if tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang'): self.hreflang[a['hreflang']] = a['href']
        if tag == 'meta' and a.get('name') == 'description': self.description = a.get('content', '')
        if tag == 'meta' and a.get('name', '').lower() in ('robots', 'googlebot'): self.robots.append(a.get('content', '').lower())
        if tag in ('script', 'style'):
            self._skip += 1
            if tag == 'script' and a.get('type') == 'application/ld+json': self._script = []
        if tag == 'title': self._title = True
        if tag == 'h1': self._h1 = True
        if tag == 'a' and a.get('href') and not self._skip: self._anchor = [a['href'], []]

    def handle_endtag(self, tag):
        if tag == 'script' and self._script is not None:
            self.scripts.append(json.loads(''.join(self._script)))
            self._script = None
        if tag in ('script', 'style'): self._skip = max(0, self._skip - 1)
        if tag == 'title': self._title = False
        if tag == 'h1': self._h1 = False
        if tag == 'a' and self._anchor:
            self.links.append((self._anchor[0], re.sub(r'\s+', ' ', ''.join(self._anchor[1])).strip()))
            self._anchor = None

    def handle_data(self, text):
        if self._script is not None: self._script.append(text)
        if self._skip: return
        self.text.append(text)
        if self._title: self.title += text
        if self._h1: self.h1 += text
        if self._anchor: self._anchor[1].append(text)


def file_for(root, url):
    address = urlsplit(url).path or '/'
    path = unquote(address).lstrip('/')
    return root / path / 'index.html' if address.endswith('/') else root / path


def check(root, source, fallback=None):
    errors, evidence = [], {}
    manifest_file = source / '._site-seo-checks/entity-manifest.json'
    manifest = json.loads(manifest_file.read_text(encoding='utf8')) if manifest_file.is_file() else []
    interview_urls = {unquote(BASE + entry['url']) for entry in manifest if entry.get('interview')}
    sitemap_file = root / 'sitemap.xml'
    sitemap_urls = {node.text for node in ElementTree.parse(sitemap_file).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')} if sitemap_file.is_file() else set()
    for url in EN_URLS:
        path = file_for(root, url)
        if not path.exists():
            errors.append(f'Missing {url}')
            continue
        page = Page(path.read_text(encoding='utf8'))
        evidence[url] = page
        if page.lang != 'en': errors.append(f'{url}: lang={page.lang}')
        if any('noindex' in value for value in page.robots): errors.append(f'{url}: noindex')
        if not fallback and BASE + url not in sitemap_urls: errors.append(f'{url}: missing from built sitemap')
        if page.canonical != [BASE + url]: errors.append(f'{url}: canonical {page.canonical}')
        if not page.description or not page.h1 or len(re.findall(r'[A-Za-z]+', ' '.join(page.text))) < 160: errors.append(f'{url}: missing introduction or thin visible content')
        if page.hreflang.get('en') != BASE + url or 'x-default' not in page.hreflang: errors.append(f'{url}: hreflang incomplete')
        nodes = [node for script in page.scripts for node in script.get('@graph', [script])]
        if sum(node.get('@type') == 'CollectionPage' for node in nodes) != 1: errors.append(f'{url}: CollectionPage count')
        if sum(node.get('@type') == 'WebSite' for node in nodes) != int(url == '/en/'): errors.append(f'{url}: WebSite count')
        for node in nodes:
            if node.get('description') and node['description'] not in ' '.join(page.text): errors.append(f'{url}: invisible schema description')
        for href, _ in page.links:
            parsed = urlsplit(urljoin(BASE + url, href))
            if parsed.netloc == urlsplit(BASE).netloc:
                target = file_for(root, parsed.path)
                if not target.is_file() and not (fallback and file_for(fallback, parsed.path).is_file()): errors.append(f'{url}: broken local link {href}')
    expected = {'zh-CN': BASE + '/', 'ja': BASE + '/ja/', 'en': BASE + '/en/', 'x-default': BASE + '/'}
    for url in ['/', '/ja/', '/en/']:
        page = evidence.get(url) or Page(file_for(root, url).read_text(encoding='utf8'))
        if page.hreflang != expected: errors.append(f'{url}: homepage hreflang does not close {page.hreflang}')

    import yaml
    records = yaml.load((source / '_data/people.yml').read_text(encoding='utf8'), Loader=yaml.CSafeLoader)
    credits = yaml.load((source / '_data/credits_people.yml').read_text(encoding='utf8'), Loader=yaml.CSafeLoader)
    expected_labels = {}
    for record in records:
        candidates = [record.get('name_en'), *record.get('aliases', []), record['name'], credits.get(record['slug'], {}).get('name')]
        english = next((name for name in candidates if name and re.search('[A-Za-z]', name) and not re.search('[\u3040-\u30ff\u3400-\u9fff]', name)), None)
        native = record.get('name_zh') or record['name']
        expected_labels[record['slug']] = native + (' · ' + english if english and english != native else '')

    paths = defaultdict(lambda: defaultdict(list))
    titles = defaultdict(list)
    json_count = 0
    for path in root.rglob('*.html'):
        html = path.read_text(encoding='utf8')
        try: page = Page(html)
        except (ValueError, json.JSONDecodeError) as error:
            errors.append(f'{path}: malformed JSON-LD {error}')
            continue
        json_count += len(page.scripts)
        if not page.canonical: continue
        canonical = page.canonical[0]
        if canonical == BASE + '/' + path.relative_to(root).as_posix().removesuffix('index.html'): titles[page.title].append(canonical)
        for href, text in page.links:
            target = urlsplit(urljoin(canonical, href)).path
            match = re.fullmatch(r'/people/([^/]+)/', target)
            if not match or match[1] not in PEOPLE: continue
            slug = match[1]
            if '/en/' not in urlsplit(canonical).path and PEOPLE[slug] not in text:
                # Empty image/arrow links are harmless if another named link exists.
                continue
            if '/en/' not in urlsplit(canonical).path and page.lang != 'ja' and expected_labels[slug] not in text:
                errors.append(f'{canonical}: inconsistent entity name {text}')
            category = 'home' if canonical == BASE + '/' else 'people' if canonical == BASE + '/people/' else 'credits' if '/credits/' in canonical else 'interview' if unquote(canonical) in interview_urls else 'other'
            if '/en/' in urlsplit(canonical).path: category = 'english'
            paths[slug][category].append({'source': canonical, 'anchor': text, 'target': BASE + target})
    for slug in PEOPLE:
        for category in ('home', 'people', 'credits', 'interview'):
            if not paths[slug][category]: errors.append(f'{slug}: no crawlable English alias path from {category}')
    duplicates = {title: sorted(set(urls)) for title, urls in titles.items() if len(set(urls)) > 1}
    for title, urls in duplicates.items():
        if any(url in [BASE + path for path in EN_URLS] for url in urls): errors.append(f'English duplicate title {title}: {urls}')

    catalogue_path = root / 'assets/js/catalogue.json'
    if catalogue_path.is_file():
        for row in json.loads(catalogue_path.read_text(encoding='utf8')):
            for slug, label in zip(row.get('slugs', []), row.get('people_labels', [])):
                if slug and expected_labels.get(slug) != label: errors.append(f'{row["url"]}: inconsistent search card label {slug}')
    rows = [entry for slug in PEOPLE for group in ('home', 'people', 'interview', 'credits', 'english') for entry in paths[slug][group][:1]]
    return {'errors': sorted(set(errors)), 'english_pages': {url: {'title': page.title, 'description': page.description, 'lang': page.lang, 'canonical': page.canonical, 'hreflang': page.hreflang, 'in_sitemap': BASE + url in sitemap_urls, 'robots': page.robots} for url, page in evidence.items()}, 'jsonld_scripts_parsed': json_count, 'anchor_samples': rows,
            'path_counts': {slug: {group: len(rows) for group, rows in groups.items()} for slug, groups in paths.items()}, 'existing_duplicate_title_groups': len(duplicates)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=Path('_site'))
    parser.add_argument('--source', type=Path, default=Path('.'))
    parser.add_argument('--fallback', type=Path)
    parser.add_argument('--report', type=Path, default=Path('._site-seo-checks/english-discovery-validation.json'))
    args = parser.parse_args()
    result = check(args.site.resolve(), args.source.resolve(), args.fallback.resolve() if args.fallback else None)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({key: value for key, value in result.items() if key not in ('english_pages', 'anchor_samples')}, ensure_ascii=False))
    raise SystemExit(bool(result['errors']))


if __name__ == '__main__': main()
