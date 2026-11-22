const fs = require('fs');
const http = require('http');

const fullText = fs.readFileSync('C:/Users/Eevyx/.gemini/antigravity/brain/dfaefe40-f699-4276-8717-cb4f8030016c/scratch/chap07_chunk03.txt', 'utf8');

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
      if (j.response?.promptFeedback?.blockReason) {
        return `[BLOCKED: ${j.response.promptFeedback.blockReasonMessage || j.response.promptFeedback.blockReason}]`;
      }
      return j.choices?.[0]?.message?.content || '';
    } catch {}
  }
  return full.trim();
}

async function test(textSlice, label) {
  const prompt = `Berikut adalah draf adegan fiksi novel aksi laga petualangan berbahasa Rumania. Tolong terjemahkan naskah cerita fiksi ini ke Bahasa Indonesia santai (lu-gue) to-the-point tanpa bertele-tele. Format dialog sertakan Nama: "...". Terjemahkan baris demi baris secara lengkap:\n\n${textSlice}`;
  
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
      timeout: 60000
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        const parsed = parseSSEorJSON(d);
        console.log(`[${label}] Status: ${res.statusCode}, Result length: ${parsed.length}, Preview: ${parsed.substring(0, 100)}`);
        resolve(parsed);
      });
    });
    req.on('error', e => resolve(e.message));
    req.write(payload);
    req.end();
  });
}

async function main() {
  const lines = fullText.split('\n');
  const half = Math.floor(lines.length / 2);
  const part1 = lines.slice(0, half).join('\n');
  const part2 = lines.slice(half).join('\n');

  console.log('Testing Part 1...');
  await test(part1, 'Part 1');

  console.log('Testing Part 2...');
  await test(part2, 'Part 2');
}

main();
