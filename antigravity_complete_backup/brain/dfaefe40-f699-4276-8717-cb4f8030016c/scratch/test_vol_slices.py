import os, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
txt_path = os.path.join(base_dir, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")

with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

# Let's find all headers with ###
headers = list(re.finditer(r"^(###\s+[^\n]+)", text, re.MULTILINE))

# Let's map volume slices
vol_starts = {}
for vk in vol_keys:
    m = re.search(rf"^###\s+VOLUME\s+{re.escape(vk)}\b", text, re.MULTILINE | re.IGNORECASE)
    if m:
        vol_starts[vk] = m.start()

print("Volume slices boundaries:")
for i, vk in enumerate(vol_keys):
    start = vol_starts[vk]
    end = vol_starts[vol_keys[i+1]] if i+1 < len(vol_keys) else len(text)
    vol_text = text[start:end]
    # Check headers inside this volume
    v_headers = re.findall(r"^###\s+([^\n]+)", vol_text, re.MULTILINE)
    print(f"Vol {vk}: {len(vol_text):,} chars | {len(v_headers)} sub-headers: {', '.join(v_headers[:4])}{'...' if len(v_headers)>4 else ''}")
