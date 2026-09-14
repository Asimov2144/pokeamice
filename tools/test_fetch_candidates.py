import urllib.request
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("HGSS森本", "https://dengekionline.com/elem/000/000/193/193021/"),
    ("音乐传承2083", "https://www.2083.jp/contents/201410gamefreak/"),
    ("日月发售法米通", "https://www.famitsu.com/news/201611/18120892.html"),
    ("剑盾4Gamer", "https://www.4gamer.net/games/451/G045142/20191114093/"),
    ("宇都宫构想日本", "http://www.kosonippon.org/news/2020/taidan0901/"),
    ("电击XY声优对谈", "https://dengekionline.com/elem/000/000/737/737734/"),
    ("名侦探皮卡丘法米通", "https://www.famitsu.com/news/201803/30154405.html"),
    ("宝可梦探险寻宝4Gamer", "https://www.4gamer.net/games/421/G042131/20180629087/"),
    ("PokéRig CEDEC", "https://news.denfaminicogamer.jp/kikakuthetower/2607233k"),
]

for name, url in candidates:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {url} -> status {resp.status}, size: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {url} -> error: {e}")
