const fs = require('fs');
const http = require('http');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2.txt', 'utf8');
const lines = content.split('\n');

const chapLines = lines.slice(6796, 8135).filter(l => {
  const t = l.trim();
  if (/^(TOM CLANCY\b|RAINBOW SIX\b|\d+\s+e\s+TOM CLANCY|\bRAINBOW SIX\s+e\s+\d+)/i.test(t)) return false;
  if (t.length < 5 && /^[|\-=_~+`!?.a-z\s]+$/i.test(t)) return false;
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
const chunk2Text = chunks[1];

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
      res.on('end', () => resolve(parseSSEorJSON(d)));
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  console.log('--- Test Original Prompt ---');
  const p1 = `Berikut adalah draf naskah mentah berbahasa Rumania. Tolong terjemahkan dan lokalisasikan dialog serta adegan aksi ini ke Bahasa Indonesia santai (lu-gue) to-the-point tanpa bertele-tele. Format dialog sertakan Nama: "...". Terjemahkan baris demi baris secara lengkap:\n\n${chunk2Text}`;
  const res1 = await callAPI(p1);
  console.log('Result 1 (Length: ' + res1.length + '):', res1.substring(0, 300));
}

main();
