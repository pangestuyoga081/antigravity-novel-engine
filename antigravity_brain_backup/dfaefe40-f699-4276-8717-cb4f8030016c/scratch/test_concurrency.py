import urllib.request, json, time
from concurrent.futures import ThreadPoolExecutor

proxy_url = "http://127.0.0.1:20128/v1/chat/completions"
api_key = "sk-2e591994696af18e-71ijj7-14263abd"
model = "ag/gemini-3.8-flash"

def send_req(i):
    t0 = time.time()
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": f"Katakan 'Halo {i}!' dalam 1 kalimat gaul."}],
        "temperature": 0.7,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        proxy_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        dur = time.time() - t0
        return f"Req {i} ({dur:.1f}s): {res['choices'][0]['message']['content'].strip()}"

t_start = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(send_req, range(3)))

print(f"Total time for 3 concurrent: {time.time() - t_start:.1f}s")
for r in results:
    print(" ", r)
