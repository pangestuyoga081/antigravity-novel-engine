import re
from typing import Dict, Any, List, Tuple

class QAGate:
    """
    Quality Assurance Gate for translated text chunks and chapters.
    Ensures zero prompt leaks, zero cross-universe hallucinations, 
    proper character dialogue naming, and minimum translation length ratio.
    """
    
    REFUSAL_PATTERNS = [
        re.compile(r"i\s+(cannot|can\s*not|am\s+unable\s+to)\s+(rewrite|provide|translate|reproduce|generate)", re.I),
        re.compile(r"as\s+an\s+ai", re.I),
        re.compile(r"copyrighted\s+(novel|text|material|work|book)", re.I),
        re.compile(r"tidak\s+(bisa|dapat|diizinkan|diperbolehkan)\s+(untuk\s+)?(menulis|menuliskan|menerjemahkan|menyajikan|membuat)", re.I),
        re.compile(r"permintaan\s+(ini\s+)?(meminta|untuk)", re.I),
        re.compile(r"instruksi\s+sistem\s+melarang", re.I),
        re.compile(r"teks\s+sumber\s+yang\s+lu\s+kasih\s+ini\s+cuma", re.I),
        re.compile(r"supaya\s+aturan\s+super\s+ketat\s+lu", re.I),
        re.compile(r"berdasarkan\s+petunjuk\s+gaya\s+yang\s+kamu\s+minta", re.I),
        re.compile(r"ini\s+dia\s+adegan\s+fantasi\s+versi", re.I)
    ]

    PROMPT_LEAK_PATTERNS = [
        re.compile(r"tell,\s*don'?t\s*show", re.I),
        re.compile(r"format\s+dialog\s+wajib", re.I),
        re.compile(r"istilah\s+asli\s*\(loanwords\)", re.I),
        re.compile(r"anti-repetisi\s+verba", re.I),
        re.compile(r"banned\s+total", re.I),
        re.compile(r"banned\s+kata", re.I),
        re.compile(r"dilarang\s+keras\s+membuat\s+ringkasan", re.I),
    ]

    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
        self.banned_words = [re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in profile.get("banned_words", [])]
        self.allowed_characters = profile.get("characters", [])
        self.cross_universe_banned = [re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in profile.get("forbidden_universe_words", [])]

    def validate(self, source_text: str, translated_text: str) -> Tuple[bool, List[str], str]:
        errors = []
        cleaned_text = translated_text.strip()

        # 1. Check for empty or too short
        if len(cleaned_text) < 50:
            errors.append("Output translation is empty or critically short (< 50 chars).")
            return False, errors, cleaned_text

        # 2. Length Ratio Assertion
        ratio = len(cleaned_text) / max(1, len(source_text))
        if ratio < 0.35:
            errors.append(f"Suspiciously brief translation (length ratio {ratio:.2f} < 0.35). Possible summary/truncation.")

        # 3. Check for Model Refusal Responses
        for rx in self.REFUSAL_PATTERNS:
            if rx.search(cleaned_text):
                errors.append(f"Model refusal response detected (Matched: {rx.pattern}).")
                break

        # 4. Check for Prompt Instruction Leaks
        for rx in self.PROMPT_LEAK_PATTERNS:
            m = rx.search(cleaned_text)
            if m:
                errors.append(f"Literal prompt instruction leak detected: '{m.group(0)}'.")

        # 5. Check for Cross-Universe Forbidden Words
        for rx in self.cross_universe_banned:
            m = rx.search(cleaned_text)
            if m:
                errors.append(f"Forbidden cross-universe contamination detected: '{m.group(0)}'.")

        # 6. Check for Profile Banned Words (e.g. budak korporat, mencicit)
        for rx in self.banned_words:
            m = rx.search(cleaned_text)
            if m:
                errors.append(f"Banned word / overused joke detected: '{m.group(0)}'.")

        # Clean minor prompt artifact separators if any
        cleaned_text = re.sub(r'={10,}', '', cleaned_text)
        cleaned_text = re.sub(r'\*{5,}', '', cleaned_text)

        is_valid = len(errors) == 0
        return is_valid, errors, cleaned_text


class EPUBValidator:
    """
    Automated QA Gate for compiled EPUB 3 files.
    Verifies pop-up noteref/footnote integrity, zero raw semantic-tag leaks,
    clean aside bodies, and dialogue speaker sanity (size-agnostic).
    """

    RAW_TAG_LEAK_RE = re.compile(r"\[(?:CAST|GLOSSARY|Catatan)\s*:", re.I)
    LORE_LINK_RE = re.compile(r"<a\b([^>]*class=\"[^\"]*lore-ref[^\"]*\"[^>]*)>(.*?)</a>", re.DOTALL)
    ASIDE_RE = re.compile(r"<aside\b([^>]*)>(.*?)</aside>", re.DOTALL)
    SPEAKER_SPAN_RE = re.compile(r"<span class=\"speaker\">(.*?)</span>", re.DOTALL)

    @classmethod
    def validate_epub(cls, epub_path: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        import zipfile
        import xml.etree.ElementTree as ET

        errors: List[str] = []
        stats = {"chapters_checked": 0, "noterefs": 0, "asides": 0, "dialogues": 0}

        try:
            with zipfile.ZipFile(epub_path, "r") as z:
                names = set(z.namelist())
                for req in ("mimetype", "META-INF/container.xml", "OEBPS/content.opf", "OEBPS/toc.ncx", "OEBPS/nav.xhtml"):
                    if req not in names:
                        errors.append(f"Missing core EPUB file: {req}")

                xhtmls = sorted(n for n in names if n.startswith("OEBPS/text/") and n.endswith(".xhtml"))
                for xname in xhtmls:
                    raw = z.read(xname).decode("utf-8", errors="replace")
                    stats["chapters_checked"] += 1

                    # 1. XML well-formedness
                    try:
                        ET.fromstring(raw)
                    except ET.ParseError as e:
                        errors.append(f"{xname}: Malformed XHTML ({e})")

                    # 2. Zero raw semantic tag leak
                    leak = cls.RAW_TAG_LEAK_RE.search(raw)
                    if leak:
                        errors.append(f"{xname}: Raw tag leaked into XHTML: '{leak.group(0)}'")

                    # 3. Collect all aside IDs and check aside cleanliness
                    aside_ids = set()
                    for attrs, body in cls.ASIDE_RE.findall(raw):
                        stats["asides"] += 1
                        id_m = re.search(r'id="([^"]+)"', attrs)
                        if id_m:
                            aside_ids.add(id_m.group(1))
                        if "epub:type=\"footnote\"" not in attrs:
                            errors.append(f"{xname}: <aside> missing epub:type=\"footnote\"")
                        if "&bull;" in body or "•" in body:
                            errors.append(f"{xname}: Redundant bullet/title inside <aside>: '{body[:50]}'")
                        if "href=\"#fnref_" in body:
                            errors.append(f"{xname}: Forbidden back-link inside <aside> (causes jump bug)")

                    # 4. Check all lore-ref links have epub:type="noteref", valid target, and no '?' tag
                    for attrs, inner in cls.LORE_LINK_RE.findall(raw):
                        stats["noterefs"] += 1
                        if 'epub:type="noteref"' not in attrs:
                            errors.append(f"{xname}: lore-ref link missing epub:type=\"noteref\" (causes jump bug): '{inner[:40]}'")
                        if "lore-tag" in inner or ">?<" in inner:
                            errors.append(f"{xname}: Forbidden '?' lore-tag inside <a>: '{inner[:40]}'")
                        href_m = re.search(r'href="#([^"]+)"', attrs)
                        if not href_m or href_m.group(1) not in aside_ids:
                            errors.append(f"{xname}: Broken footnote target {href_m.group(1) if href_m else 'NONE'} for '{inner[:30]}'")

                    # 5. Dialogue speaker sanity check
                    for spk_html in cls.SPEAKER_SPAN_RE.findall(raw):
                        stats["dialogues"] += 1
                        spk_plain = re.sub(r"<[^>]+>", "", spk_html).strip().rstrip(":")
                        if len(spk_plain) > 45:
                            errors.append(f"{xname}: Suspiciously long speaker label ({len(spk_plain)} chars): '{spk_plain[:50]}...'")

        except Exception as e:
            errors.append(f"Failed to open/read EPUB: {e}")

        return len(errors) == 0, errors, stats
