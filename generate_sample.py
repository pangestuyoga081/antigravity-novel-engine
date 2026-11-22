import asyncio
import os
import re
import subprocess
import edge_tts

# Konfigurasi Karakter & Voice Profile
# Ardi: Suara Pria. Kita modulasi pitch & rate agar Artyom (muda/waspada) dan Pyotr (veteran/berat) terdengar berbeda!
# Gadis: Suara Narator wanita / pembawa cerita yang tenang dan jelas.

VOICE_CONFIG = {
    "NARRATOR": {
        "voice": "id-ID-GadisNeural",
        "rate": "+0%",
        "pitch": "-2Hz"
    },
    "Artyom": {
        "voice": "id-ID-ArdiNeural",
        "rate": "+5%",
        "pitch": "+3Hz"   # Suara pemuda 20 tahun, agak tinggi/waspada
    },
    "Pyotr": {
        "voice": "id-ID-ArdiNeural",
        "rate": "-3%",
        "pitch": "-8Hz"   # Suara pria veteran, berat dan tegas
    },
    "Andrey": {
        "voice": "id-ID-ArdiNeural",
        "rate": "+2%",
        "pitch": "-2Hz"
    },
    "Patroli": {
        "voice": "id-ID-ArdiNeural",
        "rate": "+4%",
        "pitch": "+0Hz"
    }
}

SAMPLE_LINES = [
    ("NARRATOR", "METRO 2033. Bab 1. Ujung Dunia."),
    ("Pyotr", "Siapa di sana? Artyom, coba lu cek!"),
    ("NARRATOR", "Artyom bangkit malas-malasan dari dekat api unggun. Dia memindahkan senapan mesinnya dari punggung ke dada, lalu melangkah ke arah kegelapan. Dia berdiri tepat di batas cahaya, mengokang senjatanya sekeras dan seancam mungkin, lalu membentak kasar:"),
    ("Artyom", "Berhenti! Sebut sandi!"),
    ("NARRATOR", "Dari kegelapan yang tadinya terdengar suara gesekan aneh dan bisikan samar, sekarang terdengar langkah kaki cepat yang buru-buru menjauh. Sesuatu lari ke kedalaman terowongan, ketakutan gara-gara suara bentakan Artyom dan kokangan senjatanya. Artyom buru-buru balik ke dekat api dan melapor ke Pyotr Andreevich:"),
    ("Artyom", "Nggak ada yang maju. Nggak ada jawaban juga, langsung ngibrit."),
    ("Pyotr", "Tolol lu! Kan udah dibilang berkali-kali. Kalo nggak nyaut, langsung tembak! Lu kira siapa yang barusan lewat? Bisa aja the Dark Ones makin deket!"),
    ("Artyom", "Bukan... kayaknya bukan manusia. Suaranya aneh banget. Langkah kakinya juga bukan langkah orang. Lu pikir gue nggak tahu suara langkah kaki manusia kayak gimana?"),
    ("Pyotr", "Halah, lu kebanyakan mikir, Artyom! Lu punya perintah, jalanin aja, nggak usah sotoy. Gimana kalo itu tadi mata-mata? Sekarang mereka tahu personel kita cuma dikit di sini. Bisa aja mereka langsung habisi kita sekarang cuma buat senang-senang!")
]

async def generate_segment(text, role, output_file):
    cfg = VOICE_CONFIG.get(role, VOICE_CONFIG["NARRATOR"])
    communicate = edge_tts.Communicate(
        text=text,
        voice=cfg["voice"],
        rate=cfg["rate"],
        pitch=cfg["pitch"]
    )
    await communicate.save(output_file)

async def main():
    temp_dir = os.path.join("E:\\novel yoga", "temp_sample_audio")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_list = []
    print("Mulai generate dialog per karakter...")
    for idx, (role, text) in enumerate(SAMPLE_LINES):
        seg_file = os.path.join(temp_dir, f"seg_{idx:03d}_{role}.mp3")
        print(f"[{idx+1}/{len(SAMPLE_LINES)}] ({role}) -> {text[:40]}...")
        await generate_segment(text, role, seg_file)
        file_list.append(seg_file)
    
    # Buat file concat list untuk ffmpeg
    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for fpath in file_list:
            escaped_path = fpath.replace("\\", "/")
            f.write(f"file '{escaped_path}'\n")
            
    final_output = os.path.join("E:\\novel yoga", "Metro_2033_Sample_Bab1.mp3")
    print("\nMenggabungkan audio dengan ffmpeg...")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        final_output
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"\nSukses! File sampel audio tersimpan di: {final_output}")

if __name__ == "__main__":
    asyncio.run(main())
