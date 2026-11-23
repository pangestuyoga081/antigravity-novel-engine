# AGENTS.md — Panduan Lengkap Novel Translator Pipeline (Direct & Gaul)
## Antigravity Agent | Workspace: `D:\JV\novel yoga`

> **Versi Dokumen:** 3.5 (Update: November 2026 — Zero-Hallucination & Anti-Prompt-Leak Edition)  
> **Dibuat oleh:** Antigravity Agent  
> **Status Pipeline:** 🚀 Produksi Aktif (Multi-Model, Super Concurrency, Strict Full Name Dialog, Git Auto-Sync)

Dokumen ini adalah **panduan operasional teknis lengkap dan mutlak** untuk agent Antigravity maupun operator yang bekerja di workspace ini. Baca seluruh dokumen ini sebelum menjalankan atau mengedit pipeline penerjemahan.

---

## 1. IDENTITAS & FILOSOFI PENERJEMAHAN (THE GOLDEN RULE)

Target pembaca kita adalah orang dewasa/remaja yang ingin membaca kisah petualangan, fantasi, aksi militer, dan space opera dengan gaya **luwes, santai, hidup, to-the-point, dan tanpa sensor**. 

### 🛡️ ATURAN ANTI-HALUSINASI & ANTI-JOKES OVERUSE (MUTLAK):
1. **STRICT CONTEXTUAL FIDELITY (NOL MONOLOG BATIN PALSU):**
   - Karakter hanya boleh memiliki pikiran batin yang sesuai dengan teks sumber dan latar belakang aslinya!
   - **BANNED TOTAL:** DILARANG menyelipkan lelucon garing *"budak korporat"*, *"salaryman"*, *"takut kena SP"*, *"laporan bulanan jeblok"*, atau *"pengen resign"* ke tokoh yang bukan karyawan kantor (misalnya Paul Atreides di *Dune*, John Clark di *Rainbow Six*, atau Issei Hyoudou di *High School DxD*).
2. **ZERO CROSS-UNIVERSE CONTAMINATION:**
   - Dilarang keras menyisipkan nama karakter, jurus, atau istilah dari semesta novel lain (misalnya karakter Ainz/Overlord atau istilah Kwisatz Haderach/Dune nyasar ke novel lain).
3. **ZERO PROMPT LEAKS:**
   - Output model AI wajib disaring ketat sebelum disimpan. Tidak boleh ada teks canned response sistem (*"Jika Anda ingin menulis ulang..."*, *"Permintaan ini meminta..."*) yang lolos ke naskah maupun EPUB.

---

## 2. FORMAT DIALOG KONSISTEN (NAMA LENGKAP)

Setiap dialog tuturan langsung **WAJIB** diawali nama lengkap pembicara:
- `James Holden: "..."`
- `Joe Miller: "..."`
- `Issei Hyoudou: "..."`
- `Rias Gremory: "..."`
- `Harry Potter: "..."`
- `Hermione Granger: "..."`

Dilarang keras menyisakan dialog tanpa nama pembicara atau hanya menggunakan tanda petik kosong!

---

## 3. ENGINE & SINKRONISASI OTOMATIS GITHUB

Repositori resmi: `https://github.com/pangestuyoga081/antigravity-novel-engine`

- Setiap penambahan script baru, optimasi pipeline, pembersihan naskah, atau update memori chat Antigravity **WAJIB langsung di-commit dan di-push** ke remote repository agar PC lain dapat langsung melakukan `git pull` dan melanjutkan sesi kerja tanpa hambatan.
- File migrasi 1-klik: `RESTORE_CHAT_KE_PC_INI.bat` dan arsip `antigravity_conversation_backup.zip` selalu disinkronkan.
