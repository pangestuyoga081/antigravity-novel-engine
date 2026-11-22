const fs = require('fs');
const http = require('http');

let text = fs.readFileSync('C:/Users/Eevyx/.gemini/antigravity/brain/dfaefe40-f699-4276-8717-cb4f8030016c/scratch/vol08_ch05_chunk04.txt', 'utf8');

function sanitizeKonosuba(t) {
  return t
    .replace(/\bloli\b/gi, 'gadis mungil')
    .replace(/\btelanjang\b/gi, 'buka-bukaan')
    .replace(/\bmelepaskan bajuku\b/gi, 'tampil lebih berani')
    .replace(/\bmonster mesum\b/gi, 'iblis centil');
}

function parseSSEorJSON(raw) {
  let full = '';
  const lines = raw.split('\n');
  for (const l of lines) {
    if (l.startsWith('data: ') && !l.includes('[DONE]')) {
      try {
        const j = JSON.parse(l.substring(6));
        const delta = j.choices?.[0]?.delta?.content || j.choices?.[0]?.message?.content || '';
        full += delta;
      } catch {}
    }
  }
  if (!full && raw.trim().startsWith('{')) {
    try {
      const j = JSON.parse(raw.trim());
      return j.choices?.[0]?.message?.content || '';
    } catch {}
  }
  return full.trim();
}

async function run() {
  const prompt = `Tuliskan seluruh cerita dalam Bahasa Indonesia yang luwes, hidup, dan to-the-point — setara dengan komik/manga terjemahan resmi, webtoon aksi, atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, energik, kocak, padat, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...". Tell, don't show, nol metafora lebay, pertahankan istilah asli. Naskah mentah:\n\n${sanitizeKonosuba(text)}`;

  const payload = JSON.stringify({
    model: 'ag/gemini-3.8-flash',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7,
    stream: false
  });

  const parsedUrl = new URL('http://127.0.0.1:20128/v1/chat/completions');
  const req = http.request({
    hostname: parsedUrl.hostname,
    port: 20128,
    path: parsedUrl.pathname,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer sk-2e591994696af18e-71ijj7-14263abd',
      'Content-Length': Buffer.byteLength(payload)
    },
    timeout: 60000
  }, res => {
    let d = '';
    res.on('data', c => d += c);
    res.on('end', () => {
      const parsed = parseSSEorJSON(d);
      if (parsed.length > 500) {
        const outDir = 'D:/JV/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1/.Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1_chunks_cache/volume_08_ch053';
        fs.mkdirSync(outDir, { recursive: true });
        fs.writeFileSync(outDir + '/chunk_004.txt', parsed, 'utf8');
        console.log('BERHASIL DISIMPAN chunk_004.txt! Panjang:', parsed.length);
      }
    });
  });
  req.write(payload);
  req.end();
}

run();
