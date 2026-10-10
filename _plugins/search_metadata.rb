# frozen_string_literal: true

require 'json'
require 'set'
require_relative 'person_identity'

module PokeAmice
  # A head-only projection of the existing registry. Never rewrites page.title,
  # page content, language, URL or the generated person/credits source files.
  class SearchMetadata
    TITLE_LIMIT = 80
    DESCRIPTION_LIMIT = 190
    ROLE_RULES = {
      'director' => /\bdirectors?\b/i,
      'producer' => /\bproducers?\b|\bproduced by\b/i,
      'composer' => /\bcompos(?:er|ers|ition)\b|\bmusic\b/i,
      'game designer' => /\bgame[ -]design(?:er|ers)?\b|\bplanning\b|\bplanners?\b/i,
      'programmer' => /\bprogram(?:mer|mers|ming)?\b/i,
      'artist' => /\bart(?:ists?)?\b|\bgraphics?\b|\billustrat|\bcharacter(?:s)? design\b|\b(?:pokémon|monster) design\b/i,
      'writer' => /\bscenario\b|\bscript\b|\bwriters?\b/i,
      'localization specialist' => /\blocali[sz]ation\b|\btranslat/i,
      'QA staff member' => /\bqa\b|\bdebug|\btest(?:er|ers|ing)?\b/i
    }.freeze

    def initialize(site)
      @site = site
      @people = index(site.data['people'])
      @profiles = index(site.data['people_profiles'])
      @credits = site.data['credits_people'] || {}
      @games = index(site.data['credits_games'])
      @interviews = Hash.new { |hash, name| hash[name] = Set.new }
      @related = Hash.new { |hash, name| hash[name] = Set.new }
      site.posts.docs.each do |post|
        names = Array((post.data['entities'] || {})['people'])
        names.each { |name| @related[name] << post.url }
        next unless self.class.interview?(post.data)

        names.each { |name| @interviews[name] << post.url }
      end
    end

    # The profile's spoken_in includes memoirs and reports. Count published
    # interview entries instead, including scanned interviews, but not columns.
    def self.interview?(data)
      categories = Array(data['categories']).join(' ')
      title = data['title'].to_s
      archive = data['archive_type'].to_s
      return false if data['search'] == false
      return false if archive.start_with?('gamefreak_')
      return false if "#{categories} #{title}".match?(/手记|回忆录|专栏|memoir|\bcolumn\b|コラム/i)

      named_interview = title.match?(/访谈|采访|对谈|座谈|インタビュー|\binterview\b/i)
      return named_interview if %w[scan_translation media_feature].include?(archive)

      archive == 'interview_translation' ||
        (named_interview && %w[interview-editorial parallel-translation].include?(data['layout']))
    end

    def apply
      pages = @site.pages.filter_map do |page|
        next if page.data['lang'] == 'ja'

        metadata = case page.data['layout']
                   when 'person' then person(page)
                   when 'credits-game' then game(page)
                   when 'people-index' then people_collection
                   when 'credits-index' then credits_collection
                   when 'home' then interview_collection if page.url == '/'
                   end
        next unless metadata

        page.data['search_metadata'] = metadata
        page
      end
      unique_titles(pages)
    end

    def person(page)
      registry = @people[page.data['slug']] || {}
      return if %w[character figure].include?(registry['kind'])

      credits = @credits[page.data['slug']] || {}
      profile = @profiles[page.data['slug']] || {}
      names = identity(registry, credits, page.data)
      name = names['name_en'] || names['name_zh'] || registry['name'] || page.data['title']
      aliases = [names['name_ja'], names['name_zh']].compact.uniq - [name]
      identity_text = aliases.empty? ? name : "#{name} (#{aliases.join(' / ')})"
      interview_count = @interviews[registry['name'] || page.data['person']].size
      related_count = @related[registry['name'] || page.data['person']].size
      works = Array(credits['credits']).map { |credit| credit['game'] }.compact.uniq.size
      works = credits['games'] || profile.dig('credits', 'games') if works.zero?
      works = works.to_i
      roles = major_roles(credits)

      purpose = if interview_count.positive? && works.to_i.positive?
                  'Interviews & Pokémon Credits'
                elsif interview_count.positive?
                  'Interview Archive'
                elsif works.to_i.positive?
                  'Pokémon Staff Credits'
                else
                  'Pokémon Articles & Sources'
                end
      facts = []
      facts << "#{interview_count} related #{plural(interview_count, 'interview')}" if interview_count.positive?
      facts << "Pokémon credits across #{works} #{plural(works, 'game')}" if works.to_i.positive?
      facts << "#{related_count} related #{plural(related_count, 'article')}" if facts.empty? && related_count.positive?
      lead = roles.empty? ? "#{identity_text}." : "#{identity_text}: #{sentence_list(roles)}."
      detail = facts.empty? ? 'Source-linked Pokémon archive records.' : "#{sentence_list(facts)}."
      description = "#{lead} #{detail} Chinese-language archive with original sources."
      # Drop the longer role clause before shortening factual/name information.
      if description.length > DESCRIPTION_LIMIT && !roles.empty?
        description = "#{identity_text}: #{roles.first}. #{detail} Chinese archive with sources."
      end
      description = "#{identity_text}. #{detail} Chinese archive with sources." if description.length > DESCRIPTION_LIMIT

      # Preserve Chinese/Japanese search identity in the title when the full
      # entity name and page intent fit. Longer names stay in the description.
      title_names = [identity_text]
      title_names << "#{name} (#{names['name_zh']})" if names['name_zh'] && names['name_zh'] != name
      title_names << name
      title = title_names.uniq.map { |candidate| "#{candidate} — #{purpose}" }
                         .find { |candidate| branded_length(candidate) <= TITLE_LIMIT }
      title ||= "#{shorten(name, title_budget - purpose.length - 3)} — #{purpose}"
      result(title, description).merge(
        'identity' => names, 'interview_count' => interview_count,
        'credited_works_count' => works, 'major_roles' => roles
      )
    end

    def game(page)
      record = @games[page.data['game']]
      return unless record

      profile_path = File.join(@site.source, 'assets', 'data', 'credits-profile', "#{record['slug']}.json")
      atlas = File.file?(profile_path) ? JSON.parse(File.read(profile_path, encoding: 'UTF-8')) : {}
      size = atlas['team_size'] || {}
      entries = size['names'] || record['count']
      people = size['persons']
      name = record['title']
      # Long paired releases repeat series words. Keep a credits intent even
      # when the complete game name cannot fit beside the site name.
      compact_name = name.sub('Explorers of Time and Explorers of Darkness', 'Explorers of Time & Darkness')
                         .sub('Red Rescue Team and Blue Rescue Team', 'Red & Blue Rescue Team')
      choices = ["#{name} Staff Credits & Development Team", "#{name} Staff Credits",
                 "#{compact_name} Staff Credits", "#{compact_name} Credits"]
      title = choices.find { |choice| branded_length(choice) <= TITLE_LIMIT }
      title ||= "#{shorten(compact_name, title_budget - ' Staff Credits'.length)} Staff Credits"
      facts = []
      facts << "#{entries} credited #{plural(entries, 'entry', 'entries')}" unless entries.nil?
      facts << "#{people} #{plural(people, 'person', 'people')}" unless people.nil?
      features = ['department breakdown']
      features << 'development atlas' unless atlas.empty?
      features << 'source-linked staff profiles'
      description = "#{name} staff credits: #{sentence_list(facts)}. Includes #{sentence_list(features)}."
      if description.length > DESCRIPTION_LIMIT
        description = "#{name} staff credits: #{sentence_list(facts)}. Includes #{sentence_list(features[0...-1])}."
      end
      result(title, description).merge(
        'credited_entries_count' => entries, 'people_count' => people
      )
    end

    def people_collection
      count = @people.values.count { |person| !%w[character figure].include?(person['kind']) }
      result('Pokémon Developers & Staff',
             "Browse #{count} Pokémon developer and staff profiles, with multilingual names, interviews, game credits and original sources. Chinese-language archive.")
    end

    def credits_collection
      result('Pokémon Game Staff Credits',
             "Explore staff credits for #{@games.size} Pokémon games, with department breakdowns, development atlases and linked staff profiles. Chinese-language archive.")
    end

    def interview_collection
      result('Pokémon Developer Interview Archive',
             'Explore interviews with Pokémon and Game Freak developers, Chinese translations, original sources, game staff credits and development documents.')
    end

    # Shared factual role projection for the English directory's visible summaries.
    def roles_for_credits(credits)
      major_roles(credits)
    end

    private

    def index(records)
      Array(records).to_h { |record| [record['slug'], record] }
    end

    def identity(registry, credits, page)
      PersonIdentity.names(registry, credits, page)
    end

    def major_roles(credits)
      games = Hash.new { |hash, role| hash[role] = Set.new }
      Array(credits['credits']).each do |credit|
        # A section heading such as "Planning Section / Composers" describes
        # the department, not a second job. Use the leaf role for attribution.
        role = credit['role'].to_s.split(' / ').last.to_s
        ROLE_RULES.each do |label, pattern|
          next unless role.match?(pattern)
          next if label == 'director' && role.match?(/art|graphic|character|sound|music|effect|movie|locali[sz]|translation/i)
          next if label == 'game designer' && role.match?(/advis[oe]r|supervis/i)
          # Sound effects and sound direction alone do not establish composition.
          next if label == 'composer' && role.match?(/music.*(?:coordination|management|locali[sz]ation|supervis)/i)

          games[label] << credit['game']
        end
      end
      # Ignore incidental one-off credits when a person's established role
      # spans many games. Prefer the core roles over a generic design label.
      threshold = games.values.map(&:size).max.to_i * 0.25
      ROLE_RULES.keys.select { |role| games.key?(role) && games[role].size >= threshold }.first(3)
    end

    def plural(number, singular, plural = "#{singular}s")
      number.to_i == 1 ? singular : plural
    end

    def sentence_list(items)
      return items.join(' and ') if items.size <= 2

      "#{items[0...-1].join(', ')} and #{items.last}"
    end

    def result(title, description)
      { 'title' => shorten(title, title_budget),
        'description' => shorten(description, DESCRIPTION_LIMIT) }
    end

    def title_budget
      TITLE_LIMIT - @site.config['title'].to_s.length - 3
    end

    def shorten(text, limit)
      return text if text.length <= limit

      prefix = text[0, limit - 1]
      prefix = prefix.sub(/\s+\S*\z/, '') if prefix.include?(' ')
      "#{prefix.rstrip}…"
    end

    def branded_length(title)
      title.length + @site.config['title'].to_s.length + 3
    end

    def unique_titles(pages)
      pages.group_by { |page| page.data['search_metadata']['title'].downcase }.each_value do |duplicates|
        next if duplicates.size == 1

        duplicates.each do |page|
          metadata = page.data['search_metadata']
          slug = page.data['slug'] || page.data['game'] || page.url.delete('/')
          # Keep the distinguishing part intact, even for long/missing names.
          suffix = " (#{slug})"
          budget = TITLE_LIMIT - @site.config['title'].to_s.length - 3 - suffix.length
          metadata['title'] = "#{shorten(metadata['title'], budget)}#{suffix}"
        end
      end
    end
  end
end

class EnglishSearchMetadataGenerator < Jekyll::Generator
  priority :low

  def generate(site)
    PokeAmice::SearchMetadata.new(site).apply
  end
end
