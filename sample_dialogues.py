import zipfile
import re

epub_path = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert.epub"
with zipfile.ZipFile(epub_path, "r") as z:
    for name in ["OEBPS/part0009.xhtml", "OEBPS/part0010.xhtml"]:
        raw = z.read(name).decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", "\n", raw)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print(f"=== {name} ===")
        for l in lines:
            if "“" in l or '"' in l:
                print("  ", l[:120])
