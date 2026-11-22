import zipfile
import re

epub_path = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes.epub"
with zipfile.ZipFile(epub_path, 'r') as z:
    prologue = z.read("OEBPS/Text/dummy_split_068.html").decode("utf-8", errors="ignore")
    # clean tags to see text
    text = re.sub(r'<[^>]+>', ' ', prologue)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print("PROLOGUE SAMPLE:")
    for line in lines[:10]:
        print(" ", line[:120])
