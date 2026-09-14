import urllib.request
import ssl
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def inspect_url(name, url):
    print(f"\n==========================================")
    print(f"Inspecting {name}: {url}")
    print(f"==========================================")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else ""
        print(f"Page Title: {title}")
        
        # Images
        imgs = [img.get('src') for img in soup.find_all('img') if img.get('src')]
        print(f"Total img tags found: {len(imgs)}")
        for img in imgs[:5]:
            print(f"  img: {img}")
            
        # Text paragraphs or headings
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        print(f"Headings ({len(headings)}): {headings[:6]}")
        
        p_tags = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        print(f"Paragraphs count: {len(p_tags)}")
        for p in p_tags[:4]:
            print(f"  p sample: {p[:80]}...")
    except Exception as e:
        print(f"Error: {e}")

inspect_url("HGSS森本", "https://dengekionline.com/elem/000/000/193/193021/")
inspect_url("音乐传承2083", "https://www.2083.jp/contents/201410gamefreak/")
inspect_url("宇都宫构想日本", "http://www.kosonippon.org/news/2020/taidan0901/")
