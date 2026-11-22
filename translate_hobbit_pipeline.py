import os
import re
import json
import zipfile
import html
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPUB_SRC = os.path.join(BASE_DIR, "The Hobbit - Tolkien, J. R. R._5022.epub")
OUT_TXT = os.path.join(BASE_DIR, "The Hobbit - J.R.R. Tolkien (Terjemahan ID-Direct).txt")
EPUB_OUT = os.path.join(BASE_DIR, "epubs", "The Hobbit - J.R.R. Tolkien (Illustrated ID-Gaul).epub")
CACHE_DIR = os.path.join(BASE_DIR, ".hobbit_chunks_cache")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "hobbit_checkpoint.json")
ILLUST_DIR = os.path.join(BASE_DIR, "illustrations", "The_Hobbit")

CONFIG = {
    "proxy_url": "http://127.0.0.1:20128/v1/chat/completions",
    "api_key": "sk-2c1573f206deb3a0-ryos2n-4198badd",
    "model": "ag/gemini-3.8-flash",
    "max_chunk_chars": 5800,
    "concurrency": 3
}

os.makedirs(os.path.dirname(EPUB_OUT), exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(ILLUST_DIR, exist_ok=True)

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

def clean_watermarks(text):
    return text.replace("The Hobbit", "").strip()

def build_prompt(chunk_text):
    explanation_rule = """- Penjelasan Istilah Asing / Fantasi / Dunia Cerita:
  Setiap istilah asing, istilah teknis, nama ras, senjata legendaris, atau konsep yang berpotensi tidak dipahami pembaca dalam narasi maupun dialog harus disertai penjelasan singkat dalam bahasa Indonesia dengan format konsisten: Istilah (arti atau penjelasan sederhana). Contoh: Hobbit (ras manusia kerdil bertelapak kaki tebal berbulu lebat yang anti ribet dan hobi rebahan di lubang tanah super nyaman), Porthole (jendela bundar di kabin kapal), Dwarf (ras kurcaci kekar pemahat batu dan petarung tangguh), Mithril (logam perak legendaris yang ringan tapi lebih keras dari baja), Runes (huruf alfabet kuno berkekuatan magis), Smaug (naga merah raksasa rakus yang merampas gunung harta kaum kurcaci).
  Terapkan secara alami sesuai konteks cerita, tanpa merusak alur, suasana, atau dialog karakter. Jelaskan hanya istilah yang benar-benar berpotensi membingungkan, utamakan saat pertama kali muncul, dan hindari pengulangan penjelasan yang sama. Gunakan bahasa sehari-hari yang lugas, bukan penjelasan formal seperti kamus."""

    return f"""Tuliskan seluruh cerita dalam Bahasa Indonesia yang luwes, santai/gaul, hidup, dan to-the-point — setara dengan novel fantasi/petualangan modern terjemahan resmi, webtoon fantasi, atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, ekspresif, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & Transparan). Langsung sampaikan situasi, suasana, dan isi pikiran karakter secara tegas.
- Nol Metafora & Anti-Puitis. Dilarang keras menggunakan kalimat berbunga-bunga lebay.
- Slang & Percakapan Santai (gue/lu atau gaya bahasa percakapan sehari-hari yang luwes dan dinamis).
- Format dialog: Nama: "..."
- PENTING: Pertahankan tag penanda seperti [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
{explanation_rule}

Naskah Mentah:
{chunk_text}"""

def call_llm(chunk_text, retry=3):
    prompt = build_prompt(chunk_text)
    payload = json.dumps({
        "model": CONFIG["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": False
    }).encode("utf-8")

    for attempt in range(1, retry + 1):
        try:
            req = urllib.request.Request(
                CONFIG["proxy_url"],
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {CONFIG['api_key']}"
                }
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                content = res["choices"][0]["message"]["content"].strip()
                if len(content) > 50:
                    return content
        except Exception as e:
            print(f"      ⚠️ Percobaan {attempt} gagal: {e}")
            time.sleep(2 * attempt)
            
    raise RuntimeError("Gagal memanggil LLM setelah beberapa kali mencoba.")

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
            # Ambil basename file
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

def extract_chapters_and_images():
    print("📦 Mengekstrak bab dan ilustrasi dari file sumber EPUB...")
    chapters = []
    images = {}
    
    with zipfile.ZipFile(EPUB_SRC, "r") as z:
        # 1. Simpan semua gambar
        for n in z.namelist():
            if n.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                bn = os.path.basename(n)
                bdata = z.read(n)
                save_path = os.path.join(ILLUST_DIR, bn)
                with open(save_path, "wb") as f:
                    f.write(bdata)
                images[bn] = save_path

        print(f"   Terekstrak {len(images)} gambar ke {ILLUST_DIR}")

        # 2. Ekstrak 19 bab (part0006.html s.d. part0024.html)
        chapter_titles = [
            "Chapter I: Pesta Dadakan Tanpa Undangan",
            "Chapter II: Daging Panggang Para Troll",
            "Chapter III: Istirahat Sejenak di Rivendell",
            "Chapter IV: Menembus Badai dan Sarang Goblin",
            "Chapter V: Teka-Teki di Balik Kegelapan",
            "Chapter VI: Lolos dari Wajan, Masuk ke Kobaran Api",
            "Chapter VII: Pondok Aneh Sang Manusia Beruang",
            "Chapter VIII: Lalat dan Laba-Laba Raksasa Mirkwood",
            "Chapter IX: Melarikan Diri dalam Tong Kayu",
            "Chapter X: Sambutan Hangat Kota Danau",
            "Chapter XI: Di Depan Ambang Pintu Rahasia",
            "Chapter XII: Informasi Rahasia dari Sarang Naga",
            "Chapter XIII: Saat Naga Tak Ada di Rumah",
            "Chapter XIV: Kobaran Api dan Hujan Panah",
            "Chapter XV: Awan Gelap Peperangan Mulai Berkumpul",
            "Chapter XVI: Pencuri yang Menyelinap di Tengah Malam",
            "Chapter XVII: Badai Pertempuran Meletus",
            "Chapter XVIII: Perjalanan Pulang Menuju Barat",
            "Chapter XIX: Babak Terakhir: Kembali ke Bag-End"
        ]

        for idx, i in enumerate(range(6, 25)):
            fname = f"text/part{i:04d}.html"
            raw = z.read(fname).decode("utf-8", errors="ignore")
            
            # Ganti tag <img> dengan penanda [[ILUSTRASI:filename]]
            def replace_img(match):
                src = match.group(1)
                bn = os.path.basename(src)
                return f"\n\n[[ILUSTRASI:{bn}]]\n\n"
            
            raw_marked = re.sub(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>', replace_img, raw, flags=re.IGNORECASE)
            
            # Bersihkan tag HTML lainnya
            clean = re.sub(r'<div[^>]*>', '\n', raw_marked)
            clean = re.sub(r'</div[^>]*>', '\n', clean)
            clean = re.sub(r'<p[^>]*>', '\n', clean)
            clean = re.sub(r'</p[^>]*>', '\n', clean)
            clean = re.sub(r'<br\s*/?>', '\n', clean)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = html.unescape(clean)
            
            # Hapus judul lama dan watermark
            lines = clean.split("\n")
            clean_lines = []
            for l in lines:
                l_s = l.strip()
                if not l_s:
                    continue
                if re.match(r"^The\s+Hobbit\b", l_s, re.I) and len(l_s) < 20:
                    continue
                if re.match(r"^Chapter\s+[IVXLCDM\d]+\b", l_s, re.I):
                    continue
                clean_lines.append(l_s)
                
            body_clean = "\n\n".join(clean_lines)
            
            # Pecah ke chunk
            paras = body_clean.split("\n\n")
            chunks = []
            cur = []
            cur_len = 0
            for p in paras:
                cur.append(p)
                cur_len += len(p)
                if cur_len >= CONFIG["max_chunk_chars"]:
                    chunks.append("\n\n".join(cur))
                    cur = []
                    cur_len = 0
            if cur:
                chunks.append("\n\n".join(cur))
                
            ch_id = f"ch_{idx+1:02d}"
            title = chapter_titles[idx]
            chapters.append({
                "id": ch_id,
                "title": title,
                "chunks": chunks,
                "raw_body": body_clean
            })

    print(f"   Berhasil memproses {len(chapters)} bab (Total {sum(len(c['chunks']) for c in chapters)} chunk).")
    return chapters, images

def translate_pipeline(chapters):
    print("\n==================================================================")
    print("🚀 MEMULAI PIPELINE TERJEMAHAN ID-DIRECT (GAUL & LENGKAP ILUSTRASI)")
    print("==================================================================")

    checkpoint = {"completed_ids": []}
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
        except Exception:
            pass

    translated_chapters = []

    for c_idx, ch in enumerate(chapters):
        ch_id = ch["id"]
        ch_title = ch["title"]
        chunks = ch["chunks"]
        ch_cache_dir = os.path.join(CACHE_DIR, ch_id)
        os.makedirs(ch_cache_dir, exist_ok=True)

        print(f"\n📖 [{c_idx+1}/{len(chapters)}] Memproses {ch_title} ({len(chunks)} chunk)...")

        # Terjemahkan chunk secara paralel
        chunk_results = [None] * len(chunks)
        pending_chunks = []

        for idx, chunk_text in enumerate(chunks):
            cf = os.path.join(ch_cache_dir, f"chunk_{idx+1:03d}.txt")
            if os.path.exists(cf):
                with open(cf, "r", encoding="utf-8") as f:
                    chunk_results[idx] = f.read()
            else:
                pending_chunks.append((idx, chunk_text, cf))

        if pending_chunks:
            print(f"   ⚡ Menerjemahkan {len(pending_chunks)} chunk baru (Concurrency {CONFIG['concurrency']})...")
            with ThreadPoolExecutor(max_workers=CONFIG["concurrency"]) as executor:
                futures = {executor.submit(call_llm, ct): (i, cf) for i, ct, cf in pending_chunks}
                for fut in as_completed(futures):
                    i, cf = futures[fut]
                    res = fut.result()
                    with open(cf, "w", encoding="utf-8") as f:
                        f.write(res)
                    chunk_results[i] = res
                    print(f"      ✅ Chunk {i+1}/{len(chunks)} selesai & dicache.")
        else:
            print(f"   ⚡ Semua {len(chunks)} chunk sudah ada di cache.")

        full_chapter_text = "\n\n".join(chunk_results)
        translated_chapters.append({
            "id": ch_id,
            "title": ch_title,
            "body": full_chapter_text
        })

        # Simpan ke checkpoint
        if ch_id not in checkpoint["completed_ids"]:
            checkpoint["completed_ids"].append(ch_id)
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, indent=2)

    # Simpan hasil teks gabungan
    print(f"\n💾 Menyimpan gabungan naskah ke {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("# THE HOBBIT - J.R.R. TOLKIEN (TERJEMAHAN ID-DIRECT)\n\n")
        for ch in translated_chapters:
            f.write(f"\n\n{'='*70}\n### {ch['title']}\n{'='*70}\n\n{ch['body']}\n\n")

    return translated_chapters

def build_epub(translated_chapters, images):
    print("\n==================================================================")
    print("📚 MENYUSUN BUKU EPUB BERILUSTRASI LENGKAP...")
    print("==================================================================")

    xhtml_files = []

    # 1. Halaman Peta Pembuka (Thror's Map & Map of Wilderland)
    maps_html = ['<div class="color-gallery"><h1>Peta & Panduan Middle-earth</h1>']
    if "00003.jpeg" in images:
        maps_html.append('<div class="illustration-container"><img src="../images/00003.jpeg" alt="Peta Thror" /><p><em>Peta Thror (Thror\'s Map) dengan Tulisan Rune Rahasia</em></p></div>')
    if "00021.jpeg" in images:
        maps_html.append('<div class="illustration-container"><img src="../images/00021.jpeg" alt="Peta Wilderland" /><p><em>Peta Wilayah Wilderland</em></p></div>')
    maps_html.append('</div>')

    maps_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<title>Peta &amp; Panduan</title>
<link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/>
</head>
<body>
{"".join(maps_html)}
</body>
</html>"""
    xhtml_files.append(("maps.xhtml", "Peta Middle-earth", maps_xhtml))

    # 2. Bab Cerita
    for idx, ch in enumerate(translated_chapters):
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

    # 3. Tulis ke file ZIP EPUB
    with zipfile.ZipFile(EPUB_OUT, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        z.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/css/stylesheet.css", CSS_CONTENT, compress_type=zipfile.ZIP_DEFLATED)

        # Masukkan semua gambar
        manifest_images = []
        for bn, fp in images.items():
            if os.path.exists(fp):
                with open(fp, "rb") as imf:
                    z.writestr(f"OEBPS/images/{bn}", imf.read(), compress_type=zipfile.ZIP_DEFLATED)
                item_id = f"img_{bn.replace('.', '_')}"
                media_type = "image/jpeg" if bn.endswith((".jpeg", ".jpg")) else "image/png"
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

        book_title = "The Hobbit (Terjemahan ID-Direct)"
        cover_id = "img_00001_jpeg" if "00001.jpeg" in images else (manifest_images[0] if manifest_images else "item_1")

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:the-hobbit-id-direct-tolkien"/>
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
        <dc:creator>J.R.R. Tolkien</dc:creator>
        <dc:language>id</dc:language>
        <dc:identifier id="BookID">urn:uuid:the-hobbit-id-direct-tolkien</dc:identifier>
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

    size_mb = os.path.getsize(EPUB_OUT) / (1024 * 1024)
    print(f"\n🎉 EPUB SUKSES DIBUAT! File: {EPUB_OUT} ({size_mb:.2f} MB, {len(translated_chapters)} Bab, {len(images)} Gambar)")

def main():
    t0 = time.time()
    chapters, images = extract_chapters_and_images()
    translated_chapters = translate_pipeline(chapters)
    build_epub(translated_chapters, images)
    print(f"⏱️ Total waktu eksekusi: {time.time() - t0:.1f} detik.")

if __name__ == "__main__":
    main()
