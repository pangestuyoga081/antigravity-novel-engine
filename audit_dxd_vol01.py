import re
from collections import Counter

with open(r"D:\JV\novel yoga\High School DxD\High_School_DxD_Volume_01_Raw_Source (Terjemahan ID-Direct).txt", "r", encoding="utf-8") as f:
    txt = f.read()

# Replace any accidental 'kamu'
txt = re.sub(r'\bkamu\b', 'lu', txt, flags=re.IGNORECASE)
with open(r"D:\JV\novel yoga\High School DxD\High_School_DxD_Volume_01_Raw_Source (Terjemahan ID-Direct).txt", "w", encoding="utf-8") as f:
    f.write(txt)

# Check dialogue labels
dialogs = re.findall(r"([A-Za-z\s]+)\:\s*[\"“]", txt)
counts = Counter([d.strip() for d in dialogs])
print("Total dialog berlabel:", len(dialogs))
for name, c in counts.most_common(15):
    print(f" - {name}: {c} kali")

# Check illustrations
tags = re.findall(r"\[\[ILUSTRASI:[^\]]+\]\]", txt)
print("\nTag ilustrasi:")
for t in tags:
    print(" -", t)
