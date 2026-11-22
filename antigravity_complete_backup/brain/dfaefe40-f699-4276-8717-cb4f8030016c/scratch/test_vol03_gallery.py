import pymupdf

pdf_03 = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1\Konosuba Volume 03 [Afterscarlet]\Konosuba Volume 03 [Afterscarlet].pdf"
doc = pymupdf.open(pdf_03)

for p in range(0, 25):
    imgs = doc[p].get_images(full=True)
    if imgs:
        xref = imgs[0][0]
        b = doc.extract_image(xref)
        print(f"Page {p+1}: xref={xref}, size={b['width']}x{b['height']}, ext={b['ext']}, colorspace={b['colorspace']}")
