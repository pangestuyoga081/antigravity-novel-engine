import os
import re
import json
import time
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import yaml

sys.path.insert(0, r"D:\JV\novel yoga")
from core_engine.src.qa_gate.validator import QAGate

SRC_TXT = r"D:\JV\novel yoga\Overlord Volume 01 - The Undead King.txt"
OUT_TXT = r"D:\JV\novel yoga\Overlord Volume 01 - The Undead King (Terjemahan ID-Direct).txt"
PROFILE_PATH = r"D:\JV\novel yoga\core_engine\config\profiles\overlord.yaml"
CHECKPOINT_PATH = r"D:\JV\novel yoga\.overlord_v1_retrans_checkpoint.json"
API_URL = "http://localhost:20128/v1/chat/completions"
MODEL_ID = "ag/gemini-3.8-flash-low"

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
    (r"\bbudak korporat\b", "mantan karyawan kantoran"),
    (r"\bsalaryman\b", "pekerja kantoran"),
    (r"\bbos toxic\b", "atasan nyebelin"),
    (r"\bshift malam\b", "lembur malam"),
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

def unwrap_pdf_lines(raw_text: str) -> list:
    """Gabungkan line-wrap PDF yang patah di tengah kalimat menjadi paragraf utuh."""
    lines = raw_text.split("\n")
    paras = []
    cur = []
    for line in lines:
        s = line.strip()
        if not s:
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        if re.match(r"^\s*Overlord\s*[–—\-]\s*Volume\s*\d+\s*$", s, re.I):
            continue
        if s.startswith("[[ILUSTRASI:"):
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        cur.append(s)
        # Jika baris diakhiri tanda baca akhir kalimat atau kutip penutup, anggap selesai 1 paragraf logis
        if s.endswith((".", "!", "?", '"', "”", "»", "…", "---")):
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]

def parse_chapters():
    with open(SRC_TXT, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    chapters = []
    cur_title = None
    cur_lines = []
    header_rx = re.compile(r"^(Prolog|Chapter\s+\d+[^\n]*|Epilog|Afterword)\s*$", re.I)

    for i, line in enumerate(lines):
        s = line.strip()
        if header_rx.match(s):
            if cur_title and cur_lines:
                paras = unwrap_pdf_lines("\n".join(cur_lines))
                if paras:
                    chapters.append({"key": f"ch_{len(chapters)+1:02d}", "title": cur_title, "paragraphs": paras})
            # Cek jika judul chapter kepotong ke baris berikutnya (misal "Chapter 1 – The End And The" + "Beginning")
            full_t = s
            if i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt and len(nxt) < 30 and re.match(r"^Chapter\s+\d+", s, re.I) and not nxt.endswith("."):
                    full_t = f"{s} {nxt}"
                    cur_lines = []
                    cur_title = full_t
                    continue
            cur_title = full_t
            cur_lines = []
            continue
        if cur_title:
            # Skip duplikat lanjutan judul di baris pertama body
            if not cur_lines and cur_title.endswith(s) and len(s) < 30:
                continue
            cur_lines.append(line)

    if cur_title and cur_lines:
        paras = unwrap_pdf_lines("\n".join(cur_lines))
        if paras:
            chapters.append({"key": f"ch_{len(chapters)+1:02d}", "title": cur_title, "paragraphs": paras})

    return chapters

SCOUT_SYSTEM = """Lu adalah Scout Engine untuk novel Overlord Volume 1.
Dari cuplikan bab ini, ekstrak daftar tokoh penting dan istilah/lokasi kunci ke format tag berikut SAJA (maksimal 6 CAST dan 6 GLOSSARY, satu tag per baris):
[CAST: Nama Tokoh | faksi | Deskripsi singkat 1 kalimat tanpa spoiler bab berikutnya]
[GLOSSARY: Istilah atau Lokasi | Penjelasan singkat 1 kalimat]

Pilihan faksi valid: dragon (Momonga/Ainz), gremory (Guardian Nazarick), spartan (Kingdom/Gazef), exorcist (Theocracy/Nigun), survivor (Warga/Desa).
Langsung keluarkan baris [CAST: ...] dan [GLOSSARY: ...] tanpa kata pengantar."""

REWRITE_SYSTEM = """Lu adalah Editor & Translator Engine untuk Overlord Volume 1 (The Undead King) ke Bahasa Indonesia gaya light novel / webtoon isekai santai.
ATURAN MUTLAK:
1. GAYA BAHASA: Santai sehari-hari, kocak, luwes, tell-don't-show (narasi padat & hidup, buang kekakuan terjemahan PDF lama).
2. KONTRAS MOMONGA:
   - Batin/pikiran Momonga: santai, panik kocak, gaya gue-lu ("Anjir, gawat nih...").
   - Dialog keluar Momonga: dingin, sok cool, berwibawa mutlak layaknya penguasa undead.
3. FORMAT DIALOG WAJIB: Ubah semua dialog menjadi `NamaTokoh: "..."` (jika ada narasi lanjutan, letakkan di baris yang sama setelah kutip penutup). Lacak nama pembicara secara konsisten (Momonga, Albedo, Shalltear, Demiurge, Aura, Mare, Cocytus, Sebas, Enri, Gazef, Nigun, dll).
4. LENGKAP 100%: DILARANG KERAS meringkas, memotong, atau menghapus satu adegan/kalimat pun dari naskah sumber!
5. BANNED TOTAL (HARAM): "budak korporat", "salaryman", "bos toxic", "shift malam", "takut kena SP", "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus", "tatkala", "terpendar", "kendati demikian".
6. OUTPUT: Langsung keluarkan naskah hasil rewrite/terjemahan murni tanpa catatan kurung [Catatan: ...], tanpa kata pengantar/penutup."""

def scout_chapter(ch_title: str, paras: list) -> str:
    sample = "\n\n".join(paras[:18])[:7000]
    for _ in range(2):
        try:
            out = call_llm(SCOUT_SYSTEM, f"Judul: {ch_title}\n\n{sample}", temperature=0.2)
            lines = [l.strip() for l in out.splitlines() if l.strip().startswith(("[CAST:", "[GLOSSARY:"))]
            if lines:
                return "\n".join(lines)
        except Exception:
            time.sleep(1)
    return "[CAST: Momonga | dragon | Guild Master Ainz Ooal Gown berwujud tengkorak Overlord]"

def chunk_paragraphs(paras: list, max_chars: int = 3400):
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

def rewrite_chunk(idx: int, chunk: str, prev_tail: str) -> tuple:
    user_msg = chunk
    if prev_tail:
        user_msg = f"[KONTEKS SEBELUMNYA UNTUK PELACAKAN PEMBICARA - JANGAN DITULIS ULANG]:\n{prev_tail}\n\n[NASKAH UNTUK DI-REWRITE]:\n{chunk}"
    models = [MODEL_ID, MODEL_ID, "ag/gemini-4-hydrogen-low", "ag/gemini-4-hydrogen-low"]
    for attempt, m_id in enumerate(models):
        try:
            out = call_llm(REWRITE_SYSTEM, user_msg, temperature=0.45, model_id=m_id)
            out = clean_banned(out)
            ok, errs, cleaned = QA.validate(chunk, out)
            ratio = len(cleaned) / max(1, len(chunk))
            if ok and ratio >= 0.60:
                return idx, cleaned, True
        except Exception:
            time.sleep(3 * (attempt + 1))
    return idx, clean_banned(chunk), False

def main():
    chapters = parse_chapters()
    print(f"Parsed {len(chapters)} chapters from Overlord Vol 01:", [c['title'] for c in chapters], flush=True)

    done_map = {}
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            done_map = json.load(f)

    final_chapters = []
    for ch in chapters:
        key = ch["key"]
        if key in done_map:
            print(f"[SKIP] {ch['title']} already in checkpoint.", flush=True)
            final_chapters.append(done_map[key])
            continue

        print(f"[PASS 1 - SCOUT] {ch['title']}...", flush=True)
        tags_block = scout_chapter(ch["title"], ch["paragraphs"])

        chunks = chunk_paragraphs(ch["paragraphs"])
        print(f"[PASS 2+3 - REWRITE & QA] {ch['title']} ({len(chunks)} chunks) using {MODEL_ID}...", flush=True)

        results = [None] * len(chunks)
        ok_count = 0
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = []
            for i, c in enumerate(chunks):
                prev_tail = "\n".join(chunks[i - 1].split("\n\n")[-2:]) if i > 0 else ""
                futs.append(ex.submit(rewrite_chunk, i, c, prev_tail))
            for fut in as_completed(futs):
                i, txt, ok = fut.result()
                results[i] = txt
                if ok:
                    ok_count += 1

        full_ch = f"### {ch['title']}\n{tags_block}\n\n" + "\n\n".join(results)
        done_map[key] = full_ch
        final_chapters.append(full_ch)
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(done_map, f, ensure_ascii=False)
        print(f"   -> {ch['title']} DONE ({ok_count}/{len(chunks)} chunks QA-passed).", flush=True)

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n\n".join(final_chapters) + "\n")
    print(f"ALL {len(final_chapters)} CHAPTERS RETRANSLATED -> {OUT_TXT}", flush=True)

if __name__ == "__main__":
    main()
