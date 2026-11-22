import re

with open(r"D:\JV\novel yoga\vk_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find texts around doc links
docs = re.findall(r'<a[^>]+href="(/doc588886715_[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"Total doc links: {len(docs)}")
for href, label in set(docs):
    clean_label = " ".join(re.sub(r'<[^>]+>', ' ', label).split())
    print(f"File: {clean_label} -> https://vk.com{href}")

# Find any author/title or main text
snippets = re.findall(r'<div[^>]+class="[^"]*wall_signed[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
print("\nSignatures:", snippets)

# Search for any epub or novel names mentioned in HTML
names = re.findall(r'([A-Za-z0-9_\-\s]+\.(?:epub|pdf|mobi|azw3|zip|rar))', html, re.IGNORECASE)
print("\nFile names mentioned:", set(names))

# Print snippet of HTML where doc appears
idx = html.find('/doc588886715_')
if idx != -1:
    print("\nSnippet around first doc:\n", html[idx-200:idx+400])
