import urllib.request
import re
import json

urls = [
    "https://vk.com/wall-193180807_7",
    "https://m.vk.com/wall-193180807_7",
    "https://vk.ru/wall-193180807_7"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

found = False
for url in urls:
    try:
        print(f"Fetching {url}...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"Success, length: {len(content)}")
            with open(r"E:\antigravity-novel-engine\vk_wall_7.html", "w", encoding="utf-8") as f:
                f.write(content)
            found = True
            break
    except Exception as e:
        print(f"Failed {url}: {e}")

if not found:
    print("Could not fetch with urllib")
