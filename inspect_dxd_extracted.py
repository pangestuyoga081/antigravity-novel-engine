import os
import glob
import fitz # PyMuPDF
import re

extracted_base = r"D:\JV\novel yoga\High School DxD\extracted"
vols = sorted([d for d in os.listdir(extracted_base) if d.startswith("Vol_")])

print(f"Total extracted volumes: {len(vols)}")

summary = []

for v in vols:
    vol_path = os.path.join(extracted_base, v)
    pdfs = glob.glob(os.path.join(vol_path, "**", "*.pdf"), recursive=True)
    epubs = glob.glob(os.path.join(vol_path, "**", "*.epub"), recursive=True)
    images = glob.glob(os.path.join(vol_path, "**", "*.jpg"), recursive=True) + \
             glob.glob(os.path.join(vol_path, "**", "*.jpeg"), recursive=True) + \
             glob.glob(os.path.join(vol_path, "**", "*.png"), recursive=True)
    
    pdf_info = ""
    if pdfs:
        doc = fitz.open(pdfs[0])
        pdf_info = f"PDF: {os.path.basename(pdfs[0])} ({len(doc)} hal)"
    elif epubs:
        pdf_info = f"EPUB: {os.path.basename(epubs[0])}"
    
    summary.append(f"{v}: {pdf_info} | {len(images)} gambar ilustrasi")

for s in summary:
    print(s)
