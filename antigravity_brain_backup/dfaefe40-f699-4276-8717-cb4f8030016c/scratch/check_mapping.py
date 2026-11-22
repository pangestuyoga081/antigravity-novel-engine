import os

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"

all_pdfs = []
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith('.pdf'):
            all_pdfs.append(os.path.join(root, f))

vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

mapping = {}
for vk in vol_keys:
    target_str = f"Volume {vk}"
    matched = None
    for p in all_pdfs:
        fname = os.path.basename(p)
        if target_str.lower() in fname.lower():
            matched = p
            break
    mapping[vk] = matched

for vk, p in mapping.items():
    print(f"Vol {vk}: {os.path.basename(p) if p else 'NOT FOUND'}")
