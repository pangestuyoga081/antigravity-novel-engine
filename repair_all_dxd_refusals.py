import os
import glob
import re
import concurrent.futures
from repair_refusals_lib import is_refusal, call_clean_ai
from marathon_clean_dxd import compile_volume_epub

DXD_ROOT = r"D:\JV\novel yoga\High School DxD"

def repair_all_volumes():
    print("🔍 Memeriksa seluruh 25 volume dari teks penolakan (refusals)...")
    
    for v in range(1, 26):
        v_str = f"{v:02d}"
        cache_dir = os.path.join(DXD_ROOT, f".High_School_DxD_Volume_{v_str}_Raw_Source_chunks_cache")
        raw_source_file = os.path.join(DXD_ROOT, f"High_School_DxD_Volume_{v_str}_Raw_Source.txt")
        trans_file = os.path.join(DXD_ROOT, f"High_School_DxD_Volume_{v_str}_Raw_Source (Terjemahan ID-Direct).txt")
        img_dir = os.path.join(DXD_ROOT, f"extracted_images_vol_{v_str}")
        if not os.path.exists(img_dir):
            sub_d = glob.glob(rf"D:\JV\novel yoga\High School DxD\extracted\Vol_{v_str}\**\Image*", recursive=True)
            img_d = sub_d[0] if sub_d else None
        else:
            img_d = img_dir
            
        if not os.path.exists(cache_dir):
            continue
            
        # Scan all chunk files in cache
        refusal_files = []
        for root, dirs, files in os.walk(cache_dir):
            for file in files:
                if file.startswith("chunk_") and file.endswith(".txt"):
                    fpath = os.path.join(root, file)
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                    if is_refusal(c):
                        refusal_files.append((fpath, c))
                        
        if refusal_files:
            print(f"\n[Vol {v_str}] Ditemukan {len(refusal_files)} chunk dengan teks penolakan. Memperbaiki...")
            
            for fpath, bad_text in refusal_files:
                # Find the clean raw text in raw_source or re-translate with mild prompt
                # Often the refusal text contains "Berikut adalah penyampaian ulang...":
                # If bad_text has actual story content below the refusal header, strip it!
                lines = bad_text.split("\n")
                story_lines = []
                in_story = False
                for l in lines:
                    if any(l.strip().startswith(k) for k in ["Berikut adalah", "Yo, udah lama", "Bab", "Life", "***"]):
                        in_story = True
                        continue
                    if in_story:
                        if not any(k in l for k in ["Permintaan ini meminta", "tidak dapat dipenuhi", "instruksi sistem melarang"]):
                            story_lines.append(l)
                            
                recovered_story = "\n".join(story_lines).strip()
                if len(recovered_story) > 300 and not is_refusal(recovered_story):
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(recovered_story)
                    print(f"   ✅ [Cleaned header] {os.path.basename(fpath)}")
                else:
                    # Need to re-translate from raw source chunk
                    # Delete the bad chunk so it will get regenerated or replace with clean AI
                    print(f"   🔄 [Re-translating] {os.path.basename(fpath)}...")
                    # We can use the text inside bad_text as query to sanitize
                    res = call_clean_ai(bad_text)
                    if res and not is_refusal(res):
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(res)
                        print(f"   ✅ [Re-translated] {os.path.basename(fpath)}")
                    else:
                        # Fallback: keep non-refusal lines
                        cleaned = re.sub(r'Permintaan.*?\n\n', '', bad_text, flags=re.DOTALL)
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(cleaned.strip())
                            
            # Reassemble full translated TXT
            chaps = sorted(os.listdir(cache_dir))
            full_assembled = []
            for ch in chaps:
                ch_p = os.path.join(cache_dir, ch)
                if os.path.isdir(ch_p):
                    cfiles = sorted([os.path.join(ch_p, f) for f in os.listdir(ch_p) if f.startswith("chunk_") and f.endswith(".txt")])
                    parts = []
                    for cf in cfiles:
                        with open(cf, "r", encoding="utf-8", errors="ignore") as f:
                            parts.append(f.read().strip())
                    full_assembled.append(f"### {ch}\n\n" + "\n\n".join(parts))
                    
            new_trans_txt = "\n\n".join(full_assembled)
            with open(trans_file, "w", encoding="utf-8") as f:
                f.write(new_trans_txt)
                
            # Recompile EPUB
            if img_d and os.path.exists(img_d):
                compile_volume_epub(v_str, trans_file, img_d)
                print(f"[Vol {v_str}] 🎉 Sukses dibersihkan dan di-recompile!")

if __name__ == "__main__":
    repair_all_volumes()
