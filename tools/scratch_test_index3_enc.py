import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index3.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read()

for enc in ['utf-8', 'shift_jis', 'cp932', 'euc-jp']:
    try:
        dec = raw.decode(enc)
        if "通信" in dec:
            print(f"[SUCCESS] index3.html decoded with {enc} contains '通信'!")
    except Exception as e:
        pass
