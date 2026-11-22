with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_found.html", encoding="utf-8") as f:
    html = f.read()

import re

# find where docs are attached
# in VK desktop, doc attachments often have doc-xxxxx or media_link
for m in re.finditer(r'href="([^"]*doc[^"]*)"', html):
    print("DOC LINK:", m.group(1))

# Check comments or replies!
replies = re.findall(r'<div class="reply_text">(.*?)</div>', html, re.DOTALL)
print(f"Replies count: {len(replies)}")
for r in replies:
    print("REPLY:", re.sub(r'<[^>]+>', ' ', r).strip())
