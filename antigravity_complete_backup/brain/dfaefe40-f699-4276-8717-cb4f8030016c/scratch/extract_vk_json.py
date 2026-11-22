import html
import json
import re

with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\post_block.html", encoding="utf-8") as f:
    block = f.read()

# unescape html entities
unescaped = html.unescape(block)

# find all json-like doc objects: "id":...,"owner_id":...,"title":...
# Let's find all occurrences of "title":
pattern = r'\{[^{}]*?"title":\s*"([^"]+)"[^{}]*?\}'
matches = re.findall(pattern, unescaped)

print(f"Total doc items: {len(matches)}")

# Let's find more detailed doc info
# e.g., "id":561272..., "owner_id":588886715, "title":..., "url":...
doc_objects = re.findall(r'(\{[^{}]*?owner_id[^{}]*?title[^{}]*?\})', unescaped)
print(f"Doc objects found: {len(doc_objects)}")

docs = []
for obj_str in doc_objects:
    try:
        # try parsing or regex extracting fields
        title = re.search(r'"title":\s*"([^"]+)"', obj_str)
        oid = re.search(r'"owner_id":\s*([0-9-]+)', obj_str)
        doc_id = re.search(r'"id":\s*([0-9]+)', obj_str)
        url = re.search(r'"url":\s*"([^"]+)"', obj_str)
        access_key = re.search(r'"access_key":\s*"([^"]+)"', obj_str)
        
        t = title.group(1) if title else "Unknown"
        o = oid.group(1) if oid else ""
        d = doc_id.group(1) if doc_id else ""
        u = url.group(1) if url else ""
        ak = access_key.group(1) if access_key else ""
        
        docs.append({
            "title": t,
            "owner_id": o,
            "id": d,
            "url": u,
            "access_key": ak,
            "raw": obj_str
        })
    except Exception as e:
        pass

# Print sorted or unique by title
seen = set()
for doc in docs:
    if doc["title"] not in seen:
        seen.add(doc["title"])
        print(f"TITLE: {doc['title']}")
        print(f"  ID: doc{doc['owner_id']}_{doc['id']}")
        print(f"  URL: {doc['url']}")
        print(f"  KEY: {doc['access_key']}")
        print()
