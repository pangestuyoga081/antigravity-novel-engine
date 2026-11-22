import zipfile
import re

epub_path = r"E:\antigravity-novel-engine\Harry Potter ID\Harry Potter 1 - Batu Bertuah.epub"
with zipfile.ZipFile(epub_path, 'r') as z:
    ncx = z.read("OPS/toc.ncx").decode("utf-8", errors="ignore")
    points = re.findall(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]+)"', ncx)
    print(f"Total Chapters in TOC: {len(points)}")
    for title, src in points:
        print(f"  {title.strip()} -> {src}")
