import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://dengekionline.com/elem/000/000/193/193021/", headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, context=ctx).read()

# try utf-8 then shift_jis
try:
    html = raw.decode('utf-8')
except:
    html = raw.decode('shift_jis', 'replace')

soup = BeautifulSoup(html, 'html.parser')
title = soup.title.string if soup.title else ""
print(f"Title: {title}")

# Check article body
article = soup.find('div', id='article-body') or soup.find('div', class_='main-article') or soup.find('article') or soup.find('div', class_='elem-body')
if not article:
    # let's find the container with text
    article = soup.find('div', class_=lambda c: c and 'text' in c) or soup

ps = article.find_all('p')
print(f"Total p tags: {len(ps)}")
for idx, p in enumerate(ps[:12]):
    print(f"[{idx}] {p.get_text(strip=True)[:80]}")
