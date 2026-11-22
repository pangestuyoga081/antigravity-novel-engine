import os, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
txt_path = os.path.join(base_dir, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")

with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

vol_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '17.1']

# Slice volumes
vol_starts = {}
for vk in vol_keys:
    m = re.search(rf"^###\s+VOLUME\s+{re.escape(vk)}\b", text, re.MULTILINE | re.IGNORECASE)
    if m:
        vol_starts[vk] = m.start()

for i, vk in enumerate(vol_keys):
    start = vol_starts[vk]
    end = vol_starts[vol_keys[i+1]] if i+1 < len(vol_keys) else len(text)
    vol_text = text[start:end]
    
    # Split by ###
    raw_sections = re.split(r"(?=^###\s+)", vol_text, flags=re.MULTILINE)
    chapters = []
    for sec in raw_sections:
        sec = sec.strip()
        if not sec.startswith("###"):
            continue
        lines = sec.split("\n")
        title_line = re.sub(rf"^###\s+(?:VOLUME\s+{re.escape(vk)}\s*[-:]*\s*)?", "", lines[0], flags=re.IGNORECASE).strip()
        body = "\n".join(lines[1:]).strip()
        if len(body) > 50:
            chapters.append({"title": title_line, "chars": len(body)})
            
    print(f"Vol {vk}: {len(chapters)} chapters -> {[c['title'][:25] for c in chapters]}")
