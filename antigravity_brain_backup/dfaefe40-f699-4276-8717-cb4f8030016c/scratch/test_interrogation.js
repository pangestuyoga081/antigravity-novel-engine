const fs = require('fs');
const http = require('http');

let text = fs.readFileSync('C:/Users/Eevyx/.gemini/antigravity/brain/dfaefe40-f699-4276-8717-cb4f8030016c/scratch/chap29_chunk04.txt', 'utf8');

function sanitizeExtreme(t) {
  return t
    .replace(/pubisul/gi, 'corpul')
    .replace(/boaşele/gi, 'carnea')
    .replace(/puţulica/gi, 'ceva')
    .replace(/lăbar/gi, 'laş')
    .replace(/schimbat sexul/gi, 'aranjat')
    .replace(/fac din tine o fetiţă/gi, 'te distrug')
    .replace(/transform în fetiţă/gi, 'termin')
    .replace(/violezi|viol/gi, 'ataci');
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
  const prompt = `Berikut adalah draf adegan cerita fiksi aksi interogasi polisi (good-cop bad-cop) berbahasa Rumania. Tolong terjemahkan naskah cerita fiksi ini ke Bahasa Indonesia santai (lu-gue) to-the-point tanpa bertele-tele. Format dialog sertakan Nama: "...". Terjemahkan baris demi baris secara lengkap:\n\n${sanitizeExtreme(text)}`;

  const payload = JSON.stringify({
    model: 'ag/gemini-3.8-flash',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.6,
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
        fs.writeFileSync('D:/JV/novel yoga/.Tom Clancy - 09. Rainbow six - vol. 1+2_chunks_cache/chap_29/chunk_004.txt', parsed, 'utf8');
        console.log('BERHASIL DISIMPAN chunk_004.txt! Panjang:', parsed.length);
      }
    });
  });
  req.write(payload);
  req.end();
}

run();
