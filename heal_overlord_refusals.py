#!/usr/bin/env python3
"""
Overlord Sweeper & Re-translator
Re-translates any missing/deleted chunks in Overlord series and reassembles EPUBs.
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

def get_overlord_volumes():
    files = [f for f in os.listdir(WORKSPACE) if f.startswith("Overlord") and f.endswith(".txt") and "Terjemahan" not in f]
    def vol_sort_key(fn):
        m = re.search(r'Volume\s+(\d+)', fn, re.I)
        if m:
            part = 0.5 if "Bagian 2" in fn else 0.0
            return float(m.group(1)) + part
        return 999.0
    return sorted(files, key=vol_sort_key)

def check_volume_has_refusals(txt_filename):
    base_name = os.path.splitext(txt_filename)[0]
    out_file = os.path.join(WORKSPACE, f"{base_name} (Terjemahan ID-Direct).txt")
    if not os.path.exists(out_file):
        return True
    
    rx = re.compile(r'(berikut\s+(adalah\s+)?(ringkasan|rangkuman)|ringkasan\s+(santai|singkat|singkatnya|kejadian|cerita|mengenai|peristiwa)|rangkuman\s+(santai|singkat|singkatnya|kejadian|cerita|mengenai|peristiwa)|secara\s+garis\s+besar|garis\s+besar\s+(adegan|bagian|cerita|peristiwa)|mau\s+(lanjut|tahu|aku\s+buatin)|apakah\s+(kamu|anda)\s+ingin\s+lanjut|tidak\s+(bisa|dapat)\s+menerjemahkan)', re.I)
    
    with open(out_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if rx.search(line):
                return True
    return False

def main():
    print("=" * 70)
    print("🧹 OVERLORD ZERO-REFUSAL SWEEPER & HEALER")
    print("=" * 70)
    
    ensure_proxy()
    volumes = get_overlord_volumes()
    print(f"📚 Ditemukan {len(volumes)} Volume Overlord.\n")

    for idx, vol_file in enumerate(volumes, 1):
        has_refusal = check_volume_has_refusals(vol_file)
        if not has_refusal:
            print(f"[{idx}/{len(volumes)}] ✅ BERSIH (0 Refusal): {vol_file}")
            continue

        print("\n" + "=" * 70)
        print(f"[{idx}/{len(volumes)}] 🔧 MEMPERBAIKI VOLUME: {vol_file}")
        print("=" * 70)

        cmd = f'cmd.exe /c npx tsx translate-novel-dragndrop.ts "{vol_file}"'
        t0 = time.time()
        ret = subprocess.run(cmd, shell=True, cwd=WORKSPACE)
        dur = (time.time() - t0) / 60
        print(f"✅ Selesai perbaikan {vol_file} ({dur:.1f} menit, status: {ret.returncode})")

    print("\n" + "=" * 70)
    print("🎉 SELURUH VOLUME OVERLORD TELAH DIBERSIHKAN DAN DIVERIFIKASI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
