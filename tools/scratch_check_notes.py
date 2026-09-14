import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0'}
u = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html"
raw = urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode('shift_jis', errors='replace')

notes = re.findall(r'<DIV CLASS="int-notes">(.*?)</DIV>', raw, re.DOTALL | re.I)
if notes:
    print(f"Notes section found: {len(notes)}")
    clean_notes = re.sub(r'<[^>]+>', '', notes[0]).strip()
    print(clean_notes[:500])
else:
    print("No int-notes found, searching for ※1...")
    m = re.findall(r'※\d+.*', re.sub(r'<[^>]+>', '', raw))
    for line in m[:5]:
        print(" ", line.strip())
