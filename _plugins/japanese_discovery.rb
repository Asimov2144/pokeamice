# frozen_string_literal: true

module PokeAmice
  # Fills site.data.ja_discovery for the Japanese entrance (_pages/ja-index.html, _layouts/japanese-archive.html):
  # the _ja collection grouped by year (with the Japanese era name), language, outlet and interviewee.
  class JapaneseDiscovery
    # language name on the page -> the one character its seal carries
    LANG_SEALS = {
      '英語' => '英', 'スペイン語' => '西', 'フランス語' => '仏',
      'イタリア語' => '伊', 'ドイツ語' => '独', '中国語' => '中', '韓国語' => '韓', 'ポルトガル語' => '葡'
    }.freeze

    def initialize(site)
      @site = site
      @posts = @site.posts.docs.to_h { |post| [File.basename(post.path, File.extname(post.path)), post] }
      @works = Array(site.data['works']).to_h { |work| [work['name'], work] }
      @games = Array(site.data['credits_games']).to_h { |game| [game['work'], game] }
      @people = {}
      Array(site.data['people']).each do |person|
        ([person['name']] + Array(person['aliases'])).each { |name| @people[name] ||= person }
      end
    end

    def apply
      docs = @site.collections['ja'].docs.sort_by { |doc| [doc.date, doc.url] }.reverse
      rows = docs.each_with_index.map { |doc, i| row(doc, docs.size - i) }

      years = rows.group_by { |r| r['year'] }.sort_by { |year, _| -year }.map do |year, items|
        { 'year' => year, 'era' => wareki(year), 'count' => items.size, 'items' => items }
      end

      @site.data['ja_discovery'] = {
        'count' => rows.size,
        'showcase' => showcase(rows),
        'years' => years,
        'first_year' => years.last['year'],
        'last_year' => years.first['year'],
        'timeline' => timeline(years),
        'languages' => tally(rows.map { |r| [r['lang'], r['seal']] }).map { |(name, seal), n| { 'name' => name, 'seal' => seal, 'count' => n } },
        'outlets' => tally(rows.map { |r| r['source'] }).map { |name, n| { 'name' => name, 'count' => n } },
        'people' => tally(rows.flat_map { |r| r['people'] }).map { |name, n| { 'name' => name, 'count' => n } }
      }
    end

    private

    def row(doc, no)
      d = doc.data
      lang = d['original_lang_name'].to_s
      names = Array(d['people_ja']).map(&:to_s).reject(&:empty?)
      post = @posts[d['zh_stem'].to_s]
      {
        'works' => works_for(post),
        'avatars' => names.filter_map { |name| (person = @people[name]) && person['avatar'] && { 'name' => name, 'src' => person['avatar'] } }.first(3),
        'initial' => d['source_name'].to_s.strip[0].to_s.upcase,
        'no' => format('%03d', no),
        'url' => doc.url,
        'title' => d['title'].to_s,
        'date' => doc.date.strftime('%Y.%m.%d'),
        'year' => doc.date.year,
        'source' => d['source_name'].to_s,
        'lang' => lang,
        'seal' => LANG_SEALS.fetch(lang, lang[0].to_s),
        'people' => names
      }
    end

    # The games the Chinese post is about, as the icons the site already draws for them (_data/works.yml);
    # the game's English title is the tooltip, a name every reader knows.
    def works_for(post)
      return [] unless post
      Array((post.data['entities'] || {})['works']).filter_map do |name|
        work = @works[name]
        next unless work && work['icon']
        { 'name' => name, 'title' => (@games[name] || {})['title'] || name, 'icon' => work['icon'], 'icon2' => work['icon2'], 'color' => work['color'] }
      end.uniq { |w| w['name'] }
    end

    # the games that come up most across the interviews: the icon wall in the hero
    def showcase(rows)
      counts = Hash.new(0)
      info = {}
      rows.each { |r| r['works'].each { |w| counts[w['name']] += 1; info[w['name']] ||= w } }
      counts.sort_by { |name, n| [-n, name] }.first(12).map { |name, n| info[name].merge('count' => n) }
    end

    # most frequent first; ties keep the order they first appear in
    def tally(values)
      counts = Hash.new(0)
      order = []
      values.reject { |v| v.nil? || v == '' || v == [nil, ''] }.each do |v|
        order << v unless counts.key?(v)
        counts[v] += 1
      end
      order.each_with_index.sort_by { |v, i| [-counts[v], i] }.map { |v, _| [v, counts[v]] }
    end

    # one tick per year from the first to the last; a year with interviews gets a dot
    def timeline(years)
      by_year = years.to_h { |y| [y['year'], y['count']] }
      (years.last['year']..years.first['year']).map do |year|
        { 'year' => year, 'count' => by_year[year].to_i, 'era' => wareki(year) }
      end
    end

    def wareki(year)
      if year >= 2019
        n = year - 2018
        "令和#{n == 1 ? '元' : n}年"
      elsif year >= 1989
        n = year - 1988
        "平成#{n == 1 ? '元' : n}年"
      else
        n = year - 1925
        "昭和#{n == 1 ? '元' : n}年"
      end
    end
  end
end

class JapaneseDiscoveryGenerator < Jekyll::Generator
  priority :low
  def generate(site)
    PokeAmice::JapaneseDiscovery.new(site).apply if site.collections['ja']
  end
end
