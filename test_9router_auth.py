import urllib.request
import json

data = {
    'model': 'ag/gemini-3.8-flash-low',
    'messages': [{'role': 'user', 'content': 'Halo tes'}]
}

for key in [None, 'sk-2e591994696af18e-71ijj7-14263abd', '', 'test']:
    headers = {'Content-Type': 'application/json'}
    if key is not None:
        headers['Authorization'] = f'Bearer {key}'
    req = urllib.request.Request('http://localhost:20128/v1/chat/completions', data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode('utf-8')
            print(f"Key={key} -> SUCCESS: {raw[:150]}")
            break
    except Exception as e:
        print(f"Key={key} -> FAILED: {e}")
