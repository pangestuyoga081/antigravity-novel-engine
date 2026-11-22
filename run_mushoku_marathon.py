#!/usr/bin/env python3
"""
Marathon Translation Runner for Mushoku Tensei [LN] (Volumes 01 - 26)
Ensures 9router is online, translates sequentially, and compiles illustrated EPUBs.
"""

import os
import sys
import re
import subprocess
import time
import urllib.request
import json

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

def get_ordered_volumes():
    files = [f for f in os.listdir(WORKSPACE) if f.startswith("Mushoku Tensei - Volume") and f.endswith(".txt") and "Terjemahan" not in f]
    def vol_sort_key(fn):
        m = re.search(r'Volume\s+(\d+)', fn, re.I)
        return int(m.group(1)) if m else 999
    return sorted(files, key=vol_sort_key)

def is_volume_completed(txt_filename):
    base_name = os.path.splitext(txt_filename)[0]
    epub_path = os.path.join(WORKSPACE, "epubs", f"{base_name} (Illustrated ID-Direct).epub")
    txt_out = os.path.join(WORKSPACE, f"{base_name} (Terjemahan ID-Direct).txt")
    return os.path.exists(epub_path) and os.path.getsize(epub_path) > 100000 and os.path.exists(txt_out) and os.path.getsize(txt_out) > 50000

def main():
    print("=" * 70)
    print("🚀 MUSHOKU TENSEI MARATHON RUNNER (VOLUMES 01 - 26)")
    print("=" * 70)
    
    ensure_proxy()
    volumes = get_ordered_volumes()
    print(f"📚 Total file sumber terdeteksi: {len(volumes)} Volume\n")

    for idx, vol_file in enumerate(volumes, 1):
        vol_path = os.path.join(WORKSPACE, vol_file)
        base_name = os.path.splitext(vol_file)[0]
        
        if is_volume_completed(vol_file):
            print(f"[{idx}/{len(volumes)}] ⏭️  LEWATI (Sudah Selesai): {vol_file}")
            continue

        print("\n" + "=" * 70)
        print(f"[{idx}/{len(volumes)}] ▶️  MEMPROSES: {vol_file}")
        print("=" * 70)

        cmd = f'cmd.exe /c npx tsx translate-novel-dragndrop.ts "{vol_file}"'
        
        start_time = time.time()
        ret = subprocess.run(cmd, shell=True, cwd=WORKSPACE)
        elapsed = time.time() - start_time

        if ret.returncode == 0 and is_volume_completed(vol_file):
            print(f"✅ [{idx}/{len(volumes)}] SUKSES: {vol_file} selesai dalam {elapsed/60:.1f} menit!")
        else:
            print(f"⚠️ [{idx}/{len(volumes)}] Terhenti atau perlu retry: {vol_file} (Exit Code: {ret.returncode})")

if __name__ == "__main__":
    main()
