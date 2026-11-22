import zipfile
import re

p = r"E:\antigravity-novel-engine\Harry Potter ID\Harry Potter 2 - Kamar Rahasia.epub"
with zipfile.ZipFile(p, 'r') as z:
    for name in z.namelist():
        if name.endswith('.ncx'):
            ncx = z.read(name).decode('utf-8', errors='ignore')
            points = re.findall(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]+)"', ncx)
            print(f"Total Chapters in HP2: {len(points)}")
            for t, s in points:
                print(f"  {t.strip()} -> {s}")
