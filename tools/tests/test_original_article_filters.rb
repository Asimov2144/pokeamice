# frozen_string_literal: true

require 'minitest/autorun'
require 'liquid'
require_relative '../../_plugins/original_article'

class OriginalArticleFiltersTest < Minitest::Test
  def setup
    @filters = Object.new.extend(PokeAmice::OriginalArticleFilters)
  end

  def test_preserves_prose_links_images_and_heading_contents
    original = '<p style="color:red">原话 &amp; <a href="https://example.com/x">原链接</a></p><h1><em>正文</em></h1><img src="/real.jpg">'
    output = @filters.original_article_markup(original)
    assert_includes output, '<p style="color:red">原话 &amp; <a href="https://example.com/x">原链接</a></p>'
    assert_includes output, '<h2 id="article-section-1"><em>正文</em></h2>'
    assert_includes output, '<img src="/real.jpg">'
  end

  def test_preserves_existing_anchors_and_avoids_collisions
    output = @filters.original_article_markup('<h2 id="article-section-1">旧标题</h2><h2>新标题</h2><h3 id="中文锚点">中文</h3>')
    assert_includes output, 'id="article-section-2"'
    toc = @filters.original_article_toc(output)
    assert_includes toc, 'href="#article-section-1"'
    assert_includes toc, 'href="#中文锚点"'
  end

  def test_data_id_is_not_a_heading_anchor
    output = @filters.original_article_markup('<h2 data-id="source-123">标题</h2>')
    assert_includes output, 'id="article-section-1"'
    assert_includes @filters.original_article_toc(output), 'href="#article-section-1"'
  end

  def test_no_invented_sections_for_bold_paragraphs_or_empty_headings
    output = @filters.original_article_markup('<p><strong>原文强调</strong></p><h2> </h2>')
    assert_equal '', @filters.original_article_toc(output)
    assert_includes output, '<strong>原文强调</strong>'
  end

  def test_toc_escapes_the_title_and_excludes_embedded_markup
    output = @filters.original_article_markup('<h2>A &amp; B <em>标题</em></h2>')
    toc = @filters.original_article_toc(output)
    assert_includes toc, 'A &amp; B 标题'
    refute_includes toc, '<em>'
  end

  def test_only_uses_measured_intrinsic_image_sizes
    site = Struct.new(:data).new({ 'weibo_article_images' => { '/real.jpg' => { 'width' => 1200, 'height' => 800 } } })
    @filters.instance_variable_set(:@context, Struct.new(:registers).new({ site: site }))
    output = @filters.original_article_markup('<img src="/real.jpg" loading="lazy"/><img src="/unknown.jpg"><img src="/real.jpg" width="90">')
    assert_includes output, 'loading="lazy" width="1200" height="800"'
    assert_includes output, '<img src="/unknown.jpg">'
    assert_includes output, '<img src="/real.jpg" width="90">'
  end

  def test_rejects_incomplete_deks_without_rewriting_metadata
    assert_equal '', @filters.original_article_dek('全文6346')
    assert_equal '', @filters.original_article_dek('原文:https://example.com')
    assert_equal '', @filters.original_article_dek('很长的摘要' * 25)
    assert_equal '原来的短导语。', @filters.original_article_dek('原来的短导语。')
  end
end
