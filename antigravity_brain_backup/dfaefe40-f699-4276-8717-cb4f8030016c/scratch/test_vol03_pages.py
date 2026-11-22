import pymupdf

pdf_03 = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1\Konosuba Volume 03 [Afterscarlet]\Konosuba Volume 03 [Afterscarlet].pdf"
doc = pymupdf.open(pdf_03)

for p in range(10, 26):
    txt = doc[p].get_text("text").strip()
    imgs = doc[p].get_images(full=True)
    print(f"Page {p+1}: {len(imgs)} imgs. Text preview: {repr(txt[:60])}")
