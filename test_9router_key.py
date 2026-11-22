import urllib.request
import json

data = {
    'model': 'ag/gemini-3.8-flash-low',
    'messages': [{'role': 'user', 'content': 'Halo! Balas dengan kata SUKSES.'}]
}

key = 'sk-2c1573f206deb3a0-ryos2n-4198badd'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {key}'
}

req = urllib.request.Request('http://localhost:20128/v1/chat/completions', data=json.dumps(data).encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode('utf-8')
        print("RAW RESPONSE:", repr(raw))
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode('utf-8'))
except Exception as e:
    print("OTHER ERROR:", e)
