# ==============================================================================
# ANTIGRAVITY ENGINE: SYSTEM ERROR LOG
# ==============================================================================

### [2026-11-24] EPUB XML & Reader Rendering Anomalies
1. **Error**: Tag HTML bocor ke teks naskah pembaca (`&lt;a id="fnref_38"...&gt;`).
   - *Impact*: Pembaca melihat kode mentah HTML di layar HP.
   - *Root Cause*: `html.escape()` dipanggil setelah fungsi regex link injection selesai mengeksekusi string.
   - *Mitigation*: Escape seluruh entitas teks dialog dan narasi SEBELUM link semantik dirakit.

2. **Error**: Peta Middle-Earth dan ikon Twitter muncul di novel Metro 2034.
   - *Impact*: Halaman pembuka novel Metro memuat gambar dan judul *The Hobbit*.
   - *Root Cause*: Cek keberadaan file gambar generik `00003.jpeg` memicu blok rendering Middle-Earth.
   - *Mitigation*: Validasi nama buku secara ketat: `if "hobbit" in base_name.lower():`.

3. **Error**: Broken Image Placeholder (Kotak Toska/Biru Rusak) di Bab 12 Metro 2034.
   - *Impact*: Muncul kotak kecil rusak di tengah teks cerita saat dibaca di Moon+ Reader.
   - *Root Cause*: Teks deskripsi ilustrasi `[[ILUSTRASI: Escalator runtuh...]]` dirender jadi `<img src="...">` padahal file gambar fisiknya belum dibuat.
   - *Mitigation*: Tambahkan `available_images` whitelist filter; hanya tag yang gambarnya ada secara fisik di arsip ZIP yang boleh dibuat tag `<img>`.
