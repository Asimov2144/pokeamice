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

url = 'https://lavacutcontent.com/masuda-interview-pokemon-platinum/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
req = urllib.request.Request(url, headers=headers)
content = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
parser = TextExtractor()
parser.feed(content)
lines = parser.get_lines()

print(f"Total lines: {len(lines)}")
start = False
article = []
for i, l in enumerate(lines):
    if "Special emphasis on developing Pokemon Platinum" in l or "Nintendo Power magazine" in l:
        start = True
    if "Related Posts" in l or "Leave a Reply" in l:
        start = False
    if start:
        article.append(l)

print(f"Extracted article lines: {len(article)}")
for idx, l in enumerate(article):
    print(f"[{idx}] {l}")
