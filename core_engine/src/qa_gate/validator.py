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
