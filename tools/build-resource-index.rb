require "cgi"
require "date"
require "digest"
require "fileutils"
require "json"
require "psych"
require "time"

ROOT = File.expand_path("..", __dir__)
POSTS_DIR = File.join(ROOT, "_posts")
DATA_DIR = File.join(ROOT, "_data")
GENERATED_DIR = File.join(ROOT, "_pages", "generated")

ENTITY_TYPES = {
  "people" => "人物",
  "works" => "作品",
  "organizations" => "组织",
  "events" => "事件"
}.freeze

def read_front_matter(path)
  text = File.read(path, encoding: "UTF-8")
  match = text.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  return [{}, text] unless match

  yaml = Psych.safe_load(
    match[1],
    permitted_classes: [Date, Time, Symbol],
    aliases: true
  ) || {}
  [yaml, text[(match.end(0))..] || ""]
rescue Psych::Exception => error
  warn "Skip #{path}: #{error.message}"
  [{}, ""]
end

def array(value)
  case value
  when nil
    []
  when Array
    value.compact.map(&:to_s).reject(&:empty?)
  else
    [value.to_s].reject(&:empty?)
  end
end

def entity_map(value)
  value = {} unless value.is_a?(Hash)
  ENTITY_TYPES.keys.each_with_object({}) do |key, memo|
    memo[key] = array(value[key] || value[key.to_sym])
  end
end

def merge_entities(parent, child, inherit)
  parent = entity_map(parent)
  child = entity_map(child)
  ENTITY_TYPES.keys.each_with_object({}) do |key, memo|
    source = inherit ? parent[key] + child[key] : child[key]
    memo[key] = source.uniq
  end
end

def compact_entities(entities)
  entities.select { |_key, values| values.any? }
end

def slug(value)
  text = value.to_s.strip
  ascii = text.downcase.gsub(/[^0-9a-z]+/, "-").gsub(/\A-|-+\z/, "")
  ascii.empty? ? CGI.escape(text).gsub("%", "").downcase[0, 48] : ascii
end

def permalink_part(value, downcase: true)
  text = value.to_s
  text = text.downcase if downcase
  text.gsub(/[^\p{Alnum}\p{Han}\p{Hiragana}\p{Katakana}\p{Hangul}]+/u, "-")
      .gsub(/\A-+|-+\z/, "")
end

def strip_markdown(text)
  text.to_s
      .gsub(/\{[%{].*?[%}]\}/m, "")
      .gsub(/!\[[^\]]*\]\([^)]+\)/, "")
      .gsub(/\[([^\]]+)\]\([^)]+\)/, "\\1")
      .gsub(/[`*_>#]/, "")
      .gsub(/\s+/, " ")
      .strip
end

def post_url(path, front)
  categories = array(front["categories"])
  date_slug = File.basename(path, ".md").sub(/\A\d{4}-\d{2}-\d{2}-/, "")
  category_parts = categories.map { |part| permalink_part(part, downcase: true) }
  title_part = permalink_part(date_slug, downcase: false)
  "/" + (category_parts + [title_part]).reject(&:empty?).join("/") + "/"
end

def post_year(front)
  date = front["date"]
  return date.year.to_s if date.respond_to?(:year)
  text = date.to_s
  match = text.match(/\d{4}/)
  match ? match[0] : ""
end

def source_title(front, annotation = nil)
  annotation_source = annotation.is_a?(Hash) ? annotation["source"] || annotation[:source] : nil
  return annotation_source if annotation_source.is_a?(String)
  return annotation_source["title"] if annotation_source.is_a?(Hash) && annotation_source["title"]

  source = front["source"]
  return source["title"] if source.is_a?(Hash) && source["title"]
  return front["publication"] if front["publication"]
  ""
end

def entity_url(type, name)
  "/entities/#{type}/#{slug(name)}/"
end

def add_entity(index, type, name)
  index["entities"][type][name] ||= {
    "name" => name,
    "type" => type,
    "type_label" => ENTITY_TYPES[type],
    "url" => entity_url(type, name),
    "posts" => [],
    "annotations" => [],
    "years" => []
  }
end

def add_timeline(index, year)
  return if year.to_s.empty?
  index["timeline"][year] ||= {
    "year" => year,
    "url" => "/timeline/#{year}/",
    "posts" => [],
    "annotations" => []
  }
end

def unique_push(list, item, key)
  list << item unless list.any? { |existing| existing[key] == item[key] }
end

index = {
  "generated_at" => Time.now.iso8601,
  "entities" => ENTITY_TYPES.keys.to_h { |type| [type, {}] },
  "timeline" => {},
  "posts" => [],
  "annotations" => []
}

Dir.glob(File.join(POSTS_DIR, "*.md")).sort.each do |path|
  front, body = read_front_matter(path)
  title = front["title"].to_s.empty? ? File.basename(path, ".md") : front["title"].to_s
  url = post_url(path, front)
  year = post_year(front)
  entities = entity_map(front["entities"])
  post_record = {
    "id" => Digest::SHA1.hexdigest(path.sub(ROOT, ""))[0, 10],
    "title" => title,
    "url" => url,
    "date" => front["date"].to_s,
    "year" => year,
    "source" => source_title(front),
    "type" => front["archive_type"] || front["resource_type"] || array(front["categories"]).first || "article",
    "excerpt" => strip_markdown(front["excerpt"] || body).slice(0, 180).to_s,
    "entities" => compact_entities(entities)
  }

  index["posts"] << post_record
  add_timeline(index, year)
  unique_push(index["timeline"][year]["posts"], post_record, "url") unless year.empty?

  ENTITY_TYPES.keys.each do |type|
    entities[type].each do |name|
      entity = add_entity(index, type, name)
      unique_push(entity["posts"], post_record, "url")
      entity["years"] << year unless year.empty? || entity["years"].include?(year)
    end
  end

  annotations = front["annotations"].is_a?(Array) ? front["annotations"] : []
  annotations.each_with_index do |annotation, annotation_index|
    next unless annotation.is_a?(Hash)

    inherit = annotation["inherit_entities"] != false
    annotation_entities = merge_entities(front["entities"], annotation["entities"], inherit)
    next if compact_entities(annotation_entities).empty?

    annotation_id = annotation["id"] || "annotation-#{annotation_index + 1}"
    annotation_year = (annotation["date"] || year).to_s[/\d{4}/] || year
    annotation_record = {
      "id" => "#{post_record["id"]}-#{annotation_id}",
      "annotation_id" => annotation_id.to_s,
      "title" => annotation["title"].to_s.empty? ? "未命名评注" : annotation["title"].to_s,
      "type" => annotation["type"] || "note",
      "text" => strip_markdown(annotation["text"]).slice(0, 220).to_s,
      "url" => "#{url}#annotation-#{slug(annotation_id)}",
      "link_url" => annotation["url"].to_s,
      "date" => annotation["date"].to_s,
      "year" => annotation_year,
      "source" => source_title(front, annotation),
      "post_title" => title,
      "post_url" => url,
      "entities" => compact_entities(annotation_entities)
    }

    index["annotations"] << annotation_record
    add_timeline(index, annotation_year)
    unique_push(index["timeline"][annotation_year]["annotations"], annotation_record, "id") unless annotation_year.to_s.empty?

    ENTITY_TYPES.keys.each do |type|
      annotation_entities[type].each do |name|
        entity = add_entity(index, type, name)
        unique_push(entity["annotations"], annotation_record, "id")
        entity["years"] << annotation_year unless annotation_year.to_s.empty? || entity["years"].include?(annotation_year)
      end
    end
  end
end

ENTITY_TYPES.keys.each do |type|
  index["entities"][type].each_value do |entity|
    entity["years"].sort!.reverse!
    entity["posts"].sort_by! { |post| post["date"].to_s }.reverse!
    entity["annotations"].sort_by! { |annotation| [annotation["year"].to_s, annotation["post_title"].to_s] }.reverse!
  end
end

index["timeline"].each_value do |year|
  year["posts"].sort_by! { |post| post["date"].to_s }.reverse!
  year["annotations"].sort_by! { |annotation| [annotation["date"].to_s, annotation["post_title"].to_s] }.reverse!
end

FileUtils.mkdir_p(DATA_DIR)
File.write(File.join(DATA_DIR, "resource-index.json"), JSON.pretty_generate(index), encoding: "UTF-8")

FileUtils.rm_rf(GENERATED_DIR)
FileUtils.mkdir_p(GENERATED_DIR)

def write_page(path, front, body)
  FileUtils.mkdir_p(File.dirname(path))
  yaml = front.map { |key, value| "#{key}: #{value.to_json}" }.join("\n")
  File.write(path, "---\n#{yaml}\n---\n\n#{body}", encoding: "UTF-8")
end

def card_list(items, empty)
  return "<p class=\"resource-network-empty\">#{empty}</p>" if items.empty?

  items.map do |item|
    meta = [item["year"], item["type"], item["source"]].compact.reject(&:empty?).join(" · ")
    text = item["excerpt"] || item["text"]
    <<~HTML
      <article class="resource-network-card">
        <p>#{CGI.escapeHTML(meta)}</p>
        <h3><a href="#{item["url"]}">#{CGI.escapeHTML(item["title"])}</a></h3>
        <span>#{CGI.escapeHTML(text.to_s)}</span>
      </article>
    HTML
  end.join("\n")
end

def annotation_list(items)
  return "<p class=\"resource-network-empty\">暂无评注。</p>" if items.empty?

  items.map do |item|
    meta = [item["year"], item["source"], item["post_title"]].compact.reject(&:empty?).join(" · ")
    <<~HTML
      <article class="resource-network-card resource-network-card--annotation">
        <p>#{CGI.escapeHTML(meta)}</p>
        <h3><a href="#{item["url"]}">#{CGI.escapeHTML(item["title"])}</a></h3>
        <span>#{CGI.escapeHTML(item["text"].to_s)}</span>
      </article>
    HTML
  end.join("\n")
end

ENTITY_TYPES.each do |type, label|
  entities = index["entities"][type].values.sort_by { |entity| entity["name"] }
  listing = entities.map do |entity|
    count = entity["posts"].size + entity["annotations"].size
    "<a href=\"#{entity["url"]}\"><strong>#{CGI.escapeHTML(entity["name"])}</strong><span>#{count} 条资料</span></a>"
  end.join("\n")

  write_page(
    File.join(GENERATED_DIR, "entities", "#{type}.md"),
    {
      "title" => "#{label}索引",
      "permalink" => "/entities/#{type}/",
      "layout" => "single",
      "search" => false
    },
    <<~HTML
      <section class="resource-network-page">
        <div class="resource-network-hero">
          <p>#{label} Index</p>
          <h2>#{label}索引</h2>
          <span>由文章和评注元数据自动生成。</span>
        </div>
        <div class="resource-network-index">
          #{listing.empty? ? "<p>暂无资料。</p>" : listing}
        </div>
      </section>
    HTML
  )

  entities.each do |entity|
    body = <<~HTML
      <section class="resource-network-page">
        <div class="resource-network-hero">
          <p>#{label}</p>
          <h2>#{CGI.escapeHTML(entity["name"])}</h2>
          <span>#{entity["posts"].size} 篇文章 · #{entity["annotations"].size} 条评注 · #{entity["years"].join(" / ")}</span>
        </div>
        <div class="resource-network-jump">
          <a href="/entities/#{type}/">返回#{label}索引</a>
          <a href="/timeline/">时间线</a>
          <a href="/resource-graph/">关系图谱</a>
        </div>
        <section class="resource-network-section">
          <h2>相关文章</h2>
          #{card_list(entity["posts"], "暂无相关文章。")}
        </section>
        <section class="resource-network-section">
          <h2>相关评注</h2>
          #{annotation_list(entity["annotations"])}
        </section>
      </section>
    HTML

    write_page(
      File.join(GENERATED_DIR, "entities", type, "#{slug(entity["name"])}.md"),
      {
        "title" => "#{entity["name"]} - #{label}",
        "permalink" => entity["url"],
        "layout" => "single",
        "search" => false
      },
      body
    )
  end
end

timeline_listing = index["timeline"].values.sort_by { |item| item["year"] }.reverse.map do |item|
  count = item["posts"].size + item["annotations"].size
  "<a href=\"#{item["url"]}\"><strong>#{item["year"]}</strong><span>#{count} 条资料</span></a>"
end.join("\n")

write_page(
  File.join(GENERATED_DIR, "timeline.md"),
  {
    "title" => "资料时间线",
    "permalink" => "/timeline/",
    "layout" => "single",
    "search" => false
  },
  <<~HTML
    <section class="resource-network-page">
      <div class="resource-network-hero">
        <p>Timeline</p>
        <h2>资料时间线</h2>
        <span>按年份汇总文章和评注，适合追踪同一人物、作品或事件的资料变化。</span>
      </div>
      <div class="resource-network-index resource-network-index--years">
        #{timeline_listing}
      </div>
    </section>
  HTML
)

index["timeline"].values.each do |year|
  write_page(
    File.join(GENERATED_DIR, "timeline", "#{year["year"]}.md"),
    {
      "title" => "#{year["year"]} - 资料时间线",
      "permalink" => year["url"],
      "layout" => "single",
      "search" => false
    },
    <<~HTML
      <section class="resource-network-page">
        <div class="resource-network-hero">
          <p>Timeline</p>
          <h2>#{year["year"]}</h2>
          <span>#{year["posts"].size} 篇文章 · #{year["annotations"].size} 条评注</span>
        </div>
        <div class="resource-network-jump">
          <a href="/timeline/">返回时间线</a>
          <a href="/resource-graph/">关系图谱</a>
        </div>
        <section class="resource-network-section">
          <h2>文章</h2>
          #{card_list(year["posts"], "这一年暂无文章。")}
        </section>
        <section class="resource-network-section">
          <h2>评注</h2>
          #{annotation_list(year["annotations"])}
        </section>
      </section>
    HTML
  )
end

puts "Generated resource index: #{index["posts"].size} posts, #{index["annotations"].size} annotations"
puts "Generated entity pages under #{GENERATED_DIR.sub(ROOT + File::SEPARATOR, "")}"
