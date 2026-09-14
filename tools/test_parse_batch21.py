import urllib.request
import ssl
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_dengeki():
    url = "https://dengekionline.com/elem/000/000/193/193021/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, context=ctx).read()
    html = raw.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # We want paragraphs, headings, images
    article = soup.find('div', class_='elem-body') or soup.find('div', id='article-body') or soup
    # find all p, h2, h3, img
    items = []
    for tag in soup.find_all(['h2', 'h3', 'p', 'img']):
        if tag.name in ['h2', 'h3']:
            txt = tag.get_text(strip=True)
            if txt and not any(k in txt for k in ['最新記事', 'ランキング', '電撃']):
                items.append({'type': 'heading', 'level': int(tag.name[1]), 'original': txt})
        elif tag.name == 'p':
            txt = tag.get_text(strip=True)
            if not txt:
                continue
            if any(k in txt for k in ['2009年9月18日', '文：電撃オンライン', '◆◇◆']):
                continue
            if 'Amazon' in txt or 'http://' in txt and len(txt) < 30:
                continue
            # check if Q&A
            if txt.startswith('――'):
                items.append({'type': 'dialogue', 'speaker_orig': '電撃', 'original': txt[2:].strip()})
            elif txt.startswith('森本さん：'):
                items.append({'type': 'dialogue', 'speaker_orig': '森本さん', 'original': txt[5:].strip()})
            elif txt.startswith('■'):
                items.append({'type': 'heading', 'level': 2, 'original': txt[1:].strip()})
            else:
                items.append({'type': 'text', 'original': txt})
    print(f"Dengeki parsed {len(items)} items")
    for it in items[:5]:
        print(" ", it)

def test_famitsu():
    url = "https://www.famitsu.com/news/201803/30154405.html"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, context=ctx).read()
    html = raw.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Article body in Famitsu
    article = soup.find('div', class_=lambda c: c and ('article' in c or 'entry' in c or 'body' in c)) or soup
    items = []
    # inspect p tags inside article
    for p in soup.find_all(['h2', 'h3', 'p']):
        txt = p.get_text(strip=True)
        if not txt:
            continue
        if any(skip in txt for skip in ['ファミ通.com', '株式会社KADOKAWA', 'Twitterでシェア', 'ページの先頭へ', '前ページ', '次ページ']):
            continue
        if txt.startswith('――'):
            items.append({'type': 'dialogue', 'speaker_orig': 'ファミ通', 'original': txt[2:].strip()})
        elif txt.startswith('陣内　') or txt.startswith('陣内 '):
            items.append({'type': 'dialogue', 'speaker_orig': '陣内', 'original': txt[3:].strip()})
        elif txt.startswith('陣内'):
            items.append({'type': 'dialogue', 'speaker_orig': '陣内', 'original': txt[2:].strip()})
        elif txt.startswith('宮下　') or txt.startswith('宮下 '):
            items.append({'type': 'dialogue', 'speaker_orig': '宮下', 'original': txt[3:].strip()})
        elif txt.startswith('宮下'):
            items.append({'type': 'dialogue', 'speaker_orig': '宮下', 'original': txt[2:].strip()})
        elif p.name in ['h2', 'h3']:
            items.append({'type': 'heading', 'level': int(p.name[1]), 'original': txt})
        elif txt.startswith('■'):
            items.append({'type': 'heading', 'level': 2, 'original': txt[1:].strip()})
        else:
            items.append({'type': 'text', 'original': txt})
    print(f"Famitsu parsed {len(items)} items")
    for it in items[:6]:
        print(" ", it)

def test_2083():
    base = "http://www.2083.jp/contents/201410gamefreak/"
    pages = [
        ("page_01.html", "第1章：すべてのはじまり、『ポケットモンスター 赤・緑』の楽曲に迫る"),
        ("page_02.html", "第2章：野生のポケモンとの戦闘曲を増田さんが作り続けている理由"),
        ("page_03.html", "第3章：増田さん、音楽を託すさみしさってありましたか？"),
        ("page_04.html", "第4章・特別編：祝・TGS 日本ゲーム大賞 2014 特別賞！一之瀬さんに聞く『ソリティ馬』")
    ]
    total_items = 0
    for page_name, chapter_title in pages:
        url = base + page_name
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, context=ctx).read()
        try:
            html = raw.decode('shift_jis')
        except:
            html = raw.decode('utf-8', 'replace')
        soup = BeautifulSoup(html, 'html.parser')
        lines = [l.strip() for l in soup.get_text().split('\n') if l.strip()]
        page_items = []
        for l in lines:
            if any(skip in l for skip in ['2083', 'Copyright', 'Tweet', '演奏会', 'オーケストラ', 'はてなブックマーク', '特集コンテンツ', '関連情報']):
                continue
            page_items.append(l)
        total_items += len(page_items)
        print(f"2083 {page_name} -> {len(page_items)} lines (sample: {page_items[0] if page_items else 'none'})")
    print(f"2083 total lines: {total_items}")

test_dengeki()
test_famitsu()
test_2083()
