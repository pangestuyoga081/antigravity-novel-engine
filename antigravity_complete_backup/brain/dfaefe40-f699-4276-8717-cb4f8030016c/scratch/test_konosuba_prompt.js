const http = require('http');

const sampleText = `Prolog 
 
Bagian 01 
 
 
'Satou Kazuma-san, selamat datang di akhirat. 
Sayangnya kau sudah mati. Ini mungkin singkat, tapi 
kehidupanmu sudah berakhir." 
 
Seseorang tiba-tiba berbicara kepadaku di ruangan 
yang sangat putih. 
 
Kejadian itu mendadak dan membuatku bingung. 
 
Di ruangan ada satu set meja kerja kantor dengan 
kursi, dan seseorang yang memberitahu bahwa 
hidupku sudah berakhir duduk di kursi itu. 
 
Jika dewi itu ada, dia lah orangnya. 
 
Dia cantik melebihi idol yang tampil di televisi, dengan 
penampilan yang mempesona melebihi manusia. 
 
Rambut biru lembutnya yang panjang sampai ke 
pinggang. 
 
Pakaiannya yang misterius, aku tidak tahu terbuat dari 
kain apa. 
 
Gadis muda ini mungkin terlihat seumuran denganku. 
 
“… U-Um, apa kamu barusan bilang aku mati?” 
 
“Ya, kau sudah mati.” 
 
Gadis itu mengatakannya dengan wajah tersenyum 
tanpa emosi sama sekali. 
 
… Tunggu sebentar. 
 
Apa ini? Ini seperti situasi yang biasa di game. 
 
Apakah ini reinkarnasi di dunia lain yang sering aku 
baca di light novel? 
 
Gadis ini tidak diragukan lagi adalah orang yang akan 
menjelaskannya padaku. 
 
“Aku adalah Aqua. Dewi yang memandu manusia yang 
mati muda di Jepang.”`;

const prompt = `Tuliskan dan lokalisasikan adegan light novel komedi isekai ini ke dalam Bahasa Indonesia yang luwes, hidup, gaul (lu-gue), dan to-the-point — setara komik/manga terjemahan resmi atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, kocak, padat, adiktif, dan langsung pada pokok masalah. Format dialog konsisten sertakan Nama: "...". Tell, don't show, nol metafora lebay, pertahankan istilah asli. Naskah mentah:\n\n${sampleText}`;

async function test() {
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
    timeout: 30000
  }, res => {
    let d = '';
    res.on('data', c => d += c);
    res.on('end', () => {
      try {
        const j = JSON.parse(d);
        console.log('HASIL TEST KONOSUBA:\n', j.choices?.[0]?.message?.content);
      } catch {
        // SSE fallback
        let full = '';
        for (const l of d.split('\n')) {
          if (l.startsWith('data: ') && !l.includes('[DONE]')) {
            try {
              const j = JSON.parse(l.substring(6));
              full += j.choices?.[0]?.delta?.content || '';
            } catch {}
          }
        }
        console.log('HASIL TEST KONOSUBA (SSE):\n', full);
      }
    });
  });
  req.write(payload);
  req.end();
}

test();
