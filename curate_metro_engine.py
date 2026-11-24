import os
import re

# Definisi Judul Bab Resmi Metro 2033
OFFICIAL_TITLES = {
    1: "CHAPTER 1: Ujung Dunia",
    2: "CHAPTER 2: Sang Pemburu",
    3: "CHAPTER 3: Jika Aku Tak Kembali",
    4: "CHAPTER 4: Suara-Suara Terowongan",
    5: "CHAPTER 5: Imbalan Selongsong Peluru",
    6: "CHAPTER 6: Hukum Rimba yang Kuat",
    7: "CHAPTER 7: Kekhanan Kegelapan",
    8: "CHAPTER 8: Reich Keempat",
    9: "CHAPTER 9: Du Stirbst (Kau Pasti Mati)",
    10: "CHAPTER 10: No Pasarán! (Pantang Lolos!)",
    11: "CHAPTER 11: Aku Tak Percaya!",
    12: "CHAPTER 12: Polis (Jantung Peradaban)",
    13: "CHAPTER 13: Perpustakaan Agung Moskwa",
    14: "CHAPTER 14: Di Atas Sana (Dunia Luar)",
    15: "CHAPTER 15: Peta Rahasia Metro-2",
    16: "CHAPTER 16: Senandung Kematian",
    17: "CHAPTER 17: Anak-Anak Dewa Cacing",
    18: "CHAPTER 18: Pusat Komando Bawah Tanah",
    19: "CHAPTER 19: Pertempuran Terakhir di Menara Ostankino",
    20: "CHAPTER 20: Terlahir Merayap",
}

# Cast tokoh kunci per bab
CHAPTER_CASTS = {
    1: [
        ("Artyom", "metro", "Pemuda 20 tahun yatim piatu penjaga perimeter pos VDNKh"),
        ("Pyotr Andreevich", "metro", "Komandan senior regu jaga pos 450 meter VDNKh"),
        ("Andrey", "metro", "Rekan prajurit regu patroli perbatasan VDNKh"),
        ("Kirill", "metro", "Prajurit penjaga perimeter VDNKh"),
    ],
    2: [
        ("Artyom", "metro", "Pemuda 20 tahun yatim piatu penjaga perimeter pos VDNKh"),
        ("Hunter", "spartan", "Sosok pria botak berotot tegap berjaket kulit, stalker legendaris Ordo Spartan"),
        ("Sukhoi", "metro", "Sasha Sukhoi, ayah tiri Artyom sekaligus perwira senior pengawas pos VDNKh"),
        ("Andrey", "metro", "Rekan prajurit regu patroli perbatasan VDNKh"),
        ("Pyotr Andreevich", "metro", "Komandan senior regu jaga pos 450 meter VDNKh"),
    ],
    3: [
        ("Artyom", "metro", "Pemuda 20 tahun yang menerima sumpah rahasia dari Hunter"),
        ("Hunter", "spartan", "Stalker legendaris Ordo Spartan yang bersiap berangkat misi bunuh diri ke utara"),
        ("Sukhoi", "metro", "Sasha Sukhoi, perwira senior VDNKh yang skeptis terhadap ramalan kiamat"),
    ],
    4: [
        ("Artyom", "metro", "Pemuda 20 tahun yang memulai pengembaraan menembus terowongan Metro"),
        ("Bourbon", "metro", "Pedagang pasar gelap dan penjahat terowongan penyewa jasa Artyom"),
        ("Pyotr Andreevich", "metro", "Komandan pos VDNKh yang melepas keberangkatan karavan"),
        ("Vitaly", "metro", "Rekan pengawal karavan jalur VDNKh ke Alekseevskaya"),
    ],
    5: [
        ("Artyom", "metro", "Pemuda pengelana terowongan yang menembus terowongan maut"),
        ("Bourbon", "metro", "Pedagang pasar gelap berwatak keras rekan seperjalanan Artyom"),
    ],
    6: [
        ("Artyom", "metro", "Pemuda VDNKh yang selamat dari jebakan stasiun hantu Sukharevskaya"),
        ("Bourbon", "metro", "Pedagang terowongan yang tewas tersedot bisikan anomali gaib"),
    ],
    7: [
        ("Artyom", "metro", "Pemuda yatim piatu yang mencari jalan ke Polis"),
        ("Khan", "metro", "Sosok mistis pengelana terowongan yang memahami anomali gaib dan suara arwah"),
        ("Ace", "metro", "Stalker tangguh pengawal kafilah pedagang"),
    ],
    8: [
        ("Artyom", "metro", "Buronan yang tertangkap di stasiun cengkeraman fasis"),
        ("Mikhail Porfirevich", "metro", "Kakek tua cendekiawan pelindung bocah telantar"),
        ("Vanechka", "metro", "Bocah bisu keterbelakangan mental yang dieksekusi pasukan Reich"),
    ],
    9: [
        ("Artyom", "metro", "Tahanan yang berhasil diselamatkan dari tiang gantungan fasis"),
        ("Alexei Feodorovich", "metro", "Komandan regu pejuang Brigade Internasional Garis Merah"),
        ("Rusakov", "metro", "Pejuang garis depan penentang tirani Reich"),
    ],
    10: [
        ("Artyom", "metro", "Penjelajah yang berusaha menembus barikade perbatasan"),
        ("Anton", "metro", "Mantan tentara tangguh penjaga barikade Polyanka"),
        ("Oleg", "metro", "Bocah cerdas putra Anton rekan seperjalanan Artyom"),
    ],
    11: [
        ("Artyom", "metro", "Pemuda yang mencari suaka dan izin masuk ke stasiun Polis"),
        ("Mark", "metro", "Pria oportunis penjudi taruhan tikus balap di Prospekt Mira"),
    ],
    12: [
        ("Artyom", "metro", "Utusan pembawa pesan Hunter yang akhirnya tiba di Polis"),
        ("Kolonel Melnik", "spartan", "Pemimpin tertinggi pasukan elit Spartan Rangers benteng peradaban manusia"),
        ("Danila", "metro", "Cendekiawan pustakawan penuntun misi ke Perpustakaan Agung Moskwa"),
    ],
    13: [
        ("Artyom", "metro", "Stalker yang naik ke permukaan kota mati Moskwa berselimut salju radioaktif"),
        ("Danila", "metro", "Pustakawan yang terluka parah diserang mutan pustakawan"),
        ("Kolonel Melnik", "spartan", "Komandan ekspedisi pembersih mutan Ordo Spartan"),
    ],
    14: [
        ("Artyom", "metro", "Pemuda yang menjelajahi reruntuhan ruang bawah tanah Perpustakaan Moskwa"),
        ("Pustakawan", "mutant", "Mutan kera raksasa ganas pemangsa manusia berdaya penciuman tajam"),
    ],
    15: [
        ("Artyom", "metro", "Pembawa peta rahasia silo rudal Metro-2"),
        ("Anton", "metro", "Sahabat setia pengawal Artyom"),
        ("Tretyak", "spartan", "Ahli sistem pemandu rudal nuklir bawah tanah"),
        ("Kolonel Melnik", "spartan", "Komandan operasi penyerangan sarang mutan Dark Ones"),
    ],
    16: [
        ("Artyom", "metro", "Penembus jalur rahasia Metro-2 menuju instalasi bunker militer D-6"),
        ("Anton", "metro", "Pejuang penjaga perimeter yang tersesat dalam senandung maut"),
        ("Oleg", "metro", "Putra kecil Anton"),
    ],
    17: [
        ("Artyom", "metro", "Tawanan sekte kanibal fanatik pemuja cacing raksasa"),
        ("Anton", "metro", "Pejuang yang mempertaruhkan nyawa demi menyelamatkan putranya"),
        ("Dron", "spartan", "Pasukan pelopor penyelamat dari Ordo Spartan"),
    ],
    18: [
        ("Artyom", "metro", "Navigator penunjuk arah ke ruang kendali bunker strategis D-6"),
        ("Kolonel Melnik", "spartan", "Panglima Spartan pengambil alih instalasi militer D-6"),
    ],
    19: [
        ("Artyom", "metro", "Pengarah laser pemandu rudal di puncak Menara Televisi Ostankino"),
        ("Kolonel Melnik", "spartan", "Pemimpin regu tempur penyerbu sarang Dark Ones"),
        ("Ulman", "spartan", "Sniper elit Spartan berwatak santai dan berdarah dingin"),
    ],
    20: [
        ("Artyom", "metro", "Manusia penghubung yang akhirnya menyadari kebenaran di balik Dark Ones"),
        ("Dark Ones", "mutant", "Ras mutan telepati Homines Novi yang sebenarnya ingin berdamai dengan manusia"),
        ("Kolonel Melnik", "spartan", "Komandan penekan tombol peluncuran rudal penghancur sarang"),
    ],
}

# Pembersihan kata baku usang (Banlist QA)
BANLIST_REPLACEMENTS = [
    (r"\bmencicit\b", "merintih lirih"),
    (r"\bmenimpali\b", "menyahut"),
    (r"\bbergumam\b", "nyeletuk"),
    (r"\bmeracau\b", "ngelantur"),
    (r"\bmendengus\b", "menghela napas panjang"),
    (r"\btersenyum simpul\b", "nyengir kecut"),
    (r"\btatkala\b", "pas"),
    (r"\bkendati demikian\b", "meski begitu"),
    (r"\bterpendar\b", "berpendar"),
]

def clean_banned_words(text):
    for pat, rep in BANLIST_REPLACEMENTS:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text

def extract_term_from_note(pre, desc):
    """Mengekstraksi istilah inti dari teks sebelum [Catatan: ...] dan teks catatan itu sendiri."""
    # 1. Cek apakah catatan berbentuk "Istilah adalah / berarti / singkatan ..."
    m_def = re.match(r"^([A-Za-z0-9_\-\s]{2,30}?)\s+(?:adalah|berarti|merupakan|singkatan dari)\b", desc, re.I)
    if m_def:
        t = m_def.group(1).strip()
        if len(t) >= 3 and not any(t.lower() == w for w in ['ini', 'itu', 'dia', 'mereka', 'hal']):
            return t

    # 2. Ambil dari kata terakhir di depan catatan
    pre_clean = re.sub(r'[\"“”\'\.,;!?]', '', pre).strip()
    words = pre_clean.split()
    if not words:
        return "Istilah"

    # Ambil Title-Case jika ada
    cap_words = []
    i = len(words) - 1
    while i >= 0:
        w = words[i]
        if w and (w[0].isupper() or w.isupper()):
            cap_words.insert(0, w)
            i -= 1
        else:
            break
    if cap_words:
        return " ".join(cap_words)
    
    return words[-1]

def curate_chapter(ch_num, raw_chapter_text):
    lines = raw_chapter_text.strip().split("\n")
    
    # 1. Tentukan judul resmi
    ch_title = OFFICIAL_TITLES.get(ch_num, f"CHAPTER {ch_num}")
    
    # 2. Siapkan wadah glossary dan cast
    chapter_glossary = {}
    
    # Kumpulkan teks bersih
    cleaned_lines = []
    skip_next_italic_route = False

    for line in lines:
        stripped = line.strip()
        
        # Lewati header lama dan garis separator
        if re.match(r"^###\s+", stripped):
            continue
        if re.match(r"^={10,}\s*$", stripped):
            continue
        if re.match(r"^#+\s*(?:BAB|CHAPTER)\s*\d+.*$", stripped, re.I):
            continue
        if stripped.upper() in ["METRO 2033", "METRO 2033:"]:
            continue
        if re.match(r"^\[\[ILUSTRASI:map_route.*?\]\]$", stripped):
            skip_next_italic_route = True
            continue
        if skip_next_italic_route and stripped.startswith("*Ilustrasi Rute Perjalanan:"):
            skip_next_italic_route = False
            continue
        skip_next_italic_route = False

        # Tangkap dan konversi [Catatan: ...]
        def replace_catatan(m):
            full_match = m.group(0)
            desc = m.group(1).strip()
            # Cari teks sebelum kurung catatan di baris ini
            start_pos = m.start()
            pre_text = line[:start_pos]
            term = extract_term_from_note(pre_text, desc)
            if term and len(term) >= 2:
                chapter_glossary[term] = desc
            # Hapus tag [Catatan: ...] dari teks utama
            return ""

        processed_line = re.sub(r"\[Catatan:\s*([^\]]+)\]", replace_catatan, line)
        processed_line = processed_line.rstrip()
        
        # Bersihkan kata baku usang
        processed_line = clean_banned_words(processed_line)

        # Rapikan spasi ganda yang mungkin tertinggal setelah penghapusan catatan
        processed_line = re.sub(r"\s{2,}", " ", processed_line)
        processed_line = re.sub(r"\s+([,\.!\?])", r"\1", processed_line)
        
        cleaned_lines.append(processed_line)

    # Susun ulang bab: Header -> CAST -> GLOSSARY -> Body
    body_text = "\n".join(cleaned_lines).strip()
    
    # Format CAST
    cast_tags = []
    for c_name, c_faction, c_desc in CHAPTER_CASTS.get(ch_num, []):
        cast_tags.append(f"[CAST: {c_name} | {c_faction} | {c_desc}]")
    
    # Format GLOSSARY
    gloss_tags = []
    for g_term, g_desc in chapter_glossary.items():
        # Jangan duplikasi jika sudah ada di cast
        if any(c[0].lower() == g_term.lower() for c in CHAPTER_CASTS.get(ch_num, [])):
            continue
        gloss_tags.append(f"[GLOSSARY: {g_term} | {g_desc}]")

    header_block = f"### {ch_title}\n"
    if cast_tags:
        header_block += "\n".join(cast_tags) + "\n"
    if gloss_tags:
        header_block += "\n".join(gloss_tags) + "\n"
    if cast_tags or gloss_tags:
        header_block += "\n"

    return header_block + body_text

def main():
    src_file = r"D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt"
    backup_file = r"D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt.bak"
    
    with open(src_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Backup original
    if not os.path.exists(backup_file):
        with open(backup_file, "w", encoding="utf-8") as bf:
            bf.write(full_text)
        print(f"📦 Backup naskah disimpan di: {backup_file}")

    parts = re.split(r"(?=^###\s+)", full_text, flags=re.MULTILINE)
    curated_chapters = []

    ch_counter = 1
    for p in parts:
        p = p.strip()
        if not p.startswith("###"):
            continue
        curated_ch = curate_chapter(ch_counter, p)
        curated_chapters.append(curated_ch)
        print(f"✅ Bab {ch_counter:02d} berhasil dikurasi: {OFFICIAL_TITLES.get(ch_counter)}")
        ch_counter += 1

    final_full_text = "\n\n".join(curated_chapters) + "\n"
    
    with open(src_file, "w", encoding="utf-8") as f:
        f.write(final_full_text)

    print(f"\n🎉 SUKSES! Seluruh {len(curated_chapters)} bab Metro 2033 berhasil dikurasi dan diselaraskan!")

if __name__ == "__main__":
    main()
