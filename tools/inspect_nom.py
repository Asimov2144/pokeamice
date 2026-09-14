import urllib.request
import re
from pathlib import Path

def test_url(url, encoding="shift_jis"):
    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            content = r.read().decode(encoding, errors="replace")
            title_m = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            title = title_m.group(1).strip() if title_m else "No title"
            print(f"Title: {title}")
            links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
            print(f"Found {len(links)} links:")
            for href, text in links:
                clean_text = re.sub(r"<[^>]+>", "", text).strip().replace("\n", " ")
                if clean_text and not href.startswith("#"):
                    print(f"  [{clean_text[:40]}] -> {href}")
            return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

if __name__ == "__main__":
    test_url("http://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/gfreak/page01.html")
