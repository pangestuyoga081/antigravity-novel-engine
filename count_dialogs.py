import re
from collections import Counter

with open(r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert (Terjemahan ID-Direct).txt", "r", encoding="utf-8") as f:
    txt = f.read()

# Replace any accidental banned words
replacements = {
    "menimpali": "menyahut",
    "Menimpali": "Menyahut",
    "mendengus": "menghela napas kesal",
    "Mendengus": "Menghela napas kesal"
}
for k, v in replacements.items():
    txt = txt.replace(k, v)

with open(r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert (Terjemahan ID-Direct).txt", "w", encoding="utf-8") as f:
    f.write(txt)

dialogs = re.findall(r"([A-Za-z\’\']+(?:\s+[A-Za-z\’\']+)*)\:\s*\"", txt)
counts = Counter(dialogs)
print("Total dialog berlabel:", len(dialogs))
for name, c in counts.most_common(15):
    print(f" - {name}: {c} kali")
