# 🧠 ANTIGRAVITY PERSISTENT MEMORY, SKILLS & TS DRAG-AND-DROP PLAYBOOK
> **Workspace Utama:** `D:\JV\novel yoga`  
> **Engine Spec:** [AGENTS.md](file:///D:/JV/novel%20yoga/AGENTS.md)  
> **Fokus Runner:** [translate-novel-dragndrop.ts](file:///D:/JV/novel%20yoga/translate-novel-dragndrop.ts)  
> **Compiler Utama:** [compile_epub_helper.py](file:///D:/JV/novel%20yoga/compile_epub_helper.py)  
> **Terakhir Diperbarui:** 27 November 2026  

---

## 1. 🎯 PROFIL & SELERA MUTLAK USER (WAJIB DIPATUHI AGENT)

1. **Gaya Bahasa Terjemahan / Adaptasi:**
   - **WAJIB:** Bahasa Indonesia santai, ceplas-ceplos, gaya tongkrongan **`gue-lo`**, cepat, *punchy*, mengalir alami.
   - **BANNED TOTAL (DILARANG KERAS):** `aku`, `kamu`, `kau`, `engkau`, `diriku`, `kepadamu`, `tatkala`, `kendati demikian`, `merupakan`, `adalah` (jika kaku), `mencicit`, `menukas`, `menimpali`, `tersenyum simpul`, `bergumam`, `meracau`, `mendengus`, `budak korporat`, `salaryman`.
   - **Format Dialog Wajib:** Setiap dialog **HARUS** diawali nama pembicara agar terdeteksi oleh parser EPUB:
     ```text
     Michio: "Sialan, mahal banget harganya!"
     Roxanne: "Saya akan melayani Tuan sebaik mungkin..."
     ```

2. **Kadar Konten & Anti-Sensor:**
   - **100% NO-SENSOR:** Adegan kekerasan, darah, umpatan kasar (`anjing`, `bangsat`, `sialan`, `brengsek`), serta deskripsi erotis/vulgar (tubuh wanita, nafsu, adegan ranjang basah, desahan, penetrasi) **WAJIB** diterjemahkan frontal dan detail tanpa eufemisme atau sensor moral.
   - **Anti-Trope Munafik:** User paling benci MC planga-plongo yang *"secara tak sengaja membangkitkan nafsu"* atau *"pura-pura gak peduli cewek"*. User suka MC yang **proaktif, pragmatis, niat berburu/menaklukkan** (seperti *Isekai Meikyuu*, *Overlord*, atau gaya penaklukan ala *HuniePop*).

3. **Selera Genre & Proyek yang Sudah Tuntas:**
   - **Dark Fantasy / Isekai:** *Overlord Vol 01 & Vol 02* (versi `3.8-flash-low` & `4-hydrogen-low`).
   - **Post-Apocalyptic Survival:** *Metro 2033*, *Metro 2034*, *Metro 2035*.
   - **Lewd / Harem Conquest:** *Isekai Meikyuu de Harem wo Vol 01*, *High School DxD Vol 01–25*, *Breeder Mage 1*.
   - **Monster Lore:** *Monster Girl Encyclopedia Vol 01* (EPUB Visi OCR).

---

## 2. 🚀 FOKUS UTAMA: `translate-novel-dragndrop.ts`

File [translate-novel-dragndrop.ts](file:///D:/JV/novel%20yoga/translate-novel-dragndrop.ts) adalah **mesin utama penerjemahan otomatis** (tinggal lempar file `.epub` / `.txt` / `.pdf` yang sudah diekstrak).

### A. Konfigurasi & Endpoint LLM (9router)
- **URL Proxy Lokal:** `http://localhost:20128/v1/chat/completions`
- **API Key:** Diambil dari database SQLite 9router: `C:\Users\Eevyx\AppData\Roaming\9router\db\data.sqlite` (tabel `apiKeys`).
- **Pilihan Model:**
  - `ag/gemini-3.8-flash-low`: Cepat, hemat kuota, cocok untuk novel aksi/sci-fi panjang (*Metro*, *Expanse*, *Overlord* standar).
  - `ag/gemini-4-hydrogen-low`: **Pilihan terbaik untuk novel ceplas-ceplos, vulgar maksimal, dan no-sensor** (*Isekai Meikyuu*, *Overlord Hydrogen*, *DxD*).
- **Peringatan Penting Teknis:** 9router sering mengembalikan format **Server-Sent Events (`data: {...}`)** meskipun `stream: false`. Selalu gunakan `parseSSEorJSON()` (jangan pernah `JSON.parse()` langsung mentah-mentah!).

### B. Alur Eksekusi 3-Pass di `translate-novel-dragndrop.ts`
1. **Pass 1 — Context Scouter (`_scout_tags.txt`):**
   - Mengambil sampel awal tiap bab (~7.000 karakter) untuk mengekstrak maksimal 6 tag `[CAST: Nama | faksi | Deskripsi]` dan 6 tag `[GLOSSARY: Istilah | Penjelasan]`.
2. **Pass 2 — Concurrent Chunked Localization (`concurrency: 15`, `maxChunkChars: 6500`):**
   - Membagi bab menjadi chunk berbasis paragraf (`splitParagraphSafe`), membersihkan watermark (`cleanWatermarks`), menjaga kontinuitas konteks (`prevContext`), dan menyimpan cache per chunk (`chunk_001.txt`, dst.).
   - **Zero-Refusal Guard:** `isRefusalResponse()` otomatis mendeteksi penolakan AI/ringkasan palsu dan menghapus cache rusak agar bisa diulang atau di-sub-chunk.
   - **Style Adapter (`StyleMode`):** Menyesuaikan prompt per universe (`carl`, `dxd`, `overlord`, `metro`, `expanse`, `hobbit`, `default`, dll.). *Catatan pengembangan: tambahkan mode `vulgar_harem` / `isekai_meikyuu` ke dalam `StyleMode` untuk proyek dewasa berikutnya.*
3. **Pass 3 — Kompilasi EPUB 3 & QA Gate (`compile_epub_helper.py`):**
   - **ATURAN KERAS:** **DILARANG** membuat script kompilasi EPUB polosan dadakan! Semua kompilasi **WAJIB** melalui [compile_epub_helper.py](file:///D:/JV/novel%20yoga/compile_epub_helper.py) agar mendapat:
     - **Reader-Theme Agnostic CSS:** `background-color: transparent; color: inherit;` (aman di Dark Mode, AMOLED, Sepia, Light Mode).
     - **Cast Drawer:** `<details class="chapter-cast">` di awal setiap bab.
     - **Non-Jumping Pop-up Footnotes:** `<a epub:type="noteref">` + `<aside epub:type="footnote">`.
     - **Speaker Highlights:** Format `Nama: "..."` otomatis diberi warna & badge faksi.
     - **Broken Image Guard:** Cek keberadaan file di `illustrations/<NovelName>/` sebelum menulis tag `<img>`.
     - **Automated QA Gate:** `EPUBValidator.validate_epub()` di `core_engine/src/qa_gate/validator.py` memvalidasi parity `noteref`/`aside`, nol tag bocor, dan integritas XHTML.

### C. Cara Menjalankan `translate-novel-dragndrop.ts`
```powershell
# Menjalankan dengan model default (3.8-flash-low)
npx tsx "D:\JV\novel yoga\translate-novel-dragndrop.ts" "D:\JV\novel yoga\NamaNovel.epub"

# Menjalankan dengan model Hydrogen Low (gaya vulgar / ceplas-ceplos maksimal)
$env:LLM_MODEL="ag/gemini-4-hydrogen-low"
$env:CONCURRENCY="6"
npx tsx "D:\JV\novel yoga\translate-novel-dragndrop.ts" "D:\JV\novel yoga\NamaNovel.epub"
```

---

## 3. 🧩 PELAJARAN & CATATAN PENTING DARI SESI LAINNYA

1. **Pelajaran Ekstraksi Sumber (RuiDrive & PDF Terenkripsi):**
   - PDF dari RuiDrive umumnya pakai enkripsi AES (bikin `pypdf` error kalau tidak ada `cryptography`). **Solusi:** Selalu gunakan **PyMuPDF (`import pymupdf`)** untuk mengekstrak teks bersih, dan **7-Zip (`C:\Program Files\7-Zip\7z.exe`)** untuk mengekstrak arsip `.rar`.
   - Naskah MTL blog biasanya sangat kaku (`aku/kamu`, kalimat terbalik). Wajib dijalankan lewat pass lokalisasi/poles `gemini-4-hydrogen-low` + banlist scrubber.

2. **Pelajaran Audio / Audiobook:**
   - TTS lokal atau standar seperti Edge TTS terdengar kaku/robotik dan ikut membacakan label pembicara (`Momonga: "..."`). Jika nanti menggarap audiobook lagi, wajib strip tag speaker sebelum sintesis suara dan gunakan engine TTS ekspresif (seperti ElevenLabs / F5-TTS yang sudah di-tune).

3. **Pelajaran Image Typesetting (*Monster Girl Encyclopedia*):**
   - **Hindari `image-generator` AI** untuk halaman teks penuh karena cepat terkena limit kuota **HTTP 429 (`ResourceExhausted`)**.
   - Untuk typesetting lokal (`RapidOCR` + `OpenCV Inpaint` + `Pillow`), jangan pernah menghitung ukuran font per kotak kecil (bikin ukuran huruf acak kegedean/kekecilan) dan jangan pisah kolom sembarangan pada halaman 1-kolom (bikin teks numpuk). Wajib pakai *page-level median line pitch* dan deteksi kolom berbasis distribusi pusat horizontal.

4. **Struktur Penyimpanan Resmi:**
   - **EPUB Final Siap Baca:** `D:\JV\novel yoga\HASIL_TERJEMAHAN\EPUB_SIAP_BACA\` (dan cerminan di `epubs/`).
   - **Naskah Master TXT:** `D:\JV\novel yoga\HASIL_TERJEMAHAN\NASKAH_TXT\`.
   - **Ilustrasi:** `D:\JV\novel yoga\illustrations\<Nama_Novel>\`.
   - **Living Universe Profiles:** `D:\JV\novel yoga\core_engine\config\profiles\<novel>.yaml`.
   - **GitHub Sync:** Commit & push perubahan penting ke `origin main`.
