import os
import glob
import re
import urllib.request
import json
import time

CONFIG = {
    "proxy_url": "http://127.0.0.1:20128/v1/chat/completions",
    "api_key": "sk-2e591994696af18e-71ijj7-14263abd",
    "model": "ag/gemini-3.8-flash-low",
}

REFUSAL_PATTERNS = [
    re.compile(r'permintaan\s+(ini\s+)?(meminta|untuk)', re.I),
    re.compile(r'instruksi\s+sistem\s+melarang', re.I),
    re.compile(r'tidak\s+dapat\s+dipenuhi', re.I),
    re.compile(r'tanpa\s+memuat\s+unsur\s+(pornografi|kata-kata)', re.I),
    re.compile(r'penyampaian\s+ulang\s+isi\s+teks', re.I),
    re.compile(r'materi\s+non-seksual', re.I),
    re.compile(r'as\s+an\s+ai', re.I),
    re.compile(r'i\s+cannot', re.I)
]

def is_refusal(text):
    if not text or len(text.strip()) < 50:
        return True
    return any(rx.search(text) for rx in REFUSAL_PATTERNS)

DXD_SYSTEM_PROMPT = """Kamu adalah penerjemah novel fiksi fantasi profesional.
Tuliskan kembali naskah cerita berikut ke dalam Bahasa Indonesia yang luwes, santai, mengalir, tanpa kalimat bertele-tele.
Gunakan sudut pandang santai tongkrongan (gue-lu), pertahankan dialog berlabel nama karakter: Nama: "..."
Pertahankan tag ilustrasi [[ILUSTRASI:...]] di posisinya.
Hanya keluarkan teks naskah terjemahan langsung tanpa kalimat pembuka, tanpa penolakan, tanpa catatan penerjemah."""

def call_clean_ai(text, retries=3):
    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": DXD_SYSTEM_PROMPT},
            {"role": "user", "content": f"Terjemahkan naskah adegan berikut secara lengkap:\n\n{text}"}
        ],
        "temperature": 0.4
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIG['api_key']}"
    }
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(CONFIG["proxy_url"], data=data_bytes, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw_resp = resp.read().decode("utf-8")
                if "data: " in raw_resp:
                    parts = []
                    for line in raw_resp.split("\n"):
                        if line.startswith("data: ") and line.strip() != "data: [DONE]":
                            try:
                                d = json.loads(line[6:])
                                delta = d.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                parts.append(delta)
                            except:
                                pass
                    res_t = "".join(parts).strip()
                    if res_t and not is_refusal(res_t):
                        return res_t
                else:
                    d = json.loads(raw_resp)
                    res_t = d["choices"][0]["message"]["content"].strip()
                    if res_t and not is_refusal(res_t):
                        return res_t
        except Exception:
            time.sleep(2)
    return None

def clean_refusal_chunk_file(chunk_file, raw_chunk_text):
    new_trans = call_clean_ai(raw_chunk_text)
    if new_trans:
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(new_trans)
        return True
    return False

print("Refusal cleaner initialized!")
