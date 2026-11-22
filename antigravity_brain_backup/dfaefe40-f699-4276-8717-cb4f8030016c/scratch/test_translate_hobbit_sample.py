import urllib.request, json

proxy_url = "http://127.0.0.1:20128/v1/chat/completions"
api_key = "sk-2e591994696af18e-71ijj7-14263abd"
model = "ag/gemini-3.8-flash"

sample_text = """In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort.
It had a perfectly round door like a porthole, painted green, with a shiny yellow brass knob in the exact middle. The door opened on to a tube-shaped hall like a tunnel: a very comfortable tunnel without smoke, with panelled walls, and floors tiled and carpeted, provided with polished chairs, and lots and lots of pegs for hats and coats—the hobbit was fond of visitors.
This hobbit was a very well-to-do hobbit, and his name was Baggins. The Bagginses had lived in the neighbourhood of The Hill for time out of mind, and people considered them very respectable, not only because most of them were rich, but also because they never had any adventures or did anything unexpected: you could tell what a Baggins would say on any question without the bother of asking him.

"Good morning!" said Bilbo, and he meant it. The sun was shining, and the grass was very green. But Gandalf looked at him from under long bushy eyebrows that stuck out further than the brim of his shady hat.
"What do you mean?" he said. "Do you wish me a good morning, or mean that it is a good morning whether I want it or not; or that you feel good this morning; or that it is a morning to be good on?"
"All of them at once," said Bilbo. "And a very fine morning for a pipe of tobacco out of doors, into the bargain. If you have a pipe about you, sit down and have a fill of mine! There's no hurry, we have all the day before us!" Then Bilbo sat down on a seat by his door, crossed his legs, and blew out a beautiful grey ring of smoke that sailed up into the air without breaking and floated away over The Hill.
"Very pretty!" said Gandalf. "But I have no time to blow smoke-rings this morning. I am looking for someone to share in an adventure that I am arranging, and it's very difficult to find anyone."
"I should think so — in these parts! We are plain quiet folk and have no use for adventures. Nasty disturbing uncomfortable things! Make you late for dinner! I can't think what anybody sees in them," said our Mr. Baggins."""

explanationRule = """- Penjelasan Istilah Asing / Teknis / Konsep Dunia Cerita:
  Setiap istilah asing, istilah teknis, atau konsep yang berpotensi tidak dipahami pembaca dalam narasi maupun dialog harus disertai penjelasan singkat dalam bahasa Indonesia dengan format konsisten: Istilah (arti atau penjelasan sederhana). Contoh: Hobbit (ras manusia kerdil bertelapak kaki tebal berbulu lebat yang anti ribet dan hobi rebahan di lubang tanah super nyaman), Porthole (jendela bundar di kabin kapal).
  Terapkan secara alami sesuai konteks cerita, tanpa merusak alur, suasana, atau dialog karakter. Jelaskan hanya istilah yang benar-benar berpotensi membingungkan, utamakan saat pertama kali muncul, dan hindari pengulangan penjelasan yang sama. Gunakan bahasa sehari-hari yang lugas, bukan penjelasan formal seperti kamus."""

prompt = f"""Tuliskan seluruh cerita dalam Bahasa Indonesia yang luwes, santai/gaul, hidup, dan to-the-point — setara dengan novel fantasi/petualangan modern terjemahan resmi, webtoon fantasi, atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, ekspresif, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & Transparan). Langsung sampaikan situasi, suasana, dan isi pikiran karakter secara tegas.
- Nol Metafora & Anti-Puitis. Dilarang keras menggunakan kalimat berbunga-bunga lebay.
- Slang & Percakapan Santai (gue/lu atau gaya bahasa percakapan sehari-hari yang luwes).
- Format dialog: Nama: "..."
- Pertahankan tag penanda seperti [[ILUSTRASI:...]] persis di posisi adegannya jika ada.
{explanationRule}

Naskah Mentah:
{sample_text}"""

payload = json.dumps({
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.7,
    "stream": False
}).encode("utf-8")

req = urllib.request.Request(
    proxy_url,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
)

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read().decode("utf-8"))
    print("OUTPUT TRANSLATION:")
    print(result["choices"][0]["message"]["content"])
