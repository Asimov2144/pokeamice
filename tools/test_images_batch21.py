import urllib.request
import ssl
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check_images(name, url, encoding='utf-8'):
    print(f"\n--- Images for {name} ---")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, context=ctx).read()
    try:
        html = raw.decode(encoding)
    except:
        html = raw.decode('shift_jis', 'replace')
    soup = BeautifulSoup(html, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        full_url = urljoin(url, src)
        if any(skip in full_url for skip in ['logo', 'icon', 'banner', 'btn', 'common', 'twitter', 'facebook', 'rss', 'ranking', 'google']):
            continue
        print(" ", full_url, "alt:", img.get('alt'))

check_images("Dengeki HGSS", "https://dengekionline.com/elem/000/000/193/193021/")
check_images("Famitsu Detective Pikachu", "https://www.famitsu.com/news/201803/30154405.html")
check_images("2083 Page 1", "http://www.2083.jp/contents/201410gamefreak/page_01.html", encoding='shift_jis')
