import os
import torch
import torchaudio
import soundfile as sf
import numpy as np
from f5_tts.infer.utils_infer import (
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    infer_batch_process
)
from f5_tts.model import DiT

# Definisi profil suara karakter berbasis F5-TTS
VOICE_PROFILES = {
    "NARRATOR": {
        "audio": "E:/novel yoga/f5_models/ref_reporter.mp3",
        "text": "dikatakan ternyata cek 3 miliar yang diberikan untuk mahar pernikahan ini adalah palsu."
    },
    "Pyotr": {
        "audio": "E:/novel yoga/f5_models/ref_prabowo.mp3",
        "text": "Selamat pagi, salam sejahtera bagi kita sekalian."
    },
    "Artyom": {
        "audio": "E:/novel yoga/f5_models/ref_windah.mp3",
        "text": "Eh, guys, gua udah sampai nih di hotel di hari kedua lagi ngerjain beberapa hal, lagi upload-upload video YouTube."
    }
}

# Dialog adegan pembuka Metro 2033
SCRIPT_LINES = [
    ("Pyotr", "Siapa di sana? Artyom, coba lu cek!"),
    ("NARRATOR", "Artyom melangkah ke arah kegelapan terowongan lalu membentak kasar:"),
    ("Artyom", "Berhenti! Sebut sandi!"),
    ("Pyotr", "Tolol lu! Kalo nggak nyaut, langsung tembak! Lu kira siapa yang barusan lewat?"),
    ("Artyom", "Bukan... kayaknya bukan manusia. Langkah kakinya bukan langkah orang.")
]

def load_voice_ref(audio_path, text, device="cpu"):
    ref_audio_path, ref_text = preprocess_ref_audio_text(audio_path, text)
    data, sr = sf.read(ref_audio_path)
    if data.ndim == 1:
        audio_tensor = torch.from_numpy(data).float().unsqueeze(0)
    else:
        audio_tensor = torch.from_numpy(data.T).float()
    return (audio_tensor, sr), ref_text

def main():
    device = "cpu"
    torch.set_num_threads(6)
    
    ckpt_file = "E:/novel yoga/f5_models/f5_tts_indo_v2.pt"
    vocab_file = "E:/novel yoga/f5_models/vocab.txt"
    
    print("Memuat model F5-TTS Indo & Vocoder...")
    model = load_model(
        model_cls=DiT,
        model_cfg=dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4),
        ckpt_path=ckpt_file,
        vocab_file=vocab_file,
        device=device
    )
    vocoder = load_vocoder(vocoder_name="vocos", device=device)
    
    # Preload voice profiles
    print("Pre-processing sampel suara karakter...")
    loaded_voices = {}
    for role, cfg in VOICE_PROFILES.items():
        ref_tuple, ref_t = load_voice_ref(cfg["audio"], cfg["text"], device=device)
        loaded_voices[role] = (ref_tuple, ref_t)
        
    temp_dir = "E:/novel yoga/temp_f5_multi"
    os.makedirs(temp_dir, exist_ok=True)
    
    generated_segments = []
    target_sample_rate = 24000
    
    print("\n--- Memulai Generate Dialog Multi-Karakter F5-TTS ---")
    for idx, (role, text) in enumerate(SCRIPT_LINES):
        print(f"\n[{idx+1}/{len(SCRIPT_LINES)}] Karakter: [{role}]")
        print(f"Teks: \"{text}\"")
        ref_audio_tuple, ref_text = loaded_voices.get(role, loaded_voices["NARRATOR"])
        
        generator = infer_batch_process(
            ref_audio=ref_audio_tuple,
            ref_text=ref_text,
            gen_text_batches=[text],
            model_obj=model,
            vocoder=vocoder,
            device=device,
            nfe_step=16
        )
        
        final_wave = None
        for wave, sr, _ in generator:
            if wave is not None:
                final_wave = wave
                target_sample_rate = sr
                
        if torch.is_tensor(final_wave):
            audio_data = final_wave.squeeze().cpu().numpy()
        else:
            audio_data = np.array(final_wave).squeeze()
            
        seg_file = os.path.join(temp_dir, f"seg_{idx:02d}_{role}.wav")
        sf.write(seg_file, audio_data, target_sample_rate)
        generated_segments.append(audio_data)
        
        # Tambahkan jeda hening 0.3 detik antar dialog
        silence = np.zeros(int(target_sample_rate * 0.35))
        generated_segments.append(silence)
        
    # Gabungkan semua audio dialog
    print("\nMenggabungkan seluruh dialog multi-karakter...")
    full_audio = np.concatenate(generated_segments)
    final_output = "E:/novel yoga/Metro_2033_F5_MultiCharacter.wav"
    sf.write(final_output, full_audio, target_sample_rate)
    print(f"\nSUKSES! File audiobook F5 Multi-Karakter tersimpan di: {final_output}")

if __name__ == "__main__":
    main()
