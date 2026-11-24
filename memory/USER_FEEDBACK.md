# ==============================================================================
# ANTIGRAVITY ENGINE: USER FEEDBACK LEDGER
# ==============================================================================

Format: Tanggal | Keluhan User | Akar Masalah | Solusi & Fix | Status

| Tanggal | Keluhan User | Akar Masalah | Solusi & Fix | Status |
|---|---|---|---|---|
| 2026-11-24 | Glosarium/nama diklik mental ke awal bab di reader tertentu | Back-link di `<aside>` memicu lompatan anchor pada reader yang tidak punya modal pop-up bawaan | Hapus tag anchor back-link di dalam `<aside>`, gunakan struktur tooltip murni EPUB 3 | IN_PROGRESS |
| 2026-11-24 | Warna background & teks aneh/bertabrakan di tiap tema reader | Hardcoded background-color & text-color di root CSS (`#fafafa`, `#1a1a1a`) | Hapus seluruh hardcoded colors di body/p; gunakan `color: inherit` & `background-color: transparent`; badge pakai `rgba()` | IN_PROGRESS |
| 2026-11-24 | Potongan gambar peta rute mengganggu alur membaca | Tag `[[ILUSTRASI:map_route...]]` disematkan langsung di badan cerita pembuka bab | Peta rute dipisahkan dari badan naskah utama atau dibuat flag opt-in/lampiran | IN_PROGRESS |
| 2026-11-24 | Peta Middle-Earth & logo Twitter nyasar di novel Metro | Gambar `00003.jpeg` dicek tanpa filter nama buku | Tambahkan proteksi ketat `if "hobbit" in base_name.lower()` | DONE |
| 2026-11-24 | Teks bocor kode HTML `<a id="fnref_38"...>` | Double escaping: teks di-escape setelah disuntik tag HTML | Ubah urutan: escape teks mentah terlebih dahulu, baru suntikkan tag semantik | DONE |
| 2026-11-24 | Penjelasan kurung ganda bertumpuk dengan tooltip `*flamethrower* (senjata pelontar...)` | Prompt lama memaksa output istilah (penjelasan dalam kurung) | Bersihkan kurung penjelasan dari naskah luring dan pindahkan murni ke tooltip | DONE |
| 2026-11-24 | Drawer tokoh dipenuhi figuran acak (Prajurit 1, Prajurit 2) | Script mengambil semua string sebelum tanda petik dua | Gunakan tag semantik `[CAST]` terkurasi langsung dari hasil Scout LLM | DONE |
