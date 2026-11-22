import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://m.vk.com/wall-207038148_680",
    "https://vk.com/wall-186523933_308",
    "https://vk.com/wall-196255529_234",
    "https://vk.com/wall-157973070_1937"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            docs = re.findall(r'(\{[^{}]*?title[^{}]*?private_url[^{}]*?\})', html)
            print(f"URL {u} -> docs: {len(docs)}")
            for d in docs:
                title = re.search(r'"title":\s*"([^"]+)"', d)
                p_url = re.search(r'"private_url":\s*"([^"]+)"', d)
                if title and 'Harry Potter' in title.group(1):
                    print(f"  {title.group(1)} -> {p_url.group(1) if p_url else 'no priv'}")
    except Exception as e:
        print(f"URL {u} err: {e}")
