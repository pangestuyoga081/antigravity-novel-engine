with open(r"E:\antigravity-novel-engine\vk_wall_7.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

for m in re.finditer(r'&quot;private_url&quot;:&quot;([^&]+)&quot;', html):
    u = m.group(1).replace(r'\/', '/')
    print("PRIVATE URL:", u)
