import zipfile
import re

epub_path = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes.epub"
with zipfile.ZipFile(epub_path, 'r') as z:
    ncx = z.read("toc.ncx").decode("utf-8", errors="ignore")
    points = re.findall(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]+)"', ncx)
    print(f"Total entries in toc.ncx: {len(points)}")
    for title, src in points:
        print(f"  {title.strip()} -> {src}")
