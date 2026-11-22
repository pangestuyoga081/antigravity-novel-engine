import urllib.request
import re

url = "https://m.vk.com/wall-207038148_745"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    docs = re.findall(r'href="(/doc[^"]+)"[^>]*>([^<]+)</a>', html)
    print("Docs in 745:", docs)
except Exception as e:
    print(e)
