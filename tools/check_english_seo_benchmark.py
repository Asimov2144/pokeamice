"""Check English query semantics in a built site, without network or ranking data.

Uses Python's standard library only. See tools/seo/README.md for the contract.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
HIDDEN_CLASSES = {'hidden', 'sr-only', 'visually-hidden', 'screen-reader-text'}


def words(value):
    """Fold Latin accents (Pokémon), case, punctuation and whitespace, not kana."""
    chars, latin = [], False
    for char in unicodedata.normalize('NFKD', str(value)):
        if unicodedata.combining(char):
            if not latin:
                chars.append(char)
        else:
            latin = unicodedata.name(char, '').startswith('LATIN')
            chars.append(char)
    value = unicodedata.normalize('NFC', ''.join(chars)).casefold()
    return ' '.join(re.findall(r'[^\W_]+', value))


def has_words(text, term):
    term = words(term)
    return bool(term) and f' {term} ' in f' {words(text)} '


def keyword_groups(text, groups):
    return all(any(has_words(text, term) for term in alternatives) for alternatives in groups)


def address(url):
    p = urlsplit(url)
    return p.scheme.lower(), p.netloc.lower(), unquote(p.path or '/'), p.query, p.fragment


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


class Page(HTMLParser):
    """Read source HTML anchors, excluding scripts and explicit hidden content."""
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack, self.titles, self.descriptions = [], [], []
        self.lang, self.canonicals, self.robots, self.refresh = None, [], [], []
        self.links, self.body_parts, self.regions, self.nodes = [], [], {}, []
        self.json_errors = []
        self.feed(html)
        self.close()
        self.text = ' '.join(self.body_parts)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        hidden = (parent.get('hidden', False) or 'hidden' in a or
                  a.get('aria-hidden', '').lower() == 'true' or
                  bool(set(a.get('class', '').split()) & HIDDEN_CLASSES) or
                  bool(re.search(r'(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))', a.get('style', ''), re.I)))
        head = parent.get('head', False) or tag == 'head'
        body = parent.get('body', False) or tag == 'body'
        skip = parent.get('skip', False) or tag in {'script', 'style', 'template'}
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'meta':
            name = a.get('name', '').lower()
            if name == 'description' and head:
                self.descriptions.append(a.get('content', ''))
            if name in {'robots', 'googlebot', 'oai-searchbot'}:
                self.robots.append(a.get('content', '').lower())
            if a.get('http-equiv', '').lower() == 'refresh':
                self.refresh.append(a.get('content', ''))
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append({'href': a.get('href', ''), 'head': head})
        frame = {'tag': tag, 'attrs': a, 'hidden': hidden, 'head': head,
                 'body': body, 'skip': skip, 'parts': []}
        if tag not in VOID:
            self.stack.append(frame)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.stack:
            return
        current = self.stack[-1]
        if current['tag'] == 'script':
            current['parts'].append(data)
            return
        for frame in self.stack:
            if frame['tag'] == 'title':
                frame['parts'].append(data)
        if not current['body'] or current['skip'] or current['hidden']:
            return
        self.body_parts.append(data)
        for frame in self.stack:
            if frame['tag'] == 'a' or 'atlas__nums' in frame['attrs'].get('class', '').split():
                frame['parts'].append(data)

    def handle_endtag(self, tag):
        index = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i]['tag'] == tag), None)
        if index is None:
            return
        frame = self.stack[index]
        del self.stack[index:]
        text = ' '.join(frame['parts']).strip()
        if tag == 'title' and frame['head']:
            self.titles.append(text)
        if tag == 'script' and frame['attrs'].get('type', '').lower() == 'application/ld+json':
            try:
                self.nodes.extend(node for node in objects(json.loads(''.join(frame['parts']))) if '@type' in node)
            except (ValueError, TypeError) as exc:
                self.json_errors.append(str(exc))
        if tag == 'a' and frame['body'] and not frame['hidden'] and not frame['skip']:
            a = frame['attrs']
            if a.get('href') and text:
                self.links.append({'href': a['href'], 'text': text,
                                   'nofollow': 'nofollow' in a.get('rel', '').lower().split()})
        if 'atlas__nums' in frame['attrs'].get('class', '').split() and not frame['hidden']:
            self.regions.setdefault('atlas__nums', []).append(text)

    def blocked(self, rule):
        return any(rule in re.split(r'[\s,;]+', value) or 'none' in re.split(r'[\s,;]+', value) for value in self.robots)

    def typed(self, kind):
        return [node for node in self.nodes if kind in (node['@type'] if isinstance(node['@type'], list) else [node['@type']])]


class Benchmark:
    def __init__(self, site, specification):
        self.site = Path(site).resolve()
        self.spec = specification
        self.origin = specification['origin'].rstrip('/')
        self.pages, self.sitemap, self.setup_errors = {}, Counter(), []
        self.robot = RobotFileParser()
        try:
            self.robot.parse(self.file('/robots.txt').read_text(encoding='utf-8-sig').splitlines())
        except OSError as exc:
            self.setup_errors.append(f'Cannot read built robots.txt: {exc}')
        self.read_sitemap('/sitemap.xml', set())

    def absolute(self, path):
        return urljoin(self.origin + '/', path)

    def file(self, url):
        path = address(self.absolute(url))[2].lstrip('/')
        result = (self.site / path / 'index.html') if not path or path.endswith('/') else self.site / path
        result = result.resolve()
        if not result.is_relative_to(self.site):
            raise ValueError(f'Path outside build: {url}')
        return result

    def page(self, url):
        path = address(self.absolute(url))[2]
        if path not in self.pages:
            self.pages[path] = Page(self.file(path).read_text(encoding='utf-8-sig'))
        return self.pages[path]

    def read_sitemap(self, url, seen):
        if address(self.absolute(url))[:2] != address(self.origin)[:2]:
            self.setup_errors.append(f'Nonlocal sitemap: {url}')
            return
        key = address(self.absolute(url))
        if key in seen:
            self.setup_errors.append(f'Repeated/cyclic sitemap: {url}')
            return
        seen.add(key)
        try:
            tree = ET.parse(self.file(url))
            kind = tree.getroot().tag.rsplit('}', 1)[-1]
            locs = [node.text.strip() for node in tree.getroot().iter() if node.tag.rsplit('}', 1)[-1] == 'loc' and node.text]
            if kind == 'sitemapindex':
                for child in locs:
                    self.read_sitemap(child, seen)
            elif kind == 'urlset':
                self.sitemap.update(address(loc) for loc in locs)
            else:
                self.setup_errors.append(f'Unsupported sitemap root: {kind}')
        except (OSError, ET.ParseError, ValueError) as exc:
            self.setup_errors.append(f'Cannot read sitemap {url}: {exc}')

    def usable_target(self, url, schema_type=None):
        parsed = address(url)
        if parsed[:2] != address(self.origin)[:2] or parsed[3]:
            return False
        try:
            page = self.page(url)
        except (OSError, ValueError):
            return False
        expected = address(self.absolute(parsed[2]))
        if page.canonicals != [{'href': self.absolute(parsed[2]), 'head': True}]:
            # Encoded and decoded Unicode paths can denote the same canonical URL.
            if len(page.canonicals) != 1 or not page.canonicals[0]['head'] or address(page.canonicals[0]['href']) != expected:
                return False
        if page.blocked('noindex') or page.blocked('nofollow') or page.refresh or page.json_errors:
            return False
        return not schema_type or any(address(node.get('url', '').split('#')[0]) == expected for node in page.typed(schema_type))

    def anchors(self, landing, rule, entity_id):
        source = rule.get('source', landing)
        page = self.page(source)
        target = rule.get('target', landing) if rule['direction'] == 'inbound' or 'target' in rule else None
        found = {}
        for link in page.links:
            href = urljoin(self.absolute(source), link['href'])
            if link['nofollow'] or not keyword_groups(link['text'], rule.get('text_keywords', [])):
                continue
            if target and address(href)[:4] != address(self.absolute(target))[:4]:
                continue
            if rule.get('path_contains') and rule['path_contains'] not in address(href)[2]:
                continue
            if not self.usable_target(href, rule.get('target_schema')):
                continue
            if rule.get('mentions_entity'):
                nodes = self.page(href).typed(rule['target_schema'])
                if not any(child.get('@id') == entity_id for node in nodes for prop in ['about', 'mentions'] for child in objects(node.get(prop, []))):
                    continue
            found[address(href)[:4]] = {'source': source, 'anchor': link['text'], 'target': address(href)[2]}
            if len(found) >= rule.get('minimum', 1):
                break
        return list(found.values())

    def check(self, case):
        target = deepcopy(self.spec['targets'][case['target']])
        expected = {**target, **case}
        url, checks = target['expected_landing_page'], []

        def record(name, passed, wanted, actual):
            checks.append({'condition': name, 'passed': bool(passed), 'expected': wanted, 'actual': actual})

        try:
            page = self.page(url)
        except (OSError, ValueError) as exc:
            record('landing_page', False, url, str(exc))
            return {'query': case['query'], 'expected': expected, 'passed': False, 'checks': checks}
        record('title_keywords', len(page.titles) == 1 and keyword_groups(page.titles[0], case['expected_title_keywords']), case['expected_title_keywords'], page.titles)
        record('description', len(page.descriptions) == 1 and bool(page.descriptions[0].strip()), 'one nonempty head description', page.descriptions)
        description = ' '.join(page.descriptions)
        record('metadata_intent', keyword_groups(' '.join(page.titles) + ' ' + description, case.get('required_metadata_keywords', [])), case.get('required_metadata_keywords', []), {'title': page.titles, 'description': description})
        record('visible_intent', keyword_groups(page.text, case.get('required_visible_keywords', [])), case.get('required_visible_keywords', []), 'visible source HTML text only')
        record('language', page.lang == target['expected_language'], target['expected_language'], page.lang)
        canonical = self.absolute(url)
        record('canonical', page.canonicals == [{'href': canonical, 'head': True}], canonical, page.canonicals)
        count = self.sitemap[address(canonical)]
        record('sitemap', count == int(target['sitemap_inclusion']), int(target['sitemap_inclusion']), count)
        record('index_follow', not page.blocked('noindex') and not page.blocked('nofollow') and not page.refresh, 'no noindex/nofollow/refresh', {'robots': page.robots, 'refresh': page.refresh})
        allowed = {bot: self.robot.can_fetch(bot, canonical) for bot in ['Googlebot', 'OAI-SearchBot']}
        record('robots_access', all(allowed.values()) and not any('robots.txt' in x for x in self.setup_errors), 'both crawlers allowed', allowed)
        record('json_ld_parse', not page.json_errors, 'all landing JSON-LD parses', page.json_errors)
        ids = Counter(node['@id'] for node in page.nodes if node.get('@id'))
        record('unique_schema_ids', not any(n > 1 for n in ids.values()), 'no duplicate typed @id in landing page', {key: n for key, n in ids.items() if n > 1})
        entity = target['expected_entity']
        entity_id = canonical + entity['id_fragment']
        nodes = [node for node in page.typed(entity['type']) if node.get('@id') == entity_id]
        names = [name for node in nodes for name in [node.get('name', ''), *as_list(node.get('alternateName'))]]
        entity_ok = len(nodes) == 1 and any(words(name) == words(entity['name']) for name in names) and nodes[0].get('url') == canonical
        record('entity_identity', entity_ok, {'type': entity['type'], '@id': entity_id, 'name': entity['name']}, names)
        aliases = as_list(nodes[0].get('alternateName')) if nodes else []
        record('alternate_names', all(any(words(alias) == words(name) for alias in aliases) for name in entity.get('alternate_names', [])), entity.get('alternate_names', []), aliases)
        record('visible_entity_names', all(has_words(page.text, name) for name in entity.get('visible_names', [])), entity.get('visible_names', []), 'visible source HTML text only')
        for rule in target['required_schema']:
            identity = rule.get('id', canonical + rule.get('id_fragment', ''))
            selected = [node for node in page.typed(rule['type']) if node.get('@id') == identity]
            ok = len(selected) == 1
            if ok:
                node = selected[0]
                ok = all(node.get(prop) not in (None, '', [], {}) for prop in rule.get('required_properties', []))
                if rule.get('entity_relation'):
                    ok = ok and node.get(rule['entity_relation']) == {'@id': entity_id}
                if rule.get('name'):
                    ok = ok and words(node.get('name', '')) == words(rule['name']) and has_words(page.text, rule['name'])
                for prop, required_ids in rule.get('required_relations', {}).items():
                    references = {child.get('@id') for child in objects(node.get(prop, []))}
                    ok = ok and set(required_ids).issubset(references)
                for prop, relation in rule.get('linked_relations', {}).items():
                    links = {address(urljoin(canonical, link['href']))[:4] for link in page.links if not link['nofollow']}
                    references = {child['@id'] for child in objects(node.get(prop, [])) if child.get('@id')}
                    good = [ref for ref in references if address(ref.split('#')[0])[:4] in links and self.usable_target(ref, relation['target_schema'])]
                    ok = ok and len(good) >= relation['minimum']
                if node.get('inLanguage'):
                    ok = ok and node['inLanguage'] == target['expected_language']
                if 'description' in rule.get('required_properties', []):
                    ok = ok and has_words(page.text, node['description'])
            record('schema:' + rule['type'], ok, rule, selected)
        for i, rule in enumerate(target['required_internal_anchors'], 1):
            try:
                found = self.anchors(url, rule, entity_id)
                record(f'anchor:{i}', len(found) >= rule.get('minimum', 1), rule, found)
            except (OSError, ValueError) as exc:
                record(f'anchor:{i}', False, rule, str(exc))
        for fact in target.get('required_facts', []):
            match = re.search(fact['pattern'], description, re.I)
            number = int(match[1]) if match else None
            actual = {'description_count': number}
            ok = number is not None
            if fact['kind'] == 'description_count':
                ok = ok and number >= fact['minimum']
            elif fact['kind'] == 'linked_game_count':
                refs = {child['@id'] for node in page.typed(fact['schema_type']) for child in objects(node.get(fact['property'], [])) if child.get('@id', '').endswith(fact['entity_suffix'])}
                links = {address(urljoin(canonical, link['href']))[:4] for link in page.links if not link['nofollow']}
                actual['linked_game_count'] = len(refs)
                ok = ok and number == len(refs) and bool(refs)
                ok = ok and all(address(ref.split('#')[0])[:4] in links and self.usable_target(ref, 'VideoGame') for ref in refs)
            elif fact['kind'] == 'data_count':
                try:
                    source = json.loads(self.file(fact['data_file']).read_text(encoding='utf-8-sig'))
                    for key in fact['data_path'].split('.'):
                        source = source[key]
                    actual['source_count'] = source
                    region = ' '.join(page.regions.get(fact['visible_region'], []))
                    ok = ok and type(source) is int and number == source and bool(re.search(rf'(?<!\d){source}(?!\d)', region))
                    actual['visible_region'] = region
                    if fact.get('schema_property'):
                        values = [node.get(fact['schema_property']) for node in page.typed(fact['schema_type'])]
                        actual['schema_counts'] = values
                        ok = ok and values == [source]
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    actual['error'] = str(exc)
                    ok = False
            record('fact:' + fact['name'], ok, fact, actual)
        return {'query': case['query'], 'expected': expected, 'passed': all(c['passed'] for c in checks), 'checks': checks}

    def run(self):
        rows = [self.check(case) for case in self.spec['queries']]
        failed = sum(not row['passed'] for row in rows)
        return {'benchmark_version': self.spec['version'], 'scope': 'local rendered semantic signals; not Google rankings',
                'site': str(self.site), 'queries': len(rows), 'passed': len(rows) - failed, 'failed': failed,
                'checks': sum(len(row['checks']) for row in rows), 'pages_read': len(self.pages),
                'setup_errors': self.setup_errors, 'results': rows}


def as_list(value):
    return value if isinstance(value, list) else [value] if value is not None else []


def validate(spec):
    if spec.get('version') != 1 or not spec.get('queries') or not spec.get('targets'):
        raise ValueError('Benchmark requires version 1, nonempty queries and targets')
    origin = urlsplit(spec.get('origin', ''))
    if origin.scheme != 'https' or not origin.netloc or origin.path not in ('', '/') or origin.query or origin.fragment:
        raise ValueError('Benchmark origin must be an absolute HTTPS origin')
    if len({case['query'] for case in spec['queries']}) != len(spec['queries']):
        raise ValueError('Duplicate benchmark query')
    for target in spec['targets'].values():
        for key in ['expected_landing_page', 'expected_entity', 'expected_language', 'required_internal_anchors', 'required_schema', 'canonical_expectation', 'sitemap_inclusion', 'indexability']:
            if key not in target:
                raise ValueError(f'Missing target field: {key}')
        page = target['expected_landing_page']
        if not page.startswith('/') or page.startswith('//') or urlsplit(page).query or urlsplit(page).fragment:
            raise ValueError('Landing pages must be local canonical paths without parameters')
        if target['canonical_expectation'] != 'absolute_self' or target['indexability'] != 'index_follow' or type(target['sitemap_inclusion']) is not bool:
            raise ValueError('Unsupported canonical/indexability/sitemap contract')
        if not target['required_internal_anchors'] or not target['required_schema']:
            raise ValueError('Each target requires anchors and schema')
        for rule in target['required_internal_anchors']:
            if rule.get('direction') not in ('inbound', 'outbound') or rule.get('minimum', 1) < 1:
                raise ValueError('Invalid anchor direction/minimum')
            if rule['direction'] == 'inbound' and not rule.get('source'):
                raise ValueError('Inbound anchor requires a source page')
            if not (rule.get('source') or rule.get('target') or rule.get('target_schema') or rule.get('path_contains')):
                raise ValueError('Anchor rule must constrain its source or target')
        for fact in target.get('required_facts', []):
            if fact.get('kind') not in ('description_count', 'linked_game_count', 'data_count'):
                raise ValueError('Unknown fact kind')
            re.compile(fact['pattern'])
    for case in spec['queries']:
        if case.get('target') not in spec['targets'] or not case.get('expected_title_keywords'):
            raise ValueError('Each query requires a known target and title keywords')
        for key in ('expected_title_keywords', 'required_metadata_keywords', 'required_visible_keywords'):
            for group in case.get(key, []):
                if not isinstance(group, list) or not group or not all(isinstance(term, str) and words(term) for term in group):
                    raise ValueError(f'{key} requires nonempty alternatives in each group')


def markdown(report):
    lines = ['# English SEO semantic benchmark', '', 'This report checks local HTML signals, not search rankings.', '',
             f"Queries: {report['queries']}; passed: {report['passed']}; failed: {report['failed']}; checks: {report['checks']}.", '',
             '| Query | Expected landing | Language | Result |', '| --- | --- | --- | --- |']
    for row in report['results']:
        expected = row['expected']
        lines.append(f"| {row['query']} | {expected['expected_landing_page']} | {expected['expected_language']} | {'PASS' if row['passed'] else 'FAIL'} |")
    for row in report['results']:
        failures = [check for check in row['checks'] if not check['passed']]
        if failures:
            lines.extend(['', f"## {row['query']}", '', *[f"- {check['condition']}: expected {json.dumps(check['expected'], ensure_ascii=False)}; actual {json.dumps(check['actual'], ensure_ascii=False)}" for check in failures]])
    if report['setup_errors']:
        lines.extend(['', '## Build input errors', '', *['- ' + value for value in report['setup_errors']]])
    return '\n'.join(lines) + '\n'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--site', type=Path, default=ROOT / '_site')
    cli.add_argument('--benchmark', type=Path, default=ROOT / 'tools/seo/english-seo-benchmark.json')
    cli.add_argument('--report', type=Path, default=ROOT / '._site-seo-checks/english-seo-benchmark-results.json')
    args = cli.parse_args()
    try:
        spec = json.loads(args.benchmark.read_text(encoding='utf-8-sig'))
        validate(spec)
        report = Benchmark(args.site, spec).run()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Benchmark input error: {exc}', file=sys.stderr)
        return 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.report.with_suffix('.md').write_text(markdown(report), encoding='utf-8')
    print(f"English SEO benchmark: {report['passed']}/{report['queries']} queries passed; {report['checks']} checks; {report['pages_read']} HTML pages read.")
    for row in report['results']:
        if not row['passed']:
            print(row['query'] + ': ' + ', '.join(check['condition'] for check in row['checks'] if not check['passed']))
    for error in report['setup_errors']:
        print(error)
    print(f'Report: {args.report}')
    return int(bool(report['failed'] or report['setup_errors']))


if __name__ == '__main__':
    raise SystemExit(main())
