import zipfile
import re

p = r"E:\antigravity-novel-engine\Harry Potter ID\Harry Potter 1 - Batu Bertuah.epub"
with zipfile.ZipFile(p, 'r') as z:
    for name in z.namelist()[:10]:
        if name.endswith(('.html', '.xhtml')):
            content = z.read(name).decode('utf-8', errors='ignore')
            clean = re.sub(r'<[^>]+>', ' ', content)
            lines = [l.strip() for l in clean.split('\n') if l.strip()]
            print("=== File:", name, "===")
            for l in lines[:8]:
                print(" ", l[:120])
