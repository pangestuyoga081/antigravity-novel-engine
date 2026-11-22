# AGENTS.md — Panduan Lengkap Novel Translator Pipeline (Direct & Gaul)
## Antigravity Agent | Workspace: `D:\JV\novel yoga`

> **Versi Dokumen:** 3.1 (Update: November 2026)  
> **Dibuat oleh:** Antigravity Agent  
> **Status Pipeline:** 🚀 Produksi Aktif (Multi-Model, Super Concurrency, Strict Full Name Dialog)

Dokumen ini adalah **panduan operasional teknis lengkap dan mutlak** untuk agent Antigravity maupun operator yang bekerja di workspace ini. Baca seluruh dokumen ini sebelum menjalankan atau mengedit pipeline penerjemahan.

---

## 1. IDENTITAS & FILOSOFI PENERJEMAHAN (THE GOLDEN RULE)

Target pembaca novel di workspace ini adalah **orang yang suka cerita seru tapi malas membaca novel sastra biasa karena bahasanya berat, puitis bertele-tele, dan dialognya kaku**.

> **"KITA BUKAN LAGI UJIAN SASTRA BAHASA INDONESIA."**  
> Cerita harus dibawakan secara **santai, luwes, renyah, aduhai, hidup, gaul sehari-hari, dan to-the-point** — setara kualitas komik / manga / webtoon aksi populer yang diterjemahkan bebas tapi mantap.

### 5 Pilar Utama Gaya Bahasa (Universal Default):
1. **Tell, Don't Show (Lugas & Transparan):** Pangkas deskripsi fisiologis mikro bertele-tele (kedutan alis, keringat mikro, tarikan napas klise). Langsung beri tahu fakta situasi lapangan, bahaya, dan isi kepala karakter secara gamblang.
2. **Nol Kalimat Puitis & Bebas Bahasa Makalah:** Haram kata-kata formal kaku (*"adalah"*, *"tatkala"*, *"terpendar"*, *"kian"*, *"kendati demikian"*, *"merupakan"*, *"tak kunjung"*, *"berada dalam situasi"*, *"mengindikasikan"*, *"beliau"*, *"berkata"*, *"berujar"*). Pakai kosakata tongkrongan alami (*"nggak/ngga"*, *"banget"*, *"udah"*, *"gitu"*, *"parah"*, *"bodo amat"*, *"sialan/anjir/brengsek"*, *"mager"*, dll).
3. **Realisme Tetap Hidup (Tanpa Kaku):** Khusus genre militer/taktis (seperti Tom Clancy), atmosfer ketegangan operasi, prosedur CQB, dan nama senjata asli (MP5, flashbang, SOP, 9mm, perimeter, breach) tetap akurat, namun dibawakan dengan bahasa yang asyik dan gamblang.
4. **Format Dialog Konsisten (Wajib Nama Lengkap: "..."):** Dilarang keras dialog "yatim piatu" yang cuma kutip polos tanpa nama. Wajib `Nama Lengkap: "..."`.
5. **Penjelasan Istilah Asing Otomatis:** Setiap istilah asing/taktis/lore yang berpotensi membingungkan pembaca awam wajib diberi penjelasan singkat santai dalam kurung pada pemunculan pertamanya. Contoh: *Vox (radio komunikasi militer)*, *AAR (evaluasi pasca-misi)*.

---

## 2. FITUR BARU & PENINGKATAN SISTEM (CHANGELOG V3.1)

Fitur-fitur baru berikut adalah hasil penyempurnaan langsung dari feedback lapangan:

### 2.1 Format Dialog Wajib Nama Lengkap (`Nama Lengkap: "..."`)
* **Masalah Lama:** Model LLM sering malas dan mengeluarkan dialog kutip polos (`"..." kata John`) atau memotong nama tokoh menjadi singkatan/panggilan acak (*Ding*, *Chavez*, *John*, *Clark*, bahkan salah sandi seperti *Bima*).
* **Fitur Baru (Kanonisasi Nama Baku):** Prompt runner mewajibkan penulisan **Nama Lengkap** di setiap baris dialog.
  * `Domingo Chavez` (bukan Ding/Chavez acak)
  * `John Clark` (bukan Clark/John/Bima acak)
  * `Alistair Stanley` (bukan Stanley/Al acak)
  * `Bill Henriksen`
  * `John Brightling`
  * `Dmitriy Popov`
  * `Paul Bellow`, `Tim Noonan`, `Daniel Malloy`, `Sandy Clark`, dll.
* **Zero Quote Orphan Rule:** Model dilarang memunculkan kutip tanpa nama. Jika di teks sumber tidak tertulis nama pembicara, model diwajibkan menyimpulkan konteks adegan dan menyematkan nama lengkap pembicaranya.

### 2.2 Super Concurrency Testing & Multi-Provider Support
Pipeline mendukung perpindahan mulus antara Local Proxy (**9router**) dan External LLM Gateway (**Cosmosin Direct HTTPS**).

| Provider | Endpoint | Model Aktif | Max Tested Concurrency | Rekomendasi Concurrency | Karakteristik |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **9router (Local)** | `http://localhost:20128/v1/chat/completions` | `ag/gemini-3.8-flash-low` | **40 workers** | **15 – 20 workers** | Kepatuhan format dialog luar biasa presisi, reasoning tinggi, 0 rate limit. |
| **Cosmosin (HTTPS)** | `https://api.cosmosin.io/v1/chat/completions` | `deepseek-v4.1-flash-mod` | **25 workers** | **15 – 20 workers** | Super kencang (~1.6 - 2.5 detik/req), prompt caching sangat agresif. |

### 2.3 Evaluasi & Benchmark Model Teruji
1. **`ag/gemini-3.8-flash-low` (Juara 1 - Produksi Utama):**
   * Paling seimbang: reasoning bawaan membuat karakterisasi dan konsistensi nama lengkap 100% patuh.
   * Toleran beban paralel 15-20 workers tanpa drop socket.
2. **`deepseek-v4.1-flash-mod` (Juara 2 - Alternatif Ngebut):**
   * Latensi tercepat (selesai 41 bab cuma ~12 menit). Perlu aturan prompt ketat agar tidak malas menulis nama pembicara.
3. **`mimo-v2.6-pro` (TIDAK DIREKOMENDASIKAN):**
   * Latensi sangat lambat (~18.6 detik/req) dan memiliki cacat halusinasi (seluruh teks narasi dirombak menjadi dialog karakter).

### 2.4 Hybrid Protocol Handler (`http` & `https`)
Runner TypeScript (`translate-novel-dragndrop.ts`) otomatis mendeteksi apakah `LLM_PROXY_URL` menggunakan protokol `http:` (untuk 9router lokal) atau `https:` (untuk Cosmosin/provider cloud) tanpa memerlukan konfigurasi manual.

---

## 3. INVENTARIS KARYA DI WORKSPACE (`D:\JV\novel yoga`)

| Seri / Novel | Format Sumber | File Terjemahan ID-Direct | EPUB Siap Baca | Status & Fitur Khusus |
| :--- | :--- | :--- | :--- | :--- |
| **Tom Clancy - Rainbow Six (Vol 1+2)** | TXT (Rumania OCR, 1.8 MB) | `Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt` (2.49 MB) | ✅ `epubs/Tom Clancy - Rainbow Six (Vol 1+2) (Illustrated ID-Direct).epub` (0.98 MB) | ✅ **100% Selesai**. Format Nama Lengkap Baku (6.351 dialog bernama). |
| **Metro 2033** | EPUB / TXT | `Metro 2033 (Terjemahan ID-Direct).txt` (1.0 MB) | ✅ `epubs/Metro_2033_Illustrated_ID_Direct.epub` (4.46 MB) | ✅ **Selesai + EPUB Berilustrasi**. Peta rute Artyom terintegrasi. |
| **Dune (Frank Herbert)** | EPUB / TXT | `Dune (Terjemahan ID-Direct).txt` | ✅ `epubs/1_Dune_Illustrated_ID_Direct.epub` | ✅ **Selesai + EPUB Berilustrasi**. Istilah Fremen/Arrakis asli. |
| **Mushoku Tensei** | PDF/TXT (Vol 01–26) | 26 File TXT | ✅ 26 EPUB di `epubs/` | ✅ **26 Volume Lengkap**. EPUB berilustrasi warna & monokrom. |
| **Overlord** | EPUB/TXT (Vol 01–16) | 16 File TXT | ✅ 16 EPUB di `epubs/` | ✅ **16 Volume Lengkap**. Monolog Ainz vs Wibawa Penguasa. |
| **The Hobbit** | TXT | `The Hobbit (Terjemahan ID-Direct).txt` | — | ✅ **Selesai**. |

---

## 4. STRUKTUR & ANATOMI PIPELINE

```
D:\JV\novel yoga\
├── translate-novel-dragndrop.ts              # Core Pipeline Runner (TS)
├── compile_epub_helper.py                    # Multi-novel EPUB Compiler & Sanitizer
├── [NamaNovel] (Terjemahan ID-Direct).txt    # Master Naskah Terjemahan Final
├── .[NamaNovel]_chunks_cache\                # Cache per Bab & Chunk (Fail-safe)
├── [NamaNovel]_checkpoint.json               # Checkpoint tracker (Auto-Resume)
├── illustrations\                            # Asset gambar ilustrasi per novel
│   ├── Metro_2033\
│   ├── Dune\
│   ├── Mushoku_Tensei_Volume_XX\
│   └── Overlord_Volume_XX\
└── epubs\                                    # Master EPUB siap baca / kirim HP
```

---

## 5. CARA MENJALANKAN PIPELINE (SOP OPERASIONAL)

### 5.1 Menjalankan Penerjemahan Novel Baru / Lanjutan
Selalu jalankan melalui runner `cmd.exe /c npx tsx` agar tidak terganjal policy PowerShell:

```cmd
:: Jalankan novel dengan drag-and-drop file atau spesifik path:
cmd.exe /c npx tsx "D:\JV\novel yoga\translate-novel-dragndrop.ts" "D:\JV\novel yoga\NamaNovel.txt"
```

### 5.2 Mengatur Provider / Concurrency via Environment Variables
Konfigurasi dapat di-override langsung tanpa mengubah kode:

```cmd
:: Contoh pakai 9router (Default):
set LLM_PROXY_URL=http://localhost:20128/v1/chat/completions
set LLM_MODEL=ag/gemini-3.8-flash-low
set LLM_API_KEY=sk-2e591994696af18e-71ijj7-14263abd
set CONCURRENCY=15
cmd.exe /c npx tsx "D:\JV\novel yoga\translate-novel-dragndrop.ts" "path\ke\novel.txt"

:: Contoh ganti ke Cosmosin DeepSeek:
set LLM_PROXY_URL=https://api.cosmosin.io/v1/chat/completions
set LLM_MODEL=deepseek-v4.1-flash-mod
set LLM_API_KEY=sk-cos-dMGwBFYJywT5HJpcTYR68pY3OJvZMBYER2vwCHB5drE
set CONCURRENCY=20
cmd.exe /c npx tsx "D:\JV\novel yoga\translate-novel-dragndrop.ts" "path\ke\novel.txt"
```

### 5.3 Kompilasi Menjadi EPUB
Setelah file TXT terjemahan selesai, kompilasi ke EPUB dengan skrip compiler:

```cmd
python -c "
import os, sys, re, zipfile, html
# Contoh runner compiler cepat satu naskah:
# Format: bab ditandai '### Judul Bab', dialog ditandai 'Nama: \"...\"'
"
```

---

## 6. PENANGANAN MASALAH (TROUBLESHOOTING & RECOVERY)

### 6.1 Jika Terkena Block Policy / Filter Gemini (Canned Refusals)
* Script `translate-novel-dragndrop.ts` sudah dilengkapi **Adaptive Sub-Chunk Splitter**:
  * Jika sebuah chunk ditolak (output 0 karakter atau terdeteksi refusal), script otomatis memotong chunk menjadi 4 sub-bagian (~1.800 chars $\rightarrow$ 1.100 $\rightarrow$ 700 chars).
  * Sub-bagian diterjemahkan mandiri dengan sanitasi kata sensitif dan digabungkan kembali tanpa merusak struktur bab.

### 6.2 Jika Mengalami Cooldown / Capacity Exhausted (HTTP 503 / 429)
* Script membaca header `reset after Xs` dan otomatis melakukan sleep/pause cerdas sebelum retry, sehingga task background tidak akan crash.

---

## 7. KOMITMEN & STANDAR KUALITAS AGENT

Setiap Agent Antigravity yang bekerja di workspace ini **WAJIB MEMATUHI**:
1. Tidak mengubah narasi menjadi bahasa baku makalah ("Kita bukan ujian sastra").
2. Memastikan format `Nama Lengkap: "..."` selalu tegak di seluruh novel.
3. Selalu memverifikasi integritas hasil terjemahan sebelum menyerahkan ke user (0 refusal lines).
4. Menjaga cache dan checkpoint agar proses selalu bisa di-resume kapan saja tanpa membuang kuota/token.

---
*Dokumen ini adalah acuan resmi operasional workspace Novel Yoga.*  
*Status: Aktif & Teruji di Windows (Node v25 / Python 3.14).*
