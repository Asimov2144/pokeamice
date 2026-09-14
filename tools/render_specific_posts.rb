require 'jekyll'
require 'fileutils'

root = 'p:/WEBSITE/pokeamice-main (1)/pokeamice-main'
Dir.chdir(root)

puts "Initializing Jekyll site..."
config = Jekyll.configuration({
  "source" => root,
  "destination" => File.join(root, "_site"),
  "incremental" => false,
  "skip_initial_build" => true
})

site = Jekyll::Site.new(config)
site.reset
site.read

target_slugs = [
  'interview-gameinformer-masuda-past-present-future',
  'interview-gameinformer-masuda-afterwords-xy',
  'interview-yomiuri-siliconera-sugimori-monster-balance',
  'interview-famitsu-usum-ohmori-iwao-director',
  'interview-famitsu-usum-iwao-suginaka-story-secrets',
  'interview-cgworld-sun-moon-3d-pipeline-creatures-gamefreak',
  'interview-iwata-asks-hgss-chapter-1-red-green-mew',
  'interview-iwata-asks-hgss-chapter-2-portable-toy-king',
  'interview-iwata-asks-hgss-chapter-3-iwata-compression-stadium',
  'interview-iwata-asks-hgss-chapter-4-pokewalker-493-following',
  'interview-iwata-asks-bw-chapter-1-second-game-on-ds',
  'interview-iwata-asks-bw-chapter-2-brand-new-world',
  'interview-iwata-asks-bw-chapter-3-expanding-play-communication',
  'interview-iwata-asks-bw-chapter-4-unchanging-pokemon-essence',
  'interview-iwata-asks-bw-chapter-5-new-world-new-encounters',
  'interview-iwata-asks-b2w2-chapter-1-two-sequels-two-years-later',
  'interview-iwata-asks-b2w2-chapter-2-100-player-co-op',
  'interview-iwata-asks-b2w2-chapter-3-pokestar-studios-space-fantasy',
  'interview-iwata-asks-b2w2-chapter-4-staying-on-ds-three-sacred-treasures',
  'interview-nom-gamefreak-roundtable-vol1-red-green',
  'interview-nom-gamefreak-roundtable-vol2-gold-silver-secrets',
  'interview-nom-special-dialogue-tajiri-ishihara',
  'interview-nom-ruby-sapphire-director-masuda',
  'interview-nom-ruby-sapphire-art-director-sugimori',
  'interview-nom-ruby-sapphire-multi-battle-secret-base',
  'interview-iwata-asks-xy-chapter-1-global-simultaneous-release',
  'interview-iwata-asks-xy-chapter-2-reborn-pokemon-3d-amie',
  'interview-iwata-asks-xy-chapter-3-new-battles-fairy-type',
  'interview-iwata-asks-xy-chapter-4-closer-bonds-mega-evolution',
  'interview-gameinformer-masuda-morimoto-hgss',
  'interview-famitsu-b2w2-fanmeeting-masuda-unno',
  'interview-famitsu-xy-music-fanmeeting-masuda-kageyama',
  'interview-denfaminicogamer-ohmori-onoue-gear-project',
  'interview-denfaminicogamer-pokemon-go-server-miracle',
  'interview-famitsu-new-pokemon-snap-ishihara-suzaki',
  'interview-time-satoshi-tajiri-ultimate-game-freak',
  'interview-nintendo-power-masuda-kawachimaru-platinum-gens',
  'interview-creators-of-pikachu',
  'interview-eurogamer-masuda-ohmori-sword-shield-dex-sirfetchd',
  'interview-game-informer-how-game-freak-designs-pokemon-creatures',
  'interview-cedec-2022-legends-arceus-scarlet-violet-pipeline',
  'interview-game-informer-why-ruby-sapphire-most-challenging',
  'interview-eurogamer-masuda-sugimori-black-white-brains',
  'interview-cedec-2023-paldea-rendering-pipeline-maeza',
  'interview-cedec-2023-sound-design-ichinose-paldea',
  'interview-game-informer-creators-on-pokemon-anime',
  'interview-eurogamer-masuda-lets-go-difficulty-meltan-future',
  'interview-4gamer-sword-shield-ohmori-masuda-strongest',
  'interview-game-informer-game-freak-origins-pre-pokemon',
  'interview-guardian-pokemon-chief-utsunomiya-hundreds-of-years',
  'interview-ign-e3-2004-pokemon-creators-speak',
  'interview-famitsu-usum-fanmeeting-masuda-battle-music',
  'interview-famitsu-pokemon-sleep-1st-anniversary-utsunomiya-nakahata',
  'interview-famitsu-e3-2019-pokemon-sword-shield-masuda-ohmori',
  'interview-4gamer-xy-music-fanmeeting-masuda-kageyama',
  'interview-dengeki-b2w2-masuda-unno-n-ghetsis-art',
  'interview-dengeki-xy-masuda-kageyama-setting-art',
  'interview-vgc-gamefreak-gear-project',
  'interview-creatures-history-special-ishihara-tanaka',
  'interview-2083-gamefreak-sound-team-red-green-to-oras',
  'interview-gnn-pokemon-go-tokyo-roundtable',
  'interview-gamefreak-official-red-green-staff',
  'interview-cgworld-creatures-cg-studio',
  'interview-denfami-xevious-tajiri-sugimori-endo',
  'interview-pokemon-com-usum-ohmori-iwao',
  'interview-famitsu-sword-shield-masuda-ohmori',
  'interview-corocoro-coco-okazaki-taiiku',
]


puts "Finding target posts..."
docs = site.posts.docs.select do |doc|
  target_slugs.any? { |slug| doc.basename.include?(slug) }
end

puts "Found #{docs.size} matching posts."

# Load layouts and includes
site.layouts.each { |k, v| }

docs.each do |doc|
  puts "Rendering #{doc.relative_path}..."
  doc.output = Jekyll::Renderer.new(site, doc, site.site_payload).run
  out_path = doc.destination(site.dest)
  FileUtils.mkdir_p(File.dirname(out_path))
  File.write(out_path, doc.output, encoding: 'utf-8')
  puts "  -> Written to #{out_path} (#{File.size(out_path)} bytes)"
end

puts "Done!"
