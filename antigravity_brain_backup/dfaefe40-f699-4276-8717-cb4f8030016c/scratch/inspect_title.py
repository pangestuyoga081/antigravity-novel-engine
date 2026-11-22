with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_6050.html", encoding="utf-8") as f:
    html = f.read()

import re
print("Title:", re.findall(r'<title>(.*?)</title>', html))
print("Wall items:", len(re.findall(r'class="[^"]*wall[^"]*"', html)))
for m in re.finditer(r'<div class="pi_text">(.*?)</div>', html, re.DOTALL):
    print("Post text:", m.group(1)[:300])
