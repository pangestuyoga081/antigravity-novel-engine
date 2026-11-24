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

4. **Error**: Download File Gagal - `HTTP 500: Reassembly byte limit exceeded (2097152 bytes)`.
   - *Impact*: Pembaca di smartphone tidak bisa mengunduh file EPUB dari web viewer.
   - *Root Cause*: Ukuran berkas EPUB (4.71 MB) melebihi batas buffer perantara proxy internal (maksimal 2.0 MB / 2,097,152 bytes) karena menyertakan 11 gambar peta rute resolusi tinggi yang tidak lagi dipakai serta peta jaringan kota berukuran 1.48 MB tanpa kompresi.
   - *Mitigation*: Terapkan filter ketat hanya mengemas gambar yang dirujuk di naskah/cover, serta kompresi otomatis gambar menggunakan PIL (max width 1200px, JPEG quality 75) saat build EPUB. Ukuran berkas berhasil ditekan ke 891 KB (< 1 MB).

5. **Error**: Karakter Dialog Tidak Memiliki Tooltip Pop-up (Kasus `Pyotr`).
   - *Impact*: Nama tokoh pembicara (`Pyotr: "..."`) tidak memiliki indikator `?` dan tidak bisa diklik.
   - *Root Cause*: Nama entri di YAML adalah `Pyotr Andreevich`, sedangkan dialog menggunakan nama pendek `Pyotr`. String lookup gagal karena hanya mencocokkan exact key.
   - *Mitigation*: Auto-registrasikan kata pertama dan alias karakter ke `lore_map` serta tambahkan fallback matching kata pertama saat parsing baris dialog.
