import urllib.request
import re
import html
import sys

sys.stdout.reconfigure(encoding="utf-8")

url = "https://note.com/anacon11/n/nf81add1aa7a1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
}
req = urllib.request.Request(url, headers=headers)
try:
    content = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
    print(f"Content length: {len(content)}")
    
    # Extract all links and anchor texts
    links = re.findall(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', content, re.DOTALL)
    print(f"Found {len(links)} links in note:")
    
    # Filter external links relevant to pokemon interviews
    interview_links = []
    for href, text in links:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if any(domain in href for domain in ['famitsu.com', '4gamer.net', 'denfaminicogamer.jp', 'nintendo.co.jp', 'gamefreak.co.jp', 'cgworld.jp', 'web.archive.org', 'inside-games.jp', 'gamer.ne.jp', 'impress.co.jp', 'ign.com', 'gameinformer.com', 'polygon.com', 'youtube.com']):
            interview_links.append((clean_text, href))
            
    print(f"Relevant interview links: {len(interview_links)}")
    for idx, (t, h) in enumerate(interview_links[:50]):
        print(f"[{idx+1}] {t} -> {h}")
except Exception as e:
    print("Err:", e)
