import urllib.request
import ssl
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "http://www.2083.jp/contents/201410gamefreak/page_01.html"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, context=ctx).read()
html = raw.decode('shift_jis', 'replace')
soup = BeautifulSoup(html, 'html.parser')

# Look at table or div structure
main_table = soup.find('table', width='720') or soup.find('table')
if main_table:
    rows = main_table.find_all('tr')
    print(f"Table rows: {len(rows)}")
    for r_idx, r in enumerate(rows):
        tds = r.find_all('td')
        txts = [td.get_text(strip=True) for td in tds if td.get_text(strip=True)]
        if txts:
            print(f"Row {r_idx} ({len(tds)} tds): {txts[0][:60]}...")
else:
    print("No table found")
