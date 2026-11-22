# Ruidrive & Ruisafe Link Extractor Guide for Antigravity Agents

Panduan ini dirancang untuk agen Antigravity agar dapat melanjutkan tugas pembongkaran (*scraping* & *bypass*) tautan unduhan dari situs **Ruidrive** dan safelink **Ruisafe** di perangkat (PC) mana pun secara cepat dan otomatis.

---

## 1. Konsep & Arsitektur Website

### A. Ruidrive (`ruidrive.com`)
* **Platform:** Blogger (Blogspot) kustom.
* **Halaman Induk Seri (Hub Page):** Berisi detail anime/LN/manga dan daftar volume yang dimuat melalui Blogger Feed API:
  ```http
  https://www.ruidrive.com/feeds/posts/default/-/<Series Label>?orderby=published&alt=json&max-results=999
  ```
* **Halaman Post Volume:** Setiap volume memiliki postingan tersendiri (misal: Volume 01, Volume 02, dst.).
* **Tautan Unduhan:** Pada HTML mentah (*server-side HTML*), tautan unduhan langsung (**MediaFire, Google Drive, Mega, Terabox, Krakenfiles, drop.download**) sebenarnya **sudah tertanam langsung di elemen `<a>`**. Skrip safelink JavaScript baru mengubahnya di sisi browser pengguna (*client-side*).

### B. Ruisafe Safelink (`ruisafe*.blogspot.com`)
* Safelink ini membungkus tautan unduhan asli ke dalam query parameter `url` dengan format **Base64**:
  ```text
  https://ruisafe5.blogspot.com/...?...url=<BASE64_ENCODED_URL>
  ```
* **Cara Bypass:** Cukup ambil nilai parameter `url` dan lakukan `base64.b64decode()`. Tidak perlu membuka browser, menunggu hitungan detik (*countdown*), atau menyelesaikan verifikasi apa pun.

---

## 2. Cara Kerja Agen Saat Menerima Request User

### Skenario 1: User mengirimkan satu link Ruisafe
* **Contoh input:** `https://ruisafe5.blogspot.com/2025/07/...html?url=aHR0cHM6Ly9...`
* **Tindakan Agen:**
  1. Ambil nilai parameter `url=...`.
  2. Dekode nilai tersebut dari Base64.
  3. Berikan tautan langsung (MediaFire/GDrive/dll) ke user.

### Skenario 2: User mengirimkan link halaman seri Ruidrive
* **Contoh input:** `https://www.ruidrive.com/2021/10/kono-subarashii-sekai-ni-shukufuku-wo.html`
* **Tindakan Agen:**
  1. Jalankan script bawaan `extractor.py` dengan URL tersebut:
     ```powershell
     python extractor.py "<URL_SERI>"
     ```
  2. Format output jawaban untuk user dengan struktur standar (lihat format output di bawah).

---

## 3. Format Standar Jawaban untuk User

Selalu sajikan jawaban dengan 2 bagian utama:

1. **Kumpulan Tautan MediaFire (Ready to Copy):**
   Gunakan blok kode ` ```text ` agar user bisa 1-klik salin semua tautan ke Download Manager (IDM / JDownloader).
   ```text
   https://www.mediafire.com/file/.../Volume_01.rar/file
   https://www.mediafire.com/file/.../Volume_02.rar/file
   ...
   ```

2. **Daftar Rinci Per Volume:**
   Tampilkan nomor volume, tautan artikel Ruidrive, tautan MediaFire, dan alternatif host (Google Drive, Mega, Terabox, dll).

---

## 4. Script Otomasi: `extractor.py`

Di folder ini tersedia skrip `extractor.py` yang hanya menggunakan library standar Python 3 (tanpa perlu `pip install`).

### Penggunaan CLI:

* **Untuk satu link Ruisafe (decode langsung):**
  ```powershell
  python extractor.py "https://ruisafe5.blogspot.com/.../?url=aHR0cHM6..."
  ```

* **Untuk satu seri penuh Ruidrive (semua volume):**
  ```powershell
  python extractor.py "https://www.ruidrive.com/2026/01/light-novel-rokudenashi-majutsu-koushi-to-akashic-records.html"
  ```

---

## 5. Tips Pemecahan Masalah (Troubleshooting)

* **Label Seri tidak terdeteksi otomatis:**
  Buka source HTML halaman seri, cari string `/feeds/posts/default/-/` untuk melihat nama tag/label Blogger yang dipakai oleh postingan tersebut.
* **Volume tidak berurutan:**
  Blogger feed mengurutkan secara kronologis terbitan (`published`). Skrip sudah otomatis mengekstrak nomor volume dari judul menggunakan ekspresi reguler `Volume\s+([\d\.]+)` dan mengurutkannya secara numerik.
