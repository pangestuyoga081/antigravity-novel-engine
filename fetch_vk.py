import urllib.request
import re

url = "https://m.vk.com/wall-196255529_6050"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("Status 200, length:", len(html))
        
        # Title
        t = re.findall(r"<title>(.*?)</title>", html)
        print("Title:", t)
        
        # Post text
        for p in re.findall(r'<div[^>]*class="[^"]*wall_post_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL):
            print("\nWall Post Text:\n", re.sub(r"<[^>]+>", " ", p))
            
        # Any links
        links = re.findall(r'href="([^"]+)"', html)
        external = [l for l in links if "vk.com" not in l and l.startswith("http")]
        print("\nExternal Links:", external[:10])
except Exception as e:
    print("Fetch error:", e)
