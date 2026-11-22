import zipfile

for b in ["Book 2 - Harry Potter and the Chamber of Secrets.epub", "Book 7 - Harry Potter and the Deathly Hallows.epub"]:
    p = f"E:\\antigravity-novel-engine\\Harry Potter\\{b}"
    with zipfile.ZipFile(p, 'r') as z:
        print(f"=== {b} ===")
        print("Total files:", len(z.namelist()))
        text_files = [f for f in z.namelist() if f.endswith(('.html', '.xhtml'))]
        print("Text files count:", len(text_files))
        # inspect sample
        for tf in text_files[:3]:
            content = z.read(tf).decode('utf-8', errors='ignore')
            print(f"  File {tf}: {len(content)} chars")
