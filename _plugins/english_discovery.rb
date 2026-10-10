# frozen_string_literal: true

require 'json'
require_relative 'search_metadata'

module PokeAmice
  class EnglishDiscovery
    def initialize(site)
      @site = site
      @config = site.data['english_discovery'] || {}
      @identities = site.data['person_identities'] || {}
      @metadata = SearchMetadata.new(site)
      @games = Array(site.data['credits_games'])
    end

    def apply
      interviews = @site.posts.docs.select { |post| SearchMetadata.interview?(post.data) }
      rows = interviews.map { |post| interview_row(post) }
      # The English shelf samples eras and then offers the complete Chinese index.
      eras = rows.group_by { |row| row['year'].to_i / 10 * 10 }.sort.map do |decade, group|
        { 'decade' => decade, 'count' => group.size,
          'items' => group.sort_by { |row| [row['original_en'] ? 0 : 1, row['year'], row['url']] }.first(6) }
      end
      people = @identities.values.map do |identity|
        record = @site.data['people'].find { |person| person['slug'] == identity['slug'] }
        credit = (@site.data['credits_people'] || {})[identity['slug']] || {}
        identity.merge('avatar' => record['avatar'],
                       'interviews' => rows.count { |row| row['people'].any? { |person| person['slug'] == identity['slug'] } },
                       'credited_games' => Array(credit['credits']).map { |row| row['game'] }.compact.uniq.size.nonzero? || credit['games'].to_i,
                       'roles' => @metadata.roles_for_credits(credit).first(3))
      end
      games = @games.map do |game|
        path = @site.in_source_dir("assets/data/credits-profile/#{game['slug']}.json")
        stats = File.file?(path) ? JSON.parse(File.read(path)) : {}
        game.merge('url' => "/credits/#{game['slug']}/", 'stats' => stats['coverage'] || {}, 'team' => stats['team_size'] || {})
      end
      posts = @site.posts.docs.to_h { |post| [File.basename(post.path, File.extname(post.path)), post] }
      recovered = Array(@config['recent_sources']).map do |entry|
        post = posts.fetch(entry['stem']) # Broken editorial references fail the build.
        interview_row(post).merge(entry)
      end
      @site.data['en_discovery'] = {
        'interview_count' => interviews.size, 'people_count' => people.size, 'game_count' => games.size,
        'scan_count' => @site.posts.docs.count { |post| Array(post.data['categories']).include?('扫描存档') || post.data['archive_type'] == 'scan_translation' },
        'japanese_count' => @site.collections['ja']&.docs&.size || 0,
        'people' => people.sort_by { |person| [-person['interviews'], person['name_en'] || person['name']] }.first(24),
        'featured_people' => Array(@config['featured_people']).map { |slug| people.find { |person| person['slug'] == slug } }.compact,
        'games' => games.sort_by { |game| [game['year'].to_s, game['slug']] },
        'major_games' => Array(@config['major_games']).map { |slug| games.find { |game| game['slug'] == slug } }.compact,
        'eras' => eras, 'english_originals' => rows.select { |row| row['original_en'] }.sort_by { |row| row['year'] }.reverse.first(8),
        'recent_sources' => recovered
      }
      @site.pages.select { |page| page.data['layout'] == 'english-discovery' }.each do |page|
        page.data['discovery_schema'] = schema(page)
      end
    end

    def interview_row(post)
      data = post.data
      source = data['source'].is_a?(Hash) ? data['source'] : {}
      language = (data['original_lang'] || data['original_language'] || source['language'] || data['source_language']).to_s.downcase
      url = [data['original_link'], data['original_url'], data['source_url'], source['url'], data['source'].is_a?(String) ? data['source'] : nil].find { |value| value.to_s.match?(%r{\Ahttps?://}) }
      people = Array((data['entities'] || {})['people']).filter_map { |name| @identities.values.find { |identity| identity['aliases'].include?(name) } }
      works = Array((data['entities'] || {})['works']).filter_map { |name| @games.find { |game| [game['work'], game['title_zh'], game['title']].include?(name) } }.uniq
      source_name = data['publication'] || source['publication'] || data['source_name'] || 'Archive source'
      english = %w[en en-us en-gb english 英语 英文].include?(language) && !url.nil?
      title = if english && !data['original_title'].to_s.empty?
                data['original_title']
              else
                subjects = people.first(3).map { |person| person['name_en'] || person['name'] }
                subjects = works.first(2).map { |game| game['title'] } if subjects.empty?
                "#{source_name} — #{subjects.empty? ? 'developer interview' : subjects.join(' / ')}"
              end
      stem = File.basename(post.path, File.extname(post.path))
      { 'url' => data['canonical_url'] || post.url, 'title' => title, 'chinese_title' => data['title'],
        'year' => post.date.year, 'source' => source_name, 'people' => people,
        'works' => works.map { |game| game['title'] }, 'original_en' => english,
        'original_url' => url, 'original_language' => language,
        'ja_url' => (@site.data['ja_edition'] || {})[stem],
        'chinese_translation' => data['archive_type'].to_s.end_with?('_translation') ||
          !data['translator'].to_s.empty? || !data['translation_segments'].nil? || !data['parallel_items'].nil? }
    end

    def schema(page)
      root = absolute('/en/')
      url = absolute(page.url)
      graph = [{ '@type' => 'CollectionPage', '@id' => "#{url}#page", 'url' => url,
                 'name' => page.data['title'], 'description' => page.data['description'],
                 'inLanguage' => 'en', 'isPartOf' => { '@id' => "#{root}#website" } }]
      if page.url == '/en/'
        graph << { '@type' => 'WebSite', '@id' => "#{root}#website", 'url' => root,
                   'name' => 'Poke Amice Docs', 'inLanguage' => 'en',
                   'description' => page.data['description'] }
      end
      { '@context' => 'https://schema.org', '@graph' => graph }
    end

    def absolute(path)
      return path if path.match?(%r{\Ahttps?://})
      "#{@site.config['url'].to_s.sub(%r{/$}, '')}#{@site.config['baseurl']}#{path}"
    end
  end
end

class EnglishDiscoveryGenerator < Jekyll::Generator
  priority :normal
  def generate(site)
    PokeAmice::EnglishDiscovery.new(site).apply
  end
end
