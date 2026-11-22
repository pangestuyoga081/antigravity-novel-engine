import os
import glob
import subprocess

rar_files = sorted(glob.glob(r"D:\JV\novel yoga\High School DxD\High_School_DxD_Volume_*.rar"))
print(f"Total RAR files found: {len(rar_files)}")

seven_zip = r"C:\Program Files\7-Zip\7z.exe"

for rar in rar_files:
    base = os.path.basename(rar).replace(".rar", "")
    vol_num = base.split("_")[-1]
    out_dir = rf"D:\JV\novel yoga\High School DxD\extracted\Vol_{vol_num}"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    
    cmd = [seven_zip, "x", rar, f"-o{out_dir}", "-y"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"[{base}] Successfully extracted -> Vol_{vol_num}")
    else:
        print(f"[{base}] Extraction failed with code {res.returncode}")

print("\nAll extractions completed!")
