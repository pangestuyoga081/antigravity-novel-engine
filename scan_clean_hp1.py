import re

txt_p = r"E:\antigravity-novel-engine\Harry Potter ID\Harry Potter 1 - Batu Bertuah (Terjemahan ID-Direct).txt"
with open(txt_p, "r", encoding="utf-8") as f:
    text = f.read()

bad_words = [
    'budak korporat',
    'bos toxic',
    'lembur shift',
    'gaji umr',
    'mencicit',
    'menukas',
    'menimpali',
    'tersenyum simpul',
    'tatkala'
]

print("Scanning for banned terms and jokes:")
for w in bad_words:
    matches = list(re.finditer(re.escape(w), text, re.I))
    print(f"Term '{w}': {len(matches)} matches")
    for m in matches:
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 80)
        print("  MATCH:", repr(text[start:end]))
