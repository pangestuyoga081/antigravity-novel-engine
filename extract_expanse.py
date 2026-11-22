import re

with open(r"D:\JV\novel yoga\vk_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find all doc blocks
pattern = re.compile(r'title&quot;:&quot;([^&]+)&quot;.*?url&quot;:&quot;([^&]+)&quot;', re.DOTALL)
items = pattern.findall(html)
print(f"Total files in post: {len(items)}")

files = {}
for title, url in items:
    clean_url = url.replace(r"\/", "/")
    files[title] = clean_url

for t, u in sorted(files.items()):
    print(f"📚 {t}")
    print(f"   Link: {u}\n")
