import os
import glob
import re
import json
import time
import urllib.request
import concurrent.futures

WORK_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
OEBPS_DIR = os.path.join(WORK_DIR, "OEBPS")
CACHE_FILE = r"D:\JV\novel yoga\breeder_mage_trans_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

SYSTEM_PROMPT = """Kamu adalah penerjemah novel profesional spesialis web novel dewasa (Lewd Fantasy / HaremLit / Monster Girl).
Tugasmu adalah menerjemahkan naskah novel bahasa Inggris ke bahasa Indonesia dengan standar kualitas TINGGI, MENGALIR, dan ENAK DIBACA.

ATURAN WAJIB & MUTLAK:
1. GAYA BAHASA:
   - NO SENSOR & TO-THE-POINT.
   - Jangan berbelit-belit atau memakai kalimat muter-muter.
   - Monolog batin Derek Shaw santai, maskulin, frontal, dan luwes.
   - Adegan lewd / ecchi / seksual diterjemahkan secara vulgar natural, frontal, to-the-point tanpa sensor munafik dan tanpa eufemisme berlebihan.

2. BANNED KATA KAKU / SEREMPET KBBI JADUL:
   - DILARANG KERAS menggunakan kata: mencicit, menukas, menimpali, bergumam, tersenyum simpul, meracau, tatkala, mendengus, tersipu malu, menyeringai masam, berujar.
   - Gunakan padanan santai/modern: bisik, seru, sahut, goda, gerutu, senyum tipis, pas/saat, desah, dengus kesal, dsb.

3. FORMAT DIALOG HARUS BERNAMA LENGKAP:
   - Seluruh baris ucapan karakter/dialog HARUS ditulis dengan format: Nama Karakter: "..."
   - Daftar karakter utama:
     * Derek Shaw: "..." (Tokoh utama / MC)
     * Ry'lah: "..." (Gadis goblin bermata merah, galak, tomboi, bicaranya patah-patah/broken English lucu)
     * Ischi: "..." (Gadis goblin bermata ungu, anggun, pintar)
     * Kel: "..." (Gadis goblin bermata kuning, ceria, nakal)
     * Celeen: "..." (Elf blonde anggun / putri elf)
     * Alistair Shaw: "..." (Sepupu licik)
     * Jeff Shaw: "..." (Sepupu bodoh / preman)
   - Jika narasi di teks asli menyebutkan siapa yang berbicara, jadikan dialog tersebut berlabel nama. Jika ada narasi pengiring sebelum atau sesudah dialog, pisahkan narasi dan dialog dengan rapi.

4. TAG HTML & FORMAT:
   - Pertahankan struktur paragraf asli. Jangan hilangkan paragraf atau memotong teks.
   - Jangan menambahkan catatan penerjemah (TL Note) atau komentar apa pun di luar naskah terjemahan.
"""

def call_ai(prompt, retries=5):
    url = "http://localhost:20128/v1/chat/completions"
    payload = {
        "model": "ag/gemini-3.8-flash-low",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    
    data_bytes = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

def split_into_chunks(text, max_chars=3500):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        p_len = len(p)
        if current_len + p_len > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = p_len
        else:
            current_chunk.append(p)
            current_len += p_len
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks

# Test translate sample
if __name__ == "__main__":
    sample_text = """Chapter One

Picking the lock on the humongous wooden door that led down into the basement of my family's old farmhouse was relatively easy. It only took me about ten minutes to do it. And it only took that long because I needed to re-watch one of those how-to videos that I'd found on YouTube in preparation for this little reconnaissance mission.

"Shit," I muttered under my breath when the flashlight flickered.

"Show yourself," I called out into the dark.

"Shaw..." the beautiful goblin girl with the purple eyes breathed my name. "Are you... Derek Shaw?" she asked, pointing a small trembling finger at me.

"I am," I nodded, my mind still reeling from what I was actually seeing here. Actual goblins, like... in real life. Here on Earth. And in my house.

"We have been waiting for you for so long," the goblin girl with the yellow eyes spoke, "so sooo long."

"Why you keep us waiting so long time?" the one with the gleaming red eyes asked me point-blank then. She was definitely the fierce one.

"Costumes?" I laughed out loud. "All right, time to fess up. Your costumes really do look great, totally convincing. And your make-up too. Who put you up to this?"

The red-eyed goblin girl narrowed her eyes seductively. "Is no joke, Derek Shaw. Honest as fuck. We come for Breeder Craft. We come to mate."
"""
    prompt = f"Terjemahkan naskah novel berikut sesuai instruksi:\n\n{sample_text}"
    print("Testing translation engine...")
    res = call_ai(prompt)
    print("\n--- HASIL TEST TERJEMAHAN ---\n")
    print(res)
