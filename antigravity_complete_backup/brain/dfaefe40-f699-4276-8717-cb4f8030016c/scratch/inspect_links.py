with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\post_block.html", encoding="utf-8") as f:
    block = f.read()

import re

# find all links in post_block
links = re.findall(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
print(f"Links in post block: {len(links)}")
for href, content in links:
    text = re.sub(r'<[^>]+>', ' ', content).strip()
    print(f"LINK: {text} | {href}")
