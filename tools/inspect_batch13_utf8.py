import urllib.request
import re
import html
import json
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

def inspect_all():
    # 1. Tajiri TIME
    url1 = "https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html"
    lines1 = fetch_url(url1)
    print("=== TAJIRI TIME ===")
    recording = False
    time_qa = []
    for l in lines1:
        if "The Ultimate Game Freak" in l:
            recording = True
        if "Click to Print" in l or "Find this article at:" in l or "Copyright ©" in l:
            recording = False
        if recording:
            time_qa.append(l)
    print(f"Tajiri extracted lines: {len(time_qa)}")
    for l in time_qa[:25]:
        print("  ", l[:100])
    print("...")
    for l in time_qa[-15:]:
        print("  ", l[:100])

    # 2. Pikachu Creators
    url2 = "https://web.archive.org/web/20180905085601/https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/"
    lines2 = fetch_url(url2)
    print("\n=== PIKACHU CREATORS ===")
    recording = False
    pika_lines = []
    for l in lines2:
        if "Creator Profile: The Creators of Pikachu" in l:
            recording = True
        if "Previous Article" in l or "Next Article" in l or "Connect With Us" in l:
            recording = False
        if recording:
            pika_lines.append(l)
    print(f"Pikachu extracted lines: {len(pika_lines)}")
    for l in pika_lines[:25]:
        print("  ", l[:100])
    print("...")
    for l in pika_lines[-15:]:
        print("  ", l[:100])

    # 3. Nintendo Power
    url3 = "https://lavacutcontent.com/masuda-interview-pokemon-platinum/"
    lines3 = fetch_url(url3)
    print("\n=== NINTENDO POWER ===")
    recording = False
    np_lines = []
    for l in lines3:
        if "Special emphasis on developing Pokemon Platinum" in l or "Nintendo Power:" in l:
            recording = True
        if "Related Posts" in l or "Leave a Reply" in l or "Share this:" in l:
            recording = False
        if recording:
            np_lines.append(l)
    print(f"Nintendo Power extracted lines: {len(np_lines)}")
    for l in np_lines[:25]:
        print("  ", l[:100])
    print("...")
    for l in np_lines[-15:]:
        print("  ", l[:100])

if __name__ == '__main__':
    inspect_all()
