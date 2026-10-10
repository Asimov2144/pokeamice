# frozen_string_literal: true

require 'cgi'

module PokeAmice
  # One sourced identity projection for head metadata, visible anchors and search.
  # Missing romanizations are left missing; slugs are never used as names.
  module PersonIdentity
    def self.names(registry, credits = {}, page = {})
      candidates = [registry['name_en'], *Array(registry['aliases']), registry['name'], credits['name']].compact
      english = candidates.find { |name| name.match?(/\p{Latin}/) && !name.match?(/[\p{Han}\p{Hiragana}\p{Katakana}]/) }
      chinese = [registry['name_zh'], registry['name'], page['person']].compact.find { |name| name.match?(/\p{Han}/) }
      japanese = [registry['name_ja'], credits['kanji'], *Array(registry['aliases']), credits['kana']].compact.find do |name|
        name.match?(/[\p{Han}\p{Hiragana}\p{Katakana}]/) && (name != chinese || name == credits['kanji'] || name == registry['name_ja'])
      end
      { 'name_en' => english, 'name_ja' => japanese, 'name_zh' => chinese }
    end

    def self.records(site)
      Array(site.data['people']).reject { |record| %w[character figure].include?(record['kind']) }.to_h do |record|
        credit = (site.data['credits_people'] || {})[record['slug']] || {}
        identity = names(record, credit).merge('slug' => record['slug'], 'name' => record['name'], 'url' => "/people/#{record['slug']}/")
        identity['aliases'] = [record['name'], *Array(record['aliases']), *identity.values_at('name_zh', 'name_ja', 'name_en'), credit['name'], credit['kana']].compact.uniq
        identity['label'] = [identity['name_zh'] || record['name'], identity['name_en']].compact.uniq.join(' · ')
        [record['slug'], identity]
      end
    end
  end

  module PersonIdentityFilters
    def person_identity(value)
      data = @context.registers[:site].data
      identities = data['person_identities'] || {}
      identities[value] || identities[(data['person_identity_aliases'] || {})[value]]
    end

    def person_record(value)
      data = @context.registers[:site].data
      identity = person_identity(value)
      return (data['person_records'] || {})[identity['slug']] if identity

      # Portraits of characters/cited figures can still appear without a profile link.
      Array(data['people']).find { |record| record['name'] == value }
    end

    # Staff rolls are generated HTML. Enrich their existing links at render time
    # instead of rewriting ninety-three generated files or duplicating name logic.
    def person_links(html)
      identities = @context.registers[:site].data['person_identities'] || {}
      base = @context.registers[:site].config['baseurl'].to_s
      html.to_s.gsub(%r{(<a\b[^>]*\bhref=["'])(/people/([^/"']+)/)(["'][^>]*>)([^<]*)(</a>)}i) do
        before, path, slug, attrs, text, close = Regexp.last_match.captures
        identity = identities[slug]
        "#{before}#{base}#{path}#{attrs}#{identity ? CGI.escapeHTML(identity['label']) : text}#{close}"
      end
    end
  end
end

Liquid::Template.register_filter(PokeAmice::PersonIdentityFilters)

class PersonIdentityGenerator < Jekyll::Generator
  priority :highest

  def generate(site)
    site.data['person_identities'] = PokeAmice::PersonIdentity.records(site)
    site.data['person_records'] = Array(site.data['people']).to_h { |record| [record['slug'], record] }
    site.data['person_identity_aliases'] = {}
    site.data['person_identities'].each do |slug, identity|
      identity['aliases'].each { |name| site.data['person_identity_aliases'][name] ||= slug }
    end
  end
end
