import os
import urllib.request
import re
import ssl
import zipfile

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

files = [
    ("Harry Potter 1 - Batu Bertuah.epub", "1FCAXzt5W6I5m1WvuoWR6PeDKy1cXLMRm"),
    ("Harry Potter 2 - Kamar Rahasia.epub", "1FHewYx1g9WvjmgwvWlEccyZZ7tsUVxb2"),
    ("Harry Potter 3 - Tawanan Azkaban.epub", "1FdlWdNWGidIuxGKVbVqBJdL3yulA-u-M"),
    ("Harry Potter 4 - Piala Api.epub", "1FYY1X2TdWed6sb5ajpljhtUMjIZwSp8V"),
    ("Harry Potter 5 - Orde Phoenix.epub", "1FQDehu3mIr7ikDElhQ3dLjEt6Lg_5ghQ"),
    ("Harry Potter 6 - Pangeran Berdarah-Campuran.epub", "1FQukgs_4gXuD1emJGHz31TgvG6PkS6EF"),
    ("Harry Potter 7 - Relikui Kematian.epub", "1FYrUUwMQlD6mm3sqHnnaq4Umjx8jYRgj")
]

dest_dir = r"E:\antigravity-novel-engine\Harry Potter ID"
os.makedirs(dest_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

for name, fid in files:
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
    target = os.path.join(dest_dir, name)
    print(f"Downloading {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp, open(target, 'wb') as fp:
            fp.write(resp.read())
        size = os.path.getsize(target)
        valid = zipfile.is_zipfile(target)
        print(f"  -> SUCCESS ({size/1024:.1f} KB, ZipValid={valid})")
    except Exception as e:
        print(f"  -> FAILED: {e}")
