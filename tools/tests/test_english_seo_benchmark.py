"""Regression tests: misleading HTML must not pass the semantic benchmark."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_english_seo_benchmark import Benchmark, validate

BASE = 'https://docs.pokeamice.com'
PROFILE = '/people/masuda-junichi/'
ARTICLE = '/interview-masuda/'
GAME = '/credits/x-y/'


def html(path, body, nodes=(), title='Junichi Masuda — Pokémon Interviews & Credits', description='1 related interview and Pokémon credits across 1 game.', lang='zh-CN'):
    schema = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": list(nodes)}, ensure_ascii=False)}</script>' if nodes else ''
    return f'<html lang="{lang}"><head><title>{title}</title><meta name="description" content="{description}"><link rel="canonical" href="{BASE}{path}">{schema}</head><body>{body}</body></html>'


class SemanticBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name)
        entity = BASE + PROFILE + '#person'
        self.person = {'@type': 'Person', '@id': entity, 'url': BASE + PROFILE, 'name': 'Junichi Masuda',
                       'alternateName': ['Junichi Masuda', '増田順一', '增田顺一'],
                       'subjectOf': [{'@id': BASE + ARTICLE + '#article'}]}
        self.profile = {'@type': 'ProfilePage', '@id': BASE + PROFILE + '#page', 'url': BASE + PROFILE,
                        'inLanguage': 'zh-CN', 'mainEntity': {'@id': entity},
                        'mentions': [{'@id': BASE + GAME + '#game'}]}
        self.body = f'<p>增田顺一 · Junichi Masuda · 増田順一</p><a href="{ARTICLE}">开发者访谈</a><a href="{GAME}">宝可梦 X·Y</a>'
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]))
        self.write('/', html('/', f'<a href="{PROFILE}">增田顺一 · <span lang="en">Junichi Masuda</span></a>'))
        self.article = {'@type': 'Article', '@id': BASE + ARTICLE + '#article', 'url': BASE + ARTICLE, 'about': {'@id': entity}}
        self.write(ARTICLE, html(ARTICLE, '<p>开发者访谈</p>', [self.article]))
        self.write(GAME, html(GAME, '<p>Pokémon X and Y</p>', [{'@type': 'VideoGame', '@id': BASE + GAME + '#game', 'url': BASE + GAME}]))
        self.write('/robots.txt', f'Sitemap: {BASE}/sitemap.xml\n')
        self.sitemap([BASE + PROFILE])
        self.spec = {'version': 1, 'origin': BASE, 'targets': {'masuda': {
            'expected_landing_page': PROFILE, 'expected_language': 'zh-CN',
            'expected_entity': {'type': 'Person', 'name': 'Junichi Masuda', 'id_fragment': '#person',
                                'alternate_names': ['Junichi Masuda', '増田順一', '增田顺一'],
                                'visible_names': ['Junichi Masuda', '増田順一', '增田顺一']},
            'required_schema': [{'type': 'Person', 'id_fragment': '#person', 'required_properties': ['alternateName', 'subjectOf'],
                                 'linked_relations': {'subjectOf': {'target_schema': 'Article', 'minimum': 1}}},
                                {'type': 'ProfilePage', 'id_fragment': '#page', 'entity_relation': 'mainEntity'}],
            'required_internal_anchors': [{'direction': 'inbound', 'source': '/', 'text_keywords': [['Junichi Masuda']], 'minimum': 1},
                                          {'direction': 'outbound', 'target_schema': 'Article', 'path_contains': 'interview', 'mentions_entity': True, 'minimum': 1}],
            'canonical_expectation': 'absolute_self', 'sitemap_inclusion': True, 'indexability': 'index_follow',
            'required_facts': [{'kind': 'description_count', 'name': 'interview_count', 'pattern': '(\\d+) related interviews?', 'minimum': 1},
                               {'kind': 'linked_game_count', 'name': 'credited_works_count', 'pattern': 'credits across (\\d+) games?', 'schema_type': 'ProfilePage', 'property': 'mentions', 'entity_suffix': '#game'}]
        }}, 'queries': [{'query': 'Junichi Masuda Pokemon interviews', 'target': 'masuda',
                         'expected_title_keywords': [['Junichi Masuda'], ['Pokemon'], ['interview', 'interviews']]}]}

    def write(self, path, content):
        target = self.site / path.lstrip('/')
        if path.endswith('/'):
            target /= 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def sitemap(self, urls):
        self.write('/sitemap.xml', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>')

    def run_report(self):
        validate(self.spec)
        return Benchmark(self.site, self.spec).run()

    def fails(self, condition):
        report = self.run_report()
        self.assertEqual(report['failed'], 1)
        check = next(c for c in report['results'][0]['checks'] if c['condition'] == condition)
        self.assertFalse(check['passed'], check)

    def test_valid_chinese_profile_matches_english_query(self):
        report = self.run_report()
        self.assertEqual(report['failed'], 0, report)
        self.assertEqual(report['setup_errors'], [])

    def test_ascii_pokemon_and_case_variation_are_accepted(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person], title='JUNICHI MASUDA — Pokemon Interviews & Credits'))
        self.assertEqual(self.run_report()['failed'], 0)

    def test_entity_in_schema_does_not_replace_title(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person], title='Pokémon Developer Interviews'))
        self.fails('title_keywords')

    def test_hidden_english_alias_does_not_count_as_visible_identity(self):
        self.write(PROFILE, html(PROFILE, f'<p>增田顺一 · 増田順一</p><span hidden>Junichi Masuda</span><a href="{ARTICLE}">访谈</a><a href="{GAME}">名单</a>', [self.profile, self.person]))
        self.fails('visible_entity_names')

    def test_hidden_and_script_only_inbound_anchors_are_rejected(self):
        for wrapper in ['<div hidden>{}</div>', '<div aria-hidden="true">{}</div>', '<div style="display:none">{}</div>', '<div class="sr-only">{}</div>', '<script>var card = "{}";</script>']:
            with self.subTest(wrapper=wrapper):
                self.write('/', html('/', wrapper.format(f'<a href="{PROFILE}">Junichi Masuda</a>')))
                self.fails('anchor:1')

    def test_nofollow_anchor_is_rejected(self):
        self.write('/', html('/', f'<a rel="nofollow" href="{PROFILE}">Junichi Masuda</a>'))
        self.fails('anchor:1')

    def test_interview_must_reference_the_expected_person(self):
        self.article['about'] = {'@id': BASE + '/people/someone-else/#person'}
        self.write(ARTICLE, html(ARTICLE, '<p>访谈</p>', [self.article]))
        self.fails('anchor:2')

    def test_broken_subjectof_relationship_is_rejected(self):
        self.person['subjectOf'] = [{'@id': BASE + '/missing/#article'}]
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]))
        self.fails('schema:Person')

    def test_wrong_entity_identity_is_rejected(self):
        self.person['name'] = 'Someone Else'
        self.person['alternateName'] = ['增田顺一', '増田順一']
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]))
        self.fails('entity_identity')

    def test_duplicate_entity_definition_is_rejected(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person, self.person]))
        self.fails('unique_schema_ids')

    def test_wrong_language_and_noindex_are_rejected(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person], lang='en'))
        self.fails('language')
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]).replace('</head>', '<meta name="robots" content="noindex,follow"></head>'))
        self.fails('index_follow')

    def test_body_canonical_is_not_a_valid_head_canonical(self):
        canonical = f'<link rel="canonical" href="{BASE}{PROFILE}">'
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]).replace(canonical, '').replace('<body>', '<body>' + canonical))
        self.fails('canonical')

    def test_duplicate_canonical_is_rejected(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]).replace('</head>', f'<link rel="canonical" href="{BASE}/"></head>'))
        self.fails('canonical')

    def test_missing_or_duplicate_sitemap_landing_is_rejected(self):
        for urls in [[], [BASE + PROFILE, BASE + PROFILE]]:
            with self.subTest(urls=urls):
                self.sitemap(urls)
                self.fails('sitemap')

    def test_sitemap_index_is_supported(self):
        self.write('/sitemap.xml', f'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{BASE}/sitemap-people.xml</loc></sitemap></sitemapindex>')
        self.write('/sitemap-people.xml', f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{BASE}{PROFILE}</loc></url></urlset>')
        self.assertEqual(self.run_report()['failed'], 0)

    def test_oai_searchbot_block_is_rejected(self):
        self.write('/robots.txt', 'User-agent: OAI-SearchBot\nDisallow: /people/\n')
        self.fails('robots_access')

    def test_malformed_json_ld_is_reported_without_crashing(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person]).replace('</head>', '<script type="application/ld+json">{broken}</script></head>'))
        self.fails('json_ld_parse')

    def test_credited_works_count_must_match_linked_game_entities(self):
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person], description='1 related interview and Pokémon credits across 99 games.'))
        self.fails('fact:credited_works_count')

    def test_live_data_count_must_match_metadata_visible_stats_and_schema(self):
        data = '/assets/data/test-counts.json'
        self.write(data, json.dumps({'team_size': {'names': 12}}))
        fact = {'kind': 'data_count', 'name': 'credited_entries', 'data_file': data, 'data_path': 'team_size.names',
                'pattern': '(\\d+) credited entries', 'visible_region': 'atlas__nums', 'schema_type': 'ItemList', 'schema_property': 'numberOfItems'}
        self.spec['targets']['masuda']['required_facts'].append(fact)
        roll = {'@type': 'ItemList', '@id': BASE + PROFILE + '#roll', 'numberOfItems': 12}
        body = self.body + '<dl class="atlas__nums"><dt>署名</dt><dd>12</dd></dl>'
        desc = '1 related interview and Pokémon credits across 1 game. 12 credited entries.'
        self.write(PROFILE, html(PROFILE, body, [self.profile, self.person, roll], description=desc))
        self.assertEqual(self.run_report()['failed'], 0)
        for bad_body, bad_desc, bad_roll in [(body, desc.replace('12 credited', '13 credited'), roll),
                                              (body.replace('<dd>12', '<dd>13'), desc, roll),
                                              (body, desc, {**roll, 'numberOfItems': 13})]:
            with self.subTest(body=bad_body, description=bad_desc, roll=bad_roll):
                self.write(PROFILE, html(PROFILE, bad_body, [self.profile, self.person, bad_roll], description=bad_desc))
                self.fails('fact:credited_entries')

    def test_unknown_fact_and_duplicate_queries_fail_configuration_validation(self):
        for change in ['fact', 'query']:
            spec = deepcopy(self.spec)
            if change == 'fact':
                spec['targets']['masuda']['required_facts'][0]['kind'] = 'ranking_prediction'
            else:
                spec['queries'].append(deepcopy(spec['queries'][0]))
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(spec)

    def test_cli_failure_returns_nonzero_and_writes_readable_evidence(self):
        spec_file, report = self.site / 'benchmark.json', self.site / 'results.json'
        spec_file.write_text(json.dumps(self.spec), encoding='utf-8')
        self.write(PROFILE, html(PROFILE, self.body, [self.profile, self.person], lang='en'))
        command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'check_english_seo_benchmark.py'),
                   '--site', str(self.site), '--benchmark', str(spec_file), '--report', str(report)]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(report.read_text(encoding='utf-8'))['failed'], 1)
        self.assertIn('language', report.with_suffix('.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
