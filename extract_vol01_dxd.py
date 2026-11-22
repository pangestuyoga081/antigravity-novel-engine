import os
import glob
import fitz

VOL_DIR = r"D:\JV\novel yoga\High School DxD\extracted\Vol_01"
PDF_PATH = r"D:\JV\novel yoga\High School DxD\extracted\Vol_01\High School Dxd - Volume 01 [RuiDrive]\High School Dxd - Volume 01 [RuiDrive].pdf"
IMG_DIR = r"D:\JV\novel yoga\High School DxD\extracted\Vol_01\High School Dxd - Volume 01 [RuiDrive]\Image"
OUTPUT_TXT = r"D:\JV\novel yoga\High School DxD\High_School_DxD_Volume_01_Raw_Source.txt"

# Mapping image page to image filename
# Color images on front pages 5-15:
# Cover: DxDLN01.jpg
# Color inserts: HSDxD_vol_01_004.jpg, HSDxD_vol_01_005-006.jpg, HSDxD_vol_01_007.jpg
# Page 28: HSDxD_vol_01_021.jpg (Yuuma reveal wings)
# Page 73: HSDxD_vol_01_057.jpg (Rias naked in bed)
# Page 96: HSDxD_vol_01_075.jpg (Koneko eating snack)
# Page 189: HSDxD_vol_01_137.jpg (Asia Argento intro)
# Page 216: HSDxD_vol_01_161.jpg (Akeno lightning attack)
# Page 296: HSDxD_vol_01_238.jpg (Freed battle / Koneko throwing bench)
# Page 352: HSDxD_vol_01_286.jpg (Rias Evil Piece for Asia)

IMAGE_MAP = {
    28: "HSDxD_vol_01_021.jpg",
    73: "HSDxD_vol_01_057.jpg",
    96: "HSDxD_vol_01_075.jpg",
    189: "HSDxD_vol_01_137.jpg",
    216: "HSDxD_vol_01_161.jpg",
    296: "HSDxD_vol_01_238.jpg",
    352: "HSDxD_vol_01_286.jpg"
}

doc = fitz.open(PDF_PATH)
lines_out = []

# Front color illustrations tag
lines_out.append("[[ILUSTRASI:DxDLN01.jpg]]")
lines_out.append("[[ILUSTRASI:HSDxD_vol_01_004.jpg]]")
lines_out.append("[[ILUSTRASI:HSDxD_vol_01_005-006.jpg]]")
lines_out.append("[[ILUSTRASI:HSDxD_vol_01_007.jpg]]\n")

for p_num in range(15, len(doc)): # start from page 16 (index 15)
    page_idx = p_num + 1
    
    # Check if this page is an illustration page
    if page_idx in IMAGE_MAP:
        lines_out.append(f"\n[[ILUSTRASI:{IMAGE_MAP[page_idx]}]]\n")
        
    page_text = doc[p_num].get_text()
    raw_lines = page_text.split('\n')
    
    cleaned_page_lines = []
    for l in raw_lines:
        l_str = l.strip()
        if not l_str:
            continue
        if "PDF HSDXD" in l_str or "https://afterscarlet" in l_str:
            continue
        cleaned_page_lines.append(l_str)
        
    if cleaned_page_lines:
        lines_out.append("\n".join(cleaned_page_lines))

full_raw_text = "\n\n".join(lines_out)
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    f.write(full_raw_text)

print(f"Extracted Vol 1 to: {OUTPUT_TXT} ({len(full_raw_text)} chars)")
