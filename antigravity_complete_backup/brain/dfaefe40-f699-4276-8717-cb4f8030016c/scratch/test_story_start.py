import os, pymupdf, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"

all_pdfs = {}
vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith('.pdf'):
            for vk in sorted(vol_keys, key=lambda k: -len(k)):
                if re.search(rf"\bVolume\s+{re.escape(vk)}\b", f, re.IGNORECASE):
                    if vk not in all_pdfs:
                        all_pdfs[vk] = os.path.join(root, f)

for vk in vol_keys:
    doc = pymupdf.open(all_pdfs[vk])
    # Find the first page with significant text (> 100 characters)
    story_start_page = -1
    for pno in range(min(50, len(doc))):
        txt = doc[pno].get_text("text").strip()
        # Clean lines that just say PDF Konosuba or watermark
        lines = [l.strip() for l in txt.split("\n") if l.strip() and not re.search(r"konosuba|ruidrive|afterscarlet|volume", l, re.IGNORECASE)]
        cleaned = " ".join(lines)
        if len(cleaned) > 80:
            story_start_page = pno + 1
            break
            
    # Count images before story start vs after story start
    gallery_xrefs = set()
    story_img_xrefs = set()
    
    for pno in range(len(doc)):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            b = doc.extract_image(xref)
            if b["width"] > 300 and b["height"] > 300 and len(b["image"]) > 30*1024:
                if (pno + 1) < story_start_page:
                    gallery_xrefs.add(xref)
                else:
                    story_img_xrefs.add(xref)
                    
    # Note: if an image in gallery is also in story, story takes precedence for inline, or it's a preview
    pure_gallery = gallery_xrefs - story_img_xrefs
    shared = gallery_xrefs & story_img_xrefs
    print(f"Vol {vk}: Story starts page {story_start_page}. Pure Gallery: {len(pure_gallery)}, Shared: {len(shared)}, Story-only: {len(story_img_xrefs - gallery_xrefs)} (Total Story Imgs: {len(story_img_xrefs)})")
