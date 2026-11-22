import re
import json

with open(r"D:\JV\novel yoga\vk_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find all JSON-like objects in data-attrs or script tags
matches = re.findall(r'(\{[^{}]*?&quot;title&quot;:[^{}]*?\})', html)
print("Matches found:", len(matches))

docs_info = []
for m in matches:
    clean = m.replace("&quot;", '"').replace("&amp;", "&").replace(r"\/", "/")
    try:
        data = json.loads(clean)
        if "title" in data and "url" in data:
            docs_info.append(data)
    except:
        pass

# Also regex directly
direct_docs = re.findall(r'&quot;title&quot;:&quot;([^&]+)&quot;.*?&quot;url&quot;:&quot;([^&]+)&quot;', html)
print("Direct docs found:", len(direct_docs))

found = {}
for title, url in direct_docs:
    clean_url = url.replace(r"\/", "/")
    found[title] = clean_url

for t, u in found.items():
    print(f"📖 {t}\n   🔗 {u}\n")
