#!/usr/bin/env python3
import os
import sys
import re
import pypdf

def extract_overlord_volume(pdf_path, workspace_root=r'E:\novel yoga'):
    if not os.path.exists(pdf_path):
        print(f"❌ File tidak ditemukan: {pdf_path}")
        return None

    raw_base = os.path.splitext(os.path.basename(pdf_path))[0]
    # Bersihkan nama file agar rapi
    clean_base = raw_base
    clean_base = re.sub(r'\[(?:RuiDrive\.com|AFTERSCARLET\.blogspot\.com)\]\s*', '', clean_base, flags=re.I)
    clean_base = re.sub(r'\[AFTERSCARLET\.blogspot\.com\]', '', clean_base, flags=re.I)
    clean_base = clean_base.strip()

    # Pastikan format standar: "Overlord Volume XX - Title"
    m_vol = re.search(r'Volume\s+(\d+)', clean_base, re.I)
    vol_num = int(m_vol.group(1)) if m_vol else 1
    vol_str = f"{vol_num:02d}"

    out_illust_dir = os.path.join(workspace_root, 'illustrations', f'Overlord_Volume_{vol_str}')
    os.makedirs(out_illust_dir, exist_ok=True)

    out_txt_path = os.path.join(workspace_root, f"{clean_base}.txt")

    print(f"📖 Membaca PDF: {pdf_path}")
    print(f"📂 Folder Ilustrasi: {out_illust_dir}")
    print(f"📄 Target TXT: {out_txt_path}")

    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"📑 Total Halaman: {total_pages}")

    # Ekstrak gambar
    extracted_images = {}
    
    # Cek apakah ada folder Ilustrasi terpisah di dekat PDF (seperti di Vol 15 & 16)
    pdf_dir = os.path.dirname(pdf_path)
    loose_illust_dir = os.path.join(pdf_dir, 'Ilustrasi')
    if os.path.isdir(loose_illust_dir):
        print("🖼️ Menemukan folder Ilustrasi pendamping...")
        for fn in sorted(os.listdir(loose_illust_dir)):
            if fn.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                src_p = os.path.join(loose_illust_dir, fn)
                dst_p = os.path.join(out_illust_dir, fn)
                with open(src_p, 'rb') as f_in, open(dst_p, 'wb') as f_out:
                    f_out.write(f_in.read())
                # Perkiraan halaman untuk ilustrasi lepas jika ada
                extracted_images[len(extracted_images) + 1] = fn

    for i, page in enumerate(reader.pages):
        p_num = i + 1
        try:
            for img in page.images:
                if len(img.data) > 5000:
                    img_filename = f"page_{p_num:03d}_{img.name}"
                    if not img_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        img_filename += '.jpg'
                    img_path = os.path.join(out_illust_dir, img_filename)
                    if not os.path.exists(img_path):
                        with open(img_path, 'wb') as f:
                            f.write(img.data)
                    extracted_images[p_num] = img_filename
        except Exception as e:
            pass

    print(f"🖼️ Berhasil mengekstrak {len(extracted_images)} ilustrasi.")

    full_output = []
    full_output.append(f"# {clean_base.upper()}\n")

    # Galeri Ilustrasi Karakter & Warna (halaman pembuka biasanya 1-25)
    color_pages = [p for p in sorted(extracted_images.keys()) if p <= 25]
    if color_pages:
        full_output.append("### Galeri Ilustrasi Karakter & Warna\n")
        for p in color_pages:
            full_output.append(f"[[ILUSTRASI:{extracted_images[p]}]]\n")

    # Cari halaman awal cerita (Prolog atau Chapter 1)
    story_start_page = 1
    for i, page in enumerate(reader.pages[:40]):
        t = page.extract_text() or ''
        lines = [l.strip() for l in t.split('\n') if l.strip()]
        for l in lines[:5]:
            if re.match(r'^(Prolog\b|Chapter\s+[0-9IVXLCDM]+)', l, re.I):
                story_start_page = i + 1
                break
        if story_start_page > 1:
            break

    print(f"🚀 Cerita utama dimulai pada halaman {story_start_page}.")

    # Baca halaman teks
    for i in range(story_start_page - 1, total_pages):
        p_num = i + 1
        page = reader.pages[i]
        t = page.extract_text() or ''

        # Bersihkan watermark & artefak
        lines = t.split('\n')
        cleaned_lines = []
        for l in lines:
            ls = l.strip()
            if not ls:
                continue
            if re.search(r'PDF\s+Overlo[a-z]*\s+Vol|by\s*:\s*Kenny|PDF\s+by\s*:|afterscarlet|ruidrive|Attention', ls, re.I):
                continue
            if re.match(r'^\d+$', ls) and len(ls) < 5:
                continue
            cleaned_lines.append(ls)

        page_text = '\n'.join(cleaned_lines)

        # Sisipkan gambar jika ada di halaman adegan ini
        if p_num in extracted_images and p_num >= story_start_page:
            full_output.append(f"\n\n[[ILUSTRASI:{extracted_images[p_num]}]]\n\n")

        if page_text:
            full_output.append(page_text + '\n')

    raw_content = '\n'.join(full_output)
    raw_content = re.sub(r'\n{3,}', '\n\n', raw_content)

    with open(out_txt_path, 'w', encoding='utf-8') as f:
        f.write(raw_content)

    print(f"✅ Selesai mengekstrak {clean_base}! ({len(raw_content)} karakter, {os.path.getsize(out_txt_path)} bytes)\n")
    return out_txt_path

if __name__ == '__main__':
    if len(sys.argv) > 1:
        extract_overlord_volume(sys.argv[1])
    else:
        print("Usage: python extract_overlord_pdf.py <pdf_path>")
