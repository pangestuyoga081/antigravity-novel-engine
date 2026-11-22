import os
import sys
import re
import zipfile
import html

CSS_CONTENT = """@charset "utf-8";
body {
    margin: 5% 8%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.8;
    color: #2b2b2b;
    background-color: #fafafa;
    text-align: justify;
}
h1, h2, h3 {
    text-align: center;
    color: #1a1a1a;
    margin-top: 1.5em;
    margin-bottom: 1em;
    font-weight: 700;
}
p {
    margin: 0.8em 0;
    text-indent: 1.5em;
}
p.dialogue {
    text-indent: 0;
    margin-left: 0.5em;
    font-weight: 500;
}
.speaker {
    font-weight: 700;
    color: #8b3a00;
}
.illustration-container {
    text-align: center;
    margin: 2em 0;
    page-break-inside: avoid;
}
.illustration-container img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.color-gallery {
    text-align: center;
    page-break-after: always;
}
.color-gallery img {
    max-width: 100%;
    max-height: 90vh;
    height: auto;
    margin: 1em auto;
}
"""

def text_to_html(body_text):
    paragraphs = body_text.split("\n")
    html_parts = []
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
            
        img_match = re.match(r"^\[\[ILUSTRASI:(.*?)\]\]$", p)
        if img_match:
            img_file = img_match.group(1)
            base_img = os.path.basename(img_file)
            html_parts.append(f'<div class="illustration-container"><img src="../images/{base_img}" alt="Ilustrasi" /></div>')
            continue
            
        spk_match = re.match(r"^([^:]+?):\s*\"(.*)\"$", p)
        if spk_match:
            spk = html.escape(spk_match.group(1))
            dial = html.escape(spk_match.group(2))
            html_parts.append(f'<p class="dialogue"><span class="speaker">{spk}:</span> &#8220;{dial}&#8221;</p>')
            continue
            
        esc_p = html.escape(p)
        esc_p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", esc_p)
        esc_p = re.sub(r"\*(.*?)\*", r"<em>\1</em>", esc_p)
        html_parts.append(f"<p>{esc_p}</p>")
        
    return "\n".join(html_parts)

def main():
    if len(sys.argv) < 4:
        print("Usage: python compile_epub_helper.py <txt_file> <src_epub> <out_epub>")
        sys.exit(1)

    txt_file = sys.argv[1]
    src_epub = sys.argv[2]
    out_epub = sys.argv[3]

    base_name = os.path.splitext(os.path.basename(src_epub))[0]
    base_dir = os.path.dirname(os.path.abspath(txt_file))
    with open(txt_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Extract all images from source epub or illustrations directory
    images_data = {}
    if os.path.isfile(src_epub) and src_epub.lower().endswith(".epub"):
        with zipfile.ZipFile(src_epub, "r") as z:
            for n in z.namelist():
                if n.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                    bn = os.path.basename(n)
                    images_data[bn] = z.read(n)

    # Selalu muat juga gambar dari folder illustrations terkait jika ada
    search_dirs = [
        os.path.join(base_dir, "illustrations", base_name),
        os.path.join(base_dir, "illustrations", base_name.replace(" ", "_"))
    ]
    for sdir in search_dirs:
        if os.path.isdir(sdir):
            for root, _, files in os.walk(sdir):
                for fn in files:
                    if fn.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                        if fn not in images_data:
                            with open(os.path.join(root, fn), "rb") as f:
                                images_data[fn] = f.read()

    print(f"🖼️ Ditemukan {len(images_data)} berkas gambar untuk EPUB.")

    # Parse chapters
    sections = re.split(r"(?=^###\s+)", full_text, flags=re.MULTILINE)
    chapters = []
    for s in sections:
        s = s.strip()
        if not s.startswith("###"):
            continue
        lines = s.split("\n")
        raw_title = lines[0].replace("###", "").strip()
        title = re.sub(r"^([=*\s]+)", "", raw_title).strip()
        body = "\n".join(lines[1:]).strip()
        # Clean separator lines
        body = re.sub(r"^={10,}\s*$", "", body, flags=re.MULTILINE)
        if len(body) > 100:
            chapters.append({"title": title, "body": body})

    print(f"📚 Terdeteksi {len(chapters)} bab cerita.")

    xhtml_files = []

    # Galeri Peta Pembuka (Khusus Hobbit jika ada file petanya)
    if "00003.jpeg" in images_data or "00021.jpeg" in images_data:
        maps_html = ['<div class="color-gallery"><h1>Peta &amp; Ilustrasi Middle-earth</h1>']
        if "00003.jpeg" in images_data:
            maps_html.append('<div class="illustration-container"><img src="../images/00003.jpeg" alt="Peta Thror" /><p><em>Peta Thror (Thror\'s Map) dengan Tulisan Rune Rahasia</em></p></div>')
        if "00021.jpeg" in images_data:
            maps_html.append('<div class="illustration-container"><img src="../images/00021.jpeg" alt="Peta Wilderland" /><p><em>Peta Wilayah Wilderland</em></p></div>')
        maps_html.append('</div>')
        maps_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Peta &amp; Panduan</title><link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/></head>
<body>{"".join(maps_html)}</body>
</html>"""
        xhtml_files.append(("maps.xhtml", "Peta Middle-earth", maps_xhtml))

    # Galeri Peta Pembuka Metro 2033
    if "map_full_moscow_metro.jpg" in images_data:
        metro_maps_html = [
            '<div class="color-gallery"><h1>Peta Jaringan Metro Moskwa (Tahun 2033)</h1>',
            '<div class="illustration-container"><img src="../images/map_full_moscow_metro.jpg" alt="Peta Lengkap Metro Moskwa" />',
            '<p><em>Peta Panduan Lengkap Jaringan Terowongan Metro Moskwa, Jalur Cincin Hanza, Stasiun Faksi, &amp; Wilayah Bahaya Mutan</em></p></div>',
            '</div>'
        ]
        metro_maps_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Peta Lengkap Metro Moskwa</title><link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/></head>
<body>{"".join(metro_maps_html)}</body>
</html>"""
        xhtml_files.append(("metro_map_full.xhtml", "Peta Lengkap Metro Moskwa", metro_maps_xhtml))

    # Bab Cerita
    for idx, ch in enumerate(chapters):
        fname = f"chapter_{idx+1:02d}.xhtml"
        title_esc = html.escape(ch["title"])
        body_html = text_to_html(ch["body"])

        doc_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{title_esc}</title><link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/></head>
<body><h2>{title_esc}</h2>{body_html}</body>
</html>"""
        xhtml_files.append((fname, ch["title"], doc_xhtml))

    # Tulis ke EPUB
    os.makedirs(os.path.dirname(out_epub), exist_ok=True)
    with zipfile.ZipFile(out_epub, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        z.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/css/stylesheet.css", CSS_CONTENT, compress_type=zipfile.ZIP_DEFLATED)

        manifest_images = []
        for bn, bdata in images_data.items():
            z.writestr(f"OEBPS/images/{bn}", bdata, compress_type=zipfile.ZIP_DEFLATED)
            item_id = f"img_{bn.replace('.', '_')}"
            media_type = "image/jpeg" if bn.lower().endswith((".jpeg", ".jpg")) else "image/png"
            manifest_images.append(f'<item id="{item_id}" href="images/{bn}" media-type="{media_type}"/>')

        manifest_items = []
        spine_items = []
        toc_ncx_items = []
        nav_html_items = []

        for idx, (fname, title, xhtml_body) in enumerate(xhtml_files):
            z.writestr(f"OEBPS/text/{fname}", xhtml_body, compress_type=zipfile.ZIP_DEFLATED)
            item_id = f"item_{idx+1}"
            manifest_items.append(f'<item id="{item_id}" href="text/{fname}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="{item_id}"/>')
            toc_ncx_items.append(f"""<navPoint id="np_{idx+1}" playOrder="{idx+1}">
                <navLabel><text>{html.escape(title)}</text></navLabel>
                <content src="text/{fname}"/>
            </navPoint>""")
            nav_html_items.append(f'<li><a href="text/{fname}">{html.escape(title)}</a></li>')

        # Metadata buku dinamis
        if "overlord" in base_name.lower():
            book_title = f"{base_name} (Terjemahan ID-Direct)"
            author = "Kugane Maruyama"
            book_uid = f"urn:uuid:overlord-{re.sub(r'[^a-zA-Z0-9]+', '-', base_name.lower())}"
        elif "hobbit" in base_name.lower():
            book_title = "The Hobbit (Terjemahan ID-Direct)"
            author = "J.R.R. Tolkien"
            book_uid = "urn:uuid:the-hobbit-id-direct-tolkien"
        elif "dune" in base_name.lower():
            book_title = "Dune (Terjemahan ID-Direct)"
            author = "Frank Herbert"
            book_uid = "urn:uuid:dune-id-direct-frank-herbert"
        elif "metro" in base_name.lower():
            book_title = "Metro 2033 (Terjemahan ID-Direct)"
            author = "Dmitry Glukhovsky"
            book_uid = "urn:uuid:metro-2033-id-direct-dmitry-glukhovsky"
        else:
            book_title = f"{base_name} (Terjemahan ID-Direct)"
            author = "Penulis"
            book_uid = f"urn:uuid:{re.sub(r'[^a-zA-Z0-9]+', '-', base_name.lower())}"

        # Cover image ID
        cover_id = "img_00001_jpeg" if "00001.jpeg" in images_data else (
            "img_page_001_Image1_jpg" if "page_001_Image1.jpg" in images_data else (
                manifest_images[0] if manifest_images else "item_1"
            )
        )
        if isinstance(cover_id, str) and cover_id.startswith('<item id="'):
            m_id = re.search(r'id="([^"]+)"', cover_id)
            if m_id:
                cover_id = m_id.group(1)

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="{book_uid}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{html.escape(book_title)}</text></docTitle>
    <navMap>{"".join(toc_ncx_items)}</navMap>
</ncx>"""
        z.writestr("OEBPS/toc.ncx", toc_ncx, compress_type=zipfile.ZIP_DEFLATED)

        nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Daftar Isi</title><link rel="stylesheet" type="text/css" href="css/stylesheet.css"/></head>
<body><nav epub:type="toc" id="toc"><h1>Daftar Isi</h1><ol>{"".join(nav_html_items)}</ol></nav></body>
</html>"""
        z.writestr("OEBPS/nav.xhtml", nav_xhtml, compress_type=zipfile.ZIP_DEFLATED)

        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{html.escape(book_title)}</dc:title>
        <dc:creator>{html.escape(author)}</dc:creator>
        <dc:language>id</dc:language>
        <dc:identifier id="BookID">{book_uid}</dc:identifier>
        <meta name="cover" content="{cover_id}"/>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
        <item id="css" href="css/stylesheet.css" media-type="text/css"/>
        {"".join(manifest_items)}
        {"".join(manifest_images)}
    </manifest>
    <spine toc="ncx">{"".join(spine_items)}</spine>
</package>"""
        z.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)

    sz_mb = os.path.getsize(out_epub) / (1024 * 1024)
    print(f"🎉 SUKSES! EPUB berilustrasi lengkap berhasil dibuat di: {out_epub} ({sz_mb:.2f} MB)")

if __name__ == "__main__":
    main()
