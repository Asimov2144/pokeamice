import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

html = urllib.request.urlopen('http://www.2083.jp/contents/201410gamefreak/page_01.html', context=ctx).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

# Look at body
body = soup.find('body')
for child in body.descendants:
    if child.name in ['div', 'table', 'section'] and any(k in child.get_text() for k in ['増田', '一之瀬']):
        c_cls = child.get('class')
        c_id = child.get('id')
        print(f"Matched tag <{child.name}> id={c_id} class={c_cls} len={len(child.get_text(strip=True))}")
        break

# Print the text in chunks
text = soup.get_text()
lines = [l.strip() for l in text.split('\n') if l.strip()]
print(f"Total lines of text: {len(lines)}")
for l in lines[15:35]:
    print("  ", l)
