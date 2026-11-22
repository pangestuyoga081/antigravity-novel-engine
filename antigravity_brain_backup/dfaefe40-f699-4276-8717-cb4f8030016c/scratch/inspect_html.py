import re

with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_6050.html", encoding="utf-8") as f:
    html = f.read()

print("File size:", len(html))

# search for Expanse
matches = list(re.finditer(r'Expanse', html, re.I))
print("Expanse count:", len(matches))
for m in matches[:10]:
    start = max(0, m.start()-150)
    end = min(len(html), m.end()+250)
    print("--- SNIP ---")
    print(html[start:end])
