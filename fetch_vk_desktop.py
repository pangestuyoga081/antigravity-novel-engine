import urllib.request
import re

url = "https://vk.com/wall-196255529_6050"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

try:
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    
    # Save html to examine
    with open(r"D:\JV\novel yoga\vk_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Saved HTML dump, size:", len(html))
    
    # Look for post texts
    texts = re.findall(r'class="[^"]*wall_post_text[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    print("Found wall_post_text:", len(texts))
    for t in texts:
        clean = re.sub(r'<[^>]+>', ' ', t)
        print("--- POST CONTENT ---")
        print(" ".join(clean.split()))
        
    # Look for media links or doc links
    doc_matches = re.findall(r'href="([^"]*(?:doc|\.epub|\.pdf|\.rar|\.zip)[^"]*)"', html, re.IGNORECASE)
    print("Doc / File matches:", doc_matches)
    
except Exception as e:
    print("Error:", e)
