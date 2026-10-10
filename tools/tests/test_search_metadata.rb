# frozen_string_literal: true

require 'jekyll'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require 'cgi'
require_relative '../../_plugins/search_metadata'

class SearchMetadataTest < Minitest::Test
  Page = Struct.new(:data, :url)
  Post = Struct.new(:data, :url)
  Site = Struct.new(:data, :config, :source, :posts, :pages)

  def setup
    @directory = Dir.mktmpdir('search-metadata')
    @site = Site.new(
      { 'people' => [], 'people_profiles' => [], 'credits_people' => {}, 'credits_games' => [] },
      { 'title' => 'Poke Amice Docs', 'url' => 'https://docs.pokeamice.com/', 'baseurl' => '' },
      @directory, Struct.new(:docs).new([]), []
    )
  end

  def teardown
    FileUtils.remove_entry(@directory)
  end

  def person(slug = 'masuda-junichi', name = '增田顺一', aliases = ['増田順一', 'Junichi Masuda'])
    @site.data['people'] << { 'slug' => slug, 'name' => name, 'aliases' => aliases }
    page = Page.new({ 'layout' => 'person', 'slug' => slug, 'person' => name, 'title' => name }, "/people/#{slug}/")
    @site.pages << page
    page
  end

  def apply
    PokeAmice::SearchMetadata.new(@site).apply
  end

  def test_multilingual_identity_does_not_change_chinese_title_or_invent_names
    page = person
    apply
    metadata = page.data['search_metadata']
    assert_equal '增田顺一', page.data['title']
    assert_includes metadata['title'], 'Junichi Masuda (増田順一 / 增田顺一)'
    assert_equal 'Junichi Masuda', metadata.dig('identity', 'name_en')
    assert_equal '増田順一', metadata.dig('identity', 'name_ja')
    assert_includes metadata['description'], '増田順一 / 增田顺一'
    assert_nil metadata['schema'], 'Entity schema is independent of the head-only SEO projection'

    other = person('unknown', '未录姓名', [])
    apply
    assert_nil other.data.dig('search_metadata', 'identity', 'name_en')
    assert_nil other.data.dig('search_metadata', 'identity', 'name_ja')
  end

  def test_interview_count_excludes_memoirs_blogs_and_hidden_posts_and_deduplicates_urls
    page = person
    entries = [
      ['a', 'interview_translation', '开发访谈', nil],
      ['a', 'interview_translation', '开发访谈', nil],
      ['b', 'scan_translation', '开发者采访', nil],
      ['c', 'interview_translation', '动画回忆录', nil],
      ['d', 'gamefreak_staff_blog', '开发者访谈', nil],
      ['e', 'scan_translation', '杂志专题', nil],
      ['f', 'interview_translation', '开发访谈', false]
    ]
    @site.posts.docs = entries.map do |url, archive, title, search|
      Post.new({ 'entities' => { 'people' => ['增田顺一'] }, 'archive_type' => archive, 'title' => title, 'search' => search }, "/#{url}/")
    end
    @site.data['people_profiles'] << { 'slug' => 'masuda-junichi', 'interviews' => { 'spoken_in' => 999 } }
    apply
    assert_equal 2, page.data.dig('search_metadata', 'interview_count')
    assert_includes page.data.dig('search_metadata', 'description'), '2 related interviews'
  end

  def test_credit_works_are_unique_and_roles_do_not_infer_jobs_from_department_or_advisor
    page = person
    @site.data['credits_people']['masuda-junichi'] = {
      'credits' => [
        { 'game' => 'red-green', 'role' => 'Director' },
        { 'game' => 'red-green', 'role' => 'Music Composition' },
        { 'game' => 'x-y', 'role' => 'Produced By' },
        { 'game' => 'x-y', 'role' => 'Planning Section / Composers' },
        { 'game' => 'sun-moon', 'role' => 'Game Design Advisors' }
      ]
    }
    apply
    assert_equal 3, page.data.dig('search_metadata', 'credited_works_count')
    assert_equal %w[director producer composer], page.data.dig('search_metadata', 'major_roles')
  end

  def test_incidental_qa_and_art_direction_do_not_become_general_director
    page = person('artist', 'Artist', ['Artist'])
    @site.data['credits_people']['artist'] = { 'credits' => (1..8).map { |i| { 'game' => i.to_s, 'role' => 'Art Director' } } + [{ 'game' => 'a', 'role' => 'Debug Play' }] }
    apply
    assert_equal ['artist'], page.data.dig('search_metadata', 'major_roles')
  end

  def test_credits_numbers_follow_atlas_and_fallback_does_not_guess_unique_people
    @site.data['credits_games'] = [{ 'slug' => 'x-y', 'title' => 'Pokémon X and Y', 'title_zh' => '宝可梦 X／Y', 'count' => 20 }]
    page = Page.new({ 'layout' => 'credits-game', 'game' => 'x-y', 'title' => '宝可梦 X／Y' }, '/credits/x-y/')
    @site.pages << page
    apply
    assert_includes page.data.dig('search_metadata', 'description'), '20 credited entries'
    refute_includes page.data.dig('search_metadata', 'description'), '20 people'
    refute_includes page.data.dig('search_metadata', 'description'), 'development atlas'

    directory = File.join(@directory, 'assets/data/credits-profile')
    FileUtils.mkdir_p(directory)
    File.write(File.join(directory, 'x-y.json'), JSON.generate('team_size' => { 'names' => 37, 'persons' => 29 }))
    apply
    assert_includes page.data.dig('search_metadata', 'description'), '37 credited entries and 29 people'
    assert_includes page.data.dig('search_metadata', 'description'), 'development atlas'
    assert_nil page.data.dig('search_metadata', 'schema')
  end

  def test_long_titles_keep_credits_intent_and_brand_within_limit
    @site.data['credits_games'] = [{ 'slug' => 'long', 'title' => 'Pokémon Mystery Dungeon: Explorers of Time and Explorers of Darkness', 'count' => 175 }]
    page = Page.new({ 'layout' => 'credits-game', 'game' => 'long' }, '/credits/long/')
    @site.pages << page
    apply
    title = page.data.dig('search_metadata', 'title')
    assert_match(/Credits\z/, title)
    assert_operator "#{title} | #{@site.config['title']}".length, :<=, 80
    assert_includes page.data.dig('search_metadata', 'description'), '175 credited entries'
  end

  def test_same_english_name_gets_distinct_titles_and_characters_and_japanese_pages_are_untouched
    first = person('alex-a', '甲', ['Alex'])
    second = person('alex-b', '甲', ['Alex'])
    japanese = person('ja', '日文', ['Japanese'])
    japanese.data['lang'] = 'ja'
    character = person('pikachu', '皮卡丘', ['Pikachu'])
    @site.data['people'].last['kind'] = 'character'
    apply
    refute_equal first.data.dig('search_metadata', 'title'), second.data.dig('search_metadata', 'title')
    assert_nil japanese.data['search_metadata']
    assert_nil character.data['search_metadata']
  end

  def test_only_the_main_homepage_gets_interview_collection_metadata
    main = Page.new({ 'layout' => 'home' }, '/')
    other = Page.new({ 'layout' => 'home' }, '/poke/')
    @site.pages.concat([main, other])
    apply
    assert_equal 'Pokémon Developer Interview Archive', main.data.dig('search_metadata', 'title')
    assert_nil other.data['search_metadata']
  end

  def test_real_seo_include_preserves_plain_text_pipe_and_name_punctuation
    include_directory = File.join(@directory, '_includes')
    FileUtils.mkdir_p(include_directory)
    %w[seo.html page-image.html].each do |name|
      FileUtils.cp(File.expand_path("../../_includes/#{name}", __dir__), include_directory)
    end
    config = Jekyll.configuration('source' => @directory, 'destination' => File.join(@directory, '_site'),
                                  'quiet' => true, 'title' => 'Poke Amice Docs', 'url' => 'https://docs.pokeamice.com')
    site = Jekyll::Site.new(config)
    page = Jekyll::PageWithoutAFile.new(site, @directory, 'people/test', 'index.html')
    title = "Ken'ichi Test — Pokémon Staff Credits"
    description = "Ken'ichi Test. Pokémon credits across 3 games."
    page.data['search_metadata'] = { 'title' => title, 'description' => description }
    page.content = '{% include seo.html %}'
    html = Jekyll::Renderer.new(site, page, site.site_payload).run
    assert_equal "#{title} | Poke Amice Docs", CGI.unescapeHTML(html[/<title>(.*?)<\/title>/m, 1])
    assert_equal description, CGI.unescapeHTML(html[/<meta name="description" content="([^"]*)"/, 1])
  end
end
