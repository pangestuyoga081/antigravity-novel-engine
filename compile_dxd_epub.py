import os
import zipfile
import re
import shutil

VOL_NUM = "01"
SRC_TXT = r"D:\JV\novel yoga\High School DxD\High_School_DxD_Volume_01_Raw_Source (Terjemahan ID-Direct).txt"
IMG_SRC_DIR = r"D:\JV\novel yoga\High School DxD\extracted\Vol_01\High School Dxd - Volume 01 [RuiDrive]\Image"
OUTPUT_EPUB = rf"D:\JV\novel yoga\epubs\High_School_DxD_Volume_{VOL_NUM} (Illustrated ID-Direct).epub"
BUILD_DIR = rf"D:\JV\novel yoga\High School DxD\build_epub_vol_{VOL_NUM}"

os.makedirs(r"D:\JV\novel yoga\epubs", exist_ok=True)
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(os.path.join(BUILD_DIR, "META-INF"), exist_ok=True)
os.makedirs(os.path.join(BUILD_DIR, "OEBPS", "images"), exist_ok=True)

# 1. mimetype
with open(os.path.join(BUILD_DIR, "mimetype"), "w", encoding="utf-8") as f:
    f.write("application/epub+zip")

# 2. container.xml
container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
with open(os.path.join(BUILD_DIR, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
    f.write(container_xml)

# 3. Copy Images
img_files = os.listdir(IMG_SRC_DIR)
manifest_images = []
for img in img_files:
    shutil.copy(os.path.join(IMG_SRC_DIR, img), os.path.join(BUILD_DIR, "OEBPS", "images", img))
    mtype = "image/jpeg" if img.lower().endswith(('.jpg', '.jpeg')) else "image/png"
    manifest_images.append(f'<item id="img_{img.replace(".", "_")}" href="images/{img}" media-type="{mtype}"/>')

# 4. Read translated text and split into chapters
with open(SRC_TXT, "r", encoding="utf-8") as f:
    full_text = f.read()

def clean_xml(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&#8220;").replace('"', "&#8221;")
    return text

# Split by bab header
chapter_regex = r"(?=Life\s+[0-9]+|New\s+Life|Afterword)"
raw_chaps = re.split(chapter_regex, full_text)

chapters_data = []
ch_idx = 1

# If there are color illustrations before Life 00, add to titlepage / gallery
color_inserts = ["HSDxD_vol_01_004.jpg", "HSDxD_vol_01_005-006.jpg", "HSDxD_vol_01_007.jpg"]
gallery_html = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id">
<head>
  <title>Ilustrasi Berwarna</title>
  <style>
    body { margin: 0; padding: 0; text-align: center; background: #000; }
    img { max-width: 100%; height: auto; margin-bottom: 10px; }
  </style>
</head>
<body>
"""
for ci in color_inserts:
    if os.path.exists(os.path.join(IMG_SRC_DIR, ci)):
        gallery_html += f'  <p><img src="images/{ci}" alt="Ilustrasi"/></p>\n'
gallery_html += "</body></html>"
with open(os.path.join(BUILD_DIR, "OEBPS", "color_gallery.xhtml"), "w", encoding="utf-8") as f:
    f.write(gallery_html)

for rc in raw_chaps:
    rc_str = rc.strip()
    if not rc_str:
        continue
    
    lines = rc_str.split("\n")
    title = lines[0].strip()
    
    html_paragraphs = []
    html_paragraphs.append(f'<h1 class="chapter-title">{clean_xml(title)}</h1>')
    
    # Process body
    body_text = "\n".join(lines[1:])
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    
    for p in paragraphs:
        # Check illustration tag
        img_match = re.search(r'\[\[ILUSTRASI:([^\]]+)\]\]', p)
        if img_match:
            img_name = img_match.group(1).strip()
            html_paragraphs.append(f'<div class="illust-box"><img src="images/{img_name}" alt="Ilustrasi"/><p class="caption">Ilustrasi DxD Volume {VOL_NUM}</p></div>')
            p_clean = p.replace(img_match.group(0), "").strip()
            if not p_clean:
                continue
            p = p_clean
            
        if ":" in p and any(k in p for k in ["Issei Hyoudou:", "Rias Gremory:", "Asia Argento:", "Akeno Himejima:", "Koneko Toujou:", "Kiba Yuuto:", "Raynare:", "Freed Sellzen:"]):
            html_paragraphs.append(f'<p class="dialogue"><b>{clean_xml(p)}</b></p>')
        else:
            sub_lines = [clean_xml(l) for l in p.split("\n") if l.strip()]
            html_paragraphs.append(f'<p>{"<br/>".join(sub_lines)}</p>')
            
    ch_file = f"chapter_{ch_idx:02d}.xhtml"
    ch_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id">
<head>
  <title>{clean_xml(title)}</title>
  <style>
    body {{ font-family: "Georgia", "Times New Roman", serif; line-height: 1.65; margin: 5%; color: #1a1a1a; }}
    h1.chapter-title {{ text-align: center; margin-top: 1.5em; margin-bottom: 1.5em; font-size: 1.6em; color: #b30000; font-weight: bold; border-bottom: 2px solid #b30000; padding-bottom: 0.3em; }}
    p {{ margin-bottom: 0.9em; text-indent: 1.2em; text-align: justify; }}
    p.dialogue {{ text-indent: 0; margin-left: 0.5em; margin-bottom: 0.8em; color: #111; }}
    b {{ color: #8b0000; }}
    .illust-box {{ text-align: center; margin: 2em 0; }}
    .illust-box img {{ max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
    .caption {{ font-size: 0.85em; color: #666; margin-top: 0.5em; text-indent: 0; text-align: center; font-style: italic; }}
  </style>
</head>
<body>
  {"\n  ".join(html_paragraphs)}
</body>
</html>"""
    with open(os.path.join(BUILD_DIR, "OEBPS", ch_file), "w", encoding="utf-8") as f:
        f.write(ch_content)
        
    chapters_data.append((ch_file, title))
    ch_idx += 1

# 5. Build content.opf and toc.ncx
manifest_items = [
    '<item id="color_gallery" href="color_gallery.xhtml" media-type="application/xhtml+xml"/>'
]
spine_items = [
    '<itemref idref="color_gallery"/>'
]
nav_points = [
    '<navPoint id="nav_gallery" playOrder="1"><navLabel><text>Ilustrasi Berwarna</text></navLabel><content src="color_gallery.xhtml"/></navPoint>'
]

for idx, (cf, c_title) in enumerate(chapters_data):
    cid = f"ch_{idx+1:02d}"
    manifest_items.append(f'<item id="{cid}" href="{cf}" media-type="application/xhtml+xml"/>')
    spine_items.append(f'<itemref idref="{cid}"/>')
    nav_points.append(f'<navPoint id="nav_{cid}" playOrder="{idx+2}"><navLabel><text>{clean_xml(c_title)}</text></navLabel><content src="{cf}"/></navPoint>')

content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>High School DxD - Volume {VOL_NUM} (No Sensor - ID-Direct)</dc:title>
    <dc:creator>Ichiei Ishibumi</dc:creator>
    <dc:language>id</dc:language>
    <dc:identifier id="BookId">urn:uuid:hsdxd-vol{VOL_NUM}-direct-id</dc:identifier>
    <meta name="cover" content="img_DxDLN01_jpg"/>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    {"\n    ".join(manifest_images)}
    {"\n    ".join(manifest_items)}
  </manifest>
  <spine toc="ncx">
    {"\n    ".join(spine_items)}
  </spine>
</package>"""

with open(os.path.join(BUILD_DIR, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
    f.write(content_opf)

toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:hsdxd-vol{VOL_NUM}-direct-id"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>High School DxD - Volume {VOL_NUM}</text>
  </docTitle>
  <navMap>
    {"\n    ".join(nav_points)}
  </navMap>
</ncx>"""

with open(os.path.join(BUILD_DIR, "OEBPS", "toc.ncx"), "w", encoding="utf-8") as f:
    f.write(toc_ncx)

# 6. Zip to EPUB
with zipfile.ZipFile(OUTPUT_EPUB, "w", zipfile.ZIP_DEFLATED) as z_out:
    z_out.write(os.path.join(BUILD_DIR, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, dirs, files in os.walk(BUILD_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BUILD_DIR).replace("\\", "/")
            if rel_path == "mimetype":
                continue
            z_out.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

print(f"🎉 SUKSES! EPUB Volume {VOL_NUM} berhasil dibuat di: {OUTPUT_EPUB} ({os.path.getsize(OUTPUT_EPUB)} bytes)")
