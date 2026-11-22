import fitz
import os
import glob
import re
import io
from PIL import Image

EXTRACTED_BASE = r"D:\JV\novel yoga\High School DxD\extracted"
DXD_ROOT = r"D:\JV\novel yoga\High School DxD"

def extract_all_images_direct_from_pdf(pdf_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    extracted_map = {} # page_num (1-based) -> list of saved image filenames
    
    img_counter = 1
    for p_num in range(len(doc)):
        page = doc[p_num]
        imgs = page.get_images()
        if not imgs:
            continue
            
        for img_info in imgs:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image['image']
            ext = base_image['ext']
            
            # Filter out tiny icon / banner images (below 300x300)
            try:
                im = Image.open(io.BytesIO(image_bytes))
                w, h = im.size
                if w < 350 and h < 350:
                    continue
            except Exception:
                pass
                
            fname = f"page_{p_num+1:03d}_img_{img_counter:02d}.{ext}"
            fpath = os.path.join(dest_dir, fname)
            if not os.path.exists(fpath):
                with open(fpath, "wb") as f_out:
                    f_out.write(image_bytes)
                    
            if (p_num + 1) not in extracted_map:
                extracted_map[p_num + 1] = []
            extracted_map[p_num + 1].append(fname)
            img_counter += 1
            
    return extracted_map

def extract_volume_text_with_images(vol_num):
    v_str = f"{vol_num:02d}"
    vol_dir = os.path.join(EXTRACTED_BASE, f"Vol_{v_str}")
    pdfs = glob.glob(os.path.join(vol_dir, "**", "*.pdf"), recursive=True)
    if not pdfs:
        print(f"[Vol {v_str}] PDF tidak ditemukan!")
        return None, None
        
    pdf_path = pdfs[0]
    images_dir = os.path.join(DXD_ROOT, f"extracted_images_vol_{v_str}")
    raw_txt_path = os.path.join(DXD_ROOT, f"High_School_DxD_Volume_{v_str}_Raw_Source.txt")
    
    # 1. Ekstrak gambar langsung dari PDF stream asli
    img_map = extract_all_images_direct_from_pdf(pdf_path, images_dir)
    print(f"[Vol {v_str}] Berhasil mengekstrak {sum(len(v) for v in img_map.values())} gambar asli dari {len(img_map)} halaman PDF.")
    
    doc = fitz.open(pdf_path)
    lines_out = []
    
    # Kumpulkan gambar halaman awal (1 s.d. 15) sebagai galeri depan
    front_images = []
    for p in sorted(img_map.keys()):
        if p <= 15:
            for f in img_map[p]:
                front_images.append(f)
                
    for f in front_images:
        lines_out.append(f"[[ILUSTRASI:{f}]]")
    if front_images:
        lines_out.append("\n")
        
    # Ekstrak teks halaman per halaman dan selipkan tag gambar tepat di halamannya
    for p_num in range(len(doc)):
        p_real = p_num + 1
        page = doc[p_num]
        
        # Jika halaman ini memiliki gambar cerita (di atas halaman 15)
        if p_real > 15 and p_real in img_map:
            for f in img_map[p_real]:
                lines_out.append(f"\n[[ILUSTRASI:{f}]]\n")
                
        txt = page.get_text()
        page_lines = [l.strip() for l in txt.split("\n") if l.strip()]
        clean_lines = [l for l in page_lines if "PDF HSDXD" not in l and "afterscarlet" not in l and "RuiDrive" not in l]
        
        # Rapikan judul bab yang terpotong 2 baris
        for i in range(len(clean_lines)):
            if re.match(r'^(Life|Next\s*Life|New\s*Life|Prolog|Epilog|Afterword)', clean_lines[i], re.IGNORECASE) and len(clean_lines[i]) < 40:
                if i + 1 < len(clean_lines) and len(clean_lines[i+1]) < 35 and not re.match(r'^(Life|Bagian|#|["“])', clean_lines[i+1], re.IGNORECASE):
                    clean_lines[i] = clean_lines[i] + " " + clean_lines[i+1]
                    clean_lines[i+1] = ""
                    
        clean_lines = [l for l in clean_lines if l]
        if clean_lines:
            lines_out.append("\n".join(clean_lines))
            
    full_text = "\n\n".join(lines_out)
    with open(raw_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"[Vol {v_str}] RAW TXT diperbarui -> {raw_txt_path} ({len(full_text)} chars)")
    return raw_txt_path, images_dir

if __name__ == "__main__":
    for v in [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
        extract_volume_text_with_images(v)
