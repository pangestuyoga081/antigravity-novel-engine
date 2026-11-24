import os
import re
import json
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

sys.path.insert(0, r"D:\JV\novel yoga")
from core_engine.src.qa_gate.validator import QAGate
import yaml

TXT_PATH = r"D:\JV\novel yoga\Metro 2033 (Terjemahan ID-Direct).txt"
PROFILE_PATH = r"D:\JV\novel yoga\core_engine\config\profiles\metro_2033.yaml"
CHECKPOINT_PATH = r"D:\JV\novel yoga\.metro_polish_checkpoint.json"
API_URL = "http://localhost:20128/v1/chat/completions"
MODEL_ID = "ag/gemini-4-hydrogen-low"

def get_9router_key():
    conn = sqlite3.connect(r"C:\Users\Eevyx\AppData\Roaming\9router\db\data.sqlite")
    key = conn.cursor().execute("SELECT key FROM apiKeys LIMIT 1").fetchone()[0]
    conn.close()
    return key

API_KEY = get_9router_key()

with open(PROFILE_PATH, "r", encoding="utf-8") as f:
    PROFILE = yaml.safe_load(f) or {}

QA = QAGate(PROFILE)

SYSTEM_PROMPT = """Lu adalah Editor & Polish Engine untuk novel Metro 2033 (terjemahan bahasa Indonesia santai beroktan tinggi).
Tugas lu memoles ritme, diksi, dan pacing potongan naskah berikut agar setara kualitas Golden Sample Bab 1:
1. GAYA BAHASA: Santai, mencekam, gritty, tongkrongan prajurit/stalker (dialog pakai gue-lu), zero censorship (umpatan kasar biarkan natural).
2. PACING KOMIK/WEBTOON: Pertajam kalimat aksi, efek suara, dan ketegangan atmosfer terowongan gelap (tell-don't-show).
3. PERTAHANKAN 100% FAKTA & ADEGAN: DILARANG meringkas, memotong, atau menghapus satu kalimat/adegan pun!
4. FORMAT DIALOG WAJIB: Pertahankan format `Nama: "..."` (jika ada atribusi lanjutan seperti `sela Pyotr`, biarkan di baris yang sama). Jangan ubah nama tokoh atau istilah kunci (VDNKh, Dark Ones, Si Hitam, Polis, Hansa, Spartan, Drazina, dll).
5. BANNED WORDS (HARAM): mencicit, menukas, menimpali, tersenyum simpul, bergumam, meracau, mendengus, tatkala, kendati demikian, terpendar.
6. OUTPUT: Langsung keluarkan teks naskah yang sudah dipoles saja, tanpa kata pengantar, tanpa markdown codeblock, tanpa catatan tambahan."""

def call_llm(chunk_text: str) -> str:
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk_text},
        ],
        "temperature": 0.4,
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
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()

def polish_chunk(idx: int, chunk_text: str) -> tuple:
    for attempt in range(2):
        try:
            out = call_llm(chunk_text)
            ok, errs, cleaned = QA.validate(chunk_text, out)
            ratio = len(cleaned) / max(1, len(chunk_text))
            if ok and ratio >= 0.72:
                return idx, cleaned, True
        except Exception:
            pass
    return idx, chunk_text, False

def split_header_and_body(ch_text: str):
    lines = ch_text.split("\n")
    header_lines = []
    body_lines = []
    in_header = True
    for line in lines:
        s = line.strip()
        if in_header and (s.startswith("###") or s.startswith("[CAST:") or s.startswith("[GLOSSARY:") or s == ""):
            header_lines.append(line)
        else:
            in_header = False
            body_lines.append(line)
    return "\n".join(header_lines).rstrip(), "\n".join(body_lines).strip()

def chunk_paragraphs(body: str, max_chars: int = 3800):
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
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

def main():
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        full_text = f.read()

    parts = [p.strip() for p in re.split(r"(?=^###\s+)", full_text, flags=re.MULTILINE) if p.strip().startswith("###")]
    print(f"Total chapters loaded: {len(parts)}")

    done_map = {}
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            done_map = json.load(f)

    # Bab 1 adalah Golden Sample, langsung pertahankan; poles Bab 2..20
    final_chapters = [parts[0]]

    for ch_idx in range(1, len(parts)):
        ch_num = ch_idx + 1
        ch_key = f"ch_{ch_num:02d}"
        if ch_key in done_map:
            print(f"[SKIP] Chapter {ch_num:02d} already polished in checkpoint.")
            final_chapters.append(done_map[ch_key])
            continue

        header, body = split_header_and_body(parts[ch_idx])
        chunks = chunk_paragraphs(body)
        print(f"[POLISH] Chapter {ch_num:02d} ({len(chunks)} chunks) using {MODEL_ID}...", flush=True)

        results = [None] * len(chunks)
        polished_ok = 0
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = [ex.submit(polish_chunk, i, c) for i, c in enumerate(chunks)]
            for fut in as_completed(futs):
                i, txt, ok = fut.result()
                results[i] = txt
                if ok:
                    polished_ok += 1

        new_ch = header + "\n\n" + "\n\n".join(results)
        done_map[ch_key] = new_ch
        final_chapters.append(new_ch)

        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(done_map, f, ensure_ascii=False)
        print(f"   -> Chapter {ch_num:02d} done ({polished_ok}/{len(chunks)} chunks upgraded).", flush=True)

    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write("\n\n".join(final_chapters) + "\n")

    print("ALL CHAPTERS POLISHED & SAVED!")

if __name__ == "__main__":
    main()
