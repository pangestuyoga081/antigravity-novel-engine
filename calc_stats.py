import zipfile
import re

for b in ["Book 2 - Harry Potter and the Chamber of Secrets.epub", "Book 7 - Harry Potter and the Deathly Hallows.epub"]:
    p = f"E:\\antigravity-novel-engine\\Harry Potter\\{b}"
    total_chars = 0
    with zipfile.ZipFile(p, 'r') as z:
        for f in z.namelist():
            if f.endswith(('.html', '.xhtml')):
                raw = z.read(f).decode('utf-8', errors='ignore')
                clean = re.sub(r'<[^>]+>', ' ', raw)
                total_chars += len(' '.join(clean.split()))
    words = total_chars / 6
    print(f"{b}: ~{total_chars:,} chars (~{words:,.0f} words)")
