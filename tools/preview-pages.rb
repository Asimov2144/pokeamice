# Render only the pages you are working on, with the real site behind them.
#
# A full build of this site takes 3–4 minutes on GitHub Actions but around 15 on this Windows
# machine (Ruby's file-system calls are slow here, and every page pulls in dozens of includes).
# Changing one post or one layout should not cost that. This reads everything a full build reads -
# every post and collection document, _data, layouts, includes and plugins - and then renders only
# the pages named on the command line, the way a full build would render them. Other pages are not
# read (they and the plugins' generators are most of a full read): the crumbs' parent page or a list
# of pages can come out shorter than on the site. --full reads and generates everything (~3 min).
#
#   ruby tools/preview-pages.rb _posts/2026-10-12-interview-….md _pages/timeline.md
#   ruby tools/preview-pages.rb --css _layouts/…            # also recompile assets/css/main.css
#   ruby tools/preview-pages.rb /timeline/2010/ /games/     # by URL works too
#   ruby tools/preview-pages.rb --layout interview-editorial --limit 3   # a few pages that use a layout
#   ruby tools/preview-pages.rb --into <a built _site> …    # refresh pages inside an existing full build
#   ruby tools/preview-pages.rb --full …                     # every page read and generated first (crumbs exact)
#   python tools/preview-serve.py                           # serve the result on :4759
#
# Output goes to .preview-build/pages/ (git-ignored). preview-serve.py serves it and falls back to the
# source tree for everything that was not rendered - assets, images, scripts are copied verbatim by a
# full build anyway - so a rendered page looks as it will on the site. Pages that were not named are
# not there (links to them 404 in the preview); files that Liquid builds (feeds, search JSON) are
# not rendered unless named.
#
# Ruby: the same as a full build here - vendor/bundle (or GEM_PATH) and C:/Ruby33-x64, with RUBYOPT,
# GEM_HOME and BUNDLE_GEMFILE unset (see tools/README or the build notes).
require 'rubygems'
root = File.expand_path('..', __dir__)
local_gems = File.join(root, 'vendor/bundle/ruby/3.3.0')
Gem.use_paths(Gem.dir, Gem.path + [local_gems]) if Dir.exist?(local_gems)
require 'jekyll'
require 'fileutils'
require 'uri'

args = ARGV.dup
take = ->(flag) { (i = args.index(flag)) ? args.delete_at(i + 1).tap { args.delete_at(i) } : nil }
dest = File.expand_path(take.call('--into') || File.join(root, '.preview-build', 'pages'))
layout = take.call('--layout')
limit = (take.call('--limit') || '3').to_i
want_css = !args.delete('--css').nil?
full = !args.delete('--full').nil?
abort "usage: ruby tools/preview-pages.rb [--css] [--full] [--into DIR] [--layout NAME [--limit N]] <file or URL>…" if args.empty? && !layout && !want_css

t0 = Time.now
config = Jekyll.configuration('source' => root, 'destination' => dest, 'incremental' => false, 'quiet' => true)
site = Jekyll::Site.new(config)
site.reset
norm = ->(p) { p.to_s.tr('\\', '/').sub(%r{\A\./}, '') }
if full
  #  everything a full build reads, and the plugins' generators: every page exists (crumbs, lists of pages)
  site.read
  site.generate
else
  #  what a page needs to render: layouts, _data, every post and collection document. Other pages are
  #  not read (that and the generators are most of the time), so lookups of other pages - the crumbs'
  #  parent page, a list of pages - come out shorter than on the site; --full when that matters.
  site.layouts = Jekyll::LayoutReader.new(site).read
  site.reader.read_data
  site.reader.retrieve_posts('')
  site.collections.each { |label, c| c.read unless label == 'posts' }
  site.reader.sort_files!
end
docs = site.pages + site.documents
by_permalink = lambda do |url|
  #  a page not read yet: find the file whose front matter gives this URL
  Dir.glob(File.join(root, '{_pages/**/*,*}.{md,html}')).each do |f|
    head = File.read(f, 4096, encoding: 'UTF-8') rescue next
    next unless head.start_with?('---') && head =~ /^permalink:\s*["']?([^"'\s]+)/
    return f if Regexp.last_match(1) == url
  end
  nil
end
page_for = lambda do |file|
  rel = norm.call(file.sub(root + '/', ''))
  docs.find { |d| norm.call(d.relative_path) == rel } || begin
    page = Jekyll::Page.new(site, root, File.dirname(rel), File.basename(rel))
    site.pages << page
    docs << page
    page
  end
end
puts format('read %d posts and documents%s in %.0f s', site.documents.size, full ? " and #{site.pages.size} pages" : '', Time.now - t0)

targets = []
args.each do |arg|
  hit = nil
  #  Git Bash rewrites a leading-slash argument into its install dir (/games/ → C:/Program Files/Git/games/)
  arg = Regexp.last_match(1) if arg =~ %r{\A[A-Za-z]:/(?:[^/]+/)*Git(/.*)\z} && !File.exist?(arg)
  if arg.start_with?('/')
    plain = URI::DEFAULT_PARSER.unescape(arg)
    hit = docs.find { |d| URI::DEFAULT_PARSER.unescape(d.url) == plain }
    if !hit && (file = by_permalink.call(plain))
      hit = page_for.call(file)
    end
  else
    file = File.expand_path(arg, Dir.pwd)
    file = File.expand_path(arg, root) unless File.exist?(file)
    hit = page_for.call(file) if File.exist?(file)
  end
  hit ? targets << hit : warn("not found: #{arg}")
end
if layout
  targets.concat(docs.select { |d| d.data['layout'] == layout }.first(limit))
end
if want_css
  targets << page_for.call(File.join(root, 'assets/css/main.scss'))
end
abort 'nothing to render' if targets.empty?

payload = site.site_payload
FileUtils.mkdir_p(dest)
targets.uniq.each do |doc|
  t = Time.now
  doc.output = Jekyll::Renderer.new(site, doc, payload).run
  doc.trigger_hooks(:post_render)
  doc.write(dest)
  puts format('  %-60s %.1f s', URI::DEFAULT_PARSER.unescape(doc.url), Time.now - t)
end
puts format('%d rendered into %s in %.0f s', targets.uniq.size, dest, Time.now - t0)
