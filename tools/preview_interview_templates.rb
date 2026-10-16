# Render real posts through Jekyll, plus a corpus-wide content-form probe.
# Generated files go to an ignored local preview directory, never _posts.
require 'rubygems'
# Use already installed workspace gems without changing the user's bundle.
local_gems = File.expand_path('../vendor/bundle/ruby/3.3.0', __dir__)
Gem.use_paths(Gem.dir, Gem.path + [local_gems]) if Dir.exist?(local_gems)
require 'jekyll'
require 'json'
require 'fileutils'
require 'cgi'

root = File.expand_path('..', __dir__)
dest = ARGV[0] || File.join(root, '.preview-build', 'interview-templates')
config = Jekyll.configuration('source' => root, 'destination' => dest,
  'incremental' => false, 'future' => true, 'quiet' => true)
site = Jekyll::Site.new(config)
site.reset
puts 'Reading site content...'
$stdout.flush
# Use Jekyll's real readers, but don't walk tens of thousands of static images
# just to render nine articles. The browser server serves those from the repo.
site.layouts = Jekyll::LayoutReader.new(site).read
site.reader.retrieve_posts('')
site.reader.sort_files!
site.reader.read_data
site.pages << Jekyll::Page.new(site, root, 'assets/css', 'main.scss')
puts "Loaded #{site.posts.docs.size} posts."
$stdout.flush
FileUtils.mkdir_p(dest)

examples = {
  'conversation' => '2006-04-24-interview-gpara-2006-yoshida.md',
  'roundtable' => '2000-07-01-interview-nintendopower-gold-silver-roundtable.md',
  'longform' => '1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak.md',
  'profile' => '2021-12-27-interview-gamefreak-recruit-designer-kn.md',
  'annotated' => '2009-04-01-interview-nintendo-power-masuda-gens-1-4.md',
  'narrative' => '2025-12-24-corporate-topic-46-pokemon-center-original-goods-philosophy.md',
  'technical' => '2026-07-22-interview-denfami-2026-cedec-battle.md',
  'scan' => '2006-11-01-continue-vol31-aoi-yu-pikachu.md',
  'legacy-roundtable' => '2010-11-01-interview-nintendo-joshi-daisei-bw-kiritani-masuda.md',
  'portal-roundtable' => '2002-11-01-interview-nom-2002-ruby-sapphire-staff-messages.md',
  'editorial-profile' => '2016-09-06-interview-pokemoncojp-2016-ohmori-sm.md'
}

# Probe the same include the real layout uses, without rendering 467 full pages.
probe_source = <<~LIQUID
  {% assign empty_items = "" | split: "" %}
  {% assign items = page.parallel_items | default: page.translation_segments | default: page.segments | default: empty_items %}
  {% assign reading_chars = items | map: "translation" | join: "" | size %}
  {% assign is_technical = false %}
  {% if page.source_kind == "technical_report" or page.source_kind == "lecture_report" or page.source.source_type == "technical_report" or page.source.source_type == "lecture_report" or page.article_kind == "technical_feature" %}{% assign is_technical = true %}{% endif %}
  {% assign is_scan = false %}
  {% if page.translation_segments %}{% if page.source_pages or page.scan_pages or page.archive_type == "scan_translation" %}{% assign is_scan = true %}{% endif %}{% endif %}
  {% include interview-template.html %}
  {{ interview_template }}
LIQUID
manifest = { 'routes' => [], 'examples' => {}, 'baseurl' => site.config['baseurl'],
  'expected_forms' => { 'prose-fallback' => 'narrative', 'legacy-roundtable' => 'roundtable',
    'portal-roundtable' => 'roundtable', 'editorial-profile' => 'profile' } }
site.posts.docs.select { |doc| doc.data['layout'] == 'interview-editorial' }.each do |doc|
  probe = Jekyll::PageWithoutAFile.new(site, root, '', 'probe.html')
  probe.data = doc.data.merge('layout' => nil, 'slug' => doc.data['slug'] || doc.slug)
  probe.content = probe_source
  form = Jekyll::Renderer.new(site, probe, site.site_payload).run.strip
  manifest['routes'] << { 'file' => File.basename(doc.path), 'template' => form }
end

examples.each do |form, filename|
  doc = site.posts.docs.find { |post| File.basename(post.path) == filename }
  raise "Missing preview post: #{filename}" unless doc
  output = Jekyll::Renderer.new(site, doc, site.site_payload).run
  File.write(File.join(dest, "#{form}.html"), output, encoding: 'UTF-8')
  manifest['examples'][form] = filename
  puts "Rendered #{form}: #{filename}"
end

css = site.pages.find { |page| page.relative_path == 'assets/css/main.scss' }
raise 'Missing assets/css/main.scss' unless css
FileUtils.mkdir_p(File.join(dest, 'assets', 'css'))
File.write(File.join(dest, 'assets', 'css', 'main.css'),
  Jekyll::Renderer.new(site, css, site.site_payload).run, encoding: 'UTF-8')
File.write(File.join(dest, 'manifest.json'), JSON.pretty_generate(manifest), encoding: 'UTF-8')
links = examples.keys.select { |form| site.data['interview_templates'].key?(form) }.map do |form|
  info = site.data['interview_templates'][form]
  "<li><a href=\"#{form}.html\">#{CGI.escapeHTML(info['name'])}</a><p>#{CGI.escapeHTML(info['description'])}</p></li>"
end.join
File.write(File.join(dest, 'index.html'), <<~HTML, encoding: 'UTF-8')
  <!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>访谈模板 · 实际文章预览</title><style>
  body{background:#f8f6f0;color:#292824;font:17px/1.8 'Segoe UI','Microsoft YaHei',sans-serif;margin:0;padding:32px 24px}
  main{max-width:920px;margin:auto}h1{font-size:30px;line-height:1.4;font-weight:700}a{color:#765034;text-underline-offset:5px}
  ul{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:0 40px}li{border-top:1px solid #ccc5b8;padding:20px 0}li a{font-size:20px;font-weight:600}li p{font-size:15px;color:#605c54;margin:8px 0}
  a:focus-visible{outline:2px solid #765034;outline-offset:4px}@media(max-width:640px){ul{grid-template-columns:1fr}h1{font-size:24px}}
  </style><main><p>Poke Amice Docs / Reading Forms</p><h1>同一个档案，不同的阅读节奏</h1>
  <p>8 种内容版式，配合已有的 7 套年代主题。下面均为站内真实文章；译文优先，原文与档案入口保持可用。</p><ul>#{links}</ul></main></html>
HTML
puts "Checked #{manifest['routes'].size} routes; preview: #{dest}"
