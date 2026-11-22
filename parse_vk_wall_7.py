import re
import html
import json

with open(r"E:\antigravity-novel-engine\vk_wall_7.html", "r", encoding="utf-8") as f:
    raw = f.read()

unescaped = html.unescape(raw)

# Extract post text/caption
text_match = re.search(r'class="wall_post_text[^"]*">(.*?)</div>', unescaped, re.DOTALL)
if not text_match:
    text_match = re.search(r'class="pi_text[^"]*">(.*?)</div>', unescaped, re.DOTALL)

if text_match:
    clean_text = re.sub(r'<[^>]+>', '\n', text_match.group(1)).strip()
    print("=== POST CAPTION ===")
    print(clean_text)
    print("="*50)
else:
    # check og:description
    og = re.search(r'property="og:description"\s+content="([^"]+)"', unescaped)
    if og:
        print("=== OG DESCRIPTION ===")
        print(og.group(1))
        print("="*50)

# Extract doc attachments from JSON payload
doc_objects = re.findall(r'(\{[^{}]*?owner_id[^{}]*?title[^{}]*?\})', unescaped)
print(f"Total doc objects found: {len(doc_objects)}")

docs = []
for obj_str in doc_objects:
    try:
        title = re.search(r'"title":\s*"([^"]+)"', obj_str)
        oid = re.search(r'"owner_id":\s*([0-9-]+)', obj_str)
        doc_id = re.search(r'"id":\s*([0-9]+)', obj_str)
        url = re.search(r'"url":\s*"([^"]+)"', obj_str)
        size = re.search(r'"size":\s*([0-9]+)', obj_str)
        ext = re.search(r'"ext":\s*"([^"]+)"', obj_str)
        
        t = title.group(1) if title else "Unknown"
        o = oid.group(1) if oid else ""
        d = doc_id.group(1) if doc_id else ""
        u = url.group(1) if url else ""
        s = int(size.group(1)) if size else 0
        e = ext.group(1) if ext else ""
        
        # fix escaped slashes in url
        u = u.replace(r'\/', '/')
        
        docs.append({
            "title": t,
            "owner_id": o,
            "id": d,
            "size_kb": s / 1024,
            "size_bytes": s,
            "ext": e,
            "url": u
        })
    except Exception as err:
        pass

# Deduplicate
seen = set()
unique_docs = []
for d in docs:
    key = (d["title"], d["id"])
    if key not in seen:
        seen.add(key)
        unique_docs.append(d)

print(f"\nUnique Documents ({len(unique_docs)}):")
for idx, d in enumerate(unique_docs, 1):
    print(f"{idx}. {d['title']} ({d['size_kb']:.1f} KB) -> {d['url']}")
