import os, pymupdf

pdf_17 = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1\Konosuba Volume 17  Memberikan berkah kepada petualang ini! [Afterscarlet]\Konosuba Volume 17  Memberikan berkah kepada petualang ini! [Afterscarlet].pdf"

doc = pymupdf.open(pdf_17)
print(f"Vol 17 pages: {len(doc)}")
xref_pages = {}
for pno in range(len(doc)):
    for img in doc[pno].get_images(full=True):
        xref = img[0]
        if xref not in xref_pages:
            xref_pages[xref] = []
        xref_pages[xref].append(pno + 1)

print(f"Total unique xrefs: {len(xref_pages)}")
for xref, pages in sorted(xref_pages.items(), key=lambda it: max(it[1])):
    b = doc.extract_image(xref)
    if b["width"] > 300 and b["height"] > 300:
        print(f"  xref {xref}: pages={pages}, size={b['width']}x{b['height']}")
