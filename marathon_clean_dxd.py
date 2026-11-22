import os
import glob
import fitz
import re
import shutil
import zipfile
import subprocess
import time

EXTRACTED_BASE = r"D:\JV\novel yoga\High School DxD\extracted"
DXD_ROOT = r"D:\JV\novel yoga\High School DxD"
EPUBS_DIR = r"D:\JV\novel yoga\epubs"
DRAGNDROP_SCRIPT = r"D:\JV\novel yoga\translate-novel-dragndrop.ts"

os.makedirs(EPUBS_DIR, exist_ok=True)

def compile_volume_epub(vol_num, translated_txt, img_dir):
    output_epub = os.path.join(EPUBS_DIR, f"High_School_DxD_Volume_{vol_num} (Illustrated ID-Direct).epub")
    build_dir = os.path.join(DXD_ROOT, f"build_epub_vol_{vol_num}")
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(os.path.join(build_dir, "META-INF"), exist_ok=True)
    os.makedirs(os.path.join(build_dir, "OEBPS", "images"), exist_ok=True)
    
    with open(os.path.join(build_dir, "mimetype"), "w", encoding="utf-8") as f:
        f.write("application/epub+zip")
        
    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
    with open(os.path.join(build_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
        f.write(container_xml)
        
    manifest_images = []
    cover_item_id = "cover_img"
    if img_dir and os.path.exists(img_dir):
        for img in sorted(os.listdir(img_dir)):
            src_f = os.path.join(img_dir, img)
            dst_f = os.path.join(build_dir, "OEBPS", "images", img)
            shutil.copy(src_f, dst_f)
            mtype = "image/jpeg" if img.lower().endswith(('.jpg', '.jpeg')) else "image/png"
            clean_id = re.sub(r'[^a-zA-Z0-9_]', '_', img)
            manifest_images.append(f'<item id="img_{clean_id}" href="images/{img}" media-type="{mtype}"/>')
            if any(k in img.lower() for k in ["ln", "01", "cov", "001"]):
                cover_item_id = f"img_{clean_id}"
                
    with open(translated_txt, "r", encoding="utf-8") as f:
        full_text = f.read()
        
    # HAPUS GARIS PEMBATAS '=' ATAU '-' YANG MENGGANGGU
    full_text = re.sub(r'^[=\-]{5,}\s*$', '', full_text, flags=re.MULTILINE)
    
    def clean_xml(text):
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace('"', "&#8220;").replace('"', "&#8221;")
        return text

    chapter_regex = r"(?=Life[\\s.]+[0-9]+|Next\\s+Life|New\\s+Life|Prolog(?:ue)?|Epilog(?:ue)?|Afterword|###\s+)"
    raw_chaps = re.split(chapter_regex, full_text, flags=re.IGNORECASE)
    
    chapters_data = []
    ch_idx = 1
    
    for rc in raw_chaps:
        rc_str = rc.strip()
        if not rc_str:
            continue
        lines = rc_str.split("\n")
        title = lines[0].replace("###", "").strip()
        if not title:
            title = f"Bab {ch_idx}"
            
        html_paragraphs = []
        html_paragraphs.append(f'<h1 class="chapter-title">{clean_xml(title)}</h1>')
        
        body_text = "\n".join(lines[1:])
        paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
        
        for p in paragraphs:
            # Check illustration tag
            img_match = re.search(r'\[\[ILUSTRASI:([^\]]+)\]\]', p)
            if img_match:
                img_name = img_match.group(1).strip()
                html_paragraphs.append(f'<div class="illust-box"><img src="images/{img_name}" alt="Ilustrasi"/><p class="caption">Ilustrasi DxD Volume {vol_num}</p></div>')
                p_clean = p.replace(img_match.group(0), "").strip()
                if not p_clean:
                    continue
                p = p_clean
                
            if ":" in p and any(k in p for k in ["Issei Hyoudou:", "Rias Gremory:", "Asia Argento:", "Akeno Himejima:", "Koneko Toujou:", "Kiba Yuuto:", "Raynare:", "Azazel:", "Vali Lucifer:"]):
                html_paragraphs.append(f'<p class="dialogue"><b>{clean_xml(p)}</b></p>')
            else:
                sub_lines = [clean_xml(l) for l in p.split("\n") if l.strip()]
                html_paragraphs.append(f'<p>{"<br/>".join(sub_lines)}</p>')
                
        ch_file = f"chapter_{ch_idx:02d}.xhtml"
        ch_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="id">
<head>
  <title>{clean_xml(title)}</title>
  <style>
    body {{ font-family: "Georgia", "Times New Roman", serif; line-height: 1.65; margin: 5%; color: #1a1a1a; }}
    h1.chapter-title {{ text-align: center; margin-top: 1.5em; margin-bottom: 1.5em; font-size: 1.6em; color: #b30000; font-weight: bold; border-bottom: 2px solid #b30000; padding-bottom: 0.3em; }}
    p {{ margin-bottom: 0.9em; text-indent: 1.2em; text-align: justify; }}
    p.dialogue {{ text-indent: 0; margin-left: 0.5em; margin-bottom: 0.8em; color: #111; }}
    b {{ color: #8b0000; }}
    .illust-box {{ text-align: center; margin: 2em 0; }}
    .illust-box img {{ max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
    .caption {{ font-size: 0.85em; color: #666; margin-top: 0.5em; text-indent: 0; text-align: center; font-style: italic; }}
  </style>
</head>
<body>
  {"\n  ".join(html_paragraphs)}
</body>
</html>"""
        with open(os.path.join(build_dir, "OEBPS", ch_file), "w", encoding="utf-8") as f:
            f.write(ch_content)
        chapters_data.append((ch_file, title))
        ch_idx += 1
        
    manifest_items = []
    spine_items = []
    nav_points = []
    for idx, (cf, c_title) in enumerate(chapters_data):
        cid = f"ch_{idx+1:02d}"
        manifest_items.append(f'<item id="{cid}" href="{cf}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{cid}"/>')
        nav_points.append(f'<navPoint id="nav_{cid}" playOrder="{idx+1}"><navLabel><text>{clean_xml(c_title)}</text></navLabel><content src="{cf}"/></navPoint>')
        
    content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>High School DxD - Volume {vol_num} (No Sensor - ID-Direct)</dc:title>
    <dc:creator>Ichiei Ishibumi</dc:creator>
    <dc:language>id</dc:language>
    <dc:identifier id="BookId">urn:uuid:hsdxd-vol{vol_num}-direct-id</dc:identifier>
    <meta name="cover" content="{cover_item_id}"/>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    {"\n    ".join(manifest_images)}
    {"\n    ".join(manifest_items)}
  </manifest>
  <spine toc="ncx">
    {"\n    ".join(spine_items)}
  </spine>
</package>"""
    with open(os.path.join(build_dir, "OEBPS", "content.opf"), "w", encoding="utf-8") as f:
        f.write(content_opf)

    toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:hsdxd-vol{vol_num}-direct-id"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>High School DxD - Volume {vol_num}</text></docTitle>
  <navMap>{"\n    ".join(nav_points)}</navMap>
</ncx>"""
    with open(os.path.join(build_dir, "OEBPS", "toc.ncx"), "w", encoding="utf-8") as f:
        f.write(toc_ncx)

    with zipfile.ZipFile(output_epub, "w", zipfile.ZIP_DEFLATED) as z_out:
        z_out.write(os.path.join(build_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, build_dir).replace("\\", "/")
                if rel_path == "mimetype":
                    continue
                z_out.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)
                
    print(f"[{vol_num}] ✅ EPUB bersih & berilustrasi berhasil dikompilasi -> {output_epub} ({os.path.getsize(output_epub)} bytes)")
    return output_epub

def run_clean_marathon():
    # List volumes to process
    # Vol 1 sampai 12 sudah selesai, re-compile jika perlu. Vol 13 ke atas dicek dan ditranslate.
    for v in range(13, 26):
        v_str = f"{v:02d}"
        print(f"\n==========================================")
        print(f"▶️ MEMPROSES VOLUME {v_str}")
        print(f"==========================================")
        
        raw_txt = os.path.join(DXD_ROOT, f"High_School_DxD_Volume_{v_str}_Raw_Source.txt")
        img_dir = os.path.join(DXD_ROOT, f"extracted_images_vol_{v_str}")
        
        if not os.path.exists(raw_txt) or not os.path.exists(img_dir):
            print(f"[{v_str}] Raw file atau gambar belum siap, generate dulu...")
            from rebuild_all_raw_and_images import extract_volume_text_with_images
            raw_txt, img_dir = extract_volume_text_with_images(v)
            
        trans_out = raw_txt.replace(".txt", " (Terjemahan ID-Direct).txt")
        
        # Check if already has 100% complete chapters
        cmd = ["npx", "tsx", DRAGNDROP_SCRIPT, raw_txt]
        print(f"[{v_str}] Menjalankan penerjemahan via translate-novel-dragndrop.ts...")
        proc = subprocess.run(cmd, shell=True)
        if proc.returncode != 0:
            print(f"[{v_str}] Warning: runner selesai dengan kode {proc.returncode}")
            
        if os.path.exists(trans_out):
            compile_volume_epub(v_str, trans_out, img_dir)
            print(f"[{v_str}] 🎉 Volume {v_str} Selesai Sempurna!\n")

if __name__ == "__main__":
    run_clean_marathon()
