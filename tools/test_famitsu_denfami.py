import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test(url, name):
    print(f"\nTesting {name}: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    raw = urllib.request.urlopen(req, context=ctx, timeout=15).read()
    try:
        html = raw.decode('utf-8')
    except:
        html = raw.decode('shift_jis', 'replace')
    soup = BeautifulSoup(html, 'html.parser')
    print("Title:", soup.title.string if soup.title else "")
    ps = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
    print(f"Paragraphs: {len(ps)}")
    for p in ps[3:8]:
        print("  ", p[:75])

test("https://www.famitsu.com/news/201803/30154405.html", "Famitsu Detective Pikachu")
test("https://news.denfaminicogamer.jp/kikakuthetower/2607233k", "Denfami PokeRig")
