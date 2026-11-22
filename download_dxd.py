import urllib.request
import re
import ssl
import os
import sys
import time

urls = [
    ("Vol 01", "https://www.mediafire.com/file/05i32uf76hg8hhs/High_School_Dxd_-_Volume_01_%255BRuiDrive%255D.rar/file"),
    ("Vol 02", "https://www.mediafire.com/file/3ayuv1e89tl0ugh/High_School_Dxd_-_Volume_02_%255BRuiDrive%255D.rar/file"),
    ("Vol 03", "https://www.mediafire.com/file/zsn8jxv9jn8rl0k/High_School_Dxd_-_Volume_03_%255BRuiDrive%255D.rar/file"),
    ("Vol 04", "https://www.mediafire.com/file/btkp78wkvnp2nzd/High_School_Dxd_-_Volume_04_%255BRuiDrive%255D.rar/file"),
    ("Vol 05", "https://www.mediafire.com/file/altyngwxmizg3vz/High_School_Dxd_-_Volume_05_%255BRuiDrive%255D.rar/file"),
    ("Vol 06", "https://www.mediafire.com/file/iza1sq9xuygappv/High_School_Dxd_-_Volume_06_%255BRuiDrive%255D.rar/file"),
    ("Vol 07", "https://www.mediafire.com/file/yzqwd1yw72uel44/High_School_Dxd_-_Volume_07_%255BRuiDrive%255D.rar/file"),
    ("Vol 08", "https://www.mediafire.com/file/pzfn0wlt6wwruj4/High_School_Dxd_-_Volume_08_%255BRuiDrive%255D.rar/file"),
    ("Vol 09", "https://www.mediafire.com/file/d043499tfqtaj5k/High_School_Dxd_-_Volume_09_%255BRuiDrive%255D.rar/file"),
    ("Vol 10", "https://www.mediafire.com/file/4ukxghuduvclpfs/High_School_Dxd_-_Volume_10_%255BRuiDrive%255D.rar/file"),
    ("Vol 11", "https://www.mediafire.com/file/qrwm4c5s65b2s5b/High_School_Dxd_-_Volume_11_%255BRuiDrive%255D.rar/file"),
    ("Vol 12", "https://www.mediafire.com/file/1u50iz7kv9p4sbd/High_School_Dxd_-_Volume_12_%255BRuiDrive%255D.rar/file"),
    ("Vol 13", "https://www.mediafire.com/file/dqxej4c4olha9d9/High_School_Dxd_-_Volume_13_%255BRuiDrive%255D.rar/file"),
    ("Vol 14", "https://www.mediafire.com/file/h4z6sea62jrvqgr/High_School_Dxd_-_Volume_14_%255BRuiDrive%255D.rar/file"),
    ("Vol 15", "https://www.mediafire.com/file/2m6z3fj11jtt1rq/High_School_Dxd_-_Volume_15_%255BRuiDrive%255D.rar/file"),
    ("Vol 16", "https://www.mediafire.com/file/4jjgh4xy3mtxjbm/High_School_Dxd_-_Volume_16_%255BRuiDrive%255D.rar/file"),
    ("Vol 17", "https://www.mediafire.com/file/wiow41q1r42bjrq/High_School_Dxd_-_Volume_17_%255BRuiDrive%255D.rar/file"),
    ("Vol 18", "https://www.mediafire.com/file/gs40m8ggg69alg9/High_School_Dxd_-_Volume_18_%255BRuiDrive%255D.rar/file"),
    ("Vol 19", "https://www.mediafire.com/file/z3c5saq6m54fpj8/High_School_Dxd_-_Volume_19_%255BRuiDrive%255D.rar/file"),
    ("Vol 20", "https://www.mediafire.com/file/j6j65qwknrju3sw/High_School_Dxd_-_Volume_20_%255BRuiDrive%255D.rar/file"),
    ("Vol 21", "https://www.mediafire.com/file/r10b36s9mnlgp8n/High_School_Dxd_-_Volume_21_%255BRuiDrive%255D.rar/file"),
    ("Vol 22", "https://www.mediafire.com/file/ic2oqfvqnd5p6cs/High_School_Dxd_-_Volume_22_%255BRuiDrive%255D.rar/file"),
    ("Vol 23", "https://www.mediafire.com/file/fqneo8hzvmn9bfe/High_School_Dxd_-_Volume_23_%255BRuiDrive%255D.rar/file"),
    ("Vol 24", "https://www.mediafire.com/file/feoarr5u0ct0iny/High_School_Dxd_-_Volume_24_%255BRuiDrive%255D.rar/file"),
    ("Vol 25", "https://www.mediafire.com/file/osg3en118ig1uf6/High+School+Dxd+-+Volume+25+[RuiDrive].rar/file")
]

target_dir = r"D:\JV\novel yoga\High School DxD"
os.makedirs(target_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_direct_url(page_url):
    req = urllib.request.Request(page_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                m = re.search(r'href="(https?://download[^"]+)"', html)
                if m:
                    return m.group(1)
                m2 = re.search(r'aria-label="Download file"\s+href="([^"]+)"', html)
                if m2:
                    return m2.group(1)
        except Exception as e:
            time.sleep(2)
    return None

def download_file(vol_label, page_url):
    vol_num = vol_label.replace("Vol ", "").strip()
    dest_path = os.path.join(target_dir, f"High_School_DxD_Volume_{vol_num}.rar")
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
        print(f"[{vol_label}] Sudah ada ({os.path.getsize(dest_path) / (1024*1024):.2f} MB), lewati.")
        return True

    print(f"[{vol_label}] Mengambil direct link...")
    direct_url = get_direct_url(page_url)
    if not direct_url:
        print(f"[{vol_label}] ❌ Gagal mendapatkan link MediaFire!")
        return False

    print(f"[{vol_label}] Mengunduh dari {direct_url[:60]}...")
    req = urllib.request.Request(direct_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
        sz_mb = len(data) / (1024 * 1024)
        print(f"[{vol_label}] ✅ Sukses diunduh ({sz_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"[{vol_label}] ❌ Error saat mengunduh: {e}")
        return False

def main():
    print("🚀 Memulai proses unduh 25 Volume High School DxD...")
    success_count = 0
    for label, url in urls:
        ok = download_file(label, url)
        if ok:
            success_count += 1
        time.sleep(1)
    print(f"\n🎉 Selesai! Berhasil mengunduh {success_count}/{len(urls)} file.")

if __name__ == "__main__":
    main()
