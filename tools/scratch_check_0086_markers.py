import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

u2 = "https://www.famitsu.com/news/201208/05019240.html"
raw2 = urllib.request.urlopen(urllib.request.Request(u2, headers=headers)).read().decode('utf-8')

# Check headers (h2/h3) or bold titles
sections2 = re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', raw2, re.I | re.DOTALL)
print("PKMN-0086 Headings:", [re.sub(r'<[^>]+>', '', h).strip() for h in sections2])

# Check strong tags or question markers like ▼ or ■ or ――
markers2 = re.findall(r'(?:<strong[^>]*>|<b>|■|▼|――)(.*?)(?:</strong>|</b>|\n|<br>)', raw2, re.I)
print("Sample markers/questions in PKMN-0086:", [re.sub(r'<[^>]+>', '', m).strip() for m in markers2 if len(m.strip()) > 3][:10])
