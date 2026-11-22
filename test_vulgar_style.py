sample_en = """
Chapter One

Picking the lock on the humongous wooden door that led down into the basement of my family’s old farmhouse was relatively easy. It only took me about ten minutes to do it. And it only took that long because I needed to re-watch one of those how-to videos that I’d found on YouTube in preparation for this little reconnaissance mission.

“Shit,” I muttered under my breath when the flashlight flickered.

“Show yourself,” I called out into the dark.

“Shaw … ” the beautiful goblin girl with the purple eyes breathed my name. “Are you … Derek Shaw?” she asked, pointing a small trembling finger at me.

“I am,” I nodded, my mind still reeling from what I was actually seeing here. Actual goblins, like … in real life. Here on Earth. And in my house.

“We have been waiting for you for so long,” the goblin girl with the yellow eyes spoke, “so sooo long.”

“Why you keep us waiting so long time?” the one with the gleaming red eyes asked me point-blank then. She was definitely the fierce one.

“Costumes?” I laughed out loud. “All right, time to fess up. Your costumes really do look great, totally convincing. And your make-up too. Who put you up to this?”

The red-eyed goblin girl narrowed her eyes seductively. “Is no joke, Derek Shaw. Honest as fuck. We come for Breeder Craft. We come to mate.”
"""

import urllib.request, json

SYSTEM_PROMPT = """Kamu adalah penerjemah novel dewasa (Lewd Fantasy / HaremLit).
Naskah harus diterjemahkan dengan gaya TONGKRONGAN GAUL, FRONTAL, KASAR, VULGAR, dan NO SENSOR.

ATURAN GAYA BAHASA:
1. SUDUT PANDANG & PRONOUNS:
   - Tokoh utama (Derek Shaw) menggunakan kata ganti: GUE (bukan "aku").
   - Menghadap orang lain/dialog menggunakan: LU / ELO (bukan "kamu" atau "kau").
   - BANNED TOTAL: kata "aku", "kamu", "kau", "diriku", "kepadamu". Ganti semuanya jadi gue/lu!

2. TONE & KATA KASAR / VULGAR:
   - Jangan disopankan! Gunakan bahasa kasar, frontal, vulgar, dan santai tongkrongan.
   - Kata umpatan dan seksual jangan disensor: sialan, bangsat, anjing, brengsek, toket, ngentot, kawin, puki, kontol, grepe, basah, desah liar.
   - Tanpa kalimat berbelit-belit atau muter-muter. Langsung to-the-point dan nampol.

3. DIALOG FORMAT:
   - Seluruh dialog wajib format: Nama Karakter: "..."
   - Derek Shaw: "..."
   - Ry'lah: "..."
   - Ischi: "..."
   - Kel: "..."
"""

payload = {
    "model": "ag/gemini-3.8-flash-low",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Terjemahkan dengan gaya gue-lu, kasar, vulgar, frontal tanpa sensor:\n\n{sample_en}"}
    ],
    "temperature": 0.5
}

req = urllib.request.Request(
    "http://127.0.0.1:20128/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-2e591994696af18e-71ijj7-14263abd"
    }
)

with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode("utf-8")
    content = []
    for line in raw.split("\n"):
        if line.startswith("data: ") and line != "data: [DONE]":
            chunk = json.loads(line[6:])
            d = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            content.append(d)
    print("".join(content))
