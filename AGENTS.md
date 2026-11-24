# ==============================================================================
# ANTIGRAVITY NOVEL TRANSLATION ENGINE & SUBSYSTEM ARCHITECTURE SPECIFICATION
# ==============================================================================
# Document : AGENTS.md
# Standard : Linux Kernel Subsystem Documentation Style (RFC-2119 / KernelDoc)
# Scope    : Autonomous Translation Pipeline, Living Universe, & EPUB3 Subsystems
# Target   : D:\JV\novel yoga
# Maintain : Antigravity Autonomous Agent (Google DeepMind Architecture)
# Git Upstr: https://github.com/pangestuyoga081/antigravity-novel-engine.git (main)
# ==============================================================================

Table of Contents
-----------------
1.  System Overview & Core Philosophy
2.  High-Level System Topology (Block Diagram)
3.  Subsystem 1: The Three-Pass Pipeline (Scout -> Translate -> QA Audit)
4.  Subsystem 2: Living Universe Profile & Dynamic Memory (YAML Evolution)
5.  Subsystem 3: Semantic Tag Specification & Syntax Grammar
6.  Subsystem 4: EPUB 3 Packaging & DOM Compilation Pipeline
7.  Subsystem 5: Reader-Theme Agnostic CSS & Visual Ergonomics
8.  Subsystem 6: Fault Tolerance, Checkpointing, & Zero-Leak Protocols
9.  Subsystem 7: File Hierarchy & Repository Layout
10. Hardware, Concurrency, & Runtime Specifications
11. Developer Operation Manual & CLI Reference

==============================================================================
1. System Overview & Core Philosophy
==============================================================================

The Antigravity Novel Translation Engine is an industrial-grade, autonomous,
multi-pass text-processing and publication pipeline. It transforms raw,
unstructured foreign-language literature (EPUB/PDF/TXT) into interactive,
highly engaging, mobile-optimized EPUB 3 digital books and raw master text
manuscripts.

Core Axioms:
  I.   Context Precedes Execution (Scout Before Chunking):
       A translation unit MUST never process text in isolation without a global
       contextual graph of the chapter's dramatis personae and lore domain.
  II.  Living Universe Memory:
       The universe schema (characters, factions, geographies, technologies) is
       NOT static. It expands organically as each chapter is parsed and digested.
  III. Semantic Markup Over Regex Guesswork:
       The engine deprecates heuristic regex extraction of terms and parentheses.
       The Large Language Model (LLM) injects explicit, deterministic semantic
       tags (`[CAST]`, `[GLOSSARY]`, `[SPEAKER]`) during translation.
  IV.  Theme Agnosticism:
       The generated artifacts MUST adapt seamlessly across diverse e-reader
       display engines (Light, Sepia, Dark, AMOLED Black, E-Ink) without color
       inversion artifacts or unreadable contrast collisions.
  V.   GitHub-First Persistence:
       All code changes, configuration mutations, and engine heuristics must
       synchronize immediately with Git version control.

==============================================================================
2. High-Level System Topology (Block Diagram)
==============================================================================

               +---------------------------------------+
               |         RAW SOURCE NOVEL (EPUB)       |
               +---------------------------------------+
                                   |
                                   v
               +---------------------------------------+
               |  EPUB UNPACKER & CHAPTER EXTRACTOR    |
               +---------------------------------------+
                                   |
                 [Raw English Chapter Body (k words)]
                                   |
       +---------------------------+---------------------------+
       |                                                       |
       v                                                       v
+-------------------------------+             +-------------------------------+
|  PASS 1: CONTEXT SCOUTER      |             |  HISTORICAL UNIVERSE MEMORY   |
|  - Fast-Scan Architecture     |             |  core_engine/config/profiles/ |
|  - Entity Extraction          |<------------|  (metro_2033.yaml, etc.)      |
|  - Lore Term Isolation        |             +-------------------------------+
+-------------------------------+                             ^
       |                                                       |
       | Emit: [CAST], [GLOSSARY]                              | (Living Profile
       |                                                       |  Auto-Commit)
       v                                                       |
+--------------------------------------------------------------+--------------+
| PASS 1.5: LIVING PROFILE UPDATER (`update_living_profile.py`)                |
| - Resolves new dramatis personae vs known entity registry                   |
| - Registers aliases, roles, factions, and loanwords to disk YAML            |
+-----------------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------------+
| PASS 2: CHUNKED LOCALIZATION OPERATOR (`translate-novel-dragndrop.ts`)       |
| - Style: High-Octane Tell-Don't-Show (Indonesian, gaul santai, gue-lu)      |
| - Zero-Censorship Dialogue & Raw Military Colloquialism                     |
| - Deterministic Semantic Injection (`[SPEAKER]`, `[GLOSSARY]`, `[CAST]`)   |
+-----------------------------------------------------------------------------+
                                   |
                     [Translated Chapter Draft]
                                   |
                                   v
+-----------------------------------------------------------------------------+
| PASS 3: ZERO-LEAK QA VALIDATOR & AUDIT GATE                                  |
| - Source-to-Target Sentence Continuity Check                                |
| - Anti-Banned Words Filter (tatkala, menukas, mencicit, budak korporat)     |
| - Bracket / Parentheses Leak Quarantine                                     |
+-----------------------------------------------------------------------------+
                                   |
                       [Verified Master Text]
                                   |
       +---------------------------+---------------------------+
       |                                                       |
       v                                                       v
+-------------------------------+             +-------------------------------+
| NASKAH_TXT/ STORAGE           |             | EPUB 3 COMPILER PIPELINE      |
| Master Flatfiles (.txt)       |             | (`compile_epub_helper.py`)    |
+-------------------------------+             +-------------------------------+
                                                               |
                                                               v
                                              +-------------------------------+
                                              | - Semantic Parser             |
                                              | - Dynamic Cast Drawer Injector|
                                              | - Non-Jumping Popup Footnotes |
                                              | - Agnostic Dark/Light CSS     |
                                              | - Broken Image Guard          |
                                              +-------------------------------+
                                                               |
                                                               v
                                              +-------------------------------+
                                              | EPUB_SIAP_BACA/ STORAGE       |
                                              | Validated EPUB 3 (.epub)      |
                                              +-------------------------------+

==============================================================================
3. Subsystem 1: The Three-Pass Pipeline
==============================================================================

The core translation flow operates on a strict three-pass state machine per
chapter:

3.1. Pass 1: Context Scouter
----------------------------
- Input : Full raw English chapter text (3,000 - 8,000 words).
- Execution: Rapid extraction pass utilizing high-throughput inference.
- Function:
  1. Identifies active speakers in the chapter, separating primary characters
     from nameless background extras (e.g., "Artyom", "Hunter" vs "Soldier 1").
  2. Isolates novel jargon, military technical terms, and world-specific lore
     (e.g., "The Dark Ones", "VDNKh", "Berdan rifle", "Flamethrower").
- Output: Structured headers containing `[CAST]` and `[GLOSSARY]` tags.

3.2. Pass 2: Chunked Localization Operator
------------------------------------------
- Input : Raw chapter partitioned into sliding context chunks (1,500 - 2,500
          tokens) + Pass 1 Memory Buffer.
- Directives:
  - Pronoun Mapping: Strict informal "gue-lu" for peers, military personnel,
    and street wanderers.
  - Tone: Fast-paced, punchy, gritty post-apocalyptic narrative.
  - Banlist Enforcement: Zero tolerance for stiff archaic phrasing ("tatkala",
    "kendati demikian", "merupakan", "adalah") and AI cliches ("budak korporat").
  - Semantic Tag Adherence: Every line of dialogue is bound to an identified
    speaker; terms defined in the glossary are rendered cleanly without in-line
    bracket explanations.

3.3. Pass 3: Zero-Leak QA Validator
-----------------------------------
- Input : Raw chapter source paired with generated target chapter draft.
- Verification Gates:
  1. Parity Check: Paragraph-by-paragraph parity to eliminate omitted scenes.
  2. Cleanliness Gate: Rejects and scrubs any residual LLM boilerplate ("Berikut
     adalah terjemahan...", "Tentu, ini hasilnya...").
  3. XML Safety Gate: Guarantees no raw HTML entities (`<a id...>`, `&`) leak into
     the plain text stream unescaped.

==============================================================================
4. Subsystem 2: Living Universe Profile & Dynamic Memory
==============================================================================

Module: `D:\JV\novel yoga\update_living_profile.py`
Storage: `D:\JV\novel yoga\core_engine\config\profiles\<book_id>.yaml`

4.1. The Static Bottleneck Problem
----------------------------------
Conventional translation engines rely on static configuration files. As a
novel progresses, newly introduced characters, factions, and locations are
absent from the knowledge base, leading to inconsistent naming and broken
cross-references in later chapters.

4.2. The Living Evolution Mechanism
-----------------------------------
The Living Universe subsystem continuously updates the target YAML schema:
- When Pass 1 encounters an entity not present in `key_characters`, it appends
  the entity along with its role description, dialogue format, and faction.
- If an existing entity undergoes status change (e.g., Hunter disappearing),
  the subsystem updates the entity's profile.
- Geographic locations and factions are routed to `locations_and_factions`.
- Terminology and weaponry are routed to `loanwords`.
- Memory is immediately committed and available for subsequent chapters.

==============================================================================
5. Subsystem 3: Semantic Tag Specification & Syntax Grammar
==============================================================================

All translated chapter manuscripts adhere to the following EBNF grammar:

5.1. Syntax Grammar
-------------------
  ChapterFile    ::= HeaderSection BodySection
  HeaderSection  ::= ChapterTitle [ImageTag] {CastTag} {GlossaryTag}
  ChapterTitle   ::= "### CHAPTER " Number ": " TitleText "\n\n"
  ImageTag       ::= "[[ILUSTRASI:" ImagePath "]]\n" [CaptionText "\n"] "\n"
  CastTag        ::= "[CAST: " CharacterName " | " FactionID " | " Description "]\n"
  GlossaryTag    ::= "[GLOSSARY: " Term " | " Explanation "]\n"
  BodySection    ::= { Paragraph | Dialogue | BoxNotification }
  Paragraph      ::= NarrativeText "\n\n"
  Dialogue       ::= SpeakerPrefix ': "' Utterance '"\n\n'
  SpeakerPrefix  ::= CharacterName
  BoxNotification::= "[" ("PEMBERITAHUAN" | "ACHIEVEMENT" | "SYSTEM") ":" Content "]\n\n"

5.2. Tag Semantics
------------------
- `[CAST: Name | Faction | Desc]`:
  Defines a primary character for the chapter's Dramatis Personae.
  FactionID maps to visual CSS badges:
  - `spartan`  -> ⚔️ SPARTAN / 🎖️ RANGER (Ordo Spartan / Rangers)
  - `metro`    -> 📜 METRO (Warga Sipil / Independen Metro)
  - `hanza`    -> 💰 HANZA (Hanseatic League)
  - `redline`  -> 🔴 RED LINE (Garis Merah Komunis)
  - `reich`    -> ⚡ REICH (Fourth Reich)
  - `carl`     -> 💥 CRAWLER (Dungeon Crawler Carl)
  - `donut`    -> 👑 DIVA CAT (Princess Donut)
  - `system`   -> 🤖 SYSTEM (AI Announcer)

- `[GLOSSARY: Term | Explanation]`:
  Declares an interactive popup definition. When `Term` appears in narrative
  or dialogue, the compiler binds it to an EPUB 3 footnote popup without
  polluting the sentence with bracketed explanations.

==============================================================================
6. Subsystem 4: EPUB 3 Packaging & DOM Compilation Pipeline
==============================================================================

Module: `D:\JV\novel yoga\compile_epub_helper.py`

6.1. Compilation Lifecycle
--------------------------
1. Ingestion: Reads the curated `.txt` manuscript and source `.epub`.
2. Binary Extraction: Unpacks valid illustrations, covers, and typography from
   the source archive into an in-memory dictionary (`images_data`).
3. Chapter Splitting: Partitions text on `###` tokens.
4. AST / DOM Generation (`text_to_html`):
   a. Parses `[CAST]` entries into `<details class="chapter-cast">`.
   b. Parses `[GLOSSARY]` entries into the chapter lore table.
   c. Checks `[[ILUSTRASI:...]]` against `images_data`. If the binary does NOT
      exist, the tag is suppressed to prevent broken-image placeholders.
   d. Escapes text entities to prevent raw markup injection.
   e. Synthesizes dialogue blocks with faction badges.
   f. Injects non-jumping popup footnote links.
   g. Appends `<aside epub:type="footnote">` blocks at document termination.
5. Packaging: Emits standard Open Container Format (OCF) structures:
   - `mimetype` (stored uncompressed as first 20 bytes)
   - `META-INF/container.xml`
   - `OEBPS/content.opf` (Manifest with spine, metadata, and EPUB3 semantics)
   - `OEBPS/toc.ncx` & `OEBPS/toc.xhtml` (Dual NCX and Navigation Documents)
   - `OEBPS/css/stylesheet.css` (Universal theme-agnostic styling)
   - `OEBPS/text/chapter_*.xhtml` (Strict XML-compliant XHTML5 documents)

==============================================================================
7. Subsystem 5: Reader-Theme Agnostic CSS & Visual Ergonomics
==============================================================================

To guarantee zero contrast collisions across e-reader engines (Lithium, Moon+,
Apple Books, Kobo, Calibre), the CSS follows strict isolation rules:

7.1. Color Inversion Safety
---------------------------
- Never hardcode `background-color` or `color` on `body`, `p`, or container
  roots. These are set to `inherit` or transparent to respect the user's
  chosen reading background (e.g. Sepia parchment, Dark, OLED Black).
- Faction Badges and Drawers use low-opacity alpha channels (`rgba(x, y, z, 0.15)`)
  which tint gracefully against both white, cream, and pure black screens.

7.2. Anti-Jumping Footnote Architecture
---------------------------------------
- Standard HTML anchor links (`<a href="#fn_1">`) trigger page jumps in naive
  readers, disrupting reading flow.
- The engine implements EPUB 3 semantic attributes:
  ```html
  <!-- Reference in text -->
  <a id="fnref_1" href="#fn_1" class="lore-ref" epub:type="noteref">
    VDNKh<span class="lore-tag">?</span>
  </a>

  <!-- Target in Footnotes Section -->
  <aside id="fn_1" class="footnote" epub:type="footnote">
    <strong><a href="#fnref_1">&uarr; VDNKh</a>:</strong>
    Stasiun benteng paling utara Metro...
  </aside>
  ```
- Compliant readers intercept `epub:type="noteref"` to display a modal popup
  overlay, completely preventing unwanted viewport scrolling.

==============================================================================
8. Subsystem 6: Fault Tolerance, Checkpointing, & Zero-Leak Protocols
==============================================================================

8.1. State Persistence & Checkpointing
--------------------------------------
- Long-running novel batch operations record progress in `<book>_checkpoint.json`.
- State tracks: `last_completed_chapter`, `completed_chunks`, `token_usage`,
  and `error_recovery_attempts`.
- If an unhandled interrupt (e.g., process termination, network partition)
  occurs, re-running resumes from the exact boundary without reprocessing
  completed chapters.

8.2. Broken Image Quarantine
----------------------------
- Descriptive image markers (e.g. `[[ILUSTRASI: Escalator runtuh...]]`) that
  have not yet been rendered by diffusion models are filtered out during DOM
  assembly. Only filenames resolving to verified binary payloads in `images_data`
  generate `<img>` tags.

8.3. XML Entity Quarantine
--------------------------
- Double-escaping vulnerabilities (where `<a href...>` converts to
  `&lt;a href...&gt;`) are systematically prevented by performing HTML
  entity escaping on raw dialogue/narrative FIRST, prior to semantic link
  injection.

==============================================================================
9. Subsystem 7: File Hierarchy & Repository Layout
==============================================================================

The workspace layout on disk (`D:\JV\novel yoga`):

```
D:\JV\novel yoga\
├── core_engine/
│   ├── config/
│   │   └── profiles/                # Living Universe Profiles (YAML)
│   │       ├── metro_2033.yaml
│   │       ├── metro_2034.yaml
│   │       ├── dungeon_crawler_carl.yaml
│   │       └── the_expanse_2.yaml
│   └── src/
│       └── server/
│           └── api.py               # Telemetry & Monitoring API
├── HASIL_TERJEMAHAN/                # Centralized Output Distribution Hub
│   ├── EPUB_SIAP_BACA/              # Verified Production-Ready EPUB 3 Files
│   │   ├── Metro 2033 (Illustrated ID-Direct).epub
│   │   └── Metro 2034 (Illustrated ID-Direct).epub
│   └── NASKAH_TXT/                  # Master Raw Text Manuscripts
│       ├── Metro 2033 (Terjemahan ID-Direct).txt
│       └── Metro 2034 (Terjemahan ID-Direct).txt
├── illustrations/                   # Canonical Image Repositories per Novel
│   ├── Metro_2033/
│   └── Metro_2034/
├── epubs/                           # Staging directory for build artifacts
├── compile_epub_helper.py           # Core DOM / AST EPUB 3 Compiler Engine
├── update_living_profile.py         # Dynamic Universe Schema Evolution Engine
├── translate-novel-dragndrop.ts     # Multi-Pass Autonomous Translator Pipeline
├── AGENTS.md                        # Subsystem Architectural Specification (This File)
└── package.json / tsconfig.json     # Node.js / TypeScript Toolchain Config
```

==============================================================================
10. Hardware, Concurrency, & Runtime Specifications
==============================================================================

- Execution Platform: Windows NT / PowerShell 7+ / Python 3.11+ / Node v20+
- Host Working Path : `D:\JV\novel yoga`
- Concurrency Engine: Python Subprocess & Async TS Pipeline
- Encoding Standard : UTF-8 (Strict, BOM-less)
- Target Format     : EPUB 3.2 (IDPF Specification compliant)
- Network Interface : GitHub Remote over HTTPS (`pangestuyoga081/antigravity-novel-engine`)

==============================================================================
11. Developer Operation Manual & CLI Reference
==============================================================================

11.1. Compiling a Novel into EPUB 3
-----------------------------------
Command:
```powershell
python "D:\JV\novel yoga\compile_epub_helper.py" `
  "D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt" `
  "D:\JV\novel yoga\Metro 2033.epub" `
  "D:\JV\novel yoga\epubs\Metro 2033 (Illustrated ID-Direct).epub"
```

11.2. Updating Living Universe Profile Manually
----------------------------------------------
```python
from update_living_profile import update_living_profile

casts = [('Artyom', 'metro', 'Hero of VDNKh')]
glossaries = [('VDNKh', 'Northern fortress station')]
update_living_profile(r'D:\JV\novel yoga\core_engine\config\profiles\metro_2033.yaml', casts, glossaries)
```

11.3. Git Synchronization
-------------------------
```powershell
git -C "D:\JV\novel yoga" add -A
git -C "D:\JV\novel yoga" commit -m "feat(pipeline): sync living profile & curated chapters"
git -C "D:\JV\novel yoga" push origin main
```

==============================================================================
[END OF AGENTS.MD ARCHITECTURE SPECIFICATION]
==============================================================================
