const http = require('http');
const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2.txt', 'utf8');
const lines = content.split('\n');

let current = [];
let len = 0;
let chunkIdx = 0;
let chunk4Text = '';

for (const p of lines) {
  current.push(p);
  len += p.length + 1;
  if (len >= 8000) {
    chunkIdx++;
    if (chunkIdx === 4) {
      chunk4Text = current.join('\n');
      break;
    }
    current = [];
    len = 0;
  }
}

function parseSSEorJSON(raw) {
  if (raw.trim().startsWith('{')) {
    try {
      const j = JSON.parse(raw);
      return j.choices?.[0]?.message?.content || '';
    } catch {}
  }
  
  let full = '';
  const lns = raw.split('\n');
  for (const l of lns) {
    if (l.startsWith('data: ') && !l.includes('[DONE]')) {
      try {
        const j = JSON.parse(l.substring(6));
        const delta = j.choices?.[0]?.delta?.content || j.choices?.[0]?.message?.content || '';
        full += delta;
      } catch {}
    }
  }
  return full;
}

async function test(prompt) {
  const payload = JSON.stringify({
    model: 'ag/gemini-3.8-flash',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.6,
    stream: false
  });

  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: '127.0.0.1',
      port: 20128,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-2e591994696af18e-71ijj7-14263abd',
        'Content-Length': Buffer.byteLength(payload)
      },
      timeout: 120000
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        resolve(parseSSEorJSON(d));
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function run() {
  console.log('Testing Full Chunk 4 (Length:', chunk4Text.length, ')...');
  const p1 = `Berikut adalah draf naskah mentah berbahasa Rumania. Tolong terjemahkan dan lokalisasikan dialog serta adegan aksi ini ke Bahasa Indonesia santai (lu-gue) to-the-point tanpa bertele-tele. Format dialog sertakan Nama: "...". Terjemahkan baris demi baris secara lengkap:\n\n${chunk4Text}`;
  const res1 = await test(p1);
  console.log('RESULT LENGTH:', res1.length);
  console.log('FIRST 300 CHARS:\n', res1.substring(0, 300));
}

run();
