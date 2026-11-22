#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import time

os.environ["LLM_MODEL"] = "ag/gemini-3.8-flash-low"

WORKSPACE = r"E:\novel yoga"

def get_ordered_volumes():
    files = [f for f in os.listdir(WORKSPACE) if f.startswith("Overlord") and f.endswith(".txt") and "Terjemahan" not in f]
    
    def vol_sort_key(fn):
        m = re.search(r'Volume\s+(\d+)', fn, re.I)
        if m:
            # Jika ada "Bagian 2", beri bobot 0.5
            part = 0.5 if "Bagian 2" in fn else 0.0
            return float(m.group(1)) + part
        return 999.0

    return sorted(files, key=vol_sort_key)

def is_volume_completed(txt_filename):
    base_name = os.path.splitext(txt_filename)[0]
    epub_path = os.path.join(WORKSPACE, "epubs", f"{base_name} (Illustrated ID-Direct).epub")
    return os.path.exists(epub_path) and os.path.getsize(epub_path) > 100000

def main():
    print("=" * 70)
    print("🚀 OVERLORD MARATHON RUNNER (VOLUME 02 - 16)")
    print("=" * 70)

    vols = get_ordered_volumes()
    print(f"📚 Ditemukan {len(vols)} volume Overlord:")
    for idx, v in enumerate(vols, 1):
        status = "✅ SELESAI" if is_volume_completed(v) else "⏳ BELUM"
        print(f"  {idx:02d}. {v} [{status}]")

    print("\n⚡ Memulai eksekusi maraton berurutan...")

    for v in vols:
        if is_volume_completed(v):
            print(f"\n⏭️  Melewati {v} (Sudah selesai & EPUB terkompilasi).")
            continue

        cmd = ["cmd.exe", "/c", "npx", "tsx", "translate-novel-dragndrop.ts", v]
        
        while not is_volume_completed(v):
            print(f"\n" + "=" * 70)
            print(f"📖 MEMPROSES: {v}")
            print("=" * 70)

            start_t = time.time()
            proc = subprocess.Popen(cmd, cwd=WORKSPACE)
            proc.wait()

            dur = (time.time() - start_t) / 60.0
            if proc.returncode == 0:
                print(f"\n🎉 {v} BERHASIL DISELESAIKAN DALAM {dur:.1f} MENIT!")
                break
            else:
                print(f"\n⚠️ {v} keluar dengan kode {proc.returncode}. Menunggu 15 detik lalu melanjutkan bagian yang belum selesai...")
                time.sleep(15)

    print("\n" + "=" * 70)
    print("🏆 SELURUH VOLUME OVERLORD TELAH TUNTAS!")
    print("=" * 70)

if __name__ == '__main__':
    main()
