import os
import re
import yaml
from typing import Dict, Any, List, Set

class DynamicEntityAppender:
    """
    Handles on-the-fly entity discovery during chapter translation.
    When a chapter introduces a new character name or unique universe lore
    that was not in the initial pre-translation YAML profile, this module:
    1. Detects newly introduced entities.
    2. Appends them dynamically into the novel's YAML profile.
    3. Keeps character and loanword consistency locked across all subsequent chapters.
    """

    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        self.profile_data = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _save_profile(self):
        with open(self.profile_path, "w", encoding="utf-8") as f:
            yaml.dump(self.profile_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    def extract_new_speakers_from_output(self, translated_chapter_text: str) -> List[str]:
        """
        Scans translated text for dialogue speakers: Name: "..."
        If the speaker is not yet in the profile's character list, registers them.
        """
        existing_chars = set(self.profile_data.get("characters", []))
        new_speakers = []

        # Find all lines matching: Speaker Name: "..."
        matches = re.findall(r"^([A-Z][A-Za-z0-9'\s\-\.]+?):\s*\"", translated_chapter_text, re.MULTILINE)
        for spk in matches:
            spk_clean = spk.strip()
            # Filter out non-character words (e.g. Catatan, Bab, Life, Audio)
            if spk_clean and len(spk_clean) < 40 and not any(k in spk_clean.lower() for k in ["bab", "chapter", "catatan", "life", "interlude", "prolog"]):
                if spk_clean not in existing_chars:
                    existing_chars.add(spk_clean)
                    new_speakers.append(spk_clean)

        if new_speakers:
            print(f"✨ [Dynamic Lore Discovery] Menemukan {len(new_speakers)} tokoh baru di bab ini: {new_speakers}")
            if "characters" not in self.profile_data:
                self.profile_data["characters"] = []
            self.profile_data["characters"].extend(new_speakers)
            self._save_profile()

        return new_speakers

    def register_loanword(self, term: str, explanation: str):
        """
        Registers a newly discovered in-universe technical term or magic spell on-the-fly.
        """
        if "loanwords" not in self.profile_data:
            self.profile_data["loanwords"] = []

        existing_terms = {item.get("term", "").lower() for item in self.profile_data["loanwords"] if isinstance(item, dict)}
        if term.lower() not in existing_terms:
            self.profile_data["loanwords"].append({
                "term": term,
                "explanation": explanation
            })
            self._save_profile()
            print(f"📖 [Dynamic Lore Discovery] Menambahkan istilah baru ke profil: '{term}' -> ({explanation})")
