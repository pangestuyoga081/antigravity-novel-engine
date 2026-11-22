import os, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
txt_path = os.path.join(base_dir, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")

with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect Vol 01 Chapter 01
m = re.search(r"###\s+VOLUME 01 - Chapter 01(.*?)(?=###\s+VOLUME 01 - Chapter 02)", text, re.DOTALL | re.IGNORECASE)
if m:
    ch1 = m.group(1)
    print("Chapter 1 length:", len(ch1))
    print(ch1[:500])
