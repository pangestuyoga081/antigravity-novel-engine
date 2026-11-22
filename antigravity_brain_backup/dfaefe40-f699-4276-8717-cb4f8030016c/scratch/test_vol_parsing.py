import os, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
txt_path = os.path.join(base_dir, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")

with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

# Pattern for volume boundary:
# Look for the first chapter header of each volume
vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

# Let's find all headers with ### VOLUME
headers = list(re.finditer(r"^(###\s+VOLUME\s+(\d+(?:\.\d+)?)[^\n]*)", text, re.MULTILINE | re.IGNORECASE))
print(f"Total volume chapter headers: {len(headers)}")

# Group by volume
vol_groups = {}
for h in headers:
    full_h = h.group(1)
    vk = h.group(2)
    start_pos = h.start()
    if vk not in vol_groups:
        vol_groups[vk] = []
    vol_groups[vk].append((start_pos, full_h))

print("\nVolume headers count:")
for vk in vol_keys:
    hs = vol_groups.get(vk, [])
    print(f"Vol {vk}: {len(hs)} chapters. First: {hs[0][1] if hs else 'None'}")
