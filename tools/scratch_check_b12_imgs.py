import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== 1. PKMN-0091 Images & Structure ===")
u1 = "https://news.denfaminicogamer.jp/interview/170703/2"
raw1 = urllib.request.urlopen(urllib.request.Request(u1, headers=headers)).read().decode('utf-8')
imgs1 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw1, re.I)
f_imgs1 = [i for i in imgs1 if 'uploads' in i and any(ext in i for ext in ['.jpg', '.png', '.webp'])]
print("Denfami 0091 upload imgs:", len(f_imgs1))
for img in f_imgs1[:5]:
    print(" ", img)

print("\n=== 2. PKMN-0678 Images & Structure ===")
u2 = "https://news.denfaminicogamer.jp/interview/180608/2"
raw2 = urllib.request.urlopen(urllib.request.Request(u2, headers=headers)).read().decode('utf-8')
imgs2 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw2, re.I)
f_imgs2 = [i for i in imgs2 if 'uploads' in i and any(ext in i for ext in ['.jpg', '.png', '.webp'])]
print("Denfami 0678 upload imgs:", len(f_imgs2))
for img in f_imgs2[:5]:
    print(" ", img)

print("\n=== 3. PKMN-0050 Images & Structure ===")
u3 = "https://www.famitsu.com/news/202104/30218824.html"
raw3 = urllib.request.urlopen(urllib.request.Request(u3, headers=headers)).read().decode('utf-8')
imgs3 = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw3, re.I)
f_imgs3 = [i for i in imgs3 if '/images/000/' in i]
print("Famitsu 0050 imgs:", len(f_imgs3))
for img in f_imgs3[:5]:
    print(" ", img)
