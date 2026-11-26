import os
import io
import re
import json
import time
import base64
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import pypdf
from PIL import Image

PDF_PATH = r"F:\Monster Girl Encyclopedia Vol.1 (Kenkou Cross) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
ILLUST_DIR = r"D:\JV\novel yoga\illustrations\Monster_Girl_Encyclopedia_Vol_01"
OUT_TXT = r"D:\JV\novel yoga\Monster_Girl_Encyclopedia_Vol_01 (Terjemahan ID-Direct).txt"
CHECKPOINT_PATH = r"D:\JV\novel yoga\.mge_v1_checkpoint.json"
API_URL = "http://localhost:20128/v1/chat/completions"
MODEL_ID = "ag/gemini-4-hydrogen-low"

def get_9router_key():
    conn = sqlite3.connect(r"C:\Users\Eevyx\AppData\Roaming\9router\db\data.sqlite")
    key = conn.cursor().execute("SELECT key FROM apiKeys LIMIT 1").fetchone()[0]
    conn.close()
    return key

API_KEY = get_9router_key()

VISION_PROMPT = """Lu adalah Vision OCR + Translator Engine untuk Monster Girl Encyclopedia Vol. 1.
Lihat halaman scan ini:
1. Jika halaman ini HANYA gambar ilustrasi/cover/halaman kosong tanpa teks cerita/entri yang berarti, balas PERSIS: [NO_TEXT]
2. Jika halaman ini berisi teks (entri monster, tabel stat, atau penjelasan lore):
   - Baca dan terjemahkan SELURUH teksnya secara LENGKAP ke Bahasa Indonesia gaya santai, ceplas-ceplos, dan NO SENSOR (jangan diringkas, jangan diperhalus).
   - Awali dengan baris judul singkat jika ada judul monster/bab di halaman ini, format: `## <Judul>`
   - Susun stat/info (Family, Type, Habitat, Disposition, Diet, dll.) dan paragraf deskripsi secara rapi dan mudah dibaca di HP.
   - Jangan gunakan kata baku usang (tatkala, terpendar, kendati demikian, mencicit, bergumam, mendengus)."""

def extract_all_pages():
    os.makedirs(ILLUST_DIR, exist_ok=True)
    reader = pypdf.PdfReader(PDF_PATH)
    total = len(reader.pages)
    saved = 0
    for i, page in enumerate(reader.pages):
        p_num = i + 1
        out_p = os.path.join(ILLUST_DIR, f"page_{p_num:03d}.jpg")
        if os.path.exists(out_p):
            saved += 1
            continue
        try:
            imgs = list(page.images)
            if imgs:
                with open(out_p, "wb") as f:
                    f.write(imgs[0].data)
                saved += 1
        except Exception:
            pass
    print(f"Extracted/verified {saved}/{total} page images in {ILLUST_DIR}", flush=True)
    return total

def process_page(p_num: int) -> tuple:
    img_fn = f"page_{p_num:03d}.jpg"
    img_path = os.path.join(ILLUST_DIR, img_fn)
    if not os.path.exists(img_path):
        return p_num, ""

    im = Image.open(img_path).convert("RGB")
    im.thumbnail((1300, 1300))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=82)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    models = [MODEL_ID, MODEL_ID, "ag/gemini-3.8-flash-low"]
    for attempt, m_id in enumerate(models):
        try:
            payload = {
                "model": m_id,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }],
                "temperature": 0.35,
                "stream": False,
            }
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                txt = res["choices"][0]["message"]["content"].strip()
                if txt == "[NO_TEXT]" or len(txt) < 15:
                    return p_num, f"[[ILUSTRASI:{img_fn}]]"
                # Format entry: judul (jika ada) + ilustrasi asli + teks terjemahan
                lines = txt.splitlines()
                title_line = ""
                body_start = 0
                if lines and lines[0].startswith("##"):
                    title_line = f"### {lines[0].lstrip('#').strip()} (Hal. {p_num})\n\n"
                    body_start = 1
                else:
                    title_line = f"### Halaman {p_num}\n\n"
                body = "\n".join(lines[body_start:]).strip()
                return p_num, f"{title_line}[[ILUSTRASI:{img_fn}]]\n\n{body}"
        except Exception:
            time.sleep(2 * (attempt + 1))
    return p_num, f"### Halaman {p_num}\n\n[[ILUSTRASI:{img_fn}]]"

def main():
    total = extract_all_pages()
    done_map = {}
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            done_map = json.load(f)

    todo = [p for p in range(1, total + 1) if str(p) not in done_map]
    print(f"Total pages: {total} | Already done: {len(done_map)} | Todo: {len(todo)}", flush=True)

    batch_size = 20
    for start in range(0, len(todo), batch_size):
        batch = todo[start:start + batch_size]
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [ex.submit(process_page, p) for p in batch]
            for fut in as_completed(futs):
                p_num, content = fut.result()
                done_map[str(p_num)] = content
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(done_map, f, ensure_ascii=False)
        print(f"Progress: {len(done_map)}/{total} pages processed.", flush=True)

    ordered = [done_map[str(p)] for p in range(1, total + 1) if done_map.get(str(p))]
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n\n".join(ordered) + "\n")
    print(f"ALL {total} PAGES DONE -> {OUT_TXT}", flush=True)

if __name__ == "__main__":
    main()
