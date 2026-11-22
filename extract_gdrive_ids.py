with open(r"E:\antigravity-novel-engine\gdrive_folder.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

for name in [
    "Harry Potter dan Batu Bertuah",
    "Harry Potter dan Kamar Rahasia",
    "Harry Potter dan Tawanan Azkaban",
    "Harry Potter dan Piala Api",
    "Harry Potter dan Orde Phoenix",
    "Harry Potter dan Pangeran Berdarah-Campuran",
    "Harry Potter dan Relikui Kematian"
]:
    idx = html.find(name)
    if idx != -1:
        snippet = html[max(0, idx-200):min(len(html), idx+300)]
        print(f"=== {name} ===")
        print(repr(snippet))
        print("="*50)
