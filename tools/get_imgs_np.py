import urllib.request
import re

url = 'https://lavacutcontent.com/masuda-interview-pokemon-platinum/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html)
for img in imgs:
    if 'wp-content/uploads' in img:
        print(img)
