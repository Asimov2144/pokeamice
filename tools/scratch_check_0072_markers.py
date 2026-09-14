import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

u3 = "https://www.famitsu.com/news/201311/16043307.html"
raw3 = urllib.request.urlopen(urllib.request.Request(u3, headers=headers)).read().decode('utf-8')

sections3 = re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', raw3, re.I | re.DOTALL)
print("PKMN-0072 Headings:", [re.sub(r'<[^>]+>', '', h).strip() for h in sections3[:8]])

markers3 = re.findall(r'(?:<strong[^>]*>|<b>|■|▼|――)(.*?)(?:</strong>|</b>|\n|<br>)', raw3, re.I)
print("Sample markers/questions in PKMN-0072:", [re.sub(r'<[^>]+>', '', m).strip() for m in markers3 if len(m.strip()) > 3][:10])
