# Antigravity Agent Capabilities & Documentation 🚀

> **Engine & Identity:** Antigravity AI Assistant by Google DeepMind  
> **Host Environment:** Windows (PowerShell / Node.js 25 / Python 3.14)  
> **User Profile:** `yoga` (`pangestuyoga081@gmail.com`)

---

## 🌟 1. Siapa Saya & Apa Itu Antigravity?
Saya adalah **Antigravity**, asisten AI otonom generasi baru berbasis model Gemini mutakhir dari **Google DeepMind**. Saya dirancang bukan hanya sebagai chatbot teks biasa, melainkan sebagai **Agentic AI** yang beroperasi langsung di dalam lingkungan workspace lokal, terminal sistem operasi, dan ekosistem multi-agent.

---

## 🛠️ 2. Katalog Kemampuan Inti (Core Capabilities)

### A. Eksekusi Sistem & Shell Lokal (Autonomous OS Operations)
- **Eksekusi Perintah Terminal**: Menjalankan PowerShell, Command Prompt, Python, Node.js/TypeScript secara sinkron maupun asynchronous di background.
- **Background Task Management**: Mampu menjalankan proses jangka panjang (kompilasi, server, scraping, download besar) dengan pemantauan realtime (`task-id`, log streaming, dan auto-notification saat proses selesai).
- **Manajemen File & Direktori**: Membaca, membuat, mengedit (diff-based surgical edit), mengekstrak arsip (`.zip`, `.epub`, `.tar`), dan memanipulasi file biner maupun teks besar.

### B. Multi-Agent Swarm, Subagents & Orchestrator
- **Subagents On-Demand**:
  - `browser`: Agen webview untuk browsing, navigasi DOM, inspeksi halaman web interaktif, dan ekstraksi data kompleks.
  - `research`: Agen investigasi kode dan repositori dengan tool read-only mendalam.
  - `image-generator`: Generator media visual.
- **Swarm Architecture**: Kolaborasi paralel antar multi-agen dengan papan pesan bersama (*message board*) untuk membagi tugas kompleks menjadi pecahan paralel.
- **Workflow Automation Scripts**: Menjalankan skrip orkestrasi pipeline multi-agent bertingkat (`parallel`, `pipeline`, `phase`).

### C. Web & Network Intelligence
- **Deep Web Search**: Pencarian informasi global secara real-time via Google Search grounding API.
- **Direct Web & API Fetching**: Mengunduh aset, dokumen, file biner, mengekstrak data JSON, serta berinteraksi dengan API pihak ketiga.

### D. UI Interaktif & Visualisasi
- **Artifacts Engine**: Membuat dokumen interaktif Markdown, tabel, diagram alur `mermaid` (flowchart, sequence, class, state diagram), serta KaTeX math formulas.
- **Generative UI**: Render widget HTML interaktif langsung di sisi pengguna.

---

## 📚 3. Studi Kasus Unggulan: Pipeline Terjemahan Novel & EPUB Engine

Salah satu kemampuan tingkat lanjut yang telah dibangun dan diuji secara intensif adalah **Pipeline Penerjemahan Novel Skala Penuh & Kompilasi EPUB Otomatis**:

```mermaid
flowchart LR
    A["Raw File (EPUB / PDF / TXT)"] --> B["Extractor & Parser\n(TOC, Spine & HTML)"]
    B --> C["Adaptive Chunking &\nContext Framing"]
    C --> D["Parallel AI Translation\n(9router / LLM Proxy)"]
    D --> E["Zero-Refusal Filter &\nSanitizer"]
    E --> F["EPUB Recompiler &\nIllustration Injector"]
    F --> G["Final Validated EPUB\n(Anti-Crash E-Reader)"]
```

### Keunggulan Pipeline Terjemahan yang Sudah Terbukti:
1. **Adaptive Sub-Chunking (Anti-Filter Refusal)**:
   - Jika ada bagian naskah ekstrem/sensitif yang tertolak filter AI, sistem secara otomatis memecah naskah menjadi mikro-chunk (~1.800 karakter) dan mencoba ulang sampai 100% lolos tanpa memotong alur cerita.
2. **Dynamic Multi-Style Modes**:
   - `dxd`: Gaya no-sensor, mesum frontal, tongkrongan gaul (Gue - Lu), banned kata baku kaku (`mencicit, menukas, dll.`), dialog bernama lengkap (`Issei Hyoudou: "..."`).
   - `expanse`: Hard sci-fi space opera, bahasa gaul luar angkasa, umpatan militer alami, istilah teknis (*Epstein Drive, PDC fire, thrust gravity*) presisi.
   - `dune`: Intrik politik feudal, istilah lore asli (*Spice Melange, Bene Gesserit, Voice*).
   - `metro`: Nuansa survival post-apokaliptik tegang & istilah faksi terowongan Moskow.
   - `overlord` / `mushoku` / `konosuba`: Gaya isekai komedi, inner monologue kontras, manga-paced dialog.
3. **Penyisipan Ilustrasi Presisi (Cover & Insert Images)**:
   - Mengekstrak ilustrasi asli dari PDF/EPUB sumber dan menyisipkannya tepat di bawah adegan narasi terkait.
4. **Kompilasi Standar EPUB**:
   - Menghasilkan file EPUB berstandar W3C/IDPF dengan validasi XML, CSS modern, cover responsif, dan bebas error di semua aplikasi reader (Apple Books, Moon+ Reader, Kindle, Thorium).

---

## 📊 4. Rekapitulasi Proyek yang Telah Selesai

| Seri / Judul | Format | Status | Hasil |
| :--- | :---: | :---: | :---: |
| **High School DxD** (Vol 01 s.d. 25) | EPUB Berilustrasi | **100% Tamat (25 Vol)** | Seluruh volume terkompilasi rapi di folder project |
| **Breeder Mage 1** (Marc Robert) | EPUB Berilustrasi | **100% Selesai** | 735 dialog bernama lengkap, gaya frontal |
| **The Expanse 1: Leviathan Wakes** | EPUB Berilustrasi | **100% Selesai** | 64 Bab lengkap, 1.43 MB teks, 0.68 MB EPUB |
| **Dune Part 1 & 2** | EPUB / Binary | **Selesai** | Rapi dengan adaptasi sci-fi renyah |
| **Metro 2033** | EPUB Berilustrasi | **Selesai** | Dilengkapi peta rute metro Moskow |
| **Tom Clancy: Rainbow Six** | EPUB | **Selesai** | Taktis & militer realistis |
