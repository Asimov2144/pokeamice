# Real Jekyll preview, reading current posts without walking the static archive.
require 'rubygems'
local_gems = File.expand_path('../vendor/bundle/ruby/3.3.0', __dir__)
Gem.use_paths(Gem.dir, Gem.path + [local_gems]) if Dir.exist?(local_gems)
require 'jekyll'
require 'json'
require 'fileutils'
require 'uri'

root = File.expand_path('..', __dir__)
dest = File.join(root, '.preview-build', 'timeline')
config = Jekyll.configuration('source' => root, 'destination' => dest,
  'incremental' => false, 'future' => true, 'quiet' => true)
site = Jekyll::Site.new(config)
site.reset
site.layouts = Jekyll::LayoutReader.new(site).read
if ARGV.include?('--css-only')
  site.reader.read_data
  css = Jekyll::Page.new(site, root, 'assets/css', 'main.scss')
  site.pages << css
  FileUtils.mkdir_p(File.join(dest, 'assets/css'))
  File.write(File.join(dest, 'assets/css/main.css'), Jekyll::Renderer.new(site, css, site.site_payload).run, encoding: 'UTF-8')
  puts 'Updated timeline preview styles.'
  exit
end
site.reader.retrieve_posts('')
site.reader.sort_files!
site.reader.read_data
site.pages << Jekyll::Page.new(site, root, '_pages', 'timeline.md')
Dir.glob(File.join(root, '_pages/generated/timeline/*.md')).each do |file|
  site.pages << Jekyll::Page.new(site, root, '_pages/generated/timeline', File.basename(file))
end
site.pages << Jekyll::Page.new(site, root, 'assets/css', 'main.scss')
FileUtils.mkdir_p(dest)

def kind(post)
  archive = post.data['archive_type'].to_s
  return 'stream' if %w[gamefreak_director_column gamefreak_masuda_lineblog gamefreak_legacy_blog].include?(archive)
  return 'scan' if archive == 'scan_translation'
  return 'topic' if Array(post.data['categories']).include?('专题报道')
  return 'interview' if %w[interview-editorial parallel-translation].include?(post.data['layout']) || archive.include?('interview') || archive == 'media_feature'
  'article'
end
posts = site.posts.docs.select { |p| kind(p) == 'stream' || p.data['search'] != false }
manifest = { 'baseurl' => site.config['baseurl'], 'years' => {}, 'routes' => [], 'posts' => [] }
posts.each do |post|
  year = post.date.year.to_s
  manifest['years'][year] ||= { 'docs' => 0, 'stream' => 0 }
  manifest['years'][year][kind(post) == 'stream' ? 'stream' : 'docs'] += 1
  manifest['posts'] << { 'year' => post.date.year, 'date' => post.date.strftime('%Y-%m-%d'), 'url' => post.url, 'kind' => kind(post) }
end
site.pages.each do |page|
  next unless page.data['layout'] == 'timeline' || page.relative_path == 'assets/css/main.scss'
  output = Jekyll::Renderer.new(site, page, site.site_payload).run
  target = File.join(dest, page.url.sub(%r{^/}, ''))
  target = File.join(target, 'index.html') if page.url.end_with?('/')
  FileUtils.mkdir_p(File.dirname(target))
  File.write(target, output, encoding: 'UTF-8')
  manifest['routes'] << page.url if page.data['layout'] == 'timeline'
  puts "Rendered #{page.url}"
  $stdout.flush
end
# The featured interview is also navigable in this local preview. This renders
# an existing reader; it does not change the post or the interview template.
featured = site.posts.docs.find { |post| post.slug == 'interview-time-satoshi-tajiri-ultimate-game-freak' }
if featured
  target = File.join(dest, URI::DEFAULT_PARSER.unescape(featured.url).force_encoding('UTF-8').sub(%r{^/}, ''), 'index.html')
  FileUtils.mkdir_p(File.dirname(target))
  File.write(target, Jekyll::Renderer.new(site, featured, site.site_payload).run, encoding: 'UTF-8')
  manifest['preview_article'] = featured.url
end
File.write(File.join(dest, 'manifest.json'), JSON.pretty_generate(manifest), encoding: 'UTF-8')
puts "#{posts.size} build-visible records; #{manifest['routes'].size} timeline routes."
