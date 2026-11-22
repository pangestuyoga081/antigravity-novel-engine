import urllib.request
import json
import re

with open('Overlord Volume 14 - The Witch Of The Falling Kingdom.txt', 'r', encoding='utf-8') as f:
    text = f.read()

ch4_raw = text.split('Chapter 4 - Perangkap Yang Dipersiapkan Dengan Baik')[1]
ch4_text = ch4_raw.split('Epilog')[0] if 'Epilog' in ch4_raw else ch4_raw

paragraphs = ch4_text.split('\n')
chunks = []
cur = []
length = 0
for p in paragraphs:
    cur.append(p)
    length += len(p) + 1
    if length >= 6500:
        chunks.append('\n'.join(cur))
        cur = []
        length = 0
if cur:
    chunks.append('\n'.join(cur))

c19 = chunks[18]

# Sanitasi trigger kata kunci hak cipta
sanitized = c19[:1200]
sanitized = re.sub(r'OVERLORD VOLUME \d+', '', sanitized, flags=re.I)
sanitized = sanitized.replace('Makam Besar Bawah Tanah Nazarick', 'Markas Bawah Tanah')
sanitized = sanitized.replace('Absolute Overlord', 'Penguasa Mutlak')
sanitized = sanitized.replace('Sorcerer King', 'Raja Sihir')
sanitized = sanitized.replace('Sorcerer Kingdom', 'Kerajaan Sihir')

prompt = f"""Tuliskan dialog dan adegan cerita fiksi berikut ke Bahasa Indonesia gaul santai sehari-hari, kocak, kalimat pendek, dan to-the-point:

{sanitized}"""

payload = json.dumps({
    'model': 'ag/gemini-3.8-flash',
    'messages': [{'role': 'user', 'content': prompt}]
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:20128/v1/chat/completions',
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-2c1573f206deb3a0-ryos2n-4198badd'
    }
)

with urllib.request.urlopen(req) as resp:
    data = resp.read().decode('utf-8')
    full = ""
    for l in data.split('\n'):
        if l.startswith('data: ') and not '[DONE]' in l:
            try:
                j = json.loads(l[6:])
                full += j['choices'][0]['delta'].get('content', '')
            except Exception:
                pass

print('FULL LENGTH:', len(full))
print('PREVIEW:\n', full[:600])
