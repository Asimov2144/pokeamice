import urllib.request
import re
import html
import json
from pathlib import Path

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def inspect_famitsu(url):
    print(f"\n==========================================")
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    html_raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    
    # Check images
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_raw, re.I)
    print(f"Total img tags: {len(imgs)}")
    for img in imgs:
        if "images" in img or "item" in img or "uploads" in img:
            print("  IMG:", img)
            
    # Check paragraphs and structure
    clean = re.sub(r'<script.*?</script>', '', html_raw, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Match article body
    m_body = re.search(r'<div class="article-body[^"]*">(.*?)<div class="article-footer', clean, re.DOTALL)
    if not m_body:
        m_body = re.search(r'<article[^>]*>(.*?)</article>', clean, re.DOTALL)
    body = m_body.group(1) if m_body else clean
    
    # Extract h2/h3 and p
    elements = re.findall(r'<(h[2-4]|p|div class="image-wrapper")[^>]*>(.*?)</\1>', body, re.DOTALL)
    print(f"Total body elements: {len(elements)}")
    for tag, content in elements[:15]:
        text = html.unescape(re.sub(r'<[^>]+>', '', content)).strip()
        if text:
            print(f"  <{tag}>: {text[:80]}...")

def inspect_cgworld(url):
    print(f"\n==========================================")
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    html_raw = urllib.request.urlopen(req).read().decode('utf-8', errors='replace')
    
    clean = re.sub(r'<script.*?</script>', '', html_raw, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', clean, re.I)
    print(f"Total img tags in CGWORLD: {len(imgs)}")
    for img in imgs[:15]:
        print("  CGWORLD IMG:", img)
        
    m_main = re.search(r'<div class="main-content">(.*?)<div class="footer', clean, re.DOTALL)
    if not m_main:
        m_main = re.search(r'<article[^>]*>(.*?)</article>', clean, re.DOTALL)
    body = m_main.group(1) if m_main else clean
    
    headings = re.findall(r'<(h[2-4])[^>]*>(.*?)</\1>', body, re.DOTALL)
    print(f"CGWORLD Headings: {len(headings)}")
    for tag, h in headings:
        t = html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
        print(f"  <{tag}>: {t}")

if __name__ == "__main__":
    inspect_famitsu("https://www.famitsu.com/news/201710/19143850.html")
    inspect_famitsu("https://www.famitsu.com/news/201801/02148529.html")
    inspect_cgworld("https://cgworld.jp/feature/201707-cgw227GG-pokemon.html")
