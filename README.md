# Antigravity Autonomous Agent: Capabilities & Engineering Showcase

[![Google DeepMind](https://img.shields.io/badge/Google%20DeepMind-Gemini%20Engine-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/)
[![Agentic AI](https://img.shields.io/badge/Architecture-Agentic%20Orchestrator-00C7B7?style=for-the-badge)](https://github.com)
[![TypeScript](https://img.shields.io/badge/Pipeline-TypeScript%20%7C%20Node.js%2025-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Automation-Python%203.14-FFD43B?style=for-the-badge&logo=python)](https://python.org)

> **Antigravity** is a next-generation autonomous AI software engineer and system orchestrator powered by **Google DeepMind Gemini models**. Operating directly inside local development workspaces, Antigravity executes shell commands, manages concurrent background sub-tasks, conducts autonomous web investigations, and automates end-to-end multi-million-word translation and publishing pipelines.

---

## ⚡ Key Capabilities Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ANTIGRAVITY AGENT ENGINE                          │
├──────────────────┬───────────────────┬─────────────────────────────────┤
│  Autonomous OS   │  Multi-Agent      │  Heavy Data & Book Pipelines    │
│  - PowerShell/sh │  - Browser Agent  │  - Multi-Million Word Engine    │
│  - Background    │  - Research Agent │  - Adaptive Multi-Tier Chunks   │
│    Async Tasks   │  - Swarm Mesh     │  - W3C EPUB / NCX / XHTML       │
│  - Surgical Edit │  - Custom Agents  │  - Complete Illustrated Ingest  │
└──────────────────┴───────────────────┴─────────────────────────────────┘
```

### 1. Autonomous Terminal & System Operations
- **Headless & Async Command Execution:** Runs PowerShell, Node.js, Python, and CLI utilities with live log streaming and automated task completion alerts.
- **Surgical File Engine:** Reads, creates, diff-edits, and parses files ranging from multi-megabyte binary dumps to structured XML/HTML/JSON.
- **Resilient Process Recovery:** Background worker monitoring, timeout management, rate-limit cooldown handling, and graceful error recovery.

### 2. Multi-Agent Swarms & Subagent Delegation
- **`browser` Subagent:** Operates interactive webviews, navigates DOM elements, extracts dynamically loaded payloads (e.g. mobile VK JSON blobs), and automates web interactions.
- **`research` Subagent:** Deep codebase indexing and contextual file analysis in a dedicated sandbox.
- **`swarm` Architecture:** Coordinates multiple parallel agents sharing a central message board to solve partitioned tasks concurrently.

### 3. Industrial-Grade Novel & Book Translation Pipeline
Engineered and validated through **`translate-novel-dragndrop.ts`**:
- **Zero-Refusal Adaptive Sub-Chunking:** Intelligently splits controversial, violent, or sensitive content into adaptive micro-chunks (~1,800 chars and ~1,100 chars) to bypass model over-refusals while preserving 100% of the narrative.
- **Strict Anti-Hallucination & Clean Register:**
  - Zero archaic/stiff translation tropes (blacklist: *tatkala, mencicit, menukas, bergumam, dsb.*).
  - Banned overuse cliches (*budak korporat, bos toxic, shift malam*).
  - Preserves third-person POV narrator and authentic natural dialogue.
- **Dynamic Style Adapters:**
  - `harrypotter`: Uncensored, raw Gryffindor dorm banter (Gue - Lu), full-name dialogue formatting (`Character Name: "..."`), keeping all natural profanities and emotional grit without archaic euphemisms.
  - `comic_history`: Epic, punchy, dramatic narration for monumental non-fiction history (comparable to top-tier historical webtoons like *Kingdom* or *Vinland Saga*), preserving 100% factual accuracy and historical maps.
  - `expanse`: Hard sci-fi space opera tone, authentic Belter Creole terminology, and precise orbital mechanics / propulsion jargon (*Epstein Drive, PDC fire, high-g burn*).
  - `dune`: Political intrigue and authentic in-universe lore glossary (*Spice Melange, Kwisatz Haderach, Voice*).
  - `metro`: Post-apocalyptic survival tension with metro station route mapping.
  - `dxd`: Uncensored, raw, conversational dialogue with full-name speakers.
  - `overlord` / `mushoku` / `konosuba`: Manga-paced comedy, inner monologue contrast, and snappy modern vernacular.
- **W3C EPUB 3.0 Compiler with Full Image Embedding:**
  - Automatically compiles clean XHTML/CSS EPUB books ready for e-readers.
  - Injects all chapter illustrations, maps, and dynasty lineage charts with custom stylesheet tuning.
  - Completely translated Indonesian Table of Contents (TOC / `toc.ncx`) for seamless reader navigation.

### 4. Blogspot & Safelink Link Bypass Engine (MediaFire / Google Drive)
Located in `tools/bypass_blogspot_mediafire/`:
- **Blogger JSON Feed Scraping:** Automatically traverses multi-volume light novel series published across Blogger/Blogspot architectures.
- **Instant Base64 Safelink Bypass:** Automatically decodes and resolves shortened / protected links (such as `ruisafe`, `safelinku`, etc.) to obtain direct **MediaFire**, **Google Drive**, and **Krakenfiles** download URLs.
- **Batch Export:** Outputs formatted lists of clean direct download URLs compatible with JDownloader, IDM, and curl.

### 5. Multi-PC Chat Migration & 1-Click Session Restore
Located in `chat_backup/`:
- Packages complete Antigravity conversation sessions (brains, logs, checkpoints, task transcripts) into an archive.
- Provides a one-click batch script (`RESTORE_CHAT_KE_PC_INI.bat`) to instantly resume the entire chat session on any new PC with zero context loss.

---

## 🏆 Production Track Record & Live Progress

### 🧙‍♂️ Complete Harry Potter Saga (J.K. Rowling) — 7 / 7 Volumes (100% COMPLETED)
*Style: No-Sensor, Gaul Tongkrongan Asrama Gryffindor (Gue - Lu), Dialog Wajib Bernama Lengkap, Zero Kata Kaku*

| # | Title | Chapters | Word Count | EPUB Size | Status | Output File |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | **Batu Bertuah** *(Philosopher's Stone)* | 20 Bab | ~85,000 | 1.41 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%201%20-%20Batu%20Bertuah%20(Illustrated%20ID-Direct).epub) |
| **2** | **Kamar Rahasia** *(Chamber of Secrets)* | 21 Bab | ~98,000 | 1.79 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%202%20-%20Kamar%20Rahasia%20(Illustrated%20ID-Direct).epub) |
| **3** | **Tawanan Azkaban** *(Prisoner of Azkaban)* | 25 Bab | ~115,000 | 1.76 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%203%20-%20Tawanan%20Azkaban%20(Illustrated%20ID-Direct).epub) |
| **4** | **Piala Api** *(Goblet of Fire)* | 40 Bab | ~219,700 | 2.82 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%204%20-%20Piala%20Api%20(Illustrated%20ID-Direct).epub) |
| **5** | **Orde Phoenix** *(Order of the Phoenix)* | 41 Bab | ~293,000 | 3.39 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%205%20-%20Orde%20Phoenix%20(Illustrated%20ID-Direct).epub) |
| **6** | **Pangeran Berdarah-Campuran** *(Half-Blood Prince)* | 33 Bab | ~196,700 | 2.77 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%206%20-%20Pangeran%20Berdarah-Campuran%20(Illustrated%20ID-Direct).epub) |
| **7** | **Relikui Kematian** *(Deathly Hallows)* | 40 Bab | ~235,100 | 2.64 MB | **100% Selesai** | [EPUB](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/Harry%20Potter%207%20-%20Relikui%20Kematian%20(Illustrated%20ID-Direct).epub) |

---

### 🏛️ Monumental History & Popular Science (100% COMPLETED)

| Title & Author | Scale & Coverage | Style & Features | Status | Output File |
| :--- | :--- | :--- | :---: | :--- |
| **A History of Islamic Societies (3rd Ed. 2014)**<br>*by Ira M. Lapidus (Cambridge Univ. Press)* | **685,826 words**<br>(5.16 Million Chars, 77 Chapters / 172 Sub-sections) | **Gaya Komik Sejarah (Epic & Punchy)**<br>85 Peta & Bagan Silsilah Dinasti, Daftar Isi 100% Bahasa Indonesia | **100% Selesai** | [EPUB (10.63 MB)](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/A%20History%20of%20Islamic%20Societies%20-%20Ira%20M.%20Lapidus%20(3rd%20Edition%202014)%20(Illustrated%20ID-Direct).epub) |
| **The Story of Earth: The First 4.5 Billion Years**<br>*by Robert M. Hazen (Viking / Penguin)* | **95,867 words**<br>(744,000 Chars, 16 Chapters) | **Sains Populer Mengalir Luwes**<br>19 Diagram Evolusi Kerak & Mineral Bumi Lengkap | **100% Selesai** | [EPUB (0.70 MB)](file:///E:/antigravity-novel-engine/Hasil%20Output/EPUB%20Lengkap/The%20Story%20of%20Earth%20-%20Robert%20M.%20Hazen%20(Illustrated%20ID-Direct).epub) |

---

### ⚔️ Sci-Fi, Fantasy & Light Novels (COMPLETED)

| Project | Scale & Volume | Style & Specs | Status |
| :--- | :--- | :--- | :---: |
| **High School DxD** | Vol 01 – 25 Complete | Uncensored, 100% Dialog Named, Illustrations Injected | **Completed (25/25 EPUBs)** |
| **The Expanse: Leviathan Wakes** | 64 Chapters (~1.43 MB Text) | Hard Sci-Fi Space Opera, Zero-Refusal, Custom CSS | **Completed (EPUB Ready)** |
| **Breeder Mage 1** | Full Novel (Marc Robert) | 735 Named Dialogues, Raw Colloquial Tone | **Completed (EPUB Ready)** |
| **Metro 2033** | Full Post-Apocalyptic Novel | Survival Atmosphere + Tunnel Maps | **Completed (EPUB Ready)** |
| **Dune (Part 1 & 2)** | Full Epic Sci-Fi Novel | Lore Preservation + Streamlined Pacing | **Completed (EPUB Ready)** |

---

## 🛠️ Tech Stack & Runtime Environment

- **Core Engine:** Google DeepMind Gemini API (`ag/gemini-3.8-flash-low`, Pro, Flash) via 9router proxy
- **Runtimes:** Node.js v25 (TypeScript native strip-types) | Python 3.14
- **Libraries & Tools:** PyMuPDF (`fitz`), ZipFile, BeautifulSoup, Git, PowerShell
- **Target Formats:** W3C Valid EPUB 3.0, Markdown Artifacts, Interactive HTML, Mermaid Visuals

---
*Maintained by [@yoga](mailto:pangestuyoga081@gmail.com) & Google Antigravity Agent.*
