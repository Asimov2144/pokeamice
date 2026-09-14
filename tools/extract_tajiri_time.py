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

url1 = "https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html"
req = urllib.request.Request(url1, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
parser = TextExtractor()
parser.feed(content)
lines = parser.get_lines()

# Extract from "Monday, Nov" down to before copyright/footer
start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if "Monday, Nov" in l or "The Ultimate Game Freak" in l:
        if start_idx == -1: start_idx = i
    if "Click to Print" in l or "Find this article at:" in l or "Back to Top" in l:
        if end_idx == -1 and i > 50: end_idx = i

article_lines = lines[start_idx:end_idx]
print(f"Article lines count: {len(article_lines)}")
for idx, l in enumerate(article_lines):
    print(f"[{idx}] {l}")
