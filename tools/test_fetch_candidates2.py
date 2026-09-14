import urllib.request
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates2 = [
    ("电击XY声优(Archive)", "https://web.archive.org/web/20131102031021/http://dengekionline.com/elem/000/000/737/737734/"),
    ("raim2005-AZ学习装置", "http://raim2005.blog18.fc2.com/blog-entry-1177.html"),
    ("秋叶原总研LGPE", "https://akiba-souken.com/article/37143/"),
    ("School of Lock", "https://www.tfm.co.jp/lock/staff/index.php?itemid=8978"),
    ("GF远古官网(Archive)", "https://web.archive.org/web/19971016215524/http://www.gamefreak.co.jp/POKEMON/INTER/INTER.HTM"),
    ("GF新办公室", "https://canuch.com/projects/game-freak"),
    ("杉森绘画天气(Archive)", "https://web.archive.org/web/20130115083749/https://www.gamefreak.co.jp/blog/art/"),
    ("女子大生问BW(Archive)", "https://web.archive.org/web/20101227010653/http://www.nintendo.co.jp/ds/interview/irbj/sp/index.html"),
]

for name, url in candidates2:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = resp.read()
            print(f"[OK] {name}: status {resp.status}, size: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: error: {e}")
