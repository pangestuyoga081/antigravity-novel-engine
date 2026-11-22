import os
import re
import json
import zipfile
import html
import glob
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pymupdf

BASE_DIR = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
COMBINED_TXT = os.path.join(BASE_DIR, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")
EPUB_OUT_DIR = os.path.join(BASE_DIR, "epubs")
ILLUST_CACHE_ROOT = os.path.join(BASE_DIR, "illustrations")

os.makedirs(EPUB_OUT_DIR, exist_ok=True)
os.makedirs(ILLUST_CACHE_ROOT, exist_ok=True)

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
    color: #0d47a1;
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
            html_parts.append(f'<div class="illustration-container"><img src="../images/{img_file}" alt="Ilustrasi" /></div>')
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

def find_pdf_for_volume(vol_str):
    all_pdfs = []
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                all_pdfs.append(os.path.join(root, f))
                
    pattern = rf"\bVolume\s+{re.escape(vol_str)}\b"
    for p in all_pdfs:
        if re.search(pattern, os.path.basename(p), re.IGNORECASE):
            return p
    return None

def process_single_volume(vol_key, vol_raw_text):
    vol_str = f"Volume {vol_key}"
    print(f"🚀 Memproses Konosuba {vol_str}...")
    
    pdf_path = find_pdf_for_volume(vol_key)
    if not pdf_path:
        print(f"❌ PDF untuk {vol_str} tidak ditemukan!")
        return False

    vol_img_dir = os.path.join(ILLUST_CACHE_ROOT, f"Konosuba_Vol{vol_key}")
    os.makedirs(vol_img_dir, exist_ok=True)
    
    # 1. Ekstraksi Gambar dari PDF
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    
    xref_pages = {}
    for pno in range(total_pages):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            if xref not in xref_pages:
                xref_pages[xref] = []
            xref_pages[xref].append(pno + 1)
            
    images_meta = []
    for xref, pages in xref_pages.items():
        base_img = doc.extract_image(xref)
        w, h = base_img["width"], base_img["height"]
        size_kb = len(base_img["image"]) / 1024
        ext = base_img["ext"]
        
        if w > 300 and h > 300 and size_kb > 30:
            true_page = max(pages)
            min_page = min(pages)
            
            # Tentukan apakah halaman warna di depan
            # Di volume 03, 05, 06, 11 galeri depan sampai ~page 25/31
            # Di volume lain galeri depan sampai ~page 12
            # Jika hanya muncul 1x di halaman <= 12 atau di preview thumbnail
            is_color = False
            if vol_key in ["03", "05", "06", "11"]:
                if true_page <= 25 and len(pages) == 1:
                    is_color = True
            else:
                if true_page <= 12 and len(pages) == 1:
                    is_color = True
                    
            img_filename = f"konosuba_vol{vol_key}_p{true_page:03d}_{xref}.{ext}"
            img_save_path = os.path.join(vol_img_dir, img_filename)
            
            if not os.path.exists(img_save_path):
                with open(img_save_path, "wb") as f:
                    f.write(base_img["image"])
                    
            # Context teks sekitar gambar untuk matching
            prev_text = ""
            p_idx = true_page - 1
            if p_idx > 0:
                pt = doc[p_idx - 1].get_text("text").strip().split("\n")
                prev_text = " ".join([l.strip() for l in pt if l.strip() and not re.search(r"konosuba|ruidrive|afterscarlet|volume", l, re.IGNORECASE)][-4:])
                
            next_text = ""
            if p_idx + 1 < total_pages:
                nt = doc[p_idx + 1].get_text("text").strip().split("\n")
                next_text = " ".join([l.strip() for l in nt if l.strip() and not re.search(r"konosuba|ruidrive|afterscarlet|volume", l, re.IGNORECASE)][:4])
                
            images_meta.append({
                "xref": xref,
                "page": true_page,
                "filename": img_filename,
                "is_color": is_color,
                "prev_text": prev_text,
                "next_text": next_text
            })

    images_meta.sort(key=lambda m: m["page"])

    # 2. Parse Bab dari Teks Volume
    raw_sections = re.split(r"(?=^###\s+)", vol_raw_text, flags=re.MULTILINE)
    chapters = []
    
    for sec in raw_sections:
        sec = sec.strip()
        if not sec.startswith("###"):
            continue
        lines = sec.split("\n")
        title_line = re.sub(rf"^###\s+(?:VOLUME\s+{re.escape(vol_key)}\s*[-:]*\s*)?", "", lines[0], flags=re.IGNORECASE).strip()
        body = "\n".join(lines[1:]).strip()
        if len(body) > 50:
            chapters.append({
                "title": title_line,
                "body": body
            })
            
    if not chapters:
        chapters = [{"title": f"Volume {vol_key}", "body": vol_raw_text}]

    # 3. Penyelipan Ilustrasi Hitam Putih / Dalam Cerita
    bw_images = [m for m in images_meta if not m["is_color"]]
    color_images = [m["filename"] for m in images_meta if m["is_color"]]
    
    stopwords = {"yang", "dengan", "untuk", "dalam", "tidak", "adalah", "pada", "dari", "ruidrive", "volume", "konosuba", "afterscarlet", "juga", "akan", "bisa", "mereka", "kami", "kita", "kamu", "saya", "tapi", "oleh", "saat", "lalu"}
    
    for bw in bw_images:
        context_words = re.findall(r"\b[A-Za-zÀ-ÿ]{4,}\b", f"{bw['prev_text']} {bw['next_text']}")
        keywords = [w for w in context_words if w.lower() not in stopwords]
        
        best_ch = None
        best_score = 0
        best_para_idx = -1
        
        for ch in chapters:
            paras = ch["body"].split("\n")
            for p_idx, p in enumerate(paras):
                p_s = p.strip()
                if not p_s or p_s.startswith("[[ILUSTRASI"):
                    continue
                score = sum(1 for kw in keywords if kw.lower() in p_s.lower())
                if score > best_score:
                    best_score = score
                    best_ch = ch
                    best_para_idx = p_idx
                    
        if best_ch and best_score >= 2:
            paras = best_ch["body"].split("\n")
            paras.insert(best_para_idx + 1, f"[[ILUSTRASI:{bw['filename']}]]")
            best_ch["body"] = "\n".join(paras)
        else:
            # Fallback relatif: masukkan berdasarkan estimasi posisi halaman
            est_ch_idx = min(len(chapters) - 1, int((bw["page"] / total_pages) * len(chapters)))
            target_ch = chapters[est_ch_idx]
            paras = target_ch["body"].split("\n")
            insert_pos = int(len(paras) * 0.5)
            paras.insert(insert_pos, f"[[ILUSTRASI:{bw['filename']}]]")
            target_ch["body"] = "\n".join(paras)

    # 4. Susun EPUB
    epub_name = f"Kono Subarashii Sekai ni Shukufuku wo! - Volume {vol_key} (Illustrated).epub"
    if vol_key == "17.1":
        epub_name = "Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1 (Illustrated).epub"
    epub_out = os.path.join(EPUB_OUT_DIR, epub_name)
    
    xhtml_files = []
    
    # Galeri Warna
    if color_images:
        color_html_parts = ['<div class="color-gallery"><h1>Ilustrasi Berwarna</h1>']
        for c_img in color_images:
            color_html_parts.append(f'<div class="illustration-container"><img src="../images/{c_img}" alt="Ilustrasi Warna" /></div>')
        color_html_parts.append('</div>')
        color_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<title>Galeri Ilustrasi Berwarna</title>
<link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/>
</head>
<body>
{"".join(color_html_parts)}
</body>
</html>"""
        xhtml_files.append(("gallery.xhtml", "Galeri Ilustrasi Berwarna", color_xhtml))

    # Bab Cerita
    for idx, ch in enumerate(chapters):
        fname = f"chapter_{idx+1:02d}.xhtml"
        title_esc = html.escape(ch["title"])
        body_html = text_to_html(ch["body"])
        
        doc_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<title>{title_esc}</title>
<link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/>
</head>
<body>
<h2>{title_esc}</h2>
{body_html}
</body>
</html>"""
        xhtml_files.append((fname, ch["title"], doc_xhtml))

    # Tulis ke berkas ZIP EPUB
    with zipfile.ZipFile(epub_out, "w") as z:
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
        for img_m in images_meta:
            fn = img_m["filename"]
            fp = os.path.join(vol_img_dir, fn)
            if os.path.exists(fp):
                with open(fp, "rb") as imf:
                    z.writestr(f"OEBPS/images/{fn}", imf.read(), compress_type=zipfile.ZIP_DEFLATED)
                item_id = f"img_{fn.replace('.', '_')}"
                media_type = "image/jpeg" if fn.endswith((".jpeg", ".jpg")) else "image/png"
                manifest_images.append(f'<item id="{item_id}" href="images/{fn}" media-type="{media_type}"/>')
                
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
            
        book_title = f"Kono Subarashii Sekai ni Shukufuku wo! - Volume {vol_key}"
        if vol_key == "17.1":
            book_title = "Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
            
        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:konosuba-vol{vol_key.replace('.', '_')}-id-direct"/>
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
        
        cover_id = f"img_{color_images[0].replace('.', '_')}" if color_images else "item_1"
        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{html.escape(book_title)}</dc:title>
        <dc:creator>Akatsuki Natsume</dc:creator>
        <dc:contributor>Kurone Mishima</dc:contributor>
        <dc:language>id</dc:language>
        <dc:identifier id="BookID">urn:uuid:konosuba-vol{vol_key.replace('.', '_')}-id-direct</dc:identifier>
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
        
    size_mb = os.path.getsize(epub_out) / (1024 * 1024)
    print(f"✅ Selesai Konosuba {vol_str}! File: {os.path.basename(epub_out)} ({size_mb:.2f} MB, {len(images_meta)} ilustrasi, {len(chapters)} bab)")
    return True

def main():
    print("==================================================================")
    print("⚡ BATCH BUILDER: SEMUA VOLUME KONOSUBA 01-17 + 17.1 (18 EPUB)")
    print("==================================================================")
    
    with open(COMBINED_TXT, "r", encoding="utf-8") as f:
        full_text = f.read()

    vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

    vol_starts = {}
    for vk in vol_keys:
        m = re.search(rf"^###\s+VOLUME\s+{re.escape(vk)}\b", full_text, re.MULTILINE | re.IGNORECASE)
        if m:
            vol_starts[vk] = m.start()

    vol_slices = []
    for i, vk in enumerate(vol_keys):
        start = vol_starts[vk]
        end = vol_starts[vol_keys[i+1]] if i+1 < len(vol_keys) else len(full_text)
        slice_text = full_text[start:end]
        vol_slices.append((vk, slice_text))

    print(f"Siap membangun {len(vol_slices)} volume secara paralel!")
    t0 = time.time()
    
    # Jalankan batch paralel dengan 6 worker
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_single_volume, vk, txt): vk for vk, txt in vol_slices}
        for fut in as_completed(futures):
            vk = futures[fut]
            try:
                fut.result()
            except Exception as e:
                print(f"❌ Error pada Volume {vk}: {e}")

    total_time = time.time() - t0
    print("\n==================================================================")
    print(f"🎉 SEMUA 18 VOLUME EPUB SUKSES DIBUAT DALAM {total_time:.1f} DETIK!")
    print(f"📁 Folder Output: {EPUB_OUT_DIR}")
    print("==================================================================")

if __name__ == "__main__":
    main()
