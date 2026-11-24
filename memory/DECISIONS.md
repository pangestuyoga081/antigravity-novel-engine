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
