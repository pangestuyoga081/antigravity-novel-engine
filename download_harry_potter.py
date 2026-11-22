import os
import urllib.request
import ssl
import zipfile
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open(r"E:\antigravity-novel-engine\vk_wall_7.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract title and private_url
pattern = r'&quot;title&quot;:&quot;([^&]+)&quot;.*?&quot;private_url&quot;:&quot;([^&]+)&quot;'
matches = re.findall(pattern, html)

output_dir = r"E:\antigravity-novel-engine\Harry Potter"
os.makedirs(output_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

print(f"Found {len(matches)} matches")
for title, p_url in matches:
    clean_title = title.replace(r'\/', '/').replace('&#39;', "'")
    direct_url = p_url.replace(r'\/', '/')
    dest = os.path.join(output_dir, clean_title)
    print(f"Downloading {clean_title} from {direct_url}...")
    try:
        req = urllib.request.Request(direct_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp, open(dest, "wb") as fp:
            fp.write(resp.read())
        size = os.path.getsize(dest)
        valid = zipfile.is_zipfile(dest)
        print(f"  -> SUCCESS ({size/1024:.1f} KB, ZipValid={valid})")
    except Exception as e:
        print(f"  -> FAILED: {e}")
