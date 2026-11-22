import urllib.request
import re
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://vk.com/wall-215501859_172"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# find doc attachments
docs = re.findall(r'(\{[^{}]*?title[^{}]*?private_url[^{}]*?\})', html)
print("Docs found in wall-215501859_172:", len(docs))
for d in docs:
    title = re.search(r'"title":\s*"([^"]+)"', d)
    u = re.search(r'"private_url":\s*"([^"]+)"', d)
    size = re.search(r'"size":\s*([0-9]+)', d)
    if title and u:
        clean_url = u.group(1).replace('\\/', '/')
        s_kb = int(size.group(1))/1024 if size else 0
        print(f"{title.group(1)} -> {s_kb:.1f} KB -> {clean_url}")
