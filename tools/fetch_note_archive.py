import urllib.request
import urllib.parse
import json
import re

url = 'https://note.com/api/v2/searches?q=' + urllib.parse.quote('ポケモン開発者インタビュー') + '&type=notes'
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    notes = data.get('data', {}).get('notes', [])
    print(f"Found {len(notes)} notes:")
    for n in notes:
        key = n.get('key')
        name = n.get('name')
        user = n.get('user', {}).get('urlname')
        note_url = f"https://note.com/{user}/n/{key}"
        print(f"- {name} | {note_url}")
except Exception as e:
    print('Err:', e)
