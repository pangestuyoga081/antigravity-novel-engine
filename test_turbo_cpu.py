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

def test_extreme_cpu():
    print("--- PENGUJIAN EKSTREM SPEEDUP CPU RYZEN 5 3600 ---")
    device = "cpu"
    
    # 1. Optimasi Threading & Cache Allocator
    torch.set_num_threads(12)
    os.environ["OMP_NUM_THREADS"] = "12"
    os.environ["MKL_NUM_THREADS"] = "12"
    
    ckpt_file = "E:/novel yoga/f5_models/f5_tts_indo_v2.pt"
    vocab_file = "E:/novel yoga/f5_models/vocab.txt"
    ref_audio_file = "E:/novel yoga/f5_models/ref_prabowo.mp3"
    ref_text = "Selamat pagi, salam sejahtera bagi kita sekalian."
    
    print("Memuat model DiT...")
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
    audio_tensor = torch.from_numpy(data.T if data.ndim > 1 else data).float().unsqueeze(0) if data.ndim == 1 else torch.from_numpy(data.T).float()
    ref_audio_tuple = (audio_tensor, sr)
    
    # Uji coba nfe_step=4 (Turbo Mode)
    print("\n[UJI COBA] Menjalankan nfe_step=4 (Turbo Mode)...")
    start = time.time()
    
    generator = infer_batch_process(
        ref_audio=ref_audio_tuple,
        ref_text=ref_text,
        gen_text_batches=[gen_text],
        model_obj=model,
        vocoder=vocoder,
        device=device,
        nfe_step=4 # 4 steps turbo!
    )
    
    final_wave = None
    target_sr = 24000
    for wave, sr, _ in generator:
        if wave is not None:
            final_wave = wave
            target_sr = sr
            
    dur = time.time() - start
    print(f"\n>> WAKTU TURBO RENDER (nfe_step=4): {dur:.2f} detik!")
    
    out_file = "E:/novel yoga/Metro_2033_CPU_Turbo_4steps.wav"
    audio_data = final_wave.squeeze().cpu().numpy() if torch.is_tensor(final_wave) else np.array(final_wave).squeeze()
    sf.write(out_file, audio_data, target_sr)
    print(f"File tersimpan di: {out_file}")

if __name__ == "__main__":
    test_extreme_cpu()
