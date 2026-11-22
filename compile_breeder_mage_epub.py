import os
import zipfile
import re
import json

WORK_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
OEBPS_DIR = os.path.join(WORK_DIR, "OEBPS")
CACHE_FILE = r"D:\JV\novel yoga\breeder_mage_cache.json"
OUTPUT_EPUB = r"D:\JV\novel yoga\epubs\Breeder_Mage_1_-_Marc_Robert (Illustrated ID-Direct).epub"
os.makedirs(r"D:\JV\novel yoga\epubs", exist_ok=True)

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cache = json.load(f)

def clean_xml(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&#8220;").replace('"', "&#8221;")
    return text

# Mapping parts
target_parts = ["part0005.xhtml"]
for i in range(9, 34):
    target_parts.append(f"part{i:04d}.xhtml")

for part in target_parts:
    part_path = os.path.join(OEBPS_DIR, part)
    if not os.path.exists(part_path):
        continue
    
    # gather all chunks
    chunks = []
    c_idx = 0
    while True:
        k = f"{part}_chunk_{c_idx}"
        if k in cache:
            chunks.append(cache[k])
            c_idx += 1
        else:
            break
            
    if not chunks:
        continue
        
    full_part_text = "\n\n".join(chunks)
    
    # replace banned words
    full_part_text = full_part_text.replace("menimpali", "menyahut").replace("Menimpali", "Menyahut")
    full_part_text = full_part_text.replace("mendengus", "menghela napas kesal").replace("Mendengus", "Menghela napas kesal")
    
    # Format to clean XHTML paragraphs
    paragraphs = [p.strip() for p in full_part_text.split("\n\n") if p.strip()]
    
    html_paragraphs = []
    for p in paragraphs:
        if p.startswith("Bab ") or p.startswith("Chapter ") or p == "Apa Itu Other Earth?":
            html_paragraphs.append(f'<h1 class="chapter-title">{clean_xml(p)}</h1>')
        elif ":" in p and any(name in p for name in ["Derek Shaw:", "Ry'lah:", "Ischi:", "Kel:", "Celeen:", "Jeff Shaw:"]):
            # Dialog styling
            html_paragraphs.append(f'<p class="dialogue"><b>{clean_xml(p)}</b></p>')
        else:
            # Check single line breaks inside paragraph
            sub_lines = [clean_xml(l) for l in p.split("\n") if l.strip()]
            html_paragraphs.append(f'<p>{"<br/>".join(sub_lines)}</p>')
            
    body_content = "\n  ".join(html_paragraphs)
    
    new_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="id">
<head>
  <title>Breeder Mage</title>
  <style>
    body {{ font-family: "Georgia", "Times New Roman", serif; line-height: 1.6; margin: 5%; }}
    h1.chapter-title {{ text-align: center; margin-top: 1.5em; margin-bottom: 1.5em; font-size: 1.6em; color: #8b0000; }}
    p {{ margin-bottom: 0.9em; text-indent: 1.2em; }}
    p.dialogue {{ text-indent: 0; margin-left: 0.5em; margin-bottom: 0.8em; color: #111; }}
    b {{ color: #003366; }}
  </style>
</head>
<body>
  {body_content}
</body>
</html>"""

    with open(part_path, "w", encoding="utf-8") as f:
        f.write(new_xhtml)

print("Updated all XHTML files in OEBPS!")

# Now package the EPUB back
with zipfile.ZipFile(OUTPUT_EPUB, "w", zipfile.ZIP_DEFLATED) as z_out:
    # write mimetype first without compression
    mimetype_path = os.path.join(WORK_DIR, "mimetype")
    if os.path.exists(mimetype_path):
        z_out.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
        
    for root, dirs, files in os.walk(WORK_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, WORK_DIR).replace("\\", "/")
            if rel_path == "mimetype":
                continue
            z_out.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

print(f"Successfully generated EPUB at: {OUTPUT_EPUB} ({os.path.getsize(OUTPUT_EPUB)} bytes)")
