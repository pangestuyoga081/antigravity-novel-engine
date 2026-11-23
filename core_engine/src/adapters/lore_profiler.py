import os
import sys
import re
import json
import urllib.request
import yaml
from typing import Dict, Any, List

ROUTER_URL = os.environ.get("LLM_PROXY_URL", "http://localhost:20128/v1/chat/completions")
MODEL_NAME = os.environ.get("LLM_MODEL", "ag/gemini-3.8-flash-low")

class NovelProfiler:
    """
    Automated pre-translation profiler.
    Analyzes sample text / prologue / dramatis personae from source novel,
    extracts all character names, titles, organizations, key terminology,
    and generates an isolated YAML profile before any translation begins.
    """

    SYSTEM_PROMPT = """Kamu adalah analis literatur dan pakar fiksi ilmiah/fantasi profesional.
Tugasmu adalah menganalisis teks sumber novel dan mengekstrak entitas penting untuk profil penerjemahan:
1. DAFTAR NAMA LENGKAP KARAKTER: Semua tokoh yang muncul beserta sebutan/panggilannya.
2. NAMA TEMPAT / PLANET / STASIUN / KERAJAAN: Entitas lokasi unik di semesta cerita.
3. ISTILAH ASLI / TEKNIS / SENJATA / SIHIR (Loanwords): Istilah unik yang harus dipertahankan aslinya beserta arti/penjelasan singkatnya dalam kurung.
4. GENRE & NADA CERITA (Tone): Apakah hard-sci-fi, space opera, dark fantasy, komedi isekai, atau supernatural romance.
5. DAFTAR KATA DILARANG (Banned Words): Kata-kata klise yang dilarang muncul (misal mencicit, menukas, budak korporat jika bukan cerita korporat).
6. FORBIDDEN UNIVERSE WORDS: Nama-nama tokoh/istilah dari semesta anime/novel lain yang HARAM bocor ke semesta novel ini!

Output WAJIB berupa format YAML yang valid dan lengkap tanpa basa-basi pembuka atau penutup markdown."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_profile(self, novel_title: str, sample_text: str, profile_id: str) -> str:
        out_yaml_path = os.path.join(self.output_dir, f"{profile_id}.yaml")
        if os.path.exists(out_yaml_path):
            print(f"⚡ Profil YAML '{profile_id}.yaml' sudah ada. Memuat profil...")
            return out_yaml_path

        print(f"🔍 Mengekstrak profil karakter & lore untuk novel '{novel_title}' (~{len(sample_text)} karakter)...")
        prompt = f"Analisis sampel naskah novel berikut dari '{novel_title}' dan buatkan spesifikasi profil YAML lengkap:\n\n{sample_text[:12000]}"

        req_data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(
                ROUTER_URL,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                yaml_content = data["choices"][0]["message"]["content"]
                
                # Strip markdown code fences if wrapped
                yaml_content = re.sub(r"^```yaml\s*", "", yaml_content, flags=re.I)
                yaml_content = re.sub(r"^```\s*", "", yaml_content)
                yaml_content = re.sub(r"\s*```$", "", yaml_content).strip()

                with open(out_yaml_path, "w", encoding="utf-8") as f:
                    f.write(yaml_content)

                print(f"✅ Profil YAML sukses diekstrak dan disimpan ke: {out_yaml_path}")
                return out_yaml_path
        except Exception as e:
            print(f"⚠️ Gagal mengekstrak profil via AI: {e}. Membuat template dasar...")
            # Fallback basic YAML
            basic_yaml = {
                "title": novel_title,
                "genre": "fantasy-sci-fi",
                "tone": "colloquial-mature",
                "pronouns": "gue-lu",
                "banned_words": ["mencicit", "menukas", "menimpali", "bergumam", "budak korporat", "salaryman"],
                "characters": [],
                "loanwords": []
            }
            with open(out_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(basic_yaml, f, allow_unicode=True)
            return out_yaml_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Penggunaan: python extractor.py <Judul_Novel> <File_Teks_Sampel> [Profile_ID]")
        sys.exit(1)
    
    title = sys.argv[1]
    sample_file = sys.argv[2]
    pid = sys.argv[3] if len(sys.argv) > 3 else re.sub(r'[^a-zA-Z0-9]+', '_', title.lower()).strip('_')
    
    with open(sample_file, "r", encoding="utf-8", errors="ignore") as fp:
        sample = fp.read()
        
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "config", "profiles")
    profiler = NovelProfiler(out_dir)
    profiler.generate_profile(title, sample, pid)
