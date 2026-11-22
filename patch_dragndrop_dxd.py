with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update StyleMode type
code = code.replace(
    "type StyleMode = 'konosuba' | 'warhammer' | 'hobbit' | 'overlord' | 'mushoku' | 'dune' | 'metro' | 'default';",
    "type StyleMode = 'dxd' | 'konosuba' | 'warhammer' | 'hobbit' | 'overlord' | 'mushoku' | 'dune' | 'metro' | 'default';"
)

# 2. Update DxD chapter parser
old_txt_parser = "function extractTxtChapters(txtPath: string): Chapter[] {\n  const content = fs.readFileSync(txtPath, 'utf-8');\n  const lines = content.split('\\n');"
dxd_txt_parser = """function extractTxtChapters(txtPath: string): Chapter[] {
  const content = fs.readFileSync(txtPath, 'utf-8');
  const lines = content.split('\\n');

  // Khusus High School DxD
  if (/high\\s*school\\s*dxd|dxd/i.test(txtPath)) {
    console.log('😈 Terdeteksi: Light Novel High School DxD (No Sensor, Frontal, Gaul Gue-Lu)!');
    const chapters: Chapter[] = [];
    let curChap: Chapter | null = null;
    let curLines: string[] = [];
    let chIdx = 1;

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      // Lewati daftar isi (TOC) dan baris halaman
      if (l.startsWith('#') || /^(List\\s+Chapter|Index|Attention|Warning!)/i.test(l)) {
        continue;
      }

      // Deteksi awal bab riil DxD: Life 00, Life 01, Life 02, New Life, Afterword
      const isDxdHeader = /^(Life\\s+[0-9]+|New\\s+Life|Afterword)/i.test(l) && !/Bagian\\s+[0-9]+/i.test(l);
      if (isDxdHeader && l.length < 50) {
        if (curChap && curLines.length > 50) {
          curChap.text = cleanWatermarks(curLines.join('\\n').trim());
          if (curChap.text.length > 200) chapters.push(curChap);
        }
        const chNum = String(chIdx++).padStart(2, '0');
        curChap = {
          id: `dxd_ch${chNum}`,
          title: l,
          text: ''
        };
        curLines = [];
        continue;
      }

      curLines.push(rawLine);
    }

    if (curChap && curLines.length > 50) {
      curChap.text = cleanWatermarks(curLines.join('\\n').trim());
      if (curChap.text.length > 200) chapters.push(curChap);
    }

    if (chapters.length > 0) return chapters;
  }"""

code = code.replace(old_txt_parser, dxd_txt_parser)

# 3. Add DxD prompt in buildPrompt
dxd_prompt_block = """  if (styleMode === 'dxd') {
    return `Tuliskan kembali SELURUH alur adegan cerita High School DxD berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, TONGKRONGAN GAUL, NO SENSOR, MESUM FRONTAL, KASAR, dan TO-THE-POINT — setara dengan light novel dewasa / manga ecchi tanpa sensor!
Target pembaca: Remaja akhir / dewasa yang mau hiburan seru, kocak, mesum to-the-point, dan ogah baca kalimat berbelit-belit atau eufemisme sopan yang munafik!

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

ATURAN WAJIB & MUTLAK:
1. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Tokoh utama (Issei Hyoudou) monolog batin dan narasi selalu menggunakan: GUE (bukan "aku").
   - Menghadap orang lain / dialog menggunakan: LU / ELO (bukan "kamu" atau "kau").
   - BANNED TOTAL: DILARANG menggunakan kata "aku", "kamu", "kau", "diriku", "kepadamu". Ganti semua jadi GUE / LU!

2. TONE & KATA KASAR / VULGAR / MESUM FRONTAL:
   - Pikiran batin Issei mesum frontal, to-the-point, liar, dan kocak (toket, toket montok, grepe, ngintip, sange, coli, binal, ngentot, kontol, memek, becek, desah liar, bangsat, anjing, sialan, taik keluar apa adanya tanpa sensor!).
   - Jangan disopankan atau diperhalus! Terjemahkan secara blak-blakan dan renyah.

3. HARAM BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
   - Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "berujar", "berkata").
   - BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus"!
   - ANTI-REPETISI VERBA: Variasikan kata kerja aksi dan dialog secara dinamis sesuai naskah asli (bisik, seru, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir, ngedumel, ngoceh, dengus kesel, hela napas).

4. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog tanpa nama pembicara!
   - Setiap baris tuturan langsung WAJIB diawali format: Nama Lengkap: "..."
   - DAFTAR NAMA LENGKAP TOKOH HIGH SCHOOL DXD:
     * Issei Hyoudou / Ise -> Selalu gunakan: Issei Hyoudou: "..."
     * Yuuma Amano / Raynare -> Selalu gunakan: Yuuma Amano: "..." (atau Raynare: "..." setelah wujud aslinya terbongkar)
     * Rias Gremory / Buchou -> Selalu gunakan: Rias Gremory: "..."
     * Akeno Himejima -> Selalu gunakan: Akeno Himejima: "..."
     * Koneko Toujou -> Selalu gunakan: Koneko Toujou: "..."
     * Kiba Yuuto -> Selalu gunakan: Kiba Yuuto: "..."
     * Asia Argento -> Selalu gunakan: Asia Argento: "..."
     * Matsuda -> Selalu gunakan: Matsuda: "..."
     * Motohama -> Selalu gunakan: Motohama: "..."
     * Ayah Issei -> Selalu gunakan: Gorou Hyoudou: "..."
     * Ibu Issei -> Selalu gunakan: Miki Hyoudou: "..."
     * Dohnaseek -> Selalu gunakan: Dohnaseek: "..."
     * Kalawarner -> Selalu gunakan: Kalawarner: "..."
     * Mittelt -> Selalu gunakan: Mittelt: "..."
     * Freed Sellzen -> Selalu gunakan: Freed Sellzen: "..."

5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
${explanationRule}

Naskah Asli:\n\n${text}`;
  }
"""

code = code.replace("  if (styleMode === 'mushoku') {", dxd_prompt_block + "\n  if (styleMode === 'mushoku') {")

# 4. Update CLI detection
old_det = "const isKonosuba = /konosuba|kono\\s*subarashii/i.test(targetFile);"
new_det = """const isDxd = /high\\s*school\\s*dxd|dxd/i.test(targetFile);
  const isKonosuba = /konosuba|kono\\s*subarashii/i.test(targetFile);"""
code = code.replace(old_det, new_det)

old_mode = "const styleMode: StyleMode = isMetro ? 'metro' : (isDune ? 'dune' : (isKonosuba ? 'konosuba' : (isWarhammer ? 'warhammer' : (isHobbit ? 'hobbit' : (isOverlord ? 'overlord' : (isMushoku ? 'mushoku' : 'default'))))));"
new_mode = "const styleMode: StyleMode = isDxd ? 'dxd' : (isMetro ? 'metro' : (isDune ? 'dune' : (isKonosuba ? 'konosuba' : (isWarhammer ? 'warhammer' : (isHobbit ? 'hobbit' : (isOverlord ? 'overlord' : (isMushoku ? 'mushoku' : 'default')))))));"
code = code.replace(old_mode, new_mode)

code = code.replace(
    "if (styleMode === 'mushoku') styleDesc = 'Fantasy Isekai Petualangan Hidup Baru (Rudy Otaku Mesum vs Tobat & Dewasa, Tell-Don\\'t-Show, Gaul & Kocak)';",
    "if (styleMode === 'dxd') styleDesc = 'High School DxD (No Sensor, Mesum Frontal, Tongkrongan Gaul Gue-Lu, Dialog Bernama Lengkap, Ilustrasi Presisi)';\n  if (styleMode === 'mushoku') styleDesc = 'Fantasy Isekai Petualangan Hidup Baru (Rudy Otaku Mesum vs Tobat & Dewasa, Tell-Don\\'t-Show, Gaul & Kocak)';"
)

with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated translate-novel-dragndrop.ts with DxD mode successfully!")
