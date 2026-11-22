import os
import zipfile
import re
import json
import time
import urllib.request
import concurrent.futures

CONFIG = {
    "proxy_url": "http://127.0.0.1:20128/v1/chat/completions",
    "api_key": "sk-2e591994696af18e-71ijj7-14263abd",
    "model": "ag/gemini-3.8-flash-low",
    "concurrency": 12,
    "max_chunk_chars": 3500
}

EPUB_PATH = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert.epub"
WORK_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
OEBPS_DIR = os.path.join(WORK_DIR, "OEBPS")
CACHE_FILE = r"D:\JV\novel yoga\breeder_mage_vulgar_cache.json"
OUTPUT_TXT = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert (Terjemahan ID-Direct).txt"
OUTPUT_EPUB = r"D:\JV\novel yoga\epubs\Breeder_Mage_1_-_Marc_Robert (Illustrated ID-Direct).epub"

SYSTEM_PROMPT = """Kamu adalah penerjemah novel dewasa profesional (Lewd Fantasy / HaremLit / Monster Girl).
Tugasmu adalah menerjemahkan naskah bahasa Inggris ke bahasa Indonesia dengan gaya TONGKRONGAN GAUL, FRONTAL, KASAR, VULGAR, dan NO SENSOR.

ATURAN WAJIB & MUTLAK:
1. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Tokoh utama (Derek Shaw) menggunakan kata ganti: GUE (bukan "aku").
   - Menghadap orang lain / dialog menggunakan: LU / ELO (bukan "kamu" atau "kau").
   - BANNED TOTAL: DILARANG menggunakan kata "aku", "kamu", "kau", "diriku", "kepadamu". Ganti semua jadi GUE / LU!

2. TONE & KATA KASAR / VULGAR:
   - Jangan disopankan atau diperhalus! Terjemahkan secara liar, frontal, vulgar, dan santai tongkrongan.
   - Kosakata kasar dan seksual to-the-point tanpa sensor: sialan, bangsat, anjing, brengsek, taik, toket, ngentot, kawin, kontol, memek, sange, binal, grepe, becek, desah liar, dsb.
   - BANNED KATA KAKU / KBBI JADUL: mencicit, menukas, menimpali, bergumam, tersenyum simpul, meracau, tatkala, mendengus, tersipu malu, berujar.

3. FORMAT DIALOG HARUS BERNAMA LENGKAP:
   - Seluruh baris dialog percakapan HARUS ditulis berlabel: Nama Karakter: "..."
   - Daftar karakter:
     * Derek Shaw: "..."
     * Ry'lah: "..." (Gadis goblin bermata merah, galak, tomboi binal, bicara agak patah/broken english lucu)
     * Ischi: "..." (Gadis goblin bermata ungu, anggun, cerdas)
     * Kel: "..." (Gadis goblin bermata kuning, ceria, nakal)
     * Celeen: "..." (Putri / Prajurit Elf pirang)
     * Alistair Shaw: "..." (Sepupu licik)
     * Jeff Shaw: "..." (Sepupu preman bodoh)

4. HANYA KELUARKAN TEKS TERJEMAHAN TANPA EMBEL-EMBEL/CATATAN PENERJEMAH.
"""

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def call_ai(prompt, retries=5):
    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIG['api_key']}"
    }
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(CONFIG["proxy_url"], data=data_bytes, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw_resp = resp.read().decode("utf-8")
                if "data: " in raw_resp:
                    content_parts = []
                    for line in raw_resp.split("\n"):
                        line = line.strip()
                        if line.startswith("data: ") and line != "data: [DONE]":
                            chunk_json = line[6:]
                            try:
                                cdata = json.loads(chunk_json)
                                delta = cdata.get("choices", [{}])[0].get("delta", {})
                                if "content" in delta:
                                    content_parts.append(delta["content"])
                            except:
                                pass
                    res_text = "".join(content_parts).strip()
                    if res_text:
                        return res_text
                res = json.loads(raw_resp)
                return res["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

def extract_clean_text_from_xhtml(xhtml_content):
    clean = re.sub(r'<(p|div|h[1-6]|br)[^>]*>', '\n\n', xhtml_content, flags=re.IGNORECASE)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'")
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    return '\n\n'.join(lines)

def split_into_chunks(text, max_chars=3200):
    paragraphs = text.split("\n\n")
    chunks = []
    curr = []
    curr_len = 0
    for p in paragraphs:
        if curr_len + len(p) > max_chars and curr:
            chunks.append("\n\n".join(curr))
            curr = [p]
            curr_len = len(p)
        else:
            curr.append(p)
            curr_len += len(p)
    if curr:
        chunks.append("\n\n".join(curr))
    return chunks

def run_translation():
    cache = load_cache()
    
    target_parts = ["part0005.xhtml"]
    for i in range(9, 34):
        target_parts.append(f"part{i:04d}.xhtml")
        
    all_tasks = []
    for part in target_parts:
        part_path = os.path.join(OEBPS_DIR, part)
        if not os.path.exists(part_path):
            continue
        with open(part_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()
        
        plain_text = extract_clean_text_from_xhtml(raw_html)
        chunks = split_into_chunks(plain_text, CONFIG["max_chunk_chars"])
        
        for c_idx, c_text in enumerate(chunks):
            chunk_key = f"{part}_chunk_{c_idx}"
            all_tasks.append((part, c_idx, len(chunks), chunk_key, c_text))
            
    print(f"Total chunk tasks to process: {len(all_tasks)}")
    pending = [t for t in all_tasks if t[3] not in cache]
    print(f"Pending tasks: {len(pending)} (Already cached: {len(all_tasks) - len(pending)})")
    
    if pending:
        def process_task(task):
            part, c_idx, total_c, chunk_key, c_text = task
            prompt = f"Terjemahkan naskah berikut dengan gaya gue-lu, kasar, vulgar, frontal, to-the-point tanpa sensor (Bagian {c_idx+1}/{total_c} dari {part}):\n\n{c_text}"
            res = call_ai(prompt)
            return chunk_key, res
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["concurrency"]) as executor:
            future_to_task = {executor.submit(process_task, t): t for t in pending}
            completed_count = len(all_tasks) - len(pending)
            
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                chunk_key, res = future.result()
                if res:
                    cache[chunk_key] = res
                    completed_count += 1
                    save_cache(cache)
                    print(f"[{completed_count}/{len(all_tasks)}] Sukses: {chunk_key}")
                else:
                    print(f"FAILED: {chunk_key}")
                    
    print("\nSemua chunk vulgar selesai diterjemahkan!")
    
    # Compile Full TXT
    full_text_parts = []
    for part in target_parts:
        part_path = os.path.join(OEBPS_DIR, part)
        if not os.path.exists(part_path):
            continue
        with open(part_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()
        plain_text = extract_clean_text_from_xhtml(raw_html)
        chunks = split_into_chunks(plain_text, CONFIG["max_chunk_chars"])
        
        part_translated = []
        for c_idx in range(len(chunks)):
            k = f"{part}_chunk_{c_idx}"
            part_translated.append(cache.get(k, ""))
        full_text_parts.append("\n\n".join(part_translated))
        
    full_novel_text = "\n\n" + ("="*50) + "\n\n".join(full_text_parts)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(full_novel_text)
    print(f"Full text saved to: {OUTPUT_TXT} ({len(full_novel_text)} chars)")
    
    # Recompile EPUB
    def clean_xml(text):
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace('"', "&#8220;").replace('"', "&#8221;")
        return text

    for part in target_parts:
        part_path = os.path.join(OEBPS_DIR, part)
        if not os.path.exists(part_path):
            continue
        chunks = []
        c_idx = 0
        while True:
            k = f"{part}_chunk_{c_idx}"
            if k in cache:
                chunks.append(cache[k])
                c_idx += 1
            else:
                break
        if not chunks:
            continue
        full_part_text = "\n\n".join(chunks)
        paragraphs = [p.strip() for p in full_part_text.split("\n\n") if p.strip()]
        html_paragraphs = []
        for p in paragraphs:
            if p.startswith("Bab ") or p.startswith("Chapter ") or p == "Apa Itu Other Earth?":
                html_paragraphs.append(f'<h1 class="chapter-title">{clean_xml(p)}</h1>')
            elif ":" in p and any(name in p for name in ["Derek Shaw:", "Ry'lah:", "Ischi:", "Kel:", "Celeen:", "Jeff Shaw:"]):
                html_paragraphs.append(f'<p class="dialogue"><b>{clean_xml(p)}</b></p>')
            else:
                sub_lines = [clean_xml(l) for l in p.split("\n") if l.strip()]
                html_paragraphs.append(f'<p>{"<br/>".join(sub_lines)}</p>')
                
        body_content = "\n  ".join(html_paragraphs)
        new_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="id">
<head>
  <title>Breeder Mage</title>
  <style>
    body {{ font-family: "Georgia", "Times New Roman", serif; line-height: 1.6; margin: 5%; }}
    h1.chapter-title {{ text-align: center; margin-top: 1.5em; margin-bottom: 1.5em; font-size: 1.6em; color: #8b0000; }}
    p {{ margin-bottom: 0.9em; text-indent: 1.2em; }}
    p.dialogue {{ text-indent: 0; margin-left: 0.5em; margin-bottom: 0.8em; color: #111; }}
    b {{ color: #003366; }}
  </style>
</head>
<body>
  {body_content}
</body>
</html>"""
        with open(part_path, "w", encoding="utf-8") as f:
            f.write(new_xhtml)
            
    with zipfile.ZipFile(OUTPUT_EPUB, "w", zipfile.ZIP_DEFLATED) as z_out:
        mimetype_path = os.path.join(WORK_DIR, "mimetype")
        if os.path.exists(mimetype_path):
            z_out.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(WORK_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, WORK_DIR).replace("\\", "/")
                if rel_path == "mimetype":
                    continue
                z_out.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)
    print(f"Successfully generated EPUB at: {OUTPUT_EPUB}")

if __name__ == "__main__":
    run_translation()
