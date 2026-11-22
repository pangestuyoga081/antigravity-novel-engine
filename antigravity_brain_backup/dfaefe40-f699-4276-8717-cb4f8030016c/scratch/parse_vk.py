import urllib.request
import re

url = "https://m.vk.ru/wall-196255529_6050"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B)"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    # Save html to examine
    with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_6050.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("HTML saved, length:", len(html))
    
    # regex for docs
    # in mobile vk: <a class="medias_link ..." href="/doc..."><span class="medias_link_text">...
    for m in re.finditer(r'href="(/doc[^"]+)"', html):
        href = m.group(1)
        # find nearby text
        sub = html[max(0, m.start()-100):min(len(html), m.end()+200)]
        print(f"HREF: {href}")
        # print text snippet
        clean = re.sub(r'<[^>]+>', ' ', sub)
        print("SNIPPET:", ' '.join(clean.split())[:150])
except Exception as e:
    print("ERROR:", e)
