import urllib.request
import re
import html
import sys
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding='utf-8')

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chunks = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.in_script = True
        elif tag in ['p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'blockquote']:
            self.chunks.append('\n')

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.in_script = False
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'blockquote']:
            self.chunks.append('\n')

    def handle_data(self, data):
        if not self.in_script:
            self.chunks.append(data)

    def get_lines(self):
        raw = ''.join(self.chunks)
        raw = html.unescape(raw)
        lines = [line.strip() for line in raw.split('\n') if line.strip()]
        return lines

def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    content = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
    parser = TextExtractor()
    parser.feed(content)
    return parser.get_lines()

# 1. Tajiri
lines1 = fetch_url("https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html")
print("=== TAJIRI TIME ALL LINES ===")
for i, l in enumerate(lines1):
    if any(k in l for k in ["Monday, Nov", "Tajiri:", "TIME:", "The Ultimate Game Freak"]):
        print(f"[{i}] {l[:100]}")

# 2. Pikachu
lines2 = fetch_url("https://web.archive.org/web/20180905085601/https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/")
print("\n=== PIKACHU ALL LINES ===")
for i, l in enumerate(lines2):
    if any(k in l for k in ["Creator Profile", "Sugimori:", "Nishida:", "Nishino:"]):
        print(f"[{i}] {l[:100]}")

# 3. Nintendo Power
lines3 = fetch_url("https://lavacutcontent.com/masuda-interview-pokemon-platinum/")
print("\n=== NINTENDO POWER ALL LINES ===")
for i, l in enumerate(lines3):
    if any(k in l for k in ["Nintendo Power", "Masuda", "Platinum", "Torn World", "Giratina"]):
        print(f"[{i}] {l[:100]}")
