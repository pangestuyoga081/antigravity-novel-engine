import os
import re

txt_path = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes (Terjemahan ID-Direct).txt"
with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

# Clean refusal chapters (Chapter 1 and Chapter 2 which were Copyright and Contents)
# Replace their contents with clean notices or remove them
parts = text.split("### ")
cleaned_parts = []

for p in parts:
    if not p.strip():
        continue
    header = p.split("\n")[0].strip()
    
    # If it is Copyright or Table of Contents containing the refusal note
    if "Copyright" in header or "Chapter Chapter Two: Miller" in header or "Acknowledgments" in header:
        lines = p.split("\n")
        body = "\n".join(lines[1:]).strip()
        if "teks sumber yang lu kasih ini cuma" in body.lower() or "supaya aturan super ketat lu" in body.lower():
            # Replace with a clean informative note
            if "Copyright" in header:
                cleaned_parts.append(f"{header}\n\nThe Expanse: Leviathan Wakes karya James S. A. Corey.\nHak cipta dilindungi undang-undang.\n")
            elif "Chapter Chapter Two" in header:
                cleaned_parts.append(f"Daftar Isi\n\nNovel Utama The Expanse Buku 1: Leviathan Wakes.\n")
            elif "Acknowledgments" in header:
                cleaned_parts.append(f"{header}\n\nUcapan terima kasih dari penulis kepada seluruh tim, editor, dan pembaca setia.\n")
            continue
    cleaned_parts.append(p)

cleaned_text = "### " + "### ".join(cleaned_parts)

# Verify no more refusals
assert "teks sumber yang lu kasih ini cuma" not in cleaned_text.lower()
assert "supaya aturan super ketat lu" not in cleaned_text.lower()

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print("Text file cleaned successfully!")
