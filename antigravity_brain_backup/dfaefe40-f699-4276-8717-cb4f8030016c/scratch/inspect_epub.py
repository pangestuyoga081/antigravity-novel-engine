import zipfile
import re

epub_path = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes.epub"
with zipfile.ZipFile(epub_path, 'r') as z:
    for name in z.namelist():
        if name.endswith(('.ncx', '.opf')):
            print(f"Meta file: {name}")
            content = z.read(name).decode('utf-8', errors='ignore')
            print(content[:500])
            print("="*50)
