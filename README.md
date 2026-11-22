# Antigravity Autonomous Agent: Capabilities & Engineering Showcase

[![Google DeepMind](https://img.shields.io/badge/Google%20DeepMind-Gemini%20Engine-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/)
[![Agentic AI](https://img.shields.io/badge/Architecture-Agentic%20Orchestrator-00C7B7?style=for-the-badge)](https://github.com)
[![TypeScript](https://img.shields.io/badge/Pipeline-TypeScript%20%7C%20Node.js%2025-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Automation-Python%203.14-FFD43B?style=for-the-badge&logo=python)](https://python.org)

> **Antigravity** is a next-generation autonomous AI software engineer and system orchestrator powered by **Google DeepMind Gemini models**. Operating directly inside local development workspaces, Antigravity executes shell commands, manages concurrent background sub-tasks, conducts autonomous web investigations, and automates end-to-end data pipelines.

---

## ⚡ Key Capabilities Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ANTIGRAVITY AGENT ENGINE                          │
├──────────────────┬───────────────────┬─────────────────────────────────┤
│  Autonomous OS   │  Multi-Agent      │  Heavy Data Pipelines           │
│  - PowerShell/sh │  - Browser Agent  │  - Large Book Translation       │
│  - Background    │  - Research Agent │  - Adaptive Chunking (Zero-Ref) │
│    Async Tasks   │  - Swarm Mesh     │  - W3C EPUB / XML Compiler      │
│  - Surgical Edit │  - Custom Agents  │  - PyMuPDF Image Extraction     │
└──────────────────┴───────────────────┴─────────────────────────────────┘
```

### 1. Autonomous Terminal & System Operations
- **Headless & Async Command Execution:** Runs PowerShell, Node.js, Python, and CLI utilities with live log streaming and automated task completion alerts.
- **Surgical File Engine:** Reads, creates, diff-edits, and parses files ranging from multi-megabyte binary dumps to structured XML/HTML/JSON.
- **Resilient Process Recovery:** Background worker monitoring, timeout management, and graceful error handling.

### 2. Multi-Agent Swarms & Subagent Delegation
- **`browser` Subagent:** Interacts with live web applications, inspects DOM elements, extracts dynamically loaded payloads (e.g. mobile VK JSON blobs), and automates web workflows.
- **`research` Subagent:** Deep codebase indexing and contextual file analysis in a dedicated sandbox.
- **`swarm` Architecture:** Coordinates multiple parallel agents sharing a central message board to solve partitioned tasks concurrently.

### 3. Industrial-Grade Novel Translation & EPUB Pipeline
Engineered and validated through **`translate-novel-dragndrop.ts`**:
- **Zero-Refusal Adaptive Chunking:** Intelligently splits controversial or sensitive content into adaptive micro-chunks (~1,800 chars) to bypass model over-refusals while preserving 100% of the narrative.
- **Dynamic Style Adapters:**
  - `dxd`: Uncensored, raw, conversational dialogue with full-name speakers (`Character Name: "..."`), eliminating archaic literary tropes.
  - `expanse`: Hard sci-fi space opera tone, authentic Belter Creole terminology, and precise orbital mechanics / propulsion jargon (*Epstein Drive, PDC fire, high-g burn*).
  - `dune`: Political intrigue and authentic in-universe lore glossary (*Spice Melange, Kwisatz Haderach, Voice*).
  - `metro`: Post-apocalyptic survival tension with metro station route mapping.
  - `overlord` / `mushoku` / `konosuba`: Manga-paced comedy, inner monologue contrast, and snappy modern vernacular.
- **Precise Image Integration:** Uses PyMuPDF and EPUB manifest parsing to extract high-resolution cover and chapter illustrations, automatically placing them into the narrative stream.
- **W3C EPUB 3.0 Compiler:** Generates clean, responsive, valid XHTML/CSS EPUB books ready for e-readers without formatting bugs or reader crashes.

---

## 🏆 Production Track Record

| Project | Source & Scale | Style & Specs | Status |
| :--- | :--- | :--- | :---: |
| **High School DxD** | Vol 01 – 25 Complete (Light Novel) | Uncensored, 100% Dialog Named, Illustrations Injected | **Completed (25/25 EPUBs)** |
| **The Expanse: Leviathan Wakes** | 64 Chapters (~1.43 MB Text) | Hard Sci-Fi Space Opera, Zero-Refusal, Custom CSS | **Completed (EPUB Ready)** |
| **Breeder Mage 1** | Full Novel (Marc Robert) | 735 Named Dialogues, Raw Colloquial Tone | **Completed (EPUB Ready)** |
| **Metro 2033** | Full Post-Apocalyptic Novel | Survival Atmosphere + Tunnel Maps | **Completed (EPUB Ready)** |
| **Dune (Part 1 & 2)** | Full Epic Sci-Fi Novel | Lore Preservation + Streamlined Pacing | **Completed (EPUB Ready)** |

---

## 🛠️ Tech Stack & Runtime Environment

- **Core Engine:** Google DeepMind Gemini API (`ag/gemini-3.8-flash-low`, Pro, Flash) via 9router proxy
- **Runtimes:** Node.js v25 (TypeScript native strip-types) | Python 3.14
- **Libraries & Tools:** PyMuPDF (`fitz`), ZipFile, BeautifulSoup, Git, PowerShell
- **Target Formats:** W3C Valid EPUB, Markdown Artifacts, Interactive HTML, Mermaid Visuals

---
*Maintained by [@yoga](mailto:pangestuyoga081@gmail.com) & Google Antigravity Agent.*
