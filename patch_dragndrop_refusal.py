with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "r", encoding="utf-8") as f:
    code = f.read()

# Add patterns to isRefusalResponse
old_pattern_end = """    /bagian\\s+awal\\s+perjalanan\\s+reinkarnasi/i,
    /kisah\\s+awal\\s+reinkarnasi/i
  ];"""

new_pattern_end = """    /bagian\\s+awal\\s+perjalanan\\s+reinkarnasi/i,
    /kisah\\s+awal\\s+reinkarnasi/i,
    /permintaan\\s+(ini\\s+)?(meminta|untuk)/i,
    /instruksi\\s+sistem\\s+melarang/i,
    /tidak\\s+dapat\\s+dipenuhi/i,
    /tanpa\\s+memuat\\s+unsur\\s+(pornografi|kata-kata)/i,
    /penyampaian\\s+ulang\\s+isi\\s+teks/i,
    /materi\\s+non-seksual/i
  ];"""

code = code.replace(old_pattern_end, new_pattern_end)

with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated refusal detection patterns in dragndrop.ts successfully!")
