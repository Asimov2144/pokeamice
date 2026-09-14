import urllib.request
import re
import html
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

url = "https://note.com/anacon11/n/nf81add1aa7a1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
}

raw_html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20).read().decode("utf-8", errors="ignore")

# Find sections and links in note
# note.com uses <p>, <h3>, <h4>, <figure class="embedded-content"> or <a>
entries = []

# Regex find all <a> tags with text and href
matches = re.findall(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', raw_html, re.DOTALL)

seen_urls = set()
for href, text in matches:
    clean_text = re.sub(r'<[^>]+>', ' ', text).strip()
    clean_text = re.sub(r'\s+', ' ', clean_text)
    if not clean_text or clean_text.startswith('http') or len(clean_text) < 3:
        continue
    # Filter out navigation / user links
    if any(k in href for k in ['note.com/anacon11', 'note.com/login', 'note.com/intent', 'twitter.com/intent', 'help.note.com']):
        continue
    if href in seen_urls:
        continue
    seen_urls.add(href)
    entries.append({
        "title": clean_text,
        "url": href
    })

print(f"Total clean entries extracted: {len(entries)}")
for i, e in enumerate(entries[:60]):
    print(f"[{i+1}] {e['title'][:50]} | {e['url']}")
