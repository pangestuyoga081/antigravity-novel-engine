import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';

const CONFIG = {
  proxyUrl: 'http://127.0.0.1:20128/v1/chat/completions',
  model: 'ag/gemini-3.8-flash',
  apiKey: 'sk-2e591994696af18e-71ijj7-14263abd',
  maxChunkChars: 6500,
  baseDir: 'D:/JV/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1'
};

const cacheDir = path.join(CONFIG.baseDir, '.Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1_chunks_cache');
const rawNovelPath = path.join(CONFIG.baseDir, 'Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1.txt');
const finalOutPath = path.join(CONFIG.baseDir, 'Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1 (Terjemahan ID-Direct).txt');

interface Chapter {
  id: string;
  title: string;
  text: string;
}

function cleanWatermarks(text: string): string {
  return text
    .replace(/PDF\s+KONOSUBA\s+Vol(?:\w+)?\s*\d*/gi, '')
    .replace(/Konosuba\s+[–-]\s+Volume\s*\d+(?:\.\d+)?/gi, '')
    .replace(/https?:\/\/[^\s]+/gi, '')
    .replace(/Ruidrive\.com/gi, '')
    .replace(/\n\s*\n\s*\n/g, '\n\n')
    .trim();
}

function splitParagraphSafe(text: string, maxChars: number): string[] {
  const paragraphs = text.split('\n');
  const chunks: string[] = [];
  let current: string[] = [];
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

function parseSSEorJSON(raw: string): string {
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
      if (j.choices?.[0]?.message?.content) {
        full = j.choices[0].message.content;
      }
    } catch {}
  }

  return full.trim();
}

function isRefusal(text: string): boolean {
  if (!text || text.trim().length === 0) return true;
  return /tidak dapat (memberikan|menerjemahkan|menulis|menuliskan|menyajikan|menghasilkan|membuat)|novel berhak cipta|karya berhak cipta|batasan hak cipta|kebijakan hak cipta|hak cipta melarang|rangkuman umum|garis besar adegan|ringkasan garis besar|gambaran besar dari|penulisan ulang adegan/i.test(text);
}

async function callSingleLLM(text: string): Promise<string> {
  const parsedUrl = new URL(CONFIG.proxyUrl);
  const prompt = `Sunting dan terjemahkan naskah adegan fiksi fantasi komedi berikut ke dalam Bahasa Indonesia santai (lu-gue/kamu-aku sesuai relasi), ekspresif, kocak, to-the-point ala manga/light novel populer, dengan format dialog konsisten Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & to-the-point). Pangkas deskripsi mikro fisiologis yang bertele-tele.
- Nol Metafora & Anti-Puitis. Hindari kalimat lebay/filosofis.
- Format dialog konsisten Nama: "...".
- TULISKAN SELURUH PERCAKAPAN DAN KEJADIAN SECARA LENGKAP TANPA MERANGKUM ATAU MEMOTONG SEDIKIT PUN.

Naskah:
${text}`;

  const payload = JSON.stringify({
    model: CONFIG.model,
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7
  });

  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 80,
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'Content-Length': Buffer.byteLength(payload)
      },
      timeout: 120000
    }, (res) => {
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

function extractTxtChapters(txtPath: string): Chapter[] {
  const content = fs.readFileSync(txtPath, 'utf-8');
  const lines = content.split('\n');
  const chapters: Chapter[] = [];
  let curVol = 'VOLUME 01';
  let curChap: Chapter | null = null;
  let curLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const l = rawLine.trim();

    const vm = l.match(/^KONO SUBARASHII SEKAI NI SHUKUFUKU WO! - (VOLUME\s+[0-9]+(?:\.[0-9]+)?)/i);
    if (vm) {
      if (curChap && curLines.length > 50) {
        curChap.text = cleanWatermarks(curLines.join('\n').trim());
        if (curChap.text.length > 400) chapters.push(curChap);
      }
      curVol = vm[1].toUpperCase();
      curChap = null;
      curLines = [];
      continue;
    }

    if (l.startsWith('#') || /^(List\s+Chapter|Index|Attention|Warning!)/i.test(l)) continue;
    if (/^\d+$/.test(l) && l.length < 5) continue;

    const isChap = /^(PROLOG(?:UE)?|EPILOG(?:UE)?|CHAPTER\s+[0-9]+|INTERLUDE|SHORT\s+STORY|EXTRA)/i.test(l);
    if (isChap) {
      const nextLines = lines.slice(i + 1, i + 8).map(x => x.trim()).filter(Boolean);
      const isReal = nextLines.some(x => /^(Bagian\s+[0-9]+|['\"“]|-)/i.test(x) || x.length > 30);
      if (isReal) {
        if (curChap && curLines.length > 50) {
          curChap.text = cleanWatermarks(curLines.join('\n').trim());
          if (curChap.text.length > 400) chapters.push(curChap);
        }
        const chNum = String(chapters.length + 1).padStart(3, '0');
        curChap = {
          id: `${curVol.toLowerCase().replace(/[\s.]+/g, '_')}_ch${chNum}`,
          title: `${curVol} - ${l}`,
          text: ''
        };
        curLines = [];
        continue;
      }
    }

    curLines.push(rawLine);
  }

  if (curChap && curLines.length > 50) {
    curChap.text = cleanWatermarks(curLines.join('\n').trim());
    if (curChap.text.length > 400) chapters.push(curChap);
  }

  return chapters;
}

async function fixCh052Chunk8() {
  console.log('Membaca chapters...');
  const chapters = extractTxtChapters(rawNovelPath);
  const ch052 = chapters.find(c => c.id.includes('ch052'))!;
  console.log('Chapter:', ch052.id, ch052.title);

  const chunks = splitParagraphSafe(ch052.text, CONFIG.maxChunkChars);
  const rawChunk8 = chunks[7];
  console.log('Chunk 8 len:', rawChunk8.length);

  // Divide into 4 smaller sub-parts ~1600 chars each to guarantee zero failure
  const lines = rawChunk8.split('\n');
  const numParts = 4;
  const partSize = Math.ceil(lines.length / numParts);
  const parts: string[] = [];
  for (let i = 0; i < numParts; i++) {
    const s = lines.slice(i * partSize, (i + 1) * partSize).join('\n').trim();
    if (s) parts.push(s);
  }

  const translatedParts: string[] = [];
  for (let i = 0; i < parts.length; i++) {
    console.log(`Translating part ${i + 1}/${parts.length} (${parts[i].length} chars)...`);
    let translated = '';
    for (let att = 1; att <= 4; att++) {
      try {
        const res = await callSingleLLM(parts[i]);
        if (!isRefusal(res) && res.length > 50) {
          translated = res;
          break;
        }
        console.warn(`   Att ${att} refused or short (${res.length} chars). Retrying...`);
      } catch (err: any) {
        console.warn(`   Att ${att} error: ${err.message}`);
      }
      await new Promise(r => setTimeout(r, 2000));
    }
    if (!translated) throw new Error(`Failed on part ${i + 1}`);
    translatedParts.push(translated);
    console.log(`   Part ${i + 1} done (${translated.length} chars)`);
  }

  const fullClean = translatedParts.join('\n\n');
  const cacheFile = path.join(cacheDir, ch052.id, 'chunk_008.txt');
  fs.writeFileSync(cacheFile, fullClean, 'utf8');
  console.log('Chunk 8 saved to cache at:', cacheFile);

  // Re-build final file
  console.log('Re-building final file...');
  const fullOutputLines: string[] = [
    '================================================================',
    'KONO SUBARASHII SEKAI NI SHUKUFUKU WO! - VOLUME 01-17 + BAKUEN 17.1',
    'Terjemahan Bahasa Indonesia (Direct, Tell-Don\'t-Show, Gaul & Lugas)',
    '================================================================\n\n'
  ];

  for (let i = 0; i < chapters.length; i++) {
    const ch = chapters[i];
    const chFolder = path.join(cacheDir, ch.id);
    fullOutputLines.push(`\n\n### ${ch.title}\n\n`);

    if (fs.existsSync(chFolder)) {
      const cFiles = fs.readdirSync(chFolder)
        .filter(f => f.endsWith('.txt'))
        .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

      for (const f of cFiles) {
        const text = fs.readFileSync(path.join(chFolder, f), 'utf8');
        fullOutputLines.push(text.trim());
        fullOutputLines.push('\n\n');
      }
    }
  }

  fs.writeFileSync(finalOutPath, fullOutputLines.join(''), 'utf8');
  console.log('FINAL FILE REBUILT SUCCESSFULLY!');
  console.log('Size:', (fs.statSync(finalOutPath).size / (1024 * 1024)).toFixed(2), 'MB');
}

fixCh052Chunk8().catch(console.error);
