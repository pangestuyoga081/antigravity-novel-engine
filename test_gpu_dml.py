import time
import os
import torch
import torch_directml
import soundfile as sf
import numpy as np
from f5_tts.infer.utils_infer import (
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    infer_batch_process
)
from f5_tts.model import DiT

def test_dml():
    print("Inisialisasi DirectML untuk GPU AMD Radeon RX 6600 XT...")
    dml_device = torch_directml.device()
    print(f"Perangkat aktif: {dml_device} ({torch_directml.device_name(0)})")
    
    ckpt_file = "E:/novel yoga/f5_models/f5_tts_indo_v2.pt"
    vocab_file = "E:/novel yoga/f5_models/vocab.txt"
    ref_audio_file = "E:/novel yoga/f5_models/ref_reporter.mp3"
    ref_text = "dikatakan ternyata cek 3 miliar yang diberikan untuk mahar pernikahan ini adalah palsu."
    
    print("Memuat model DiT ke VRAM RX 6600 XT...")
    # Load model on cpu first, then move to DirectML device (agar kompatibel dengan string check di f5-tts)
    model = load_model(
        model_cls=DiT,
        model_cfg=dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4),
        ckpt_path=ckpt_file,
        vocab_file=vocab_file,
        device="cpu"
    )
    model = model.to(dml_device)
    
    print("Memuat vocoder (Vocos) ke GPU...")
    vocoder = load_vocoder(vocoder_name="vocos", device=dml_device)
    
    gen_text = "Siapa di sana? Artyom, coba lu cek!"
    ref_audio_path, ref_text = preprocess_ref_audio_text(ref_audio_file, ref_text)
    data, sr = sf.read(ref_audio_path)
    audio_tensor = torch.from_numpy(data if data.ndim > 1 else data[None, :]).float()
    ref_audio_tuple = (audio_tensor, sr)
    
    print("\nMemulai benchmark render di GPU (nfe_step=8)...")
    start = time.time()
    
    generator = infer_batch_process(
        ref_audio=ref_audio_tuple,
        ref_text=ref_text,
        gen_text_batches=[gen_text],
        model_obj=model,
        vocoder=vocoder,
        device=dml_device,
        nfe_step=8 # Optimasi nfe_step 8
    )
    
    final_wave = None
    target_sr = 24000
    for wave, sr, _ in generator:
        if wave is not None:
            final_wave = wave
            target_sr = sr
            
    dur = time.time() - start
    print(f"\nWAKTU RENDER GPU: {dur:.2f} detik!")
    
    out_file = "E:/novel yoga/Metro_2033_GPU_Test.wav"
    audio_data = final_wave.squeeze().cpu().numpy() if torch.is_tensor(final_wave) else np.array(final_wave).squeeze()
    sf.write(out_file, audio_data, target_sr)
    print(f"File tersimpan di: {out_file}")

if __name__ == "__main__":
    test_dml()
