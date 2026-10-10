# frozen_string_literal: true

require 'jekyll'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require 'yaml'
require_relative '../../_plugins/search_metadata'
require_relative '../../_plugins/entity_graph'

class EntityGraphTest < Minitest::Test
  BASE = 'https://docs.pokeamice.com'
  Page = Struct.new(:data, :url, :output, :date)
  Site = Struct.new(:data, :config, :posts, :pages)

  def setup
    @people = [
      { 'name' => '增田顺一', 'slug' => 'masuda-junichi', 'aliases' => ['増田順一', 'Junichi Masuda'], 'avatar' => '/masuda.jpg' },
      { 'name' => '宫本茂', 'slug' => 'miyamoto-shigeru', 'aliases' => ['Shigeru Miyamoto'] }
    ]
    @game = { 'slug' => 'x-y', 'title' => 'Pokémon X and Y', 'title_zh' => '宝可梦 X·Y', 'year' => 2013,
              'developer' => 'Game Freak', 'count' => 580, 'source_ja' => 'https://example.com/wiki/ポケットモンスター_X・Yのスタッフクレジット' }
    @data = {
      'people' => @people, 'people_profiles' => [], 'credits_games' => [@game],
      'credits_people' => {
        'masuda-junichi' => { 'credits' => [{ 'game' => 'x-y', 'role' => 'Game Freak / Director' }] },
        'miyamoto-shigeru' => { 'credits' => [{ 'game' => 'x-y', 'role' => 'Art Director' }, { 'game' => 'x-y', 'role' => 'Special Thanks' }] }
      },
      'people_social' => { 'masuda-junichi' => { 'checked' => '本人核实', 'found_via' => '官方页面',
                                             'accounts' => [{ 'url' => 'https://x.com/Junichi_Masuda' }, { 'url' => 'https://x.com/not-visible' }] } },
      'resource-index' => { 'entities' => { 'organizations' => { 'Game Freak' => { 'name' => 'Game Freak', 'url' => '/entities/organizations/game-freak/' } } } }
    }
    @person_page = Page.new({ 'layout' => 'person', 'slug' => 'masuda-junichi' }, '/people/masuda-junichi/')
    @game_page = Page.new({ 'layout' => 'credits-game', 'game' => 'x-y' }, '/credits/x-y/')
    @site = Site.new(@data, { 'url' => BASE, 'title' => 'Poke Amice Docs', 'locale' => 'zh-CN' }, Struct.new(:docs).new([]), [@person_page, @game_page])
  end

  def build
    @builder = PokeAmice::EntityGraph.new(@site)
    @builder.prepare
    @builder
  end

  def visible(text, url = '/people/masuda-junichi/', head: '')
    PokeAmice::EntityGraph::VisiblePage.new("<html><head><link rel='canonical' href='#{BASE}#{url}'>#{head}</head><body>#{text}</body></html>")
  end

  def article(data = {})
    Page.new({ 'archive_type' => 'interview_translation', 'entities' => { 'people' => ['增田顺一', '宫本茂'], 'works' => ['宝可梦 X·Y'] },
               'parallel_items' => [{ 'role' => 'answer', 'speaker' => '增田顺一' }] }.merge(data), '/interview/example/', nil, Time.new(2013, 9, 21))
  end

  def test_person_uses_visible_verified_facts_and_omits_inferred_employment
    @person_page.data['search_metadata'] = { 'description' => 'English SEO description', 'major_roles' => ['Producer'] }
    build
    body = visible('<h1>增田顺一</h1><p>Junichi Masuda · 増田順一</p><img src="/masuda.jpg"><p class="person__role">宝可梦 X·Y · Director</p><a href="https://x.com/Junichi_Masuda">账号</a><a href="/credits/x-y/">X·Y</a>')
    graph = @builder.person_graph(@person_page, body, BASE + @person_page.url)
    person = graph.last
    assert_equal 'Person', person['@type']
    assert_equal 'Junichi Masuda', person['name']
    assert_equal ['增田顺一', '増田順一', 'Junichi Masuda'], person['alternateName']
    assert_equal [ 'https://x.com/Junichi_Masuda' ], person['sameAs']
    assert_equal BASE + '/masuda.jpg', person['image']
    assert_equal '宝可梦 X·Y · Director', person['description']
    assert_nil person['jobTitle']
    assert_nil person['worksFor']
    assert_equal [{ '@id' => BASE + '/credits/x-y/#game' }], graph.first['mentions']
    @data['people_social']['masuda-junichi'].delete('checked')
    build
    assert_nil @builder.person_graph(@person_page, body, BASE + @person_page.url).last['sameAs']
  end

  def test_head_only_names_and_descriptions_are_not_schema_facts
    build
    body = visible('<h1>增田顺一</h1>', head: '<title>Junichi Masuda — Producer</title><meta name="description" content="English SEO description">')
    person = @builder.person_graph(@person_page, body, BASE + @person_page.url).last
    assert_equal '增田顺一', person['name']
    assert_equal ['增田顺一'], person['alternateName']
    assert_nil person['description']
    assert_nil person['image']
    assert_nil person['sameAs']
  end

  def test_reverse_interviews_are_bounded_id_references_and_exclude_mentions
    @site.posts.docs = 12.times.map { |i| article.tap { |post| post.url = "/interview/#{i}/" } }
    build
    @site.posts.docs.each { |post| post.output = '<p>Rendered after the index was created</p>' }
    links = @site.posts.docs.map { |post| "<a href='#{post.url}'>访谈</a>" }.join
    masuda = @builder.person_graph(@person_page, visible('<h1>增田顺一</h1>' + links), BASE + @person_page.url).last
    assert_equal 8, masuda['subjectOf'].size
    assert masuda['subjectOf'].all? { |item| item.keys == ['@id'] && item['@id'].end_with?('#article') }
    other = Page.new({ 'layout' => 'person', 'slug' => 'miyamoto-shigeru' }, '/people/miyamoto-shigeru/')
    miyamoto = @builder.person_graph(other, visible('<h1>宫本茂</h1>' + links), BASE + other.url).last
    assert_nil miyamoto['subjectOf'], 'Mentioning a person does not make them an interviewee'
  end

  def test_game_names_statistics_and_explicit_director_match_the_body
    build
    body = visible('<h1>宝可梦 X·Y 制作名单</h1><p>Pokémon X and Y / ポケットモンスター X・Y / 2013 / Game Freak</p><dl class="atlas__nums"><dt>署名</dt><dd>580</dd><dt>人</dt><dd>533</dd></dl><a href="/people/masuda-junichi/">增田顺一</a><a href="/people/miyamoto-shigeru/">宫本茂</a>', @game_page.url)
    graph = @builder.game_graph(@game_page, body, BASE + @game_page.url)
    game = graph.find { |node| node['@type'] == 'VideoGame' }
    assert_includes game['alternateName'], 'ポケットモンスター X・Y'
    assert_equal '2013', game['datePublished']
    assert_equal [{ '@id' => BASE + '/people/masuda-junichi/#person' }], game['director']
    assert_equal [{ '@id' => BASE + '/entities/organizations/game-freak/#organization' }], game['creator']
    assert_equal 580, graph.find { |node| node['@type'] == 'ItemList' }['numberOfItems']
    assert_equal '署名 580 人 533', graph.first['description']
    assert_nil game['musicBy']
    assert_equal graph.size, graph.map { |node| node['@id'] }.uniq.size
  end

  def test_translation_has_one_article_and_distinguishes_interviewees_from_mentions
    build
    page = article('original_link' => 'https://example.com/interview', 'original_lang' => 'en', 'source' => { 'title' => 'Original interview' }, 'publication' => 'Nintendo Life（2013-09-21）', 'translator' => 'OCR / DeepSeek 初译')
    body = visible('<h1>开发者访谈</h1><p>增田顺一和宫本茂讨论宝可梦 X·Y。 Original interview Nintendo Life（2013-09-21） OCR / DeepSeek 初译 EN 2013.09.21</p><a href="https://example.com/interview">原文</a>', page.url)
    graph = @builder.article_graph(page, body, BASE + page.url)
    article_node = graph.first
    assert_equal 1, graph.count { |node| node['@type'] == 'Article' }
    assert_equal [{ '@id' => BASE + '/people/masuda-junichi/#person' }, { '@id' => BASE + '/credits/x-y/#game' }], article_node['about']
    assert_includes article_node['mentions'], { '@id' => BASE + '/people/miyamoto-shigeru/#person' }
    original = graph.find { |node| node['@id'] == article_node.dig('translationOfWork', '@id') }
    assert_equal 'https://example.com/interview#original-work', original['@id']
    assert_equal 'en', original['inLanguage']
    assert_equal '2013-09-21', original['datePublished']
    assert_equal({ '@id' => original['@id'] }, article_node['translationOfWork'])
    assert_equal 'OCR / DeepSeek 初译', article_node['creditText']
    assert_nil article_node['translator']
    assert_nil article_node['datePublished']
  end

  def test_unknown_language_date_and_author_are_not_guessed
    build
    page = article('original_link' => 'https://example.com/interview', 'author' => 'Unverified combined author', 'source' => { 'title' => 'Original interview' }, 'recruit' => { 'date_basis' => '约2013年' })
    graph = @builder.article_graph(page, visible('<h1>访谈</h1><p>Original interview Unverified combined author 2013.09.21</p><a href="https://example.com/interview">原文</a>', page.url), BASE + page.url)
    assert_nil graph.first['author']
    original = graph.find { |node| node['@type'] == 'CreativeWork' }
    assert_nil original['inLanguage']
    assert_nil original['datePublished']
    assert_nil original['publisher'], 'Source title is not proof of publisher identity'
  end

  def test_legal_company_names_and_joint_developers_do_not_create_phantom_organizations
    @game['developer'] = 'Creatures, Inc., DeNA Co., Ltd.'
    @data['resource-index']['entities']['organizations']['Creatures'] = { 'name' => 'Creatures', 'url' => '/entities/organizations/creatures/' }
    @data['structured_entities'] = { 'organizations' => [{ 'name' => 'Creatures', 'aliases' => ['Creatures, Inc.'], 'sources' => ['https://www.creatures.co.jp/company/'] }] }
    build
    graph = @builder.game_graph(@game_page, visible('<h1>宝可梦 X·Y</h1><p>Creatures, Inc., DeNA Co., Ltd.</p>', @game_page.url), BASE + @game_page.url)
    companies = graph.select { |node| node['@type'] == 'Organization' }
    assert_equal ['Creatures, Inc.', 'DeNA Co., Ltd.'], companies.map { |node| node['name'] }
    assert_equal BASE + '/entities/organizations/creatures/#organization', companies.first['@id']
    @game['developer'] = 'Nintendo × Game Freak'
    graph = @builder.game_graph(@game_page, visible('<h1>宝可梦 X·Y</h1><p>Nintendo × Game Freak</p>', @game_page.url), BASE + @game_page.url)
    assert_equal ['Nintendo', 'Game Freak'], graph.select { |node| node['@type'] == 'Organization' }.map { |node| node['name'] }
    @game['developer'] = 'SELECT BUTTON inc. (2023-2024), The Pokémon Works (2024-present)'
    graph = @builder.game_graph(@game_page, visible('<h1>宝可梦 X·Y</h1><p>SELECT BUTTON inc. (2023-2024), The Pokémon Works (2024-present)</p>', @game_page.url), BASE + @game_page.url)
    assert_equal ['SELECT BUTTON inc.', 'The Pokémon Works'], graph.select { |node| node['@type'] == 'Organization' }.map { |node| node['name'] }
  end

  def test_verified_social_accounts_do_not_include_a_third_party_artist_directory
    @data['people_social']['masuda-junichi']['artofpkm'] = 'https://www.artofpkm.com/illustrators/example'
    build
    body = visible('<h1>增田顺一</h1><a href="https://x.com/Junichi_Masuda">账号</a><a href="https://www.artofpkm.com/illustrators/example">插画目录</a>')
    person = @builder.person_graph(@person_page, body, BASE + @person_page.url).last
    assert_equal ['https://x.com/Junichi_Masuda'], person['sameAs']
  end

  def test_localized_game_mentions_use_the_same_id_without_invisible_chinese_copy
    build
    page = article('lang' => 'ja', 'entities' => { 'works' => ['宝可梦 X·Y'] }, 'parallel_items' => [])
    body = visible('<h1>開発者インタビュー</h1><p>ポケットモンスター X・Y</p>', page.url)
    graph = @builder.article_graph(page, body, BASE + page.url)
    assert_equal [{ '@id' => BASE + '/credits/x-y/#game' }], graph.first['about']
    refute JSON.generate(graph).include?('宝可梦 X·Y')
  end

  def test_references_follow_canonical_destinations_and_redirects_emit_no_duplicate_entity
    @person_page.data['canonical_url'] = '/people/canonical-person/'
    build
    page = article
    graph = @builder.article_graph(page, visible('<h1>访谈</h1><p>增田顺一</p>', page.url), BASE + page.url)
    assert_includes graph.first['about'], { '@id' => BASE + '/people/canonical-person/#person' }
    @person_page.output = "<head><link rel='canonical' href='#{BASE}/people/canonical-person/'></head><body><h1>增田顺一</h1>#{PokeAmice::EntityGraph::MARKER}</body>"
    @builder.render(@person_page)
    refute_includes @person_page.output, 'application/ld+json'
  end

  def test_actual_jekyll_post_render_hooks_replace_markers_for_pages_and_documents
    Dir.mktmpdir('entity-graph') do |root|
      %w[_data _layouts _includes _posts].each { |path| FileUtils.mkdir_p(File.join(root, path)) }
      File.write(File.join(root, '_data/people.yml'), YAML.dump(@people))
      File.write(File.join(root, '_layouts/default.html'), '<html><head><link rel="canonical" href="{{ page.url | absolute_url }}">{% include entity-schema.html %}</head><body>{{ content }}</body></html>')
      File.write(File.join(root, '_includes/entity-schema.html'), PokeAmice::EntityGraph::MARKER)
      File.write(File.join(root, 'person.html'), "---\nlayout: default\nslug: masuda-junichi\npermalink: /people/masuda-junichi/\n---\n<h1>增田顺一</h1><p>Junichi Masuda</p>")
      File.write(File.join(root, '_posts/2013-09-21-interview.md'), "---\nlayout: default\narchive_type: interview_translation\ninterviewee: 增田顺一\npermalink: /interview/real/\n---\n<h1>访谈</h1><p>增田顺一</p>")
      # The actual person layout is needed for dispatch; the outer default still renders the head.
      File.write(File.join(root, '_layouts/person.html'), "---\nlayout: default\n---\n{{ content }}")
      File.write(File.join(root, 'person.html'), File.read(File.join(root, 'person.html')).sub('layout: default', 'layout: person'))
      site = Jekyll::Site.new(Jekyll.configuration('source' => root, 'destination' => File.join(root, '_site'), 'url' => BASE, 'title' => 'Poke Amice Docs', 'locale' => 'zh-CN', 'quiet' => true))
      site.process
      { 'people/masuda-junichi/index.html' => 'Person', 'interview/real/index.html' => 'Article' }.each do |path, type|
        html = File.read(File.join(site.dest, path))
        refute_includes html, 'POKEAMICE_ENTITY_GRAPH'
        graphs = html.scan(/<script type="application\/ld\+json">(.*?)<\/script>/m).map { |match| JSON.parse(match.first)['@graph'] }
        assert_equal 1, graphs.size
        assert_equal 1, graphs.flatten.count { |node| node['@type'] == type }
      end
    end
  end
end
