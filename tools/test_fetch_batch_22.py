#!/usr/bin/env python3
import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def test_url(name, url):
    print(f"\n--- Testing {name} ---")
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req, context=ctx, timeout=25).read()
    soup = BeautifulSoup(raw, "html.parser")
    print("Title:", soup.title.string.strip() if soup.title else "")
    
    # Try finding article content
    article = (
        soup.find("div", class_="article-body")
        or soup.find("div", class_="entry-content")
        or soup.find("article")
        or soup.find("div", id="main-content")
        or soup.find("div", class_="main-text")
    )
    if article:
        print("Found article container:", article.name, article.get("class", article.get("id")))
        ps = article.find_all(["p", "h2", "h3"])
        print(f"Total p/h2/h3: {len(ps)}")
        imgs = article.find_all("img")
        print(f"Total images in article: {len(imgs)}")
        for idx, it in enumerate(ps[:5]):
            print(f"  [{it.name}] {it.get_text(strip=True)[:60]}")
    else:
        print("No standard article container found, inspecting body:")
        ps = soup.find_all(["p", "h2", "h3"])
        print(f"Total p/h2/h3: {len(ps)}")

test_url("CEDEC 2022 SV", "https://www.famitsu.com/news/202208/27273621.html")
test_url("Detective Pikachu 2023", "https://www.famitsu.com/news/202310/19320055.html")
test_url("Game Watch Quinty", "https://game.watch.impress.co.jp/docs/news/655639.html")
