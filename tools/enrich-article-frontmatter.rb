require "yaml"
require "uri"
require "date"

ROOT = File.expand_path("..", __dir__)
POSTS = File.join(ROOT, "_posts")

GENERIC_TAGS = %w[
  Weibo Sites Tech PTCG 文档 日志 更新中 整理 翻译 采访 长文 分析 测试 公告
  PokeAmice Updating OpenSource HappyNewYear 施工中 OCR ScanTailor
].freeze

KNOWN_PEOPLE = %w[
  增田顺一 杉森建 大森滋 岩尾和昌 田尻智 一之瀬剛 James\ Turnner
].freeze

def frontmatter_parts(text)
  return unless text.start_with?("---\n")
  second = text.index("\n---", 4)
  return unless second

  frontmatter = text[4...second]
  body = text[(second + 4)..] || ""
  [frontmatter, body]
end

def yaml_data(frontmatter)
  YAML.safe_load(frontmatter, permitted_classes: [Date, Time], aliases: true) || {}
rescue Psych::SyntaxError
  {}
end

def normal_article?(data)
  layout = data["layout"].to_s
  return false if %w[scan-translation parallel-translation].include?(layout)
  return false if data["translation_segments"] || data["parallel_items"] || data["scan_pages"]

  true
end

def host_for(url)
  URI.parse(url).host.to_s.sub(/^www\./, "")
rescue URI::InvalidURIError
  ""
end

def title_for_url(url, label = nil)
  clean_label = label.to_s.gsub(/<[^>]+>/, "").strip
  return clean_label unless clean_label.empty? || clean_label =~ %r{\Ahttps?://}

  host = host_for(url)
  return "网页链接" if host.empty?

  case host
  when /weibo/
    "微博链接"
  when /pokeamice/
    "PokeAmice 链接"
  when /youtube|youtu\.be/
    "YouTube 视频"
  when /bilibili/
    "Bilibili 视频"
  when /wikipedia/
    "Wikipedia 条目"
  when /52poke/
    "神奇宝贝百科条目"
  when /dengekionline/
    "电击 Online 文章"
  else
    host
  end
end

def type_for_url(url)
  host = host_for(url)
  return "video" if host =~ /youtube|youtu\.be|bilibili|nicovideo/
  return "social" if host =~ /weibo|twitter|x\.com/
  return "wiki" if host =~ /wikipedia|52poke/
  return "image" if url =~ /\.(png|jpe?g|gif|webp)(\?|#|\z)/i

  "web"
end

def extract_links(body)
  links = []

  body.scan(/<a\b[^>]*href\s*=\s*["']([^"']+)["'][^>]*>(.*?)<\/a>/im) do |url, label|
    links << [url.strip, label.strip]
  end

  body.scan(/!?\[([^\]]*)\]\((https?:\/\/[^)\s]+)[^)]*\)/i) do |label, url|
    links << [url.strip, label.strip]
  end

  body.scan(%r{(?<!["'=])(https?://[^\s<>)]+)}i) do |match|
    links << [match.first.strip, nil]
  end

  seen = {}
  links.filter_map do |url, label|
    url = url.gsub(/[，。)、）\]\}]+$/, "")
    next unless url.start_with?("http")
    next if seen[url]

    seen[url] = true
    {
      "title" => title_for_url(url, label),
      "url" => url,
      "domain" => host_for(url),
      "type" => type_for_url(url)
    }
  end
end

def first_summary(body)
  text = body
    .gsub(/```.*?```/m, "")
    .gsub(/<[^>]+>/, " ")
    .gsub(/!\[[^\]]*\]\([^)]+\)/, " ")
    .gsub(/\[[^\]]+\]\([^)]+\)/, " ")
    .lines
    .map { |line| line.gsub(/[#*_`\\>&;　]/, " ").strip }
    .find { |line| line.length >= 12 }

  return nil unless text

  text.length > 96 ? "#{text[0, 96]}..." : text
end

def scalar(value)
  text = value.to_s
  "\"#{text.gsub("\\", "\\\\\\").gsub('"', '\"')}\""
end

def yaml_block(key, value, indent = 0)
  space = " " * indent
  case value
  when Hash
    lines = ["#{space}#{key}:"]
    value.each { |child_key, child_value| lines.concat(yaml_block(child_key, child_value, indent + 2)) }
    lines
  when Array
    lines = ["#{space}#{key}:"]
    value.each do |item|
      if item.is_a?(Hash)
        first, *rest = item.to_a
        lines << "#{" " * (indent + 2)}- #{first[0]}: #{scalar(first[1])}"
        rest.each { |child_key, child_value| lines.concat(yaml_block(child_key, child_value, indent + 4)) }
      else
        lines << "#{" " * (indent + 2)}- #{scalar(item)}"
      end
    end
    lines
  else
    ["#{space}#{key}: #{scalar(value)}"]
  end
end

def tags_from(data)
  Array(data["tags"]) + Array(data["categories"])
end

def infer_entities(data, body)
  tags = tags_from(data).map(&:to_s)
  text = ([data["title"]] + tags + [body[0, 4000]]).join(" ")
  people = KNOWN_PEOPLE.select { |name| text.include?(name.gsub("\\ ", " ")) }
  works = []
  works << "宝可梦" if text =~ /宝可梦|Pokemon|Pokémon/i
  works.concat(tags.reject { |tag| GENERIC_TAGS.include?(tag) || tag.length < 2 }.first(5))
  organizations = []
  organizations << "Poke Amice Docs" if tags.any? { |tag| tag =~ /PokeAmice|Sites|文档|站点/ }
  organizations << "Game Freak" if text =~ /Game\s*Freak/i
  organizations << "Nintendo" if text =~ /Nintendo|任天堂/i

  entities = {}
  entities["people"] = people.uniq unless people.empty?
  entities["works"] = works.uniq unless works.empty?
  entities["organizations"] = organizations.uniq unless organizations.empty?
  entities
end

def workflow_for(data)
  translated = tags_from(data).map(&:to_s).any? { |tag| tag.include?("翻译") || tag.include?("采访") }
  {
    "scan" => "pending",
    "preprocess" => "pending",
    "ocr" => "pending",
    "translation" => translated ? "done" : "pending",
    "proofreading" => "done",
    "published" => "done"
  }
end

changed = []

Dir.glob(File.join(POSTS, "*.md")).sort.each do |path|
  text = File.read(path, encoding: "UTF-8")
  parts = frontmatter_parts(text)
  next unless parts

  frontmatter, body = parts
  data = yaml_data(frontmatter)
  next unless normal_article?(data)

  insertions = []
  links = extract_links(body).reject { |item| item["type"] == "image" }.first(10)

  insertions.concat(yaml_block("archive_type", "article")) unless data.key?("archive_type")
  if !data.key?("summary")
    summary = first_summary(body)
    insertions.concat(yaml_block("summary", summary)) if summary
  end

  unless data.key?("source")
    main_link = links.find { |item| item["type"] != "social" } || links.first
    if main_link
      insertions.concat(yaml_block("source", {
        "title" => main_link["title"],
        "url" => main_link["url"],
        "source_type" => main_link["type"]
      }))
    end
  end

  insertions.concat(yaml_block("links", links)) if !data.key?("links") && !links.empty?
  insertions.concat(yaml_block("workflow", workflow_for(data))) unless data.key?("workflow")

  entities = infer_entities(data, body)
  insertions.concat(yaml_block("entities", entities)) if !data.key?("entities") && !entities.empty?

  next if insertions.empty?

  updated = text.sub(/\A---\n.*?\n---/m) do |match|
    "#{match.sub(/\n---\z/, "")}\n#{insertions.join("\n")}\n---"
  end
  File.write(path, updated, encoding: "UTF-8")
  changed << File.basename(path)
end

puts "Updated #{changed.size} article files"
changed.each { |name| puts "- #{name}" }
