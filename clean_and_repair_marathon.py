#!/usr/bin/env python3
import os
import re
import json
import subprocess
import time

WORKSPACE = r"E:\novel yoga"

STRICT_REFUSAL_RE = re.compile(
    r'(tidak\s+(bisa|dapat|diizinkan|diperbolehkan)\s+(untuk\s+)?(menulis|menuliskan|menerjemahkan|menyajikan|membuat|mengadaptasi|memberikan)'
    r'|secara\s+(kata\s+demi\s+kata|baris\s+demi\s+baris)'
    r'|(ringkasan|rangkuman)\s+umum'
    r'|naskah\s+(novel\s+)?aslinya'
    r'|(alih-alih|daripada)\s+menulis\s+ulang'
    r'|apakah\s+(kamu|anda)\s+ingin\s+(ringkasan|melihat|saya)'
    r'|(novel|karya)\s+berhak\s+cipta'
    r'|(kebijakan|batasan|aturan)\s+hak\s+cipta'
    r'|hak\s+cipta\s+melarang'
    r'|garis\s+besar\s+adegan'
    r'|peristiwa\s+penting\s+yang\s+terjadi)',
    re.I
)

def clean_refusal_chunks():
    print("=" * 70)
    print("🧹 SCAN & CLEAN SEMUA CHUNK REFUSAL (OVERLORD)")
    print("=" * 70)

    affected_volumes = set()
    cleaned_chunks = 0

    for root, dirs, files in os.walk(WORKSPACE):
        if "_chunks_cache" in root and "overlord" in root.lower():
            for f in files:
                if f.endswith(".txt"):
                    fp = os.path.join(root, f)
                    try:
                        content = ""
                        with open(fp, "r", encoding="utf-8") as fh:
                            content = fh.read()

                        if STRICT_REFUSAL_RE.search(content):
                            os.remove(fp)
                            cleaned_chunks += 1
                            # Tentukan volume
                            rel = os.path.relpath(root, WORKSPACE)
                            cache_folder = rel.split(os.sep)[0]
                            vol_name = cache_folder.lstrip(".").replace("_chunks_cache", "")
                            affected_volumes.add(vol_name)
                            print(f"  ❌ Hapus chunk refusal: {os.path.basename(root)}/{f} ({vol_name})")
                    except Exception as e:
                        print("Error on", fp, e)

    print(f"\n✨ Total {cleaned_chunks} chunk refusal berhasil dibersihkan.")
    print(f"📚 Volume yang terdampak dan akan dire-generate ({len(affected_volumes)} volume):")
    for v in sorted(affected_volumes):
        print(f"   - {v}")
        # Reset output txt, epub, dan checkpoint agar dirakit ulang rapi
        out_txt = os.path.join(WORKSPACE, f"{v} (Terjemahan ID-Direct).txt")
        if os.path.exists(out_txt):
            os.remove(out_txt)
        
        out_epub = os.path.join(WORKSPACE, "epubs", f"{v} (Illustrated ID-Direct).epub")
        if os.path.exists(out_epub):
            os.remove(out_epub)

        ckpt = os.path.join(WORKSPACE, f"{v}_checkpoint.json")
        with open(ckpt, "w", encoding="utf-8") as fh:
            json.dump({"completedIds": []}, fh, indent=2)

    return affected_volumes

if __name__ == "__main__":
    clean_refusal_chunks()
