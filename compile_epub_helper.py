import os
import sys
import re
import zipfile
import html

CSS_CONTENT = """@charset "utf-8";
body {
    margin: 5% 7%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.8;
    color: inherit;
    background-color: transparent;
    text-align: justify;
}
h1, h2, h3, h4 {
    text-align: center;
    color: inherit;
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    font-weight: 700;
}
p {
    margin: 0.8em 0;
    text-indent: 1.5em;
    color: inherit;
    background-color: transparent;
}
p.dialogue {
    text-indent: 0;
    margin-left: 0.4em;
    font-weight: 500;
}
.speaker {
    font-weight: 700;
    color: #0284c7;
}

/* Pop-up Lore / Footnote Interaktif (Theme-Agnostic) */
.lore-ref {
    color: inherit;
    text-decoration: underline dotted #0284c7;
    font-weight: 600;
    cursor: pointer;
}
.lore-ref:hover {
    color: #0284c7;
}
.lore-tag {
    font-size: 0.72em;
    vertical-align: super;
    background-color: rgba(2, 132, 199, 0.18);
    color: #0284c7;
    border-radius: 3px;
    padding: 0 4px;
    margin-left: 2px;
    font-weight: 700;
}

/* Bagian Catatan Kaki / Glosarium di Bawah Bab */
.footnotes-section {
    margin-top: 2.5em;
    border-top: 1px dashed rgba(148, 163, 184, 0.4);
    padding-top: 1em;
}
aside[epub\\:type="footnote"], aside.footnote {
    margin: 0.6em 0;
    padding: 0.5em 0.8em;
    font-size: 0.88em;
    line-height: 1.5;
    background-color: rgba(2, 132, 199, 0.06);
    border-left: 3px solid #0284c7;
    border-radius: 4px;
    color: inherit;
}
aside.footnote strong {
    color: #0284c7;
}

.game-box {
    margin: 1.2em 0;
    padding: 0.8em 1.2em;
    background-color: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-left: 4px solid #0284c7;
    border-radius: 6px;
    font-size: 0.9em;
    font-weight: 600;
    color: inherit;
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

/* Faction Badge & Character Avatar (Agnostic Semitransparent) */
.faction-badge {
    display: inline-flex;
    align-items: center;
    font-size: 0.68em;
    padding: 1px 6px;
    margin-right: 6px;
    border-radius: 4px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    vertical-align: 0.1em;
    white-space: nowrap;
    line-height: 1.4;
}
.badge-spartan { background-color: rgba(239, 68, 68, 0.18); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.35); }
.badge-metro { background-color: rgba(148, 163, 184, 0.18); color: #64748b; border: 1px solid rgba(148, 163, 184, 0.35); }
.badge-redline { background-color: rgba(220, 38, 38, 0.18); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.35); }
.badge-hanza { background-color: rgba(234, 179, 8, 0.18); color: #ca8a04; border: 1px solid rgba(234, 179, 8, 0.35); }
.badge-carl { background-color: rgba(236, 72, 153, 0.18); color: #db2777; border: 1px solid rgba(236, 72, 153, 0.35); }
.badge-donut { background-color: rgba(168, 85, 247, 0.18); color: #9333ea; border: 1px solid rgba(168, 85, 247, 0.35); }
.badge-ai { background-color: rgba(2, 132, 199, 0.18); color: #0284c7; border: 1px solid rgba(2, 132, 199, 0.35); }

/* Interactive Chapter Cast Drawer */
.chapter-cast {
    margin: 1.5em 0 2em 0;
    padding: 0.8em 1.2em;
    background-color: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 8px;
    font-size: 0.85em;
    color: inherit;
}
.chapter-cast summary {
    font-weight: 700;
    cursor: pointer;
    color: #0284c7;
    outline: none;
}
.cast-grid {
    margin-top: 0.8em;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 8px;
}
.cast-card {
    padding: 6px 10px;
    background: rgba(148, 163, 184, 0.06);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 6px;
    color: inherit;
}
"""

def load_lore_dict(base_dir, base_name):
    """
    Muat profil YAML dari folder core_engine/config/profiles
    untuk membangun kamus karakter & glosarium istilah secara dinamis.
    """
    lore_map = {}
    engine_profiles = os.path.join(base_dir, "core_engine", "config", "profiles")
    if not os.path.exists(engine_profiles):
        engine_profiles = os.path.join(os.path.dirname(base_dir), "core_engine", "config", "profiles")

    if os.path.exists(engine_profiles):
        # Match by name
        target_yaml = None
        for yf in os.listdir(engine_profiles):
            if yf.endswith(".yaml"):
                y_clean = yf.lower().replace("_", " ").replace("-", " ")
                b_clean = base_name.lower().replace("_", " ").replace("-", " ")
                if any(w in b_clean for w in ["metro", "expanse", "carl", "dxd", "dune", "hobbit"]) and any(w in y_clean for w in ["metro", "expanse", "carl", "dxd", "dune", "hobbit"]):
                    if ("2034" in b_clean and "2034" in y_clean) or ("2033" in b_clean and "2033" in y_clean) or ("carl" in b_clean and "carl" in y_clean) or ("caliban" in b_clean and "2" in y_clean):
                        target_yaml = os.path.join(engine_profiles, yf)
                        break

        if target_yaml and os.path.exists(target_yaml):
            try:
                import yaml
                with open(target_yaml, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                # Characters
                for c in data.get("key_characters", []):
                    cname = c.get("name", "")
                    crole = c.get("role", "")
                    if cname and crole:
                        lore_map[cname] = f"👤 {crole}"

                # Loanwords / Terms
                for lw in data.get("loanwords", []):
                    if "(" in lw and ")" in lw:
                        term = lw.split("(")[0].strip()
                        desc = lw.split("(")[1].replace(")", "").strip()
                        lore_map[term] = f"📖 {desc}"

                # Locations
                for loc in data.get("locations_and_factions", []):
                    if "(" in loc and ")" in loc:
                        term = loc.split("(")[0].strip()
                        desc = loc.split("(")[1].replace(")", "").strip()
                        lore_map[term] = f"🏛️ {desc}"
            except Exception as e:
                print("Catatan lore parser:", e)

    return lore_map

def get_faction_badge(speaker_name):
    spk_low = speaker_name.lower()
    if any(w in spk_low for w in ["hunter", "miller"]):
        return '<span class="faction-badge badge-spartan">⚔️ SPARTAN</span>'
    if any(w in spk_low for w in ["homer", "nikolai"]):
        return '<span class="faction-badge badge-metro">📜 METRO</span>'
    if any(w in spk_low for w in ["sasha"]):
        return '<span class="faction-badge badge-metro">🕯️ SURVIVOR</span>'
    if any(w in spk_low for w in ["ahmed"]):
        return '<span class="faction-badge badge-metro">🛡️ SEVASTOPOL</span>'
    if any(w in spk_low for w in ["leonid", "komunis", "red line"]):
        return '<span class="faction-badge badge-redline">🚩 RED LINE</span>'
    if any(w in spk_low for w in ["hanza"]):
        return '<span class="faction-badge badge-hanza">💰 HANZA</span>'
    if any(w in spk_low for w in ["artyom"]):
        return '<span class="faction-badge badge-spartan">🎖️ RANGER</span>'
    if any(w in spk_low for w in ["carl"]):
        return '<span class="faction-badge badge-carl">💥 CRAWLER</span>'
    if any(w in spk_low for w in ["donut"]):
        return '<span class="faction-badge badge-donut">👑 DIVA CAT</span>'
    if any(w in spk_low for w in ["ai", "announcer", "dungeon"]):
        return '<span class="faction-badge badge-ai">🤖 SYSTEM</span>'
    if any(w in spk_low for w in ["holden"]):
        return '<span class="faction-badge badge-metro">🚀 ROCINANTE</span>'
    if any(w in spk_low for w in ["bobbie"]):
        return '<span class="faction-badge badge-spartan">🔴 MMC MARS</span>'
    if any(w in spk_low for w in ["avasarala"]):
        return '<span class="faction-badge badge-hanza">🌐 UN EARTH</span>'
    return ""

def text_to_html(body_text, lore_map=None, available_images=None):
    if lore_map is None:
        lore_map = {}
    if available_images is None:
        available_images = set()

    paragraphs = body_text.split("\n")
    html_parts = []
    footnotes = []
    chapter_speakers = set()
    semantic_cast = []
    fn_counter = 1

    # Pola penangkapan penjelasan dalam kurung dari model LLM:
    # Contoh: flamethrower (senjata pelontar api penghangus infeksi) atau Jalur Melingkar (Circle Line)
    # Tujuannya: hapus kurung berantakan dari naskah dan jadikan Tooltip Pop-up yang bersih dan konsisten!
    STOP_WORDS = {
        'ke', 'di', 'dari', 'pada', 'buat', 'untuk', 'sama', 'dan', 'atau', 'yang', 'si', 'para',
        'bawa', 'pake', 'pakai', 'seorang', 'jual', 'setrum', 'hasil', 'satu', 'tiap', 'ada', 'itu',
        'ini', 'kan', 'lah', 'pun', 'amat', 'juga', 'tentang', 'oleh', 'lewat', 'menuju', 'persis', 'kayak'
    }
    glossary_paren_pat = re.compile(
        r'((?:[A-Za-z0-9_\*\-\.]+(?:\s+[A-Za-z0-9_\*\-\.]+){0,3})\s*)\(([^)]{3,120})\)'
    )

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # Tangkap tag semantik [CAST: Nama | Faksi | Deskripsi]
        cast_match = re.match(r"^\[CAST:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\]$", p, re.I)
        if cast_match:
            c_name = cast_match.group(1).strip()
            c_faction = cast_match.group(2).strip().lower()
            c_desc = cast_match.group(3).strip()
            semantic_cast.append((c_name, c_faction, c_desc))
            # Daftarkan nama cast ke lore_map agar otomatis punya tooltip pop-up
            lore_map[c_name] = c_desc
            # Jika nama memiliki variasi (misal 'Pyotr Andreevich' -> daftarkan juga 'Pyotr')
            first_word = c_name.split()[0]
            if len(first_word) >= 3 and first_word not in lore_map:
                lore_map[first_word] = c_desc
            continue

        # Tangkap tag semantik [GLOSSARY: Istilah | Penjelasan]
        gloss_match = re.match(r"^\[GLOSSARY:\s*(.*?)\s*\|\s*(.*?)\s*\]$", p, re.I)
        if gloss_match:
            g_term = gloss_match.group(1).strip()
            g_desc = gloss_match.group(2).strip()
            lore_map[g_term] = g_desc
            continue
            
        img_match = re.match(r"^\[\[ILUSTRASI:(.*?)\]\]$", p)
        if img_match:
            img_file = img_match.group(1).strip()
            base_img = os.path.basename(img_file)
            # Abaikan potongan peta rute agar alur membaca tidak terpotong
            if "map_route" in base_img.lower():
                continue
            # Hanya render tag <img> jika file gambarnya benar-benar ada di dalam arsip gambar EPUB
            if base_img in available_images:
                html_parts.append(f'<div class="illustration-container"><img src="../images/{base_img}" alt="Ilustrasi" /></div>')
            continue

        if p.startswith("[PEMBERITAHUAN") or p.startswith("[ACHIEVEMENT") or (p.startswith("[") and p.endswith("]")):
            esc_box = html.escape(p)
            html_parts.append(f'<div class="game-box">{esc_box}</div>')
            continue

        # Format markdown header di dalam body teks (# BAB 1 / # Pertahanan ...)
        h_match = re.match(r"^#+\s*(.*)$", p)
        if h_match:
            h_text = html.escape(h_match.group(1).strip())
            html_parts.append(f'<h3 style="text-align:center; margin:1.2em 0 0.6em 0; color:#0284c7; font-weight:700;">{h_text}</h3>')
            continue
            
        # Bersihkan penjelasan dalam kurung ganda dan konversi menjadi Tooltip interaktif
        def extract_and_convert_paren(match):
            nonlocal fn_counter
            full_pre = match.group(1).rstrip()
            desc_text = match.group(2).strip()
            
            words = full_pre.split()
            lead_in = []
            term_words = []
            if len(words) > 2:
                lead_in.extend(words[:-2])
                words = words[-2:]
            for i, w in enumerate(words):
                clean_w = re.sub(r'[^a-zA-Z0-9]', '', w).lower()
                if clean_w in STOP_WORDS and i < len(words) - 1:
                    lead_in.append(w)
                else:
                    term_words = words[i:]
                    break
            raw_term = ' '.join(term_words) if term_words else full_pre.strip()
            prefix = (' '.join(lead_in) + ' ') if lead_in else ''
            
            clean_term = raw_term.replace('*', '').strip()
            clean_desc = desc_text.replace('*', '').strip()
            
            fn_id = f"fn_{fn_counter}"
            fn_ref_id = f"fnref_{fn_counter}"
            footnotes.append((fn_id, fn_ref_id, clean_term, clean_desc))
            res = f'{prefix}<a id="{fn_ref_id}" href="#{fn_id}" class="lore-ref" epub:type="noteref">{raw_term}<span class="lore-tag">?</span></a>'
            fn_counter += 1
            return res

        spk_match = re.match(r"^([^:]+?):\s*\"(.*)\"$", p)
        if spk_match:
            raw_spk = spk_match.group(1)
            raw_dial = spk_match.group(2)

            spk = html.escape(raw_spk)
            # Escape HTML karakter di dalam dialog dulu
            dial = html.escape(raw_dial)
            # Konversi format bold dan italic markdown di dalam dialog
            dial = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", dial)
            dial = re.sub(r"\*(.*?)\*", r"<em>\1</em>", dial)
            # Baru jalankan konversi penjelasan kurung ke tooltip (agar tag <a> tidak terkena escape)
            dial = glossary_paren_pat.sub(extract_and_convert_paren, dial)
            
            # Hanya tambahkan ke cast drawer jika karakter penting di lore_map
            if spk in lore_map:
                chapter_speakers.add(spk)
            badge_html = get_faction_badge(spk)
            
            # Check if speaker has tooltip
            spk_disp = spk
            if spk in lore_map:
                fn_id = f"fn_{fn_counter}"
                fn_ref_id = f"fnref_{fn_counter}"
                fn_desc = lore_map[spk]
                footnotes.append((fn_id, fn_ref_id, spk, fn_desc))
                spk_disp = f'<a id="{fn_ref_id}" href="#{fn_id}" class="lore-ref" epub:type="noteref">{spk}<span class="lore-tag">?</span></a>'
                fn_counter += 1

            html_parts.append(f'<p class="dialogue">{badge_html}<span class="speaker">{spk_disp}:</span> &#8220;{dial}&#8221;</p>')
            continue
            
        esc_p = html.escape(p)
        esc_p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", esc_p)
        esc_p = re.sub(r"\*(.*?)\*", r"<em>\1</em>", esc_p)
        # Baru jalankan konversi penjelasan kurung ke tooltip narasi
        esc_p = glossary_paren_pat.sub(extract_and_convert_paren, esc_p)

        # Inject lore references into narrative for unique terms (limit 1 per term per chapter)
        for term, desc in lore_map.items():
            if len(term) >= 4 and term in esc_p and not any(term == sp[2] for sp in footnotes if sp[2] == term):
                fn_id = f"fn_{fn_counter}"
                fn_ref_id = f"fnref_{fn_counter}"
                footnotes.append((fn_id, fn_ref_id, term, desc))
                # Replace only first occurrence
                pattern = re.compile(r'\b' + re.escape(term) + r'\b')
                replacement = f'<a id="{fn_ref_id}" href="#{fn_id}" class="lore-ref" epub:type="noteref">{term}<span class="lore-tag">?</span></a>'
                esc_p = pattern.sub(replacement, esc_p, count=1)
                fn_counter += 1

        html_parts.append(f"<p>{esc_p}</p>")

    # Top Cast Drawer if chapter has multiple speakers or semantic cast
    cast_header = ""
    if semantic_cast:
        cast_cards = []
        for c_name, c_faction, c_desc in semantic_cast:
            badge = get_faction_badge(c_faction)
            cast_cards.append(f'<div class="cast-card">{badge}<strong>{html.escape(c_name)}</strong><br/><span style="font-size:0.85em; color:#64748b;">{html.escape(c_desc)}</span></div>')
        cast_header = f"""<details class="chapter-cast">
<summary>👥 Tokoh Penting di Bab Ini ({len(semantic_cast)} Tokoh)</summary>
<div class="cast-grid">{"".join(cast_cards)}</div>
</details>"""
    else:
        # Fallback lama: Filter hanya karakter yang memang ada di lore map (bukan figuran acak)
        key_speakers = [spk for spk in chapter_speakers if spk in lore_map]
        if len(key_speakers) >= 2:
            cast_cards = []
            for spk in sorted(key_speakers):
                role_desc = lore_map.get(spk, "Karakter Penting")
                badge = get_faction_badge(spk)
                cast_cards.append(f'<div class="cast-card">{badge}<strong>{spk}</strong><br/><span style="font-size:0.85em; color:#64748b;">{html.escape(role_desc)}</span></div>')
            cast_header = f"""<details class="chapter-cast">
<summary>👥 Tokoh Penting di Bab Ini ({len(key_speakers)} Tokoh Utama)</summary>
<div class="cast-grid">{"".join(cast_cards)}</div>
</details>"""

    # Append interactive footnotes at end of chapter if any
    if footnotes:
        html_parts.append('<div class="footnotes-section">')
        html_parts.append('<h4 style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.05em; color: #0284c7; margin-bottom: 0.8em;">Glosarium &amp; Karakter Bab Ini:</h4>')
        for fn_id, fn_ref_id, title, desc in footnotes:
            # Gunakan span biasa tanpa tag <a href> back-link agar reader tidak mental ke awal bab
            html_parts.append(f'<aside id="{fn_id}" class="footnote" epub:type="footnote"><strong>&bull; {title}:</strong> {html.escape(desc)}</aside>')
        html_parts.append('</div>')
        
    return (cast_header + "\n" + "\n".join(html_parts)) if cast_header else "\n".join(html_parts)

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

    # Galeri Peta Pembuka (Khusus Hobbit jika benar-benar novel The Hobbit)
    if "hobbit" in base_name.lower() and ("00003.jpeg" in images_data or "00021.jpeg" in images_data):
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

    # Interactive Route Map (SVG Khusus Metro 2034: Jalur Sevastopolskaya - Tulskaya)
    if "2034" in base_name:
        metro_route_svg = """<div class="metro-map-container">
<h2>🚇 PETA JALUR TEROWONGAN METRO 2034: SEVASTOPOLSKAYA SECTOR</h2>
<p style="font-size:0.85em; color:#94a3b8; margin-bottom:1.5em;">Jalur Serpukhovsko-Timiryazevskaya (Garis Abu-Abu Selatan) &bull; Klik stasiun untuk info situasi pertahanan</p>
<svg viewBox="0 0 800 240" xmlns="http://www.w3.org/2000/svg">
  <line x1="80" y1="120" x2="720" y2="120" stroke="#64748b" stroke-width="8" stroke-linecap="round"/>
  <!-- Sevastopolskaya -->
  <g class="station-node">
    <circle cx="120" cy="120" r="18" fill="#0284c7" stroke="#ffffff" stroke-width="3"/>
    <text x="120" y="80" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">Sevastopolskaya</text>
    <text x="120" y="165" fill="#94a3b8" font-size="11" text-anchor="middle">⚡ Pembangkit Listrik Hidro</text>
    <text x="120" y="182" fill="#cbd5e1" font-size="10" text-anchor="middle">Benteng Terdepan Selatan</text>
  </g>
  <!-- Chertanovskaya -->
  <g class="station-node">
    <circle cx="270" cy="120" r="12" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <text x="270" y="85" fill="#cbd5e1" font-size="12" text-anchor="middle">Chertanovskaya</text>
    <text x="270" y="160" fill="#64748b" font-size="10" text-anchor="middle">Pos Pengintai Mati</text>
  </g>
  <!-- Nakhimovsky Prospekt -->
  <g class="station-node">
    <circle cx="420" cy="120" r="14" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>
    <text x="420" y="85" fill="#f87171" font-size="12" font-weight="bold" text-anchor="middle">Nakhimovsky</text>
    <text x="420" y="160" fill="#ef4444" font-size="10" text-anchor="middle">⚠️ Zona Sarang Monster</text>
  </g>
  <!-- Nagornaya -->
  <g class="station-node">
    <circle cx="560" cy="120" r="12" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <text x="560" y="85" fill="#cbd5e1" font-size="12" text-anchor="middle">Nagornaya</text>
    <text x="560" y="160" fill="#64748b" font-size="10" text-anchor="middle">Stasiun Terlantar</text>
  </g>
  <!-- Tulskaya -->
  <g class="station-node">
    <circle cx="680" cy="120" r="18" fill="#eab308" stroke="#ffffff" stroke-width="3"/>
    <text x="680" y="80" fill="#facc15" font-size="14" font-weight="bold" text-anchor="middle">Tulskaya</text>
    <text x="680" y="165" fill="#ca8a04" font-size="11" text-anchor="middle">🚪 Pintu Air Tertutup</text>
    <text x="680" y="182" fill="#ef4444" font-size="10" text-anchor="middle">Karantina Wabah Hitam</text>
  </g>
</svg>
<p style="font-size:0.8em; color:#64748b; margin-top:1.5em;">Kafilah mesiu Sevastopolskaya terputus di Tulskaya. Hunter, Homer, dan Ahmed ditugaskan menembus terowongan maut ini.</p>
</div>"""
        route_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Peta Rute Ekspedisi</title><link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/></head>
<body>{metro_route_svg}</body>
</html>"""
        xhtml_files.append(("metro_route_map.xhtml", "Peta Rute Ekspedisi Metro 2034", route_xhtml))

    # Galeri Peta Pembuka Metro 2033 & 2034
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

    # Load Lore Dictionary for Interactive Pop-ups
    lore_map = load_lore_dict(base_dir, base_name)
    if lore_map:
        print(f"📖 Terhubung dengan Glosarium Interaktif: {len(lore_map)} entitas/tokoh siap di-link.")

    # Bab Cerita
    for idx, ch in enumerate(chapters):
        fname = f"chapter_{idx+1:02d}.xhtml"
        title_esc = html.escape(ch["title"])
        body_html = text_to_html(ch["body"], lore_map, set(images_data.keys()))

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
