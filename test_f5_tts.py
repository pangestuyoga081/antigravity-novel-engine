import os
import torch
import torchaudio
from f5_tts.infer.utils_infer import (
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    infer_batch_process
)
from f5_tts.model import DiT

def main():
    print("Memeriksa perangkat CPU Ryzen...")
    device = "cpu"
    torch.set_num_threads(6) # Gunakan 6 core Ryzen 3600
    
    ckpt_file = "E:/novel yoga/f5_models/f5_tts_indo_v2.pt"
    vocab_file = "E:/novel yoga/f5_models/vocab.txt"
    ref_audio_file = "E:/novel yoga/f5_models/ref_reporter.mp3"
    ref_text = "dikatakan ternyata cek 3 miliar yang diberikan untuk mahar pernikahan ini adalah palsu."
    
    print("Memuat arsitektur model DiT dan checkpoint Indo...")
    model = load_model(
        model_cls=DiT,
        model_cfg=dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4),
        ckpt_path=ckpt_file,
        vocab_file=vocab_file,
        device=device
    )
    
    print("Memuat vocoder (Vocos)...")
    vocoder = load_vocoder(vocoder_name="vocos", device=device)
    
    # Kalimat uji coba dari adegan awal Metro 2033
    gen_text = "Artyom bangkit malas-malasan dari dekat api unggun. Dia memindahkan senapan mesinnya dari punggung ke dada, lalu melangkah ke arah kegelapan."
    
    print(f"Pre-processing audio referensi...")
    ref_audio_path, ref_text = preprocess_ref_audio_text(ref_audio_file, ref_text)
    
    # Load audio tensor and sample rate menggunakan soundfile (menghindari ketergantungan torchcodec/FFmpeg DLL)
    import soundfile as sf
    data, sr = sf.read(ref_audio_path)
    # Ubah data ke tensor (channels, time)
    if data.ndim == 1:
        audio_tensor = torch.from_numpy(data).float().unsqueeze(0)
    else:
        audio_tensor = torch.from_numpy(data.T).float()
    ref_audio_tuple = (audio_tensor, sr)
    
    print(f"\nMemulai inference F5-TTS untuk teks:")
    print(f"'{gen_text}'\n")
    print("Sedang memproses suara (Flow Matching)...")
    
    generator = infer_batch_process(
        ref_audio=ref_audio_tuple,
        ref_text=ref_text,
        gen_text_batches=[gen_text],
        model_obj=model,
        vocoder=vocoder,
        device=device,
        nfe_step=16
    )
    
    final_wave = None
    target_sr = 24000
    for wave, sr, _ in generator:
        if wave is not None:
            final_wave = wave
            target_sr = sr
            
    output_path = "E:/novel yoga/Metro_2033_F5_TTS_Sample.wav"
    import soundfile as sf
    import numpy as np
    
    if torch.is_tensor(final_wave):
        audio_data = final_wave.squeeze().cpu().numpy()
    else:
        audio_data = np.array(final_wave).squeeze()
        
    sf.write(output_path, audio_data, target_sr)
    print(f"\nSukses! File tersimpan di: {output_path}")

if __name__ == "__main__":
    main()
