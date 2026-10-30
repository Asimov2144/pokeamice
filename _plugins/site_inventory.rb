# frozen_string_literal: true

# The site inventory (tools/site_inventory.py -> _data/site_inventory.json): every number the home page,
# /keys/, the English layer and the sitemap print is counted there once, with its definition (口径).
# This only hands each post its row - post.inv_kind, inv_type_label, inv_scan_type, inv_listed,
# inv_indexed, inv_source_lang - so templates filter by it instead of re-deriving the type, and records
# which posts the inventory did not know; tools/site_inventory.py check fails the deploy on those.
module PokeAmice
  class SiteInventoryGenerator < Jekyll::Generator
    priority :highest

    def generate(site)
      inventory = site.data['site_inventory']
      raise 'Missing _data/site_inventory.json: run python tools/site_inventory.py build' unless inventory

      rows = inventory['posts'] || {}
      missing = []
      site.posts.docs.each do |post|
        row = rows[post.relative_path]
        next missing << post.relative_path unless row

        row.each { |key, value| post.data["inv_#{key}"] = value }
      end
      inventory['coverage'] = { 'posts_seen' => site.posts.docs.size, 'missing' => missing.sort,
                                'stale' => (rows.keys - site.posts.docs.map(&:relative_path)).sort }
      inventory['ja_seen'] = site.collections['ja']&.docs&.size || 0
    end
  end
end
