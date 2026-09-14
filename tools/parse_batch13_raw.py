import urllib.request
import re
import html
import json
from html.parser import HTMLParser

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

def test_tajiri():
    url = "https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html"
    lines = fetch_url(url)
    print(f"Tajiri TIME total lines: {len(lines)}")
    qa_list = []
    current_q = None
    current_speaker = None
    current_speaker_text = []

    # Find the start of interview
    start_idx = 0
    for i, l in enumerate(lines):
        if "The Ultimate Game Freak" in l:
            start_idx = i
            break

    sub_lines = lines[start_idx:]
    print("Start index:", start_idx)
    for l in sub_lines[:40]:
        print("  ", l[:90])

def test_pikachu():
    url = "https://web.archive.org/web/20180905085601/https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/"
    lines = fetch_url(url)
    print(f"Pikachu creators total lines: {len(lines)}")
    start_idx = 0
    for i, l in enumerate(lines):
        if "Creator Profile: The Creators of Pikachu" in l:
            start_idx = i
            break
    print("Start index:", start_idx)
    for l in lines[start_idx:start_idx+45]:
        print("  ", l[:90])

def test_nintendo_power():
    url = "https://lavacutcontent.com/masuda-interview-pokemon-platinum/"
    lines = fetch_url(url)
    print(f"Nintendo Power total lines: {len(lines)}")
    start_idx = 0
    for i, l in enumerate(lines):
        if "Special emphasis on developing Pokemon Platinum" in l or "Nintendo Power:" in l:
            start_idx = i
            break
    print("Start index:", start_idx)
    for l in lines[start_idx:start_idx+45]:
        print("  ", l[:90])

if __name__ == '__main__':
    test_tajiri()
    print("="*60)
    test_pikachu()
    print("="*60)
    test_nintendo_power()
