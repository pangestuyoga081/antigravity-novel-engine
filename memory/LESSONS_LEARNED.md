# ==============================================================================
# ANTIGRAVITY ENGINE: PERMANENT LESSONS LEARNED
# ==============================================================================

## Aturan Emas Pembelajaran (Golden Rules)

### 1. Regex Buta Konteks vs LLM Semantik
- **Masalah**: Skrip regex mencoba mengekstrak istilah dan tanda kurung dari naskah jadi footnote, berujung merusak dialog biasa, double escaping (`&lt;a id...&gt;`), dan memotong kalimat salah.
- **Penyebab**: Regex tidak paham tata bahasa, sintaksis, atau semantik cerita.
- **Aturan**: Gunakan **Semantic Tag** langsung dari LLM (`[CAST: ...]`, `[GLOSSARY: ...]`, `[SPEAKER: ...]`). Skrip compiler hanya bertindak sebagai parser tag deterministik, BUKAN penebak pola teks naskah.

### 2. Standar Footnote EPUB 3 Anti-Mental
- **Masalah**: Saat link glosarium atau nama tokoh di-tap di reader HP tertentu, pembaca malah dilempar ke awal bab atau ke akhir bab tanpa modal pop-up.
- **Penyebab**: Tag target `<aside>` memuat link balik `href="#fnref_..."`. Jika e-reader tidak mendukung pop-up bawaan, klik tersebut mengeksekusi navigasi URL anchor dan me-refresh scroll ke atas.
- **Aturan**: Gunakan `<dfn>` atau `<abbr>` dan link pop-up murni tanpa back-link `href` balik di dalam `<aside>` agar reader tidak memicu aksi navigasi halaman.

### 3. CSS Reader-Theme Agnostic
- **Masalah**: Teks atau badge tidak terbaca / background aneh ketika pembaca ganti ke mode Dark, Sepia, atau AMOLED Black.
- **Penyebab**: Warna hardcoded (`background-color: #fafafa`, `color: #1a1a1a`).
- **Aturan**: Seluruh body, paragraf, dan container WAJIB memakai `background-color: transparent` dan `color: inherit`. Komponen UI (badge/drawer) HANYA boleh memakai `rgba()` dengan saturasi tipis (0.12 - 0.20) agar menyatu dengan warna dasar tema apa pun.

### 4. Peta & Galeri Gambar Wajib Modular (Opt-In)
- **Masalah**: Potongan gambar peta menyela di tengah bab mengganggu ritme membaca, atau peta buku lain (The Hobbit / Metro 2034) salah masuk ke Metro 2033.
- **Penyebab**: Pengecekan nama file gambar umum (`00003.jpeg`) tanpa memverifikasi judul buku, dan penyisipan peta langsung di badan bab.
- **Aturan**: Potongan peta rute dipisah ke halaman lampiran atau dinonaktifkan secara default dari alur teks bab utama. Peta buku lain haram disuntikkan tanpa pencocokan ketat `base_name`.

### 5. Living Universe Profile Harus Berkembang Tiap Bab
- **Masalah**: Karakter yang muncul di pertengahan cerita (Bab 2+) tidak memiliki badge faksi atau penjelasan tooltip.
- **Penyebab**: File profil YAML bersifat statis.
- **Aturan**: Setiap bab yang selesai di-scout WAJIB memicu `update_living_profile.py` untuk mendaftarkan tokoh, faksi, dan istilah baru ke file YAML disk secara otomatis.

### 6. Batas Transfer Proxy & Kompresi Aset EPUB
- **Masalah**: Unduhan gagal di HP dengan `HTTP 500: Reassembly byte limit exceeded (2097152 bytes)`.
- **Penyebab**: Arsip EPUB membengkak di atas 2 MB karena menumpuk file gambar tak terpakai dan resolusi asli kamera/render tanpa kompresi.
- **Aturan**: Compiler EPUB wajib menerapkan filter gambar berbasis referensi naskah nyata (hanya yang dipakai yang di-pack) dan melakukan kompresi otomatis via PIL (max width 1200px, JPEG quality 75). Target ukuran EPUB akhir harus selalu < 2.0 MB.

### 7. Resolusi Nama Tokoh Multi-Kata & Alias
- **Masalah**: Nama tokoh dialog (`Pyotr: "..."`) tidak terhubung ke tooltip glosarium.
- **Penyebab**: Nama entri profil ditulis formal (`Pyotr Andreevich`), sedangkan dialog naskah menggunakan nama panggilan santai.
- **Aturan**: Parser profil lore wajib otomatis meregistrasikan kata pertama (`cname.split()[0]`) dan list aliases ke kamus lore, dan compiler dialog harus memiliki fallback matching kata pertama.
