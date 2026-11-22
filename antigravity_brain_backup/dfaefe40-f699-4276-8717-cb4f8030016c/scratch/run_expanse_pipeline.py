import os
import zipfile
import re
import json
import urllib.request
import concurrent.futures
import time

EPUB_PATH = r"D:\JV\novel yoga\The Expanse\The Expanse 1 - Leviathan Wakes.epub"
OUTPUT_DIR = r"D:\JV\novel yoga\The Expanse\raw_trans_b1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROUTER_URL = "http://localhost:20128/v1/chat/completions"
MODEL_NAME = "ag/gemini-3.8-flash-low"

SYSTEM_PROMPT = """Kamu adalah penerjemah novel fiksi ilmiah keras (hard sci-fi) profesional kelas dunia.
Tugasmu menerjemahkan bab novel "The Expanse: Leviathan Wakes" ke dalam Bahasa Indonesia dengan gaya:
1. DIALOG BERNAMA LENGKAP:
   Setiap percakapan dialog WAJIB diawali nama lengkap pembicara, contoh:
   James Holden: "..."
   Joe Miller: "..."
   Naomi Nagata: "..."
   Amos Burton: "..."
   Alex Kamal: "..."
   Julie Mao: "..."
   Ade Nygaard: "..."
   Shed Garvey: "..."
2. GAYA BAHASA GAUL REALISTIS & TONGKRONGAN LUAR ANGKASA (Gue - Lu):
   - Gunakan kata ganti lu/gue untuk percakapan akrab/informal antar kru pesawat luar angkasa.
   - Tanpa sensor untuk makian kasar dan umpatan militer (shit, fuck, damn, bastard, asshole -> anjing, bajingan, bangsat, taik, sialan).
3. BANNED TOTAL SELURUH KATA BAKU KAKU:
   Nol toleransi kata: mencicit, menukas, menimpali, bergumam, tersenyum simpul, meracau, tatkala, mendengus.
4. ISTILAH TEKNIS LUAR ANGKASA TETAP PRESISI:
   Epstein Drive, PDC fire, high-g burn, spin gravity, thrust gravity, railgun, airlock, crash couch dipertahankan dengan konteks narasi yang jelas dan natural.
5. JANGAN potong cerita, terjemahkan LENGKAP dari awal sampai akhir bagian bab ini.
6. JANGAN berikan teks basa-basi pembuka atau penutup (seperti 'Berikut terjemahannya', dll). Langsung isi cerita."""

def clean_html_to_text(html_content):
    # remove head, style, script
    text = re.sub(r'<head.*?</head>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # paragraph breaks
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    # decode basic entities
    text = text.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&').replace('&mdash;', '—').replace('&ndash;', '–')
    # collapse spaces
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in text.split('\n')]
    return '\n'.join([l for l in lines if l])

def translate_chunk(title, text_chunk):
    for attempt in range(4):
        try:
            req_data = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Bab: {title}\n\nTerjemahkan teks berikut secara lengkap sesuai seluruh instruksi:\n\n{text_chunk}"}
                ],
                "temperature": 0.3
            }
            req = urllib.request.Request(
                ROUTER_URL,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

def process_chapter(ch_num, title, filename):
    out_file = os.path.join(OUTPUT_DIR, f"{ch_num:02d}_{re.sub(r'[^a-zA-Z0-9]+', '_', title)}.txt")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 500:
        print(f"[{ch_num:02d}] SKIPPED (Already done): {title}")
        return True

    with zipfile.ZipFile(EPUB_PATH, 'r') as z:
        raw_html = z.read(filename).decode("utf-8", errors="ignore")
    
    text = clean_html_to_text(raw_html)
    if len(text.strip()) < 50:
        print(f"[{ch_num:02d}] EMPTY: {title}")
        return False

    print(f"[{ch_num:02d}] TRANSLATING ({len(text)} chars): {title}...")
    
    # chunking if needed (around 7000 chars per chunk)
    chunks = []
    if len(text) > 8000:
        paras = text.split('\n\n')
        curr = []
        curr_len = 0
        for p in paras:
            if curr_len + len(p) > 7000 and curr:
                chunks.append('\n\n'.join(curr))
                curr = [p]
                curr_len = len(p)
            else:
                curr.append(p)
                curr_len += len(p)
        if curr:
            chunks.append('\n\n'.join(curr))
    else:
        chunks = [text]

    results = []
    for i, c in enumerate(chunks):
        trans = translate_chunk(f"{title} (Part {i+1}/{len(chunks)})", c)
        if not trans:
            print(f"[{ch_num:02d}] FAILED chunk {i+1} for {title}")
            return False
        results.append(trans.strip())

    full_trans = f"# {title}\n\n" + "\n\n".join(results)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_trans)
    print(f"[{ch_num:02d}] DONE: {title} -> saved {os.path.basename(out_file)}")
    return True

if __name__ == "__main__":
    # Load TOC
    with zipfile.ZipFile(EPUB_PATH, 'r') as z:
        ncx = z.read("toc.ncx").decode("utf-8", errors="ignore")
    
    points = re.findall(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src="([^"]+)"', ncx)
    # Filter actual story chapters
    story_chapters = []
    idx = 1
    for title, src in points:
        t = title.strip()
        if any(k in t.lower() for k in ['copyright', 'contents', 'acknowledgments', 'extras', 'meet the author', 'interview', 'introducing', 'thoth station']):
            continue
        # src can have #...
        file_path = src.split('#')[0]
        story_chapters.append((idx, t, file_path))
        idx += 1

    print(f"Total story chapters to process: {len(story_chapters)}")
    
    # Parallel processing with 4 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_chapter, num, t, f): num for num, t, f in story_chapters}
        for future in concurrent.futures.as_completed(futures):
            num = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing chapter {num}: {e}")

    print("ALL DONE!")
