import re

with open(r"D:\JV\novel yoga\vk_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find all private_url and titles
pattern = re.compile(r'title&quot;:&quot;([^&]+)&quot;.*?private_url&quot;:&quot;([^&]+)&quot;', re.DOTALL)
items = pattern.findall(html)

files = {}
for title, url in items:
    clean_url = url.replace(r"\/", "/")
    files[title] = clean_url

# Also match ordinary doc hrefs
doc_links = re.findall(r'<a[^>]+href="(/doc588886715_[^"]+)"[^>]*>([^<]+)</a>', html)
for href, label in doc_links:
    l_clean = label.strip()
    if l_clean and l_clean not in files:
        files[l_clean] = f"https://vk.com{href}"

print(f"Total file ditemukan di postingan: {len(files)}\n")
for t in sorted(files.keys()):
    print(f"📖 {t}")
    print(f"   Download Link: {files[t]}\n")
