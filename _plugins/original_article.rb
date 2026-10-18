# frozen_string_literal: true

require 'cgi'
require 'set'

module PokeAmice
  module OriginalArticleFilters
    HEADING = /<(h[1-4])\b([^>]*)>(.*?)<\/\1>/mi
    ID = /(?:\A|\s)id\s*=\s*(["'])(.*?)\1/mi

    # Only known heading tags are touched; the original prose, images and links
    # stay byte-for-byte inside them. Do not interpret coloured/bold paragraphs
    # as headings: those are still the author's text.
    def original_article_markup(input)
      html = input.to_s
      used = html.scan(ID).map(&:last).to_set
      number = 0
      html = html.gsub(HEADING) do |heading|
        tag, attrs, inside = Regexp.last_match.captures
        tag = tag.downcase == 'h1' ? 'h2' : tag
        if original_article_plain(inside).empty?
          "<#{tag}#{attrs}>#{inside}</#{tag}>"
        else
          unless attrs.match?(ID)
            begin
              number += 1
              anchor = "article-section-#{number}"
            end while used.include?(anchor)
            used << anchor
            attrs += " id=\"#{anchor}\""
          end
          "<#{tag}#{attrs}>#{inside}</#{tag}>"
        end
      end
      dimensions = @context&.registers&.[](:site)&.data&.fetch('weibo_article_images', {}) || {}
      html.gsub(/<img\b[^>]*>/mi) do |image|
        src = image.match(/\bsrc\s*=\s*(["'])(.*?)\1/mi)&.captures&.last
        size = dimensions[CGI.unescapeHTML(src.to_s)]
        if size && !image.match?(/\b(?:width|height)\s*=/i)
          image.sub(/\s*\/?>\z/, " width=\"#{size['width'].to_i}\" height=\"#{size['height'].to_i}\">")
        else
          image
        end
      end
    end

    def original_article_toc(input)
      headings = input.to_s.scan(HEADING).filter_map do |tag, attrs, inside|
        id = attrs.match(ID)&.captures&.last
        text = original_article_plain(inside)
        [tag[1].to_i, id, text] if id && !text.empty?
      end
      return '' if headings.empty?

      base = headings.map(&:first).min
      rows = headings.map do |level, id, title|
        depth = [level - base, 2].min
        "<li class=\"original-toc__item depth-#{depth}\"><a href=\"##{CGI.escapeHTML(id)}\">#{CGI.escapeHTML(title)}</a></li>"
      end
      "<ol class=\"original-toc__list\">#{rows.join}</ol>"
    end

    def original_article_dek(input)
      text = original_article_plain(input)
      return '' if text.length > 90 || text.match?(/\A全文\s*\d|https?:\/\//i)

      text
    end

    def original_article_minutes(input)
      [(original_article_plain(input).length / 400.0).ceil, 1].max
    end

    private

    def original_article_plain(input)
      CGI.unescapeHTML(input.to_s.gsub(/<[^>]+>/, ' ')).gsub(/[\s\u00a0]+/, ' ').strip
    end
  end
end

Liquid::Template.register_filter(PokeAmice::OriginalArticleFilters)
