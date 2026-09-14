import urllib.request
import ssl
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://www.2083.jp/contents/201410gamefreak/", headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')
links = [(a.get_text(strip=True), a.get('href')) for a in soup.find_all('a') if a.get('href') and '201410gamefreak' in a.get('href') or (a.get('href') and a.get('href').endswith('.html'))]
print("2083 links:", links)

# Now check Famitsu Sun/Moon
req = urllib.request.Request("https://www.famitsu.com/news/201611/18120892.html", headers={'User-Agent': 'Mozilla/5.0'})
html2 = urllib.request.urlopen(req, context=ctx).read()
soup2 = BeautifulSoup(html2, 'html.parser')
print("Famitsu title:", soup2.title.string if soup2.title else "")
body = soup2.find('div', class_='article-body') or soup2.find('div', id='news-article-body') or soup2.find('div', class_='mainContents') or soup2.find('div', class_='entry-content')
print("Famitsu body found:", bool(body))
if not body:
    # let's inspect all div classes with 'article' or 'body' or 'content'
    divs = [d.get('class') for d in soup2.find_all('div') if d.get('class')]
    print("Some div classes:", divs[:10])
