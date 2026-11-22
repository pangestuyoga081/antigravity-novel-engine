import zipfile, re, os

epub_path = r"d:\JV\novel yoga\The Hobbit - Tolkien, J. R. R._5022.epub"
with zipfile.ZipFile(epub_path, "r") as z:
    total_chars = 0
    total_chunks = 0
    chap_info = []
    
    for i in range(6, 25): # part0006 to part0024
        fname = f"text/part{i:04d}.html"
        raw = z.read(fname).decode("utf-8", errors="ignore")
        # replace img with marker
        raw = re.sub(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>', r'\n\n[[ILUSTRASI:\1]]\n\n', raw)
        clean = re.sub(r'<[^>]+>', ' ', raw)
        clean = re.sub(r'[ \t]+', ' ', clean).strip()
        
        # split by paragraphs
        paras = [p.strip() for p in clean.split('\n') if p.strip()]
        # chunk by 5500 chars
        chunks = []
        cur = []
        cur_len = 0
        for p in paras:
            cur.append(p)
            cur_len += len(p)
            if cur_len >= 5500:
                chunks.append("\n\n".join(cur))
                cur = []
                cur_len = 0
        if cur:
            chunks.append("\n\n".join(cur))
            
        total_chars += len(clean)
        total_chunks += len(chunks)
        chap_info.append((fname, len(clean), len(chunks)))

    print(f"Total Chapters: {len(chap_info)}")
    print(f"Total Characters: {total_chars:,}")
    print(f"Total Chunks (~5500 chars): {total_chunks}")
    for c in chap_info:
        print(f"  {c[0]}: {c[1]:,} chars -> {c[2]} chunks")
