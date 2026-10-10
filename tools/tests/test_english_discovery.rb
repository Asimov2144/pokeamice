# frozen_string_literal: true

require 'jekyll'
require 'minitest/autorun'
require 'tmpdir'
require_relative '../../_plugins/english_discovery'

class EnglishDiscoveryTest < Minitest::Test
  Post = Struct.new(:data, :url, :date, :path)

  def setup
    @site = Jekyll::Site.new(Jekyll.configuration('source' => Dir.tmpdir, 'url' => 'https://docs.pokeamice.com', 'quiet' => true))
    @site.data['people'] = [{ 'slug' => 'masuda-junichi', 'name' => '增田顺一', 'aliases' => ['増田順一', 'Junichi Masuda'] }]
    @site.data['credits_people'] = { 'masuda-junichi' => { 'name' => "Jun'ichi Masuda", 'kanji' => '増田順一', 'games' => 2,
      'credits' => [{ 'game' => 'x-y', 'role' => 'Director' }, { 'game' => 'x-y', 'role' => 'Music' }, { 'game' => 'red-green', 'role' => 'Music' }] } }
    @site.data['credits_games'] = [{ 'slug' => 'x-y', 'title' => 'Pokémon X and Y', 'title_zh' => '宝可梦 X·Y', 'count' => 580, 'year' => 2013 }]
    PersonIdentityGenerator.new.generate(@site)
    @builder = PokeAmice::EnglishDiscovery.new(@site)
  end

  def post(data = {})
    Post.new({ 'title' => '访谈', 'layout' => 'interview-editorial', 'archive_type' => 'interview_translation',
               'entities' => { 'people' => ['增田顺一'], 'works' => ['宝可梦 X·Y'] } }.merge(data),
             '/interview/example/', Time.new(2013, 10, 12), '_posts/2013-10-12-example.md')
  end

  def test_identity_keeps_one_romanization_and_all_sourced_names
    identity = @site.data['person_identities']['masuda-junichi']
    assert_equal '增田顺一 · Junichi Masuda', identity['label']
    assert_equal '増田順一', identity['name_ja']
    assert_includes identity['aliases'], "Jun'ichi Masuda"
    page = Struct.new(:data).new({ 'slug' => 'masuda-junichi', 'person' => '增田顺一' })
    assert_equal 'Junichi Masuda', PokeAmice::SearchMetadata.new(@site).person(page)['identity']['name_en']
    assert_nil PokeAmice::PersonIdentity.names({ 'name' => '未知', 'slug' => 'unknown-developer' })['name_en']
  end

  def test_source_spelling_and_japanese_alias_resolve_to_the_same_profile
    template = Liquid::Template.parse('{% assign p = source_name | person_identity %}{{ p.url }}|{{ p.label }}|{% assign r = source_name | person_record %}{{ r.slug }}')
    ["Jun'ichi Masuda", '増田順一', '增田顺一', 'Junichi Masuda'].each do |name|
      assert_equal '/people/masuda-junichi/|增田顺一 · Junichi Masuda|masuda-junichi',
                   template.render!({ 'source_name' => name }, registers: { site: @site })
    end
    @site.data['people'] << { 'slug' => 'pikachu', 'name' => '皮卡丘', 'kind' => 'character' }
    PersonIdentityGenerator.new.generate(@site)
    assert_equal '||pikachu', template.render!({ 'source_name' => '皮卡丘' }, registers: { site: @site })
  end

  def test_original_english_requires_language_and_source_not_an_english_title
    refute @builder.interview_row(post('original_title' => 'English looking title', 'original_link' => 'https://example.com/'))['original_en']
    refute @builder.interview_row(post('original_lang' => 'en'))['original_en']
    assert @builder.interview_row(post('original_lang' => 'en', 'original_link' => 'https://example.com/'))['original_en']
    refute @builder.interview_row(post('original_lang' => 'ja', 'original_link' => 'https://example.com/'))['original_en']
  end

  def test_japanese_availability_requires_an_actual_edition_mapping
    refute @builder.interview_row(post)['ja_url']
    @site.data['ja_edition'] = { '2013-10-12-example' => '/ja/example/' }
    assert_equal '/ja/example/', @builder.interview_row(post)['ja_url']
  end

  def test_credits_count_unique_games_and_keep_data_source_counts
    @site.posts.docs << post
    @builder.apply
    record = @site.data['en_discovery']['people'].first
    assert_equal 2, record['credited_games']
    assert_equal 1, record['interviews']
    assert_equal 580, @site.data['en_discovery']['games'].first['count']
  end

  def test_schema_uses_canonical_english_collection_and_one_website
    page = Struct.new(:data, :url).new({ 'title' => 'Research archive', 'description' => 'Visible introduction' }, '/en/')
    graph = @builder.schema(page)['@graph']
    assert_equal 1, graph.count { |node| node['@type'] == 'WebSite' }
    assert_equal 'https://docs.pokeamice.com/en/#page', graph.first['@id']
    assert_equal 'en', graph.first['inLanguage']
    page.url = '/en/people/'
    assert_equal ['CollectionPage'], @builder.schema(page)['@graph'].map { |node| node['@type'] }
  end

  def test_generated_staff_roll_and_atlas_links_share_the_identity_label
    original = '<a href="/people/masuda-junichi/">Jun\'ichi Masuda</a> <a href="/people/unregistered/">Unregistered Person</a>'
    template = Liquid::Template.parse('{{ roll | person_links }}')
    rendered = template.render!({ 'roll' => original }, registers: { site: @site })
    assert_includes rendered, '>增田顺一 · Junichi Masuda</a>'
    assert_includes rendered, '>Unregistered Person</a>'
    assert_equal '増田順一', @site.data['person_identities']['masuda-junichi']['name_ja']
  end
end
