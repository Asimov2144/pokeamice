import urllib.request
import re
import html
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.in_script = True
        elif tag in ['p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr']:
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.in_script = False
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'tr']:
            self.text.append('\n')

    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            self.text.append(data)

    def get_clean_text(self):
        full = ''.join(self.text)
        lines = [line.strip() for line in full.split('\n') if line.strip()]
        return lines

def inspect_url(name, url):
    print(f"=== {name} ===")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html_content = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        parser = TextExtractor()
        parser.feed(html_content)
        lines = parser.get_clean_text()
        print(f"Total extracted lines: {len(lines)}")
        print("--- Sample snippet (first 30 lines) ---")
        for l in lines[:30]:
            print("  ", l[:120])
        print("--- Finding Q&A or key markers ---")
        for i, l in enumerate(lines):
            if any(k in l for k in ['TIME:', 'Tajiri:', 'Masuda:', 'Sugimori:', 'Nishida:', 'Nishino:', 'Q:', 'A:']):
                print(f"  Line {i}: {l[:100]}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    inspect_url("TAJIRI TIME", "https://web.archive.org/web/20090212001550/http://www.time.com/time/magazine/article/0,9171,2040095,00.html")
    inspect_url("PIKACHU CREATORS", "https://web.archive.org/web/20180905085601/https://www.pokemon.com/us/pokemon-news/creator-profile-the-creators-of-pikachu/")
    inspect_url("NINTENDO POWER LAVA CUT", "https://lavacutcontent.com/masuda-interview-pokemon-platinum/")
