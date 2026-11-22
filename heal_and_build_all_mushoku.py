#!/usr/bin/env python3
"""
Mushoku Tensei Zero-Refusal Sweeper & EPUB Builder
Heals any remaining refusal chunks and builds all 26 illustrated EPUBs.
"""

import os
import sys
import subprocess
import re
import urllib.request
import time

os.environ["LLM_MODEL"] = "ag/gemini-3.8-flash-low"
WORKSPACE = r"E:\novel yoga"

def ensure_proxy():
    try:
        req = urllib.request.Request("http://127.0.0.1:20128/v1/models")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.getcode() == 200:
                return True
    except:
        pass
    print("⚠️ 9router belum aktif. Menjalankan 9router di background...")
    subprocess.Popen("cmd.exe /c 9router -t --skip-update", shell=True)
    time.sleep(3)
    return True

def heal_volume_txt(v):
    vol_file = f"Mushoku Tensei - Volume {v:02d}.txt"
    out_file = os.path.join(WORKSPACE, f"Mushoku Tensei - Volume {v:02d} (Terjemahan ID-Direct).txt")
    print(f"\n=======================================================")
    print(f"🔧 [Vol {v:02d}] Menjalankan penerjemahan ulang chunk yang dihapus...")
    print(f"=======================================================")
    cmd = f'cmd.exe /c npx tsx translate-novel-dragndrop.ts "{vol_file}"'
    ret = subprocess.run(cmd, shell=True, cwd=WORKSPACE)
    return ret.returncode == 0

def build_volume_epub(v):
    vol_name = f"Mushoku Tensei - Volume {v:02d}"
    txt_file = os.path.join(WORKSPACE, f"{vol_name} (Terjemahan ID-Direct).txt")
    epub_out_dir = os.path.join(WORKSPACE, "epubs")
    os.makedirs(epub_out_dir, exist_ok=True)
    epub_out_file = os.path.join(epub_out_dir, f"{vol_name} (Illustrated ID-Direct).epub")
    
    # We pass a dummy source epub path pointing to illustrations folder
    src_epub = os.path.join(WORKSPACE, "illustrations", f"Mushoku_Tensei_Volume_{v:02d}")
    helper_script = os.path.join(WORKSPACE, "compile_epub_helper.py")
    
    print(f"📚 Mengompilasi EPUB Vol {v:02d}...")
    cmd = f'python "{helper_script}" "{txt_file}" "{src_epub}" "{epub_out_file}"'
    ret = subprocess.run(cmd, shell=True, cwd=WORKSPACE)
    if ret.returncode == 0 and os.path.exists(epub_out_file) and os.path.getsize(epub_out_file) > 50000:
        print(f"✅ EPUB Berhasil: {epub_out_file} ({os.path.getsize(epub_out_file)/1024/1024:.2f} MB)")
        return True
    else:
        print(f"❌ Gagal compile EPUB Vol {v:02d}")
        return False

def main():
    print("=" * 70)
    print("🌟 MUSHOKU TENSEI (VOL 01 - 26) HEALER & EPUB COMPILER")
    print("=" * 70)

    ensure_proxy()

    vols_to_heal = [3, 4, 8, 10, 12, 13, 16, 17, 20, 22, 24]
    print(f"🛠️ Volume yang butuh re-translate chunk refusal: {vols_to_heal}\n")

    for v in vols_to_heal:
        heal_volume_txt(v)

    print("\n" + "=" * 70)
    print("🎨 MEMBANGUN SEMUA EPUB BERILUSTRASI (VOLUMES 01 - 26)")
    print("=" * 70)

    success_epubs = 0
    for v in range(1, 27):
        if build_volume_epub(v):
            success_epubs += 1

    print("\n" + "=" * 70)
    print(f"🎉 SELESAI SEMPURNA! {success_epubs}/26 EPUB BERHASIL DIBUAT!")
    print("=" * 70)

if __name__ == "__main__":
    main()
