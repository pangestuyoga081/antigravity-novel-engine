import os
import re
import sys
import pypdf

BASE_DIR = r"E:\novel yoga\Mushoku Tensei"

def get_toc_entries(reader, vol_num):
    txt3 = reader.pages[2].extract_text() or ''
    txt4 = reader.pages[3].extract_text() or ''
    toc = txt3 + '\n' + txt4
    lines = [l.strip() for l in toc.split('\n') if l.strip()]
    skip = [
        'Index', 'Attention', 'Warning!!!', 'Ilustrasi', 'Ruidrive.com',
        f'Mushoku Tensei – Volume {vol_num:02d}', f'Mushoku Tensei - Volume {vol_num:02d}'
    ]
    ch_lines = []
    for l in lines:
        if any(l.startswith(s) for s in skip) or l.isdigit():
            continue
        ch_lines.append(l)
    return ch_lines

def extract_qwer_image(text, ill_files):
    m = re.search(r'QWER\s*-\s*([A-Za-z0-9_\-\.\n]+)', text)
    if not m:
        return None
    raw_str = m.group(1).replace('\n', '').replace(' ', '').strip()
    return match_image_file(raw_str, ill_files)

def match_image_file(target_str, ill_files):
    target_clean = target_str.replace('\n', '').replace(' ', '').strip()
    # Direct match
    for fn in ill_files:
        if fn.lower() == target_clean.lower():
            return fn
    # Prefix match (at least 20 chars)
    if len(target_clean) >= 15:
        prefix = target_clean[:20]
        for fn in ill_files:
            if fn.startswith(prefix):
                return fn
    # Base match
    target_base = os.path.splitext(target_clean)[0]
    for fn in ill_files:
        if os.path.splitext(fn)[0] == target_base:
            return fn
    return target_str

def extract_volume(vol_num):
    vol_dir = os.path.join(BASE_DIR, f"[Ruidrive] Mushoku Tensei [LN] - Volume {vol_num:02d}")
    pdf_name = f"[Ruidrive] Mushoku Tensei [LN] - Volume {vol_num:02d}.pdf"
    pdf_path = os.path.join(vol_dir, pdf_name)
    ill_dir = os.path.join(vol_dir, "Ilustrasi")

    if not os.path.isfile(pdf_path):
        print(f"❌ File tidak ditemukan: {pdf_path}")
        return None

    ill_files = sorted(os.listdir(ill_dir)) if os.path.isdir(ill_dir) else []
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)

    toc_entries = get_toc_entries(reader, vol_num)
    first_ch_title = toc_entries[0] if toc_entries else "Prolog"

    gallery_images = []
    story_pages = []
    story_started = False

    for p_idx in range(total_pages):
        page = reader.pages[p_idx]
        txt = page.extract_text() or ''
        lines = [l.strip() for l in txt.split('\n') if l.strip()]

        cleaned = [
            l for l in lines 
            if not (re.match(r'^Mushoku\s*Tensei\s*[–—-]\s*Volume\s*\d+', l, re.I) or l.isdigit() or 'Ruidrive.com' in l)
        ]

        if not story_started:
            matched_img = extract_qwer_image(txt, ill_files)
            if matched_img and matched_img not in gallery_images:
                gallery_images.append(matched_img)

            if cleaned and p_idx >= 5:
                first_line = cleaned[0]
                if (first_line == first_ch_title or 
                    first_line.startswith(first_ch_title[:10]) or
                    first_line in ['Prolog', 'Prologue'] or
                    first_line.startswith('Bab 1:') or 
                    first_line.startswith('Chapter 1:') or
                    first_line == 'Paulus tersayang,'):
                    story_started = True
                    story_pages.append((p_idx, txt))
        else:
            story_pages.append((p_idx, txt))

    processed_story = []
    
    for p_idx, txt in story_pages:
        # Check if pure donation page
        if 'Kami dengan sepenuh hati telah menyusun PDF' in txt or 'https://trakteer.id/ruidrive' in txt:
            continue
            
        lines = [l.strip() for l in txt.split('\n') if l.strip()]
        cleaned = [
            l for l in lines 
            if not (re.match(r'^Mushoku\s*Tensei\s*[–—-]\s*Volume\s*\d+', l, re.I) or l.isdigit() or 'Ruidrive.com' in l)
        ]
        
        # Check if page is purely a QWER illustration
        if 'QWER' in txt and (not cleaned or any('QWER' in l for l in cleaned)):
            # Check if there are other meaningful non-QWER lines
            non_qwer = [l for l in cleaned if 'QWER' not in l and not re.match(r'^[A-Za-z0-9_\-\.\=]{15,}$', l)]
            if not non_qwer:
                matched_img = extract_qwer_image(txt, ill_files)
                if matched_img:
                    processed_story.append(f"\n[[ILUSTRASI:{matched_img}]]\n")
                continue

        # Normal text page
        page_lines = []
        skip_hash_line = False
        
        for l in txt.split('\n'):
            str_l = l.strip()
            if re.match(r'^Mushoku\s*Tensei\s*[–—-]\s*Volume\s*\d+', str_l, re.I):
                continue
            if str_l.isdigit() and len(str_l) < 5:
                continue
            if 'Ruidrive.com' in str_l:
                continue
            if 'https://ruidrive.blogspot.com' in str_l or 'https://trakteer.id' in str_l:
                continue
                
            if 'QWER' in str_l:
                matched_img = extract_qwer_image(str_l, ill_files)
                if matched_img:
                    page_lines.append(f"\n[[ILUSTRASI:{matched_img}]]\n")
                skip_hash_line = True
                continue
                
            if skip_hash_line:
                if re.match(r'^[A-Za-z0-9_\-\.\=]{15,}$', str_l) or str_l.startswith('=s2000'):
                    continue
                else:
                    skip_hash_line = False

            page_lines.append(l)

        page_text = '\n'.join(page_lines).strip()
        if page_text:
            processed_story.append(f"[[PAGE:{p_idx + 1}]]\n" + page_text)

    full_text_parts = [f"# MUSHOKU TENSEI - VOLUME {vol_num:02d}\n"]
    
    if gallery_images:
        full_text_parts.append("### Galeri Ilustrasi Karakter & Warna\n")
        for g_img in gallery_images:
            full_text_parts.append(f"[[ILUSTRASI:{g_img}]]\n")
            
    full_text_parts.append('\n\n'.join(processed_story))
    
    final_text = '\n'.join(full_text_parts)
    final_text = re.sub(r'\n{3,}', '\n\n', final_text)

    out_file = os.path.join(r"E:\novel yoga", f"Mushoku Tensei - Volume {vol_num:02d}.txt")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(final_text)

    # Count illustrations embedded
    ill_embedded = len(re.findall(r'\[\[ILUSTRASI:[^\]]+\]\]', final_text))
    print(f"✅ Volume {vol_num:02d}: {len(gallery_images)} galeri, {ill_embedded} total ilustrasi, {len(final_text)} karakter -> {out_file}")
    return out_file

if __name__ == '__main__':
    vols = list(range(1, 27))
    if len(sys.argv) > 1:
        vols = [int(x) for x in sys.argv[1:]]
    for v in vols:
        extract_volume(v)
