import time
import os
import torch
import soundfile as sf
import numpy as np
from f5_tts.infer.utils_infer import (
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    infer_batch_process
)
from f5_tts.model import DiT

def test_cpu_optimized():
    print("--- BENCHMARK OPTIMISASI CPU RYZEN 5 3600 ---")
    device = "cpu"
    # Aktifkan 12 threads Ryzen (6 Core / 12 SMT Threads)
    torch.set_num_threads(12)
    print(f"Menggunakan {torch.get_num_threads()} thread Ryzen...")
    
    ckpt_file = "E:/novel yoga/f5_models/f5_tts_indo_v2.pt"
    vocab_file = "E:/novel yoga/f5_models/vocab.txt"
    ref_audio_file = "E:/novel yoga/f5_models/ref_prabowo.mp3"
    ref_text = "Selamat pagi, salam sejahtera bagi kita sekalian."
    
    print("Memuat model DiT ke CPU...")
    model = load_model(
        model_cls=DiT,
        model_cfg=dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4),
        ckpt_path=ckpt_file,
        vocab_file=vocab_file,
        device=device
    )
    vocoder = load_vocoder(vocoder_name="vocos", device=device)
    
    gen_text = "Siapa di sana? Artyom, coba lu cek!"
    ref_audio_path, ref_text = preprocess_ref_audio_text(ref_audio_file, ref_text)
    data, sr = sf.read(ref_audio_path)
    if data.ndim == 1:
        audio_tensor = torch.from_numpy(data).float().unsqueeze(0)
    else:
        audio_tensor = torch.from_numpy(data.T).float()
    ref_audio_tuple = (audio_tensor, sr)
    
    print("\n[UJI COBA 1] Menjalankan dengan nfe_step=8 (2x lebih cepat)...")
    start = time.time()
    
    generator = infer_batch_process(
        ref_audio=ref_audio_tuple,
        ref_text=ref_text,
        gen_text_batches=[gen_text],
        model_obj=model,
        vocoder=vocoder,
        device=device,
        nfe_step=8 # 8 step = 2x speedup
    )
    
    final_wave = None
    target_sr = 24000
    for wave, sr, _ in generator:
        if wave is not None:
            final_wave = wave
            target_sr = sr
            
    dur = time.time() - start
    print(f">> HASIL: Selesai dalam {dur:.2f} detik! (Sebelumnya: 37.00 detik)")
    
    out_file = "E:/novel yoga/Metro_2033_CPU_Optimized_8steps.wav"
    audio_data = final_wave.squeeze().cpu().numpy() if torch.is_tensor(final_wave) else np.array(final_wave).squeeze()
    sf.write(out_file, audio_data, target_sr)
    print(f"File tersimpan di: {out_file}")

if __name__ == "__main__":
    test_cpu_optimized()
