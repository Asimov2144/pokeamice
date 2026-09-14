import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

u = 'https://www.nintendo.co.jp/3ds/interview/ekjj/vol1/movie.html'
try:
    raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('utf-8')
    print('movie.html found! len:', len(raw))
    for yt in re.findall(r'[\w-]{11}', raw):
        pass
    print("Video tags/objects/iframes:")
    for tag in re.findall(r'<(?:video|object|embed|iframe)[^>]+>', raw, re.I):
        print(" ", tag)
    for src in re.findall(r'src=["\']([^"\']+)["\']', raw, re.I):
        if any(ext in src for ext in ['.mp4', '.flv', 'youtube', 'video']):
            print("  src:", src)
    # Check div id="movie001"
    for m in re.findall(r'<div[^>]+id=["\']movie\d+["\'][^>]*>.*?</div>', raw, re.DOTALL | re.I):
        print("  Movie div:", m)
except Exception as e:
    print('Err:', e)
