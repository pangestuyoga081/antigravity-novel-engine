# ==============================================================================
# ANTIGRAVITY ENGINE: ARCHITECTURAL DECISIONS RECORD (ADR)
# ==============================================================================

### ADR-001: Adopsi Semantic Tag Dibanding Raw JSON untuk Translasi Bab
- **Tanggal**: 2026-11-24
- **Konteks**: Muncul perdebatan apakah LLM sebaiknya mengeluarkan JSON terstruktur atau naskah mengalir berformat Semantic Tag (`[CAST]`, `[GLOSSARY]`, `[SPEAKER]`).
- **Keputusan**: Mengadopsi **Semantic Tag**.
- **Alasan**:
  1. Naskah cerita novel adalah teks mengalir panjang; jika dimasukkan ke dalam atribut JSON `"body"`, tanda petik ganda (`"`) dan backslash (`\`) rentan merusak parser JSON (Syntax Error fatal).
  2. Format teks bertag tetap manusiawi dan nyaman dibaca langsung di Notepad/HP tanpa harus dikompilasi ke EPUB.
  3. Menghemat kuota output token LLM hingga 25% dibanding sintaks JSON yang repetitif.

### ADR-002: Arsitektur Three-Pass Pipeline (Scout -> Translate -> QA Audit)
- **Tanggal**: 2026-11-24
- **Konteks**: Translasi berbasis chunk sering inkonsisten dalam memanggil nama dan sering salah membedakan tokoh utama vs figuran.
- **Keputusan**: Wajibkan Pass 1 (Scout) sebelum menerjemahkan, dan Pass 3 (QA Validator) setelah selesai bab.
- **Alasan**: Memberikan LLM konteks global per bab sehingga hasil translasi chunk memiliki kesinambungan nada dan karakter.

### ADR-003: Living Universe Profile (Dynamic YAML Memory)
- **Tanggal**: 2026-11-24
- **Konteks**: File YAML statis tidak mampu menangkap tokoh baru yang muncul di pertengahan cerita (Bab 2+).
- **Keputusan**: Modul `update_living_profile.py` otomatis mengevolusi file konfigurasi profil YAML setiap kali Pass 1 menemukan entitas baru.

### ADR-004: Kebijakan Resolusi Gambar (Uncompressed Original vs Proxy Optimization)
- **Tanggal**: 2026-11-24
- **Konteks**: Batas proxy web viewer (2 MB) memicu kompresi gambar otomatis, namun user secara eksplisit meminta kualitas gambar dipertahankan apa adanya ("udah gak usah di kompresi gapapa apa adanya aja tuh gambar").
- **Keputusan**: Kualitas visual asli adalah prioritas bila diminta user. Pipeline gambar mendukung flag opt-in kompresi bila perlu melewati batas proxy, namun secara default membiarkan gambar asli tetap tajam dan utuh bila diinginkan user.

### ADR-005: Eliminasi Karakter Penanda Visual dalam Tautan Interaktif EPUB
- **Tanggal**: 2026-11-24
- **Konteks**: Karakter teks seperti `<span class="lore-tag">?</span>` yang ditaruh di dalam tag `<a>` bocor ke judul jendela pop-up modal Moon+ Reader menjadi `Andrey?` atau `Pyotr?`.
- **Keputusan**: Tautan `<a>` untuk tokoh dan glosarium HANYA memuat teks nama murni. Indikator interaktif sepenuhnya dikontrol via CSS (`text-decoration: underline dotted #0284c7;`).

### ADR-006: Pemisahan Eksplisit Badge Faksi dan Nama Pembicara (`&nbsp;`)
- **Tanggal**: 2026-11-24
- **Konteks**: Tag `<span class="faction-badge">` dan `<span class="speaker">` menempel tanpa spasi (`RANGERArtyom`) pada engine reader mobile akibat collapse margin pada inline elements.
- **Keputusan**: Wajib menyisipkan `&nbsp;` di antara badge faksi dan span speaker di seluruh template HTML output.

### ADR-007: Fleksibilitas Parser Dialog Ber-Atribusi Naratif
- **Tanggal**: 2026-11-24
- **Konteks**: Naskah novel sering kali memuat narasi setelah dialog penutup (contoh: `Andrey: "Bagus deh!" sindir Andrey sinis.`). Pola regex yang mewajibkan `$` di akhir tanda petik menyebabkan baris tersebut gagal terdeteksi sebagai dialog.
- **Keputusan**: Gunakan regex fleksibel `r"^([^:\n]+?):\s*([\"“].*)$"` dan konversi pasangan petik menjadi entitas tipografi `&#8220;...&#8221;`.

### ADR-008: Automated EPUB QA Gate (`EPUBValidator`)
- **Tanggal**: 2026-11-25
- **Konteks**: Bug seperti tag `[GLOSSARY:]` bocor, hilangnya `epub:type="noteref"`, atau entitas XML ilegal (`&nbsp;`) baru ketahuan setelah dibuka manual di Moon+ Reader.
- **Keputusan**: Setiap proses build di `compile_epub_helper.py` otomatis menjalankan `EPUBValidator.validate_epub()` di akhir kompilasi untuk memverifikasi XML well-formedness, keutuhan pop-up `noteref`/`aside`, zero-leak tag semantik, dan validitas label speaker dialog (tanpa membatasi ukuran file).

### ADR-009: Sistem Lore Anti-Spoiler Progresif (`since_chapter` & `roles`)
- **Tanggal**: 2026-11-25
- **Konteks**: Kamus lore global dari YAML berisiko membocorkan informasi karakter bab akhir kepada pembaca yang masih berada di bab awal.
- **Keputusan**: `load_lore_dict()` mendukung `since_chapter` dan `roles` per bab, serta akumulasi lore bab berjalan secara maju (`chapter 1..N`) tanpa pernah bocor mundur ke bab sebelumnya.
