import urllib.request
import ssl
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "http://www.2083.jp/contents/201410gamefreak/"
pages = ["page_01.html", "page_02.html", "page_03.html", "page_04.html"]

for p in pages:
    url = base + p
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, context=ctx, timeout=10).read()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else ""
        print(f"=== {p}: {title} ({len(html)} bytes) ===")
        # Look for the interview body container
        container = soup.find('div', id='contents') or soup.find('div', class_='main') or soup.find('div', id='main')
        # Check speakers or dialogue
        ps = soup.find_all(['p', 'h3', 'h4'])
        print(f"  Total tags: {len(ps)}")
        samples = [x.get_text(strip=True) for x in ps if x.get_text(strip=True)][:5]
        for s in samples:
            print(f"    {s[:70]}")
    except Exception as e:
        print(f"Failed {p}: {e}")
