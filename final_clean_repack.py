import os
import zipfile
import re

TXT_PATH = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert (Terjemahan ID-Direct).txt"
WORK_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
OEBPS_DIR = os.path.join(WORK_DIR, "OEBPS")
OUTPUT_EPUB = r"D:\JV\novel yoga\epubs\Breeder_Mage_1_-_Marc_Robert (Illustrated ID-Direct).epub"

with open(TXT_PATH, "r", encoding="utf-8") as f:
    txt = f.read()

# Fix lingering artifacts
txt = txt.replace("aku gue", "gue").replace("Aku gue", "Gue")
txt = txt.replace("mendengus sinis", "senyum sinis").replace("Mendengus sinis", "Senyum sinis")
txt = txt.replace("mendengus kesel", "ngedengus kesel").replace("Mendengus kesel", "Ngedengus kesel")
txt = txt.replace("mendengus galak", "ngedengus galak").replace("Mendengus galak", "Ngedengus galak")

with open(TXT_PATH, "w", encoding="utf-8") as f:
    f.write(txt)

# Re-apply to all XHTML files
for root, dirs, files in os.walk(OEBPS_DIR):
    for file in files:
        if file.endswith(".xhtml"):
            fpath = os.path.join(root, file)
            with open(fpath, "r", encoding="utf-8") as f:
                c = f.read()
            c = c.replace("aku gue", "gue").replace("Aku gue", "Gue")
            c = c.replace("mendengus sinis", "senyum sinis").replace("Mendengus sinis", "Senyum sinis")
            c = c.replace("mendengus kesel", "ngedengus kesel").replace("Mendengus kesel", "Ngedengus kesel")
            c = c.replace("mendengus galak", "ngedengus galak").replace("Mendengus galak", "Ngedengus galak")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(c)

# Re-pack EPUB
with zipfile.ZipFile(OUTPUT_EPUB, "w", zipfile.ZIP_DEFLATED) as z_out:
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

print("Cleaned up lingering words and re-packaged EPUB successfully!")
