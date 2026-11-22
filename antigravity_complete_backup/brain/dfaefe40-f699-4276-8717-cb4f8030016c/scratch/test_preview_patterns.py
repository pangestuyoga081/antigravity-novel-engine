import os, pymupdf, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

all_pdfs = {}
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith('.pdf'):
            for vk in sorted(vol_keys, key=lambda k: -len(k)):
                if re.search(rf"\bVolume\s+{re.escape(vk)}\b", f, re.IGNORECASE):
                    if vk not in all_pdfs:
                        all_pdfs[vk] = os.path.join(root, f)

for vk in vol_keys:
    doc = pymupdf.open(all_pdfs[vk])
    xref_pages = {}
    for pno in range(len(doc)):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            if xref not in xref_pages:
                xref_pages[xref] = []
            xref_pages[xref].append(pno + 1)
            
    filtered = {}
    for xref, pages in xref_pages.items():
        b = doc.extract_image(xref)
        if b["width"] > 300 and b["height"] > 300 and len(b["image"]) > 30*1024:
            filtered[xref] = pages
            
    # Check multi-page xrefs vs single-page xrefs
    multi_page = {x: p for x, p in filtered.items() if len(p) > 1}
    single_page = {x: p for x, p in filtered.items() if len(p) == 1}
    
    print(f"Vol {vk} ({len(doc)} pages): {len(filtered)} total imgs | {len(multi_page)} multi-page (preview+story), {len(single_page)} single-page")
    # Show single-page pages
    single_pages = sorted([p[0] for p in single_page.values()])
    print(f"   Single-page at: {single_pages}")
