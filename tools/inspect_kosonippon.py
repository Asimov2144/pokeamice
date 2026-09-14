import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("http://www.kosonippon.org/news/2020/taidan0901/", headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, context=ctx).read()
html = raw.decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')
title = soup.title.string if soup.title else ""
print(f"Title: {title}")

# Find article or content
content = soup.find('div', class_='entry-content') or soup.find('div', class_='post-content') or soup.find('article') or soup
ps = content.find_all('p')
print(f"Total p tags: {len(ps)}")
for idx, p in enumerate(ps[:15]):
    t = p.get_text(strip=True)
    if t:
        print(f"[{idx}] {t[:80]}")
