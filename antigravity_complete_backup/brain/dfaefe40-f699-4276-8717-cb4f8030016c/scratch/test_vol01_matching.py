import os, pymupdf, re

base_dir = r"D:\JV\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!\[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1"
txt_path = os.path.join(base_dir, "Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt")
pdf_01 = os.path.join(base_dir, r"Konosuba Volume 01 [Afterscarlet]\Konosuba Volume 01 [Afterscarlet].pdf")

with open(txt_path, "r", encoding="utf-8") as f:
    text = f.read()

v1_end = text.find("### VOLUME 02")
v1_text = text[:v1_end]

# Parse chapters
raw_sections = re.split(r"(?=###\s+VOLUME\s+01\b)", v1_text, flags=re.IGNORECASE)
chapters = []
for sec in raw_sections:
    sec = sec.strip()
    if not sec.startswith("###"):
        continue
    lines = sec.split("\n")
    title_line = re.sub(r"^###\s+VOLUME\s+01\s*[-:]*\s*", "", lines[0], flags=re.IGNORECASE).strip()
    body = "\n".join(lines[1:]).strip()
    if len(body) > 100:
        chapters.append({"title": title_line, "body": body})

print(f"Parsed {len(chapters)} chapters in Vol 01:")
for ch in chapters:
    print(f"  - {ch['title']} ({len(ch['body'])} chars)")

# Extract images from PDF
doc = pymupdf.open(pdf_01)
total_pages = len(doc)
xref_pages = {}
for pno in range(total_pages):
    for img in doc[pno].get_images(full=True):
        xref = img[0]
        if xref not in xref_pages:
            xref_pages[xref] = []
        xref_pages[xref].append(pno + 1)

large_images = []
for xref, pages in xref_pages.items():
    b = doc.extract_image(xref)
    w, h = b["width"], b["height"]
    size_kb = len(b["image"]) / 1024
    if w > 300 and h > 300 and size_kb > 30:
        true_page = max(pages)
        min_page = min(pages)
        is_color = (len(pages) == 1 and true_page <= 10)
        large_images.append({
            "xref": xref,
            "page": true_page,
            "is_color": is_color,
            "ext": b["ext"]
        })

print(f"\nExtracted {len(large_images)} images. Color: {sum(1 for m in large_images if m['is_color'])}, Story: {sum(1 for m in large_images if not m['is_color'])}")

# Test matching for each story image
stopwords = {"yang", "dengan", "untuk", "dalam", "tidak", "adalah", "pada", "dari", "ruidrive", "volume", "konosuba", "afterscarlet", "juga", "akan", "bisa", "mereka", "kami", "kita"}

for img in [m for m in large_images if not m["is_color"]]:
    pno = img["page"] - 1
    # Extract surrounding text from PDF
    surrounding = []
    if pno > 0:
        surrounding.extend([l.strip() for l in doc[pno-1].get_text("text").split("\n") if l.strip()])
    if pno + 1 < total_pages:
        surrounding.extend([l.strip() for l in doc[pno+1].get_text("text").split("\n") if l.strip()])
        
    context_str = " ".join(surrounding)
    words = re.findall(r"\b[A-Za-zÀ-ÿ]{4,}\b", context_str)
    keywords = [w for w in words if w.lower() not in stopwords]
    
    best_ch = None
    best_score = 0
    best_para = ""
    for ch in chapters:
        paras = ch["body"].split("\n")
        for p in paras:
            p_strip = p.strip()
            if not p_strip:
                continue
            sc = sum(1 for kw in keywords if kw.lower() in p_strip.lower())
            if sc > best_score:
                best_score = sc
                best_ch = ch["title"]
                best_para = p_strip[:80]
                
    print(f"Img p.{img['page']}: Best match in '{best_ch}' (score {best_score}): {best_para}")
