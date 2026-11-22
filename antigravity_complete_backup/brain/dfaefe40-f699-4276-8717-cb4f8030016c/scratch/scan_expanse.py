import re

txt_path = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes (Terjemahan ID-Direct).txt"
with open(txt_path, encoding="utf-8") as f:
    text = f.read()

refusal_patterns = [
    r"tidak\s+dapat\s+dipenuhi",
    r"permintaan\s+ini\s+meminta",
    r"instruksi\s+sistem\s+melarang",
    r"teks\s+sumber\s+yang\s+lu\s+kasih\s+ini\s+cuma",
    r"supaya\s+aturan\s+super\s+ketat\s+lu",
    r"coba\s+tempel\s+teks\s+cuplikan",
    r"====="
]

print("Scanning for refusal patterns & separators...")
for pat in refusal_patterns:
    matches = list(re.finditer(pat, text, re.I))
    print(f"Pattern '{pat}': {len(matches)} matches")
    for m in matches:
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 100)
        print("  MATCH:", repr(text[start:end]))
