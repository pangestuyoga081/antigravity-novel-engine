import os
import re
import json
import html
import time
import zipfile
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import yaml

sys.path.insert(0, r"D:\JV\novel yoga")
from core_engine.src.qa_gate.validator import QAGate

EPUB_PATH = r"D:\JV\novel yoga\Metro 2035.epub"
OUT_TXT = r"D:\JV\novel yoga\Metro 2035 (Terjemahan ID-Direct).txt"
PROFILE_PATH = r"D:\JV\novel yoga\core_engine\config\profiles\metro_2035.yaml"
CHECKPOINT_PATH = r"D:\JV\novel yoga\.metro_2035_checkpoint.json"
API_URL = "http://localhost:20128/v1/chat/completions"
MODEL_ID = "ag/gemini-3.8-flash-low"

CHAPTER_TITLES_ID = {
    1: "CHAPTER 1: Moskwa di Sini",
    2: "CHAPTER 2: Metro",
    3: "CHAPTER 3: Pipa",
    4: "CHAPTER 4: Bayaran",
    5: "CHAPTER 5: Musuh",
    6: "CHAPTER 6: Delapan Meter",
    7: "CHAPTER 7: Tsvetnoi Boulevard",
    8: "CHAPTER 8: Heil",
    9: "CHAPTER 9: Teater",
    10: "CHAPTER 10: Merah",
    11: "CHAPTER 11: Puing-Puing",
    12: "CHAPTER 12: Ordo",
    13: "CHAPTER 13: Ruang Hidup",
    14: "CHAPTER 14: Orang Asing",
    15: "CHAPTER 15: Jalan Raya Para Penggemar",
    16: "CHAPTER 16: Siaran Terakhir",
    17: "CHAPTER 17: Semua Beres",
    18: "CHAPTER 18: Tugas Aktif",
    19: "CHAPTER 19: Apa yang Harus Ditulis",
    20: "CHAPTER 20: Keajaiban",
    21: "CHAPTER 21: Kamerad",
    22: "CHAPTER 22: Kebenaran",
    23: "CHAPTER 23: Orang-Orangnya Sendiri",
}

def get_9router_key():
    conn = sqlite3.connect(r"C:\Users\Eevyx\AppData\Roaming\9router\db\data.sqlite")
    key = conn.cursor().execute("SELECT key FROM apiKeys LIMIT 1").fetchone()[0]
    conn.close()
    return key

API_KEY = get_9router_key()

with open(PROFILE_PATH, "r", encoding="utf-8") as f:
    PROFILE = yaml.safe_load(f) or {}

QA = QAGate(PROFILE)

BANLIST_CLEAN = [
    (r"\bmencicit\b", "merintih lirih"),
    (r"\bmenimpali\b", "menyahut"),
    (r"\bbergumam\b", "nyeletuk"),
    (r"\bmeracau\b", "ngelantur"),
    (r"\bmendengus\b", "menghela napas panjang"),
    (r"\btersenyum simpul\b", "nyengir kecut"),
    (r"\btatkala\b", "pas"),
    (r"\bkendati demikian\b", "meski begitu"),
    (r"\bterpendar\b", "berpendar"),
    (r"\bmenukas\b", "memotong cepat"),
]

def clean_banned(text: str) -> str:
    for pat, rep in BANLIST_CLEAN:
        text = re.sub(pat, rep, text, flags=re.I)
    return text

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.45, model_id: str = MODEL_ID) -> str:
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "stream": False,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()

def html_to_paragraphs(raw_html: str):
    raw_html = re.sub(r"<style.*?</style>", "", raw_html, flags=re.S | re.I)
    raw_html = re.sub(r"<title.*?</title>", "", raw_html, flags=re.S | re.I)
    blocks = re.split(r"</p>|</div>|</h[1-6]>|<br\s*/?>", raw_html, flags=re.I)
    paras = []
    for b in blocks:
        txt = html.unescape(re.sub(r"<[^>]+>", " ", b))
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt or txt == "Metro 2035":
            continue
        paras.append(txt)
    return paras

def extract_chapters_from_epub():
    chapters = []
    with zipfile.ZipFile(EPUB_PATH, "r") as z:
        # 23 Bab: img di index_split_{2+2*i:03d}, teks di index_split_{3+2*i:03d}
        for ch_num in range(1, 24):
            img_file = f"index_split_{2 + 2*ch_num:03d}.html"
            txt_file = f"index_split_{3 + 2*ch_num:03d}.html"
            img_raw = z.read(img_file).decode("utf-8", errors="replace")
            img_m = re.search(r'src="([^"]+)"', img_raw)
            img_base = os.path.basename(img_m.group(1)) if img_m else None

            txt_raw = z.read(txt_file).decode("utf-8", errors="replace")
            paras = html_to_paragraphs(txt_raw)
            # Bersihkan baris judul bawaan di awal bab ("Metro 2035 CHAPTER X ...")
            if paras and re.match(r"^(?:Metro 2035\s*)?CHAPTER\s+\d+", paras[0], re.I):
                paras = paras[1:]
            if paras and re.match(r"^[—\-–\sA-Z0-9'’]+$", paras[0]) and len(paras[0]) < 60:
                paras = paras[1:]

            chapters.append({
                "key": f"ch_{ch_num:02d}",
                "title": CHAPTER_TITLES_ID[ch_num],
                "image": img_base,
                "paragraphs": paras,
            })

        # Epigraph + Afterword
        aft_raw = z.read("index_split_050.html").decode("utf-8", errors="replace")
        aft_paras = html_to_paragraphs(aft_raw)
        if aft_paras and "AFTERWORD" in aft_paras[0].upper():
            aft_paras = aft_paras[1:]
        chapters.append({
            "key": "ch_24_afterword",
            "title": "EPILOG / AFTERWORD: Dunia di Luar Sana",
            "image": None,
            "paragraphs": aft_paras,
        })
    return chapters

SCOUT_SYSTEM = """Lu adalah Scout Engine untuk novel Metro 2035.
Dari cuplikan bab ini, ekstrak daftar tokoh penting dan istilah/lokasi kunci ke format tag berikut SAJA (satu tag per baris, maksimal 6 CAST dan 6 GLOSSARY):
[CAST: Nama Tokoh | faksi | Deskripsi singkat 1 kalimat tanpa spoiler akhir cerita]
[GLOSSARY: Istilah atau Lokasi | Penjelasan singkat 1 kalimat]

Pilihan faksi valid: metro, spartan, redline, hanza, mutant, survivor.
Langsung keluarkan baris [CAST: ...] dan [GLOSSARY: ...] tanpa kata pengantar."""

TRANSLATE_SYSTEM = """Lu adalah Penerjemah Novel Metro 2035 (Dmitry Glukhovsky) ke Bahasa Indonesia gaya santai beroktan tinggi.
ATURAN MUTLAK:
1. GAYA BAHASA: Santai, gritty, mencekam, sinis, tongkrongan prajurit/penghuni terowongan (dialog pakai gue-lu), zero censorship (umpatan kasar biarkan apa adanya, jangan diperhalus).
2. PACING WEBTOON / KOMIK: Tell-don't-show, kalimat hidup, tajam, atmosfer pengap terowongan terasa nyata.
3. FORMAT DIALOG WAJIB: Ubah dialog menjadi format `NamaPembicara: "..."` (jika ada narasi lanjutan, letakkan di baris yang sama setelah kutip penutup). Untuk dialog cepat tanpa tag nama di teks Inggris, lacak pembicaranya dengan cermat dari konteks sebelumnya dan beri label `NamaPembicara: "..."` yang tepat!
4. LENGKAP 100%: DILARANG KERAS meringkas, men-skip adegan, atau menghilangkan paragraf. Terjemahkan semua kalimat secara utuh!
5. BANNED WORDS (HARAM): mencicit, menukas, menimpali, tersenyum simpul, bergumam, meracau, mendengus, tatkala, kendati demikian, terpendar, budak korporat, salaryman.
6. OUTPUT: Langsung keluarkan hasil terjemahan murni saja, tanpa catatan kurung [Catatan: ...], tanpa komentar pembuka/penutup."""

def scout_chapter(ch_title: str, paras: list) -> str:
    sample = "\n\n".join(paras[:18])[:7500]
    for _ in range(2):
        try:
            out = call_llm(SCOUT_SYSTEM, f"Judul: {ch_title}\n\n{sample}", temperature=0.2)
            lines = [l.strip() for l in out.splitlines() if l.strip().startswith(("[CAST:", "[GLOSSARY:"))]
            if lines:
                return "\n".join(lines)
        except Exception:
            time.sleep(1)
    return "[CAST: Artyom | metro | Mantan Ranger Ordo Spartan yang terobsesi mencari sinyal radio dunia luar]"

def chunk_paragraphs(paras: list, max_chars: int = 3200):
    chunks = []
    cur = []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) > max_chars and cur:
            chunks.append("\n\n".join(cur))
            cur = [p]
            cur_len = len(p)
        else:
            cur.append(p)
            cur_len += len(p) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks

def translate_chunk(idx: int, chunk: str, prev_tail: str) -> tuple:
    user_msg = chunk
    if prev_tail:
        user_msg = f"[KONTEKS SEBELUMNYA UNTUK PELACAKAN PEMBICARA - JANGAN DITERJEMAHKAN ULANG]:\n{prev_tail}\n\n[TEKS UNTUK DITERJEMAHKAN]:\n{chunk}"
    models_to_try = [MODEL_ID, MODEL_ID, "ag/gemini-3.8-flash-low", "ag/gemini-3.8-flash-low"]
    for attempt, m_id in enumerate(models_to_try):
        try:
            out = call_llm(TRANSLATE_SYSTEM, user_msg, temperature=0.45, model_id=m_id)
            out = clean_banned(out)
            ok, errs, cleaned = QA.validate(chunk, out)
            ratio = len(cleaned) / max(1, len(chunk))
            if ok and ratio >= 0.60:
                return idx, cleaned, True
        except Exception:
            time.sleep(3 * (attempt + 1))
    return idx, chunk, False

def main():
    chapters = extract_chapters_from_epub()
    print(f"Extracted {len(chapters)} sections from Metro 2035.epub", flush=True)

    done_map = {}
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            done_map = json.load(f)

    final_sections = []
    for ch in chapters:
        key = ch["key"]
        if key in done_map:
            print(f"[SKIP] {ch['title']} already in checkpoint.", flush=True)
            final_sections.append(done_map[key])
            continue

        print(f"[PASS 1 - SCOUT] {ch['title']}...", flush=True)
        tags_block = scout_chapter(ch["title"], ch["paragraphs"])

        chunks = chunk_paragraphs(ch["paragraphs"])
        print(f"[PASS 2+3 - TRANSLATE & QA] {ch['title']} ({len(chunks)} chunks)...", flush=True)

        # Siapkan prev_tail per chunk dari sumber Inggris agar tetap paralel 5 worker
        results = [None] * len(chunks)
        ok_count = 0
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = []
            for i, c in enumerate(chunks):
                prev_tail = "\n".join(chunks[i - 1].split("\n\n")[-2:]) if i > 0 else ""
                futs.append(ex.submit(translate_chunk, i, c, prev_tail))
            for fut in as_completed(futs):
                i, txt, ok = fut.result()
                results[i] = txt
                if ok:
                    ok_count += 1

        header = f"### {ch['title']}\n{tags_block}\n"
        if ch["image"]:
            header += f"\n[[ILUSTRASI:{ch['image']}]]\n"
        full_ch = header + "\n" + "\n\n".join(results)

        done_map[key] = full_ch
        final_sections.append(full_ch)
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(done_map, f, ensure_ascii=False)

        print(f"   -> {ch['title']} DONE ({ok_count}/{len(chunks)} chunks QA-passed).", flush=True)

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n\n".join(final_sections) + "\n")
    print(f"ALL {len(final_sections)} SECTIONS TRANSLATED -> {OUT_TXT}", flush=True)

if __name__ == "__main__":
    main()
