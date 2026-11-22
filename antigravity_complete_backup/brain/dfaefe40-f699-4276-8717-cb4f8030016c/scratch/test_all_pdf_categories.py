import os, pymupdf, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"

# Find all PDFs
all_pdfs = {}
vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith('.pdf'):
            for vk in sorted(vol_keys, key=lambda k: -len(k)): # Match 17.1 before 17
                pattern = rf"\bVolume\s+{re.escape(vk)}\b"
                if re.search(pattern, f, re.IGNORECASE):
                    if vk not in all_pdfs:
                        all_pdfs[vk] = os.path.join(root, f)

print(f"Total mapped PDFs: {len(all_pdfs)}/18")

for vk in vol_keys:
    pdf_path = all_pdfs.get(vk)
    if not pdf_path:
        print(f"Vol {vk}: NOT FOUND!")
        continue
    doc = pymupdf.open(pdf_path)
    
    xref_pages = {}
    for pno in range(len(doc)):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            if xref not in xref_pages:
                xref_pages[xref] = []
            xref_pages[xref].append(pno + 1)
            
    color_xrefs = []
    story_xrefs = []
    
    for xref, pages in xref_pages.items():
        base_img = doc.extract_image(xref)
        w, h = base_img["width"], base_img["height"]
        size_kb = len(base_img["image"]) / 1024
        if w > 300 and h > 300 and size_kb > 30:
            true_page = max(pages)
            min_page = min(pages)
            # If all occurrences are in the first 10-12 pages and not in preview thumbnails
            if len(pages) == 1 and true_page <= 11:
                color_xrefs.append((xref, true_page))
            elif len(pages) > 1 and min_page <= 25 and true_page > 25:
                story_xrefs.append((xref, true_page))
            elif len(pages) == 1 and true_page > 11:
                story_xrefs.append((xref, true_page))
            else:
                color_xrefs.append((xref, true_page))
                
    color_xrefs.sort(key=lambda x: x[1])
    story_xrefs.sort(key=lambda x: x[1])
    print(f"Vol {vk} ({os.path.basename(pdf_path)[:30]}...): Total {len(color_xrefs)} color, {len(story_xrefs)} story illustrations. Story pages: {[x[1] for x in story_xrefs]}")
