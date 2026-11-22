const fs = require('fs');
const http = require('http');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2.txt', 'utf8');
const lines = content.split('\n');

const chapLines = lines.slice(6796, 8135).filter(l => {
  const t = l.trim();
  if (/TOM\s*CLANCY|RAINBOW\s*SIX/i.test(t)) return false;
  if (/^\d+\s*e\s*TOM/i.test(t)) return false;
  if (t.length < 5 && /^[|\-=_~+`!?.a-z\s0-9]+$/i.test(t)) return false;
  return true;
});

function splitParagraphSafe(text, maxChars) {
  const paragraphs = text.split('\n');
  const chunks = [];
  let current = [];
  let len = 0;
  for (const p of paragraphs) {
    current.push(p);
    len += p.length + 1;
    if (len >= maxChars) {
      chunks.push(current.join('\n'));
      current = [];
      len = 0;
    }
  }
  if (current.length > 0) chunks.push(current.join('\n'));
  return chunks;
}

const chunks = splitParagraphSafe(chapLines.join('\n'), 8000);
let chunk2Text = chunks[1];

// Bersihkan juga jika ada teks watermark di dalam paragraf
chunk2Text = chunk2Text.replace(/\d+\s*e\s*TOM\s*CLANCY/gi, '');
chunk2Text = chunk2Text.replace(/TOM\s*CLANCY/gi, '');
chunk2Text = chunk2Text.replace(/RAINBOW\s*SIX/gi, '');

function parseSSEorJSON(raw) {
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
  if (!full && raw.trim().startsWith('{')) {
    try {
      const j = JSON.parse(raw);
      return j.choices?.[0]?.message?.content || '';
    } catch {}
  }
  return full.trim();
}

async function callAPI(prompt) {
  const payload = JSON.stringify({
    model: 'ag/gemini-3.8-flash',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.6,
    stream: false
  });

  return new Promise((resolve) => {
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
        console.log('STATUS:', res.statusCode);
        const parsed = parseSSEorJSON(d);
        console.log('PARSED LENGTH:', parsed.length);
        if (parsed.length > 0) {
          console.log('SAMPLE OUTPUT:\n', parsed.substring(0, 300));
        } else {
          console.log('RAW:\n', d.substring(0, 500));
        }
        resolve(parsed);
      });
    });
    req.on('error', e => console.error('REQ ERROR:', e));
    req.write(payload);
    req.end();
  });
}

async function main() {
  const prompt = `Berikut adalah draf adegan fiksi novel aksi laga berbahasa Rumania. Tolong terjemahkan naskah cerita fiksi ini ke Bahasa Indonesia santai (lu-gue) to-the-point tanpa bertele-tele. Format dialog sertakan Nama: "...". Terjemahkan baris demi baris secara lengkap:\n\n${chunk2Text}`;
  await callAPI(prompt);
}

main();
