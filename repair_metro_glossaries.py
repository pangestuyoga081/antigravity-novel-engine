import re

with open(r"D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Pecah setiap tag [GLOSSARY: ...] yang menempel rapat tanpa newline
text = re.sub(r'\]\s*\[GLOSSARY:', ']\n[GLOSSARY:', text)
text = re.sub(r'\]\s*\[CAST:', ']\n[CAST:', text)

# 2. Perbaiki istilah-istilah glosarium yang sebelumnya terpotong aneh
TERM_FIXES = [
    (r"\[GLOSSARY:\s*Subjudul:\s*Du Stirbst\s*\|", "[GLOSSARY: Du Stirbst |"),
    (r"\[GLOSSARY:\s*tiga\s*\|", "[GLOSSARY: Swastika Cabang Tiga |"),
    (r"\[GLOSSARY:\s*dorong\s*\|", "[GLOSSARY: Lori Dorong |"),
    (r"\[GLOSSARY:\s*kayu\s*\|", "[GLOSSARY: Senapan Mesin Popor Kayu |"),
    (r"\[GLOSSARY:\s*santai\s*\|", "[GLOSSARY: Patung Dostoevsky |"),
    (r"\[GLOSSARY:\s*ganda\s*\|", "[GLOSSARY: Senapan Laras Ganda |"),
    (r"\[GLOSSARY:\s*laras ganda\s*\|", "[GLOSSARY: Senapan Laras Ganda |"),
    (r"\[GLOSSARY:\s*Khan:\s*Lewat Kitai Gorod\s*\|", "[GLOSSARY: Kitai-Gorod |"),
    (r"\[GLOSSARY:\s*Istilah\s*\|\s*Prospekt Mira", "[GLOSSARY: Prospekt Mira |"),
    (r"\[GLOSSARY:\s*Istilah\s*\|\s*Menara Pengawal", "[GLOSSARY: Menara Pengawal |"),
    (r"\[GLOSSARY:\s*Toten Tatenruhm’\*\s*\|", "[GLOSSARY: Toten Tatenruhm |"),
]

for pat, rep in TERM_FIXES:
    text = re.sub(pat, rep, text)

# 3. Pastikan setiap [CAST: ...] dan [GLOSSARY: ...] berada di barisnya sendiri
lines = text.split("\n")
cleaned_lines = []
for line in lines:
    stripped = line.strip()
    # Jika baris memuat Subjudul: Du Stirbst tepat setelah glossary, pisahkan atau abaikan jika redundant
    if stripped.startswith("Subjudul: Du Stirbst"):
        continue
    cleaned_lines.append(line)

text = "\n".join(cleaned_lines)
# Rapikan newline berlebih
text = re.sub(r"\n{3,}", "\n\n", text)

with open(r"D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Repair complete! All glossaries isolated and terms cleaned.")
