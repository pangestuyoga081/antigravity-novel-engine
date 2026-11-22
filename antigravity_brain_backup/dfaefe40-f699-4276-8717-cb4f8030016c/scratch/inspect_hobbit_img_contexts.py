import zipfile, re, os

epub_path = r"d:\JV\novel yoga\The Hobbit - Tolkien, J. R. R._5022.epub"
with zipfile.ZipFile(epub_path, "r") as z:
    for name in sorted(z.namelist()):
        if name.endswith(".html") and "part" in name:
            content = z.read(name).decode("utf-8", errors="ignore")
            # Find img tags
            img_matches = list(re.finditer(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>', content, re.IGNORECASE))
            if img_matches:
                print(f"=== {name} ({len(img_matches)} images) ===")
                for m in img_matches:
                    src = m.group(1)
                    # Get surrounding text
                    start = max(0, m.start() - 250)
                    end = min(len(content), m.end() + 250)
                    context = content[start:end]
                    clean_ctx = re.sub(r'<[^>]+>', ' ', context)
                    clean_ctx = ' '.join(clean_ctx.split())
                    print(f"  Img: {src}")
                    print(f"  Context: {clean_ctx}\n")
