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

### 8. Tipografi Tautan Pop-Up & Robust Dialogue Parsing
- **Masalah**: Muncul tanda tanya `?` di nama tokoh dan judul pop-up (`Andrey?`), badge faksi menempel ke nama (`RANGERArtyom`), dan kalimat dialog dengan atribusi narasi di belakang tanda kutip gagal terdeteksi sebagai dialog.
- **Penyebab**:
  (1) Tag `<span class="lore-tag">?</span>` berada di dalam tag `<a>` sehingga diindeks sebagai bagian teks link oleh e-reader.
  (2) Margin CSS badge di-collapse saat bersanding dengan inline span di WebKit mobile reader.
  (3) Regex `r"^([^:]+?):\s*\"(.*)\"$"` mewajibkan kutip penutup di akhir baris persis (`$`).
- **Aturan**:
  (1) Haram menyuntikkan karakter teks ke dalam `<a>` tautan istilah/tokoh; gunakan border-bottom dotted CSS murni.
  (2) Wajib menyisipkan `&nbsp;` eksplisit di antara badge faksi dan nama pembicara.
  (3) Regex dialog harus fleksibel menangkap narasi pasca-kutip: `r"^([^:\n]+?):\s*([\"“].*)$"` dan mengonversi pasangan kutip ke entitas tipografi `&#8220;...&#8221;`.

### 9. Eliminasi Redundansi Judul di Isi Pop-Up Modal
- **Masalah**: Pop-up e-reader menampilkan judul dua kali secara bertumpuk (header: `cewek Tsundere`, isi: `• cewek Tsundere: tipe cewek...`).
- **Penyebab**: Tag `<aside>` membungkus teks dengan `<strong>&bull; {title}:</strong> {desc}` padahal browser/e-reader sudah otomatis mengekstrak `{title}` dari teks link sebagai header modal.
- **Aturan**: Tag `<aside>` HANYA boleh memuat teks deskripsi murni `{html.escape(desc)}` tanpa mengulang `{title}`. Tampilan pop-up menjadi ringkas, fokus, dan tidak repetitif.

### 10. Ekstraksi Term Penjelasan Kurung Presisi Tinggi (Anti-Greedy)
- **Masalah**: Link tooltip mengambil kata kerja/partikel sebelum istilah (contoh: `bikin harem`, `alias bloodlust`, `cewek Tsundere`).
- **Penyebab**: Parser regex memotong 2-4 kata sebelum kurung secara buta konteks tanpa memeriksa jenis kata.
- **Aturan**:
  (1) Jika kata berhuruf kecil semua, ambil HANYA kata terakhir sebagai term (`bikin` -> lead-in, `harem` -> term).
  (2) Jika kata berhuruf kapital (Title-Case/Akronim), telusuri kata kapital berurutan ke belakang (`Sacred Gear`, `VDNKh`).
  (3) Jika kata berformat markdown bintang (`*term*`), ambil murni teks di dalam bintang.
  (4) Kata-kata sebelum term wajib diisolasi sebagai lead-in di luar tag link `<a>`.

### 11. Moon+ Reader Footnote Decorator & Speaker Label Isolation
- **Masalah**: Muncul tanda tanya superscript `?` di setiap nama speaker dialog (`Pyotr?:`, `Andrey?:`, `Artyom?:`) dan header pop-up (`Andrey?`).
- **Penyebab**: Compiler membungkus setiap nama speaker dialog dalam `<a href="..." epub:type="noteref">`. E-reader (terutama Moon+ Reader) otomatis menyuntikkan icon `?` pada elemen ber-`epub:type="noteref"` yang teksnya bukan berupa angka catatan kaki. Selain itu, mengubah nama speaker di setiap kalimat dialog menjadi tautan footnote sangat mengotori alur baca.
- **Aturan**:
  (1) Nama speaker dalam dialog (`Speaker: "..."`) WAJIB murni teks penanda dialog tebal (plus badge faksi), HARAM dibungkus menjadi tautan footnote. Karakter kunci bab sudah diwadahi secara elegan di Cast Drawer atas bab.
  (2) Untuk tautan istilah/glosarium dalam narasi (`lore-ref`), HAPUS atribut `epub:type="noteref"` dari tag `<a>` (gunakan `<a id="{fnref}" href="#{fn}" class="lore-ref">{term}</a>`). Pertahankan `epub:type="footnote"` hanya pada elemen target `<aside>` agar modal pop-up tetap aktif tanpa memicu dekorasi icon `?` di layar pembaca.

### 12. Karantina Aset Gambar Antar-Buku
- **Masalah**: EPUB Metro 2033 membengkak dan memicu error `HTTP 500: Reassembly byte limit exceeded` karena gambar ilustrasi berwarna High School DxD ikut terkemas ke dalam Metro 2033.
- **Penyebab**: Compiler memindai direktori `High School DxD` secara serakah tanpa memeriksa `base_name` buku yang sedang dirakit.
- **Aturan**: Direktori gambar khusus suatu waralaba/judul HANYA boleh diakses jika nama buku yang sedang dirakit secara spesifik memuat kata kunci buku tersebut (`if "dxd" in base_name.lower()`). Isolasi ini menurunkan ukuran EPUB Metro 2033 dari 1.68 MB menjadi 0.86 MB, menjamin kelancaran unduhan di bawah limit proxy 2 MB.
