import os

search_roots = [r"D:\JV", r"C:\Users\Eevyx\Downloads"]
for root in search_roots:
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            fl = f.lower()
            if "hobbit" in fl or "tolkien" in fl or "lotr" in fl:
                fp = os.path.join(dirpath, f)
                try:
                    sz_mb = os.path.getsize(fp) / (1024*1024)
                    print(f"{fp} ({sz_mb:.2f} MB)")
                except Exception:
                    pass
