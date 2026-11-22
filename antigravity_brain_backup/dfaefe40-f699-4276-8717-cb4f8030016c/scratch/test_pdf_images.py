import os, pymupdf

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"

# Find all PDFs
all_pdfs = {}
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith('.pdf'):
            for vk in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']:
                if f"volume {vk}".lower() in f.lower():
                    all_pdfs[vk] = os.path.join(root, f)

print(f"Mapped {len(all_pdfs)} PDFs.")

# Test inspecting a few PDFs
for test_vk in ['01', '02', '17', '17.1']:
    pdf_path = all_pdfs[test_vk]
    doc = pymupdf.open(pdf_path)
    print(f"\n--- Checking Vol {test_vk}: {os.path.basename(pdf_path)} ({len(doc)} pages) ---")
    
    xref_pages = {}
    for pno in range(len(doc)):
        page = doc[pno]
        for img in page.get_images(full=True):
            xref = img[0]
            if xref not in xref_pages:
                xref_pages[xref] = []
            xref_pages[xref].append(pno + 1)
            
    print(f"Total unique image xrefs: {len(xref_pages)}")
    
    # Check dimensions of images
    large_images = []
    for xref, pages in xref_pages.items():
        base_img = doc.extract_image(xref)
        w, h = base_img["width"], base_img["height"]
        size_kb = len(base_img["image"]) / 1024
        ext = base_img["ext"]
        if w > 300 and h > 300 and size_kb > 30:
            large_images.append((xref, min(pages), max(pages), len(pages), w, h, size_kb, ext))
            
    print(f"Total large illustration xrefs: {len(large_images)}")
    for x in sorted(large_images, key=lambda it: it[2]):
        print(f"  xref {x[0]}: min_p={x[1]}, max_p={x[2]}, count={x[3]}, size={x[4]}x{x[5]} ({x[6]:.1f} KB, {x[7]})")
