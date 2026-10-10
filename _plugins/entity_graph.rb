# frozen_string_literal: true

require 'cgi'
require 'json'
require 'uri'

module PokeAmice
  # Facts come from the rendered body, never the English SEO copy. Shared
  # canonical IDs connect references; an ID is defined only once per graph.
  class EntityGraph
    MARKER = '<script type="application/ld+json" data-pokeamice-entity-graph>POKEAMICE_ENTITY_GRAPH</script>'
    INTERVIEW_LIMIT = 8

    class VisiblePage
      attr_reader :body, :text, :links, :images, :canonical

      def initialize(html)
        head = html[/<head\b[^>]*>(.*?)<\/head>/mi, 1].to_s
        @canonical = head.scan(/<link\b([^>]+)>/mi).filter_map do |attributes|
          attrs = attributes.first
          attribute(attrs, 'href') if attribute(attrs, 'rel') == 'canonical'
        end.first
        @body = html[/<body\b[^>]*>(.*?)<\/body>/mi, 1].to_s
        @body = html if @body.empty?
        @body = @body.gsub(/<(script|style)\b[^>]*>.*?<\/\1>/mi, '').gsub(/<!--.*?-->/m, '')
        @text = plain(@body)
        @links = @body.scan(/<a\b([^>]+)>/mi).filter_map { |attrs| attribute(attrs.first, 'href') }
        @images = @body.scan(/<img\b([^>]+)>/mi).filter_map { |attrs| attribute(attrs.first, 'src') }
      end

      def attribute(attributes, name)
        CGI.unescapeHTML(attributes[/\b#{name}=["'](.*?)["']/mi, 1].to_s)
      end

      def plain(value)
        CGI.unescapeHTML(value.to_s.gsub(/<[^>]*>/m, ' ')).gsub(/\s+/, ' ').strip
      end

      def shown?(value)
        candidate = plain(value)
        !candidate.empty? && text.downcase.include?(candidate.downcase)
      end

      def heading
        plain(body[/<h1\b[^>]*>(.*?)<\/h1>/mi, 1])
      end

      def date_shown?(date)
        %w[%Y-%m-%d %Y.%m.%d %Y/%m/%d %Y年%m月%d日].any? { |format| body.include?(date.strftime(format)) }
      end

      def language_shown?(code)
        return false unless code.is_a?(String) && !code.empty?
        return true if body.match?(/\blang=["']#{Regexp.escape(code)}(?:["']|-)/i)
        return true if body.match?(/(?<![A-Za-z])#{Regexp.escape(code)}(?![A-Za-z])/i)
        labels = { 'en' => %w[英语 英語 English], 'ja' => %w[日语 日本語 Japanese], 'es' => %w[西班牙语 スペイン語 Spanish],
                   'fr' => %w[法语 フランス語 French], 'it' => %w[意大利语 イタリア語 Italian] }
        Array(labels[code]).any? { |label| shown?(label) }
      end

      def block(class_name, tag = 'p')
        plain(body[/<#{tag}\b[^>]*class=["'][^"']*\b#{class_name}\b[^"']*["'][^>]*>(.*?)<\/#{tag}>/mi, 1])
      end
    end

    def initialize(site)
      @site = site
      @people = Array(site.data['people']).to_h { |record| [record['slug'], record] }
      @profiles = Array(site.data['people_profiles']).to_h { |record| [record['slug'], record] }
      @games = Array(site.data['credits_games']).to_h { |record| [record['slug'], record] }
      @credits = site.data['credits_people'] || {}
      @game_credits = Hash.new { |hash, slug| hash[slug] = [] }
      @credits.each do |slug, record|
        Array(record['credits']).each { |credit| @game_credits[credit['game']] << [slug, credit['role'].to_s.split(' / ').last] }
      end
      @social = site.data['people_social'] || {}
      @catalog = (site.data['resource-index'] || {})['entities'] || {}
      @page_urls = site.pages.to_h { |page| [absolute(page.url), canonical(page)] }
      @people_names = {}
      @people.each_value do |person|
        next if %w[character figure].include?(person['kind'])
        credit = @credits[person['slug']] || {}
        [person['name'], *Array(person['aliases']), credit['name'], credit['kanji'], credit['kana']].compact.each do |name|
          @people_names[fold(name)] ||= person
        end
      end
      @work_names = {}
      @japanese_game_names = {}
      @games.each_value do |game|
        @japanese_game_names[game['slug']] = japanese_game_name(game)
        [game['title'], game['title_zh'], game['work'], @japanese_game_names[game['slug']]].compact.each { |name| @work_names[fold(name)] = game }
      end
      @org_names = (@catalog['organizations'] || {}).to_h { |name, record| [fold(name), record] }
      Array((site.data['structured_entities'] || {})['organizations']).each do |identity|
        record = @org_names[fold(identity['name'])]
        next unless record && !Array(identity['sources']).empty?
        Array(identity['aliases']).each { |name| @org_names[fold(name)] = record }
      end
      @post_urls = {}
      @person_posts = Hash.new { |hash, slug| hash[slug] = [] }
      @site.posts.docs.reverse_each do |post|
        @post_urls[post.object_id] = canonical(post)
        next unless SearchMetadata.interview?(post.data) && canonical(post) == absolute(post.url)
        participant_names(post.data).each do |name|
          person = resolve_person(name, post.data)
          @person_posts[person['slug']] << post if person
        end
      end
    end

    def prepare
      @site.pages.each do |page|
        next unless page.data['layout'] == 'credits-game'
        game = @games[page.data['game']]
        next unless game && @japanese_game_names[game['slug']]
        page.data['credits_japanese_name'] = @japanese_game_names[game['slug']]
      end
    end

    def render(document)
      return unless document.output.include?(MARKER)
      visible = VisiblePage.new(document.output)
      url = absolute(visible.canonical || canonical(document))
      # A redirected copy must not define its destination's Article again.
      graph = if url != absolute(document.url)
                []
              elsif document.data['layout'] == 'person'
                person_graph(document, visible, url)
              elsif document.data['layout'] == 'credits-game'
                game_graph(document, visible, url)
              else
                article_graph(document, visible, url)
              end
      payload = graph.empty? ? '' : "<script type=\"application/ld+json\">#{JSON.generate('@context' => 'https://schema.org', '@graph' => graph).gsub('<', '\\u003c')}</script>"
      document.output = document.output.sub(MARKER, payload)
    end

    def person_graph(page, visible, url)
      record = @people[page.data['slug']]
      return [] unless record && !%w[character figure].include?(record['kind'])
      identity = (@site.data['person_identities'] || {})[record['slug']]
      names = (identity ? identity['aliases'] : [record['name'], *Array(record['aliases'])]).compact.uniq.select { |name| visible.shown?(name) }
      english = identity ? identity['name_en'] : PersonIdentity.names(record, @credits[record['slug']] || {})['name_en']
      english = nil unless visible.shown?(english)
      person = { '@type' => 'Person', '@id' => "#{url}#person", 'name' => english || visible.heading,
                 'alternateName' => names, 'url' => url, 'mainEntityOfPage' => ref("#{url}#page") }
      image = record['avatar'] || (@social[record['slug']] || {})['avatar']
      person['image'] = absolute(image) if image && visible.images.any? { |src| absolute(src) == absolute(image) }
      person['jobTitle'] = record['role'] if record['role'] && visible.shown?(record['role'])
      profile = @profiles[record['slug']] || {}
      description = profile.dig('credits', 'line')
      description = visible.block('person__role') unless description && visible.shown?(description)
      person['description'] = description unless description.to_s.empty?
      social = @social[record['slug']] || {}
      if social['checked'] && social['found_via']
        accounts = Array(social['accounts']).map { |account| account['url'] }
        same_as = accounts.compact.select { |address| http?(address) && linked?(visible, address) }.uniq
        person['sameAs'] = same_as unless same_as.empty?
      end
      subjects = @person_posts[record['slug']].filter_map do |post|
        address = @post_urls[post.object_id]
        ref("#{address}#article") if linked?(visible, address)
      end.first(INTERVIEW_LIMIT)
      person['subjectOf'] = subjects unless subjects.empty?
      works = Array((@credits[record['slug']] || {})['credits']).filter_map do |credit|
        game = @games[credit['game']]
        ref(game_id(game)) if game && linked?(visible, game_url(game))
      end.uniq
      profile_page = { '@type' => 'ProfilePage', '@id' => "#{url}#page", 'name' => visible.heading,
                       'url' => url, 'inLanguage' => language(page), 'mainEntity' => ref(person['@id']) }
      profile_page['mentions'] = works unless works.empty?
      [profile_page, person]
    end

    def game_graph(page, visible, url)
      game = @games[page.data['game']]
      return [] unless game
      names = [game['title_zh'], game['title'], page.data['credits_japanese_name']].compact.uniq.select { |name| visible.shown?(name) }
      work = { '@type' => 'VideoGame', '@id' => "#{url}#game", 'name' => game['title_zh'],
               'alternateName' => names, 'url' => url, 'mainEntityOfPage' => ref("#{url}#page") }
      # ISO reduced precision: a known year is not an invented January 1.
      work['datePublished'] = game['year'].to_s if game['year'].to_s.match?(/\A\d{4}\z/) && visible.shown?(game['year'])
      nodes = []
      developers = developer_names(game['developer']).filter_map do |name|
        next unless visible.shown?(name)
        node = organization(name)
        nodes << node
        ref(node['@id'])
      end
      work['creator'] = developers unless developers.empty?
      # Specific credited roles, never an inferred employer or team membership.
      { 'director' => /\A(?:Director|Directors|Game Director)\z/i,
        'musicBy' => /\A(?:Music|Music Composition|Composers?|Original Music)\z/i }.each do |property, pattern|
        people = @game_credits[game['slug']].filter_map do |slug, role|
          person = @people[slug]
          next unless person && role.match?(pattern) && linked?(visible, person_url(person))
          ref(person_id(person))
        end.uniq
        work[property] = people unless people.empty?
      end
      roll = { '@type' => 'ItemList', '@id' => "#{url}#roll", 'name' => '名单',
               'url' => "#{url}#roll", 'numberOfItems' => game['count'].to_i }
      collection = { '@type' => 'CollectionPage', '@id' => "#{url}#page", 'name' => visible.heading,
                     'url' => url, 'inLanguage' => language(page), 'mainEntity' => ref(work['@id']),
                     'about' => ref(work['@id']), 'mentions' => ref(roll['@id']) }
      snapshot = visible.block('atlas__nums', 'dl')
      collection['description'] = snapshot.empty? ? visible.block('credits__meta') : snapshot
      [collection, work, roll, *nodes].uniq { |node| node['@id'] }
    end

    def article_graph(page, visible, url)
      data = page.data
      return [] if visible.heading.empty?
      graph = []
      article = { '@type' => 'Article', '@id' => "#{url}#article", 'headline' => visible.heading,
                  'name' => visible.heading, 'url' => url, 'inLanguage' => language(page),
                  'mainEntityOfPage' => { '@type' => 'WebPage', '@id' => url }, 'isAccessibleForFree' => true }
      description = [data['description'], data['summary'], data['dek']].compact.find { |text| visible.shown?(text) }
      article['description'] = visible.plain(description) if description
      source = data['source'].is_a?(Hash) ? data['source'] : {}
      original_url = [data['original_link'], data['original_url'], data['source_url'], source['url'], data['source']].find do |address|
        address.is_a?(String) && http?(address) && linked?(visible, address)
      end
      original_language = data['original_lang'] || data['original_language'] || source['language'] || data['source_language']
      original_language = nil unless visible.language_shown?(original_language)
      original_title = [data['original_title'], data['gf_original_title'], data['title_ja'], source['title']].compact.find { |title| visible.shown?(title) }
      paired = Array(data['parallel_items'] || data['translation_segments'] || data['segments']).any? { |item| item['translation'] && item['original'] }
      translated_text = paired || (data['translator'].is_a?(String) && visible.shown?(data['translator']))
      translation = data['archive_type'].to_s.end_with?('_translation') || (translated_text && original_language && original_language != language(page))
      if original_url || original_title
        original = { '@type' => 'CreativeWork', '@id' => original_url ? "#{absolute(original_url).sub(/#.*$/, '')}#original-work" : "#{url}#original-work" }
        original['url'] = absolute(original_url) if original_url
        original['name'] = visible.plain(original_title) if original_title
        original['inLanguage'] = original_language if original_language && !original_language.empty?
        archive = data['archive_type'] && data['archive_type'] != 'article'
        if (translation || archive) && page.respond_to?(:date) && visible.date_shown?(page.date) && !data.dig('recruit', 'date_basis')
          original['datePublished'] = page.date.strftime('%Y-%m-%d')
        end
        publication = [data['publication'], source['publication'], data['source_name']].compact.find { |name| visible.shown?(name) }
        if publication
          # A publication/issue label is not automatically a company name.
          label = { '@type' => 'CreativeWork', '@id' => "#{url}#publication", 'name' => visible.plain(publication) }
          graph << label
          original['isPartOf'] = ref(label['@id'])
          publisher_name = publication.split(/[（(]/).first.strip
          if @org_names[fold(publisher_name)]
            publisher = organization(publisher_name)
            graph << publisher
            original['publisher'] = ref(publisher['@id'])
          end
        end
        property = translation ? 'translationOfWork' : (data['archive_type'] && data['archive_type'] != 'article' ? 'isBasedOn' : 'citation')
        article[property] = ref(original['@id'])
        graph << original
      end
      # The displayed date of a translation belongs to the original. Git's
      # archive-added date is not an evidenced translation publication date.
      if !translation && !original_url && page.respond_to?(:date) && visible.date_shown?(page.date) && !data.dig('recruit', 'date_basis')
        article['datePublished'] = page.date.strftime('%Y-%m-%d')
      end
      author = author_ref(data['author'] || source['author'], visible, graph)
      if author
        original = graph.find { |node| node['@id'] == article.dig('translationOfWork', '@id') }
        (original || article)['author'] = author
      end
      translator = data['translator']
      translator_name = translator.is_a?(Hash) ? translator['name'] : translator
      if translator_name.is_a?(String) && visible.shown?(translator_name)
        # OCR/model workflow strings are credit text, not human/organization entities.
        article['creditText'] = translator_name
        translator_entity = author_ref(translator, visible, graph)
        article['translator'] = translator_entity if translator_entity
      end
      if visible.shown?(@site.config['title'])
        publisher = organization(@site.config['title'])
        graph << publisher
        article['publisher'] = ref(publisher['@id'])
      end
      entities, mentions = data['entities'] || {}, data['mentions'] || {}
      participants = person_refs(participant_names(data), visible, data)
      primary_people = participants.empty? && !SearchMetadata.interview?(data) ? person_refs(entities['people'], visible, data) : participants
      primary_works = work_refs(entities['works'], visible)
      about = (primary_people + primary_works).uniq
      article['about'] = about unless about.empty?
      other_people = person_refs(Array(entities['people']) + Array(mentions['people']), visible, data) - primary_people
      other_works = work_refs(mentions['works'], visible) - primary_works
      organizations = (Array(entities['organizations']) + Array(mentions['organizations'])).filter_map do |name|
        next unless visible.shown?(name)
        node = organization(name)
        graph << node
        ref(node['@id'])
      end
      referenced = (other_people + other_works + organizations).uniq
      article['mentions'] = referenced unless referenced.empty?
      image = visible.images.find { |src| src.include?('/interviews/') || src.include?('/scans/') }
      article['image'] = absolute(image) if image
      [article, *graph].uniq { |node| node['@id'] }
    end

    private

    def participant_names(data)
      items = Array(data['parallel_items'] || data['translation_segments'] || data['segments'])
      names = items.filter_map { |item| item['speaker'] if item['role'] == 'answer' }
      names.empty? ? data['interviewee'].to_s.split(/[,，、;；]/) : names.uniq
    end

    def resolve_person(name, data)
      name = (data['speaker_zh'] || {})[name] || name
      @people_names[fold(name)]
    end

    def person_refs(names, visible, data)
      Array(names).filter_map do |name|
        record = resolve_person(name, data)
        next unless record
        next unless [record['name'], *Array(record['aliases'])].any? { |alias_name| visible.shown?(alias_name) } || linked?(visible, person_url(record))
        ref(person_id(record))
      end.uniq
    end

    def work_refs(names, visible)
      Array(names).filter_map do |name|
        game = @work_names[fold(name)]
        if game
          aliases = [name, game['title'], game['title_zh'], game['work'], @japanese_game_names[game['slug']]].compact
          catalog = (@catalog['works'] || {})[name]
          next unless aliases.any? { |label| visible.shown?(label) } || linked?(visible, game_url(game)) || (catalog && linked?(visible, catalog['url']))
          ref(game_id(game))
        elsif (record = (@catalog['works'] || {})[name])
          next unless visible.shown?(name) || linked?(visible, record['url'])
          ref("#{absolute(record['url'])}#work")
        end
      end.uniq
    end

    def author_ref(author, visible, graph)
      name = author.is_a?(Hash) ? author['name'] : author
      return unless name.is_a?(String) && visible.shown?(name)
      person = @people_names[fold(name)]
      return ref(person_id(person)) if person
      return unless @org_names[fold(name)] || (author.is_a?(Hash) && author['type'] == 'Organization')
      node = organization(name)
      graph << node
      ref(node['@id'])
    end

    def organization(name)
      record = @org_names[fold(name)]
      url = record && page_url(record['url'])
      id = url ? "#{url}#organization" : "#{absolute('/')}#organization-#{CGI.escape(fold(name)).gsub('+', '%20')}"
      node = { '@type' => 'Organization', '@id' => id, 'name' => name }
      node['url'] = url if url
      node
    end

    def developer_names(value)
      # A comma in a legal company name is not a separator between developers.
      protected = value.to_s.gsub(/,\s*(?=(?:Inc\.?|Ltd\.?|Corp\.?)\b)/i, "\u0001")
      protected.split(/\s*(?:\/|,|、|\+|&|×)\s*/).map do |name|
        name.gsub("\u0001", ', ').sub(/\s*\(\d{4}-(?:\d{4}|present)\)\z/i, '').strip
      end.reject(&:empty?)
    end

    def japanese_game_name(game)
      return unless game['source_ja']
      # An explicit Japanese staff-list title, not a guessed translation.
      title = CGI.unescape(URI.parse(absolute(game['source_ja'])).path.split('/wiki/', 2).last.to_s)
      title.delete_suffix('のスタッフクレジット').tr('_', ' ') if title.end_with?('のスタッフクレジット')
    end

    def language(page)
      page.data['lang'] || page.data['translation_lang'] || @site.config['locale'] || 'zh-CN'
    end

    def fold(name)
      name.to_s.downcase.gsub(/[\s・·]/, '')
    end

    def ref(id)
      { '@id' => id }
    end

    def person_url(person)
      page_url("/people/#{person['slug']}/")
    end

    def person_id(person)
      "#{person_url(person)}#person"
    end

    def game_url(game)
      page_url("/credits/#{game['slug']}/")
    end

    def game_id(game)
      "#{game_url(game)}#game"
    end

    def canonical(page)
      absolute(page.data['canonical_url'] || page.url).sub(%r{/index\.html\z}, '/')
    end

    def page_url(path)
      @page_urls[absolute(path)] || absolute(path)
    end

    def absolute(value)
      address = value.to_s
      address = "#{@site.config['url'].to_s.sub(%r{/$}, '')}#{@site.config['baseurl']}#{address.start_with?('/') ? address : '/' + address}" unless http?(address)
      URI::DEFAULT_PARSER.escape(address, /[^A-Za-z0-9\-._~!$&'()*+,;=:\/%?#\[\]@]/)
    end

    def http?(value)
      value.to_s.match?(%r{\Ahttps?://}i)
    end

    def linked?(visible, address)
      links = visible.instance_variable_get(:@absolute_links)
      unless links
        links = visible.links.to_h { |href| [absolute(href), true] }
        visible.instance_variable_set(:@absolute_links, links)
      end
      links.key?(absolute(address))
    end
  end
end

class EntityGraphGenerator < Jekyll::Generator
  priority :lowest

  def generate(site)
    builder = PokeAmice::EntityGraph.new(site)
    builder.prepare
    site.instance_variable_set(:@pokeamice_entity_graph, builder)
  end
end

%i[pages documents].each do |owner|
  Jekyll::Hooks.register owner, :post_render do |document|
    document.site.instance_variable_get(:@pokeamice_entity_graph)&.render(document)
  end
end
