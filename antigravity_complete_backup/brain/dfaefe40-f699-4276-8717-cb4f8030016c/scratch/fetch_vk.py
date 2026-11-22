import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

urls = [
    'https://vk.com/wall-196255529_6050',
    'https://m.vk.com/wall-196255529_6050'
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"URL: {url}, len: {len(content)}")
            if "Leviathan" in content:
                print("FOUND Leviathan in", url)
                with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_found.html", "w", encoding="utf-8") as f:
                    f.write(content)
                break
    except Exception as e:
        print(f"Failed {url}: {e}")
