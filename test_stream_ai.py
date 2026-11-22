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
    "concurrency": 12
}

EPUB_PATH = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert.epub"
WORK_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
CACHE_FILE = r"D:\JV\novel yoga\breeder_mage_cache.json"

SYSTEM_PROMPT = """Kamu adalah penerjemah profesional untuk web novel fantasi dewasa (Lewd Fantasy / HaremLit / Monster Girl).
Tugasmu adalah menerjemahkan naskah bahasa Inggris ke bahasa Indonesia dengan standar tinggi: mengalir, natural, luwes, dan seru.

ATURAN WAJIB & MUTLAK:
1. GAYA BAHASA:
   - NO SENSOR & TO-THE-POINT.
   - Jangan berbelit-belit atau memakai kalimat muter-muter.
   - Monolog batin Derek Shaw santai, to-the-point, sedikit sarkastik/humoris, dan luwes.
   - Adegan lewd / ecchi / seksual diterjemahkan secara vulgar natural, frontal, to-the-point tanpa sensor munafik dan tanpa eufemisme berlebihan.

2. BANNED KATA KAKU / SEREMPET KBBI JADUL:
   - DILARANG KERAS menggunakan kata: mencicit, menukas, menimpali, bergumam, tersenyum simpul, meracau, tatkala, mendengus, tersipu malu, menyeringai masam, berujar.
   - Gunakan padanan santai/modern: bisik, seru, sahut, goda, gerutu, senyum tipis, pas/saat, desah, dengus kesal, dsb.

3. FORMAT DIALOG HARUS BERNAMA LENGKAP:
   - Setiap baris percakapan/dialog HARUS ditulis dengan format: Nama Karakter: "..."
   - Karakter utama:
     * Derek Shaw: "..." (Tokoh utama / MC)
     * Ry'lah: "..." (Gadis goblin bermata merah, galak, tomboi, bicaranya patah-patah/broken English lucu)
     * Ischi: "..." (Gadis goblin bermata ungu, anggun, pintar)
     * Kel: "..." (Gadis goblin bermata kuning, ceria, nakal)
     * Celeen: "..." (Putri / Prajurit Elf blonde)
     * Alistair Shaw: "..." (Sepupu licik)
     * Jeff Shaw: "..." (Sepupu preman bodoh)
   - Jika narasi di teks asli menyebutkan siapa yang berbicara, jadikan dialog tersebut berlabel nama. Jika ada narasi pengiring sebelum atau sesudah dialog, pisahkan narasi dan dialog dengan rapi.

4. HANYA KELUARKAN TEKS TERJEMAHAN TANPA PEMBUKA/PENUTUP/CATATAN PENERJEMAH.
"""

def call_ai(prompt, retries=5):
    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
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
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw_resp = resp.read().decode("utf-8")
                
                # Check if streaming response format
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

def test_single():
    sample = """Chapter One

Picking the lock on the humongous wooden door that led down into the basement of my family’s old farmhouse was relatively easy. It only took me about ten minutes to do it.

“Shit,” I muttered under my breath.

“Shaw … ” the beautiful goblin girl with the purple eyes breathed my name. “Are you … Derek Shaw?”

“I am,” I nodded.

“We have been waiting for you for so long,” the goblin girl with the yellow eyes spoke.

“Why you keep us waiting so long time?” the one with the gleaming red eyes asked me point-blank.

“Costumes?” I laughed out loud. “Who put you up to this?”

The red-eyed goblin girl narrowed her eyes. “Is no joke, Derek Shaw. Honest as fuck. We come for Breeder Craft. We come to mate.”"""

    prompt = f"Terjemahkan naskah novel berikut sesuai instruksi:\n\n{sample}"
    res = call_ai(prompt)
    print("Test result:\n", res)

if __name__ == "__main__":
    test_single()
