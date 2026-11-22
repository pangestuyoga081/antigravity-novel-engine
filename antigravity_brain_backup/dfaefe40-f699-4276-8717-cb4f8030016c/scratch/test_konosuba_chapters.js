const fs = require('fs');

const target = 'D:/JV/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo!/[Ruidrive] Kono Subarashii Sekai ni Bakuen wo! - Volume 17.1/Kono Subarashii Sekai ni Shukufuku wo! - Volume 01-17 + Bakuen 17.1.txt';
const content = fs.readFileSync(target, 'utf8');
const lines = content.split('\n');

const chapters = [];
let currentVol = 'Volume 01';
let curChap = null;
let curLines = [];

for (let i = 0; i < lines.length; i++) {
  const rawLine = lines[i];
  const l = rawLine.trim();

  // Deteksi Volume baru
  const vm = l.match(/^KONO SUBARASHII SEKAI NI SHUKUFUKU WO! - (VOLUME\s+[0-9]+(?:\.[0-9]+)?)/i);
  if (vm) {
    if (curChap) {
      curChap.text = curLines.join('\n').trim();
      if (curChap.text.length > 500) chapters.push(curChap);
    }
    currentVol = vm[1].toUpperCase();
    curChap = null;
    curLines = [];
    continue;
  }

  // Filter daftar isi & halaman judul
  if (l.startsWith('# List Chapter') || l.startsWith('List Chapter') || l.startsWith('List chapter') || l.startsWith('Index')) {
    continue;
  }

  // Filter watermark PDF
  if (/^(PDF\s+KONOSUBA\s+Vol|Konosuba\s+[–-]\s+Volume|Ruidrive\.com|Author\s*:|Illustrasi\s*:|Illustrator\s*:|PDF\s+By\s*:|Translate\s*:|PDF\s+dan\s+dowload|Kono\s+Subarashii\s+Sekai|Attention|Warning!|\d+$)/i.test(l)) {
    continue;
  }

  // Deteksi Bab (Prolog / Chapter / Epilog)
  const isChap = /^(?:#\s*)?(PROLOG(?:UE)?|EPILOG(?:UE)?|CHAPTER\s+[0-9]+|INTERLUDE|SHORT\s+STORY|EXTRA)/i.test(l);
  if (isChap && !l.includes('List Chapter')) {
    // Pastikan bukan di dalam 120 baris pertama suatu volume yang merupakan daftar isi
    if (curLines.length > 50 || !curChap) {
      if (curChap && curLines.length > 50) {
        curChap.text = curLines.join('\n').trim();
        if (curChap.text.length > 500) chapters.push(curChap);
      }
      const cleanTitle = l.replace(/^#\s*/, '').trim();
      curChap = {
        vol: currentVol,
        id: `${currentVol.toLowerCase().replace(/\s+/g, '_')}_ch${String(chapters.length + 1).padStart(3, '0')}`,
        title: `${currentVol} - ${cleanTitle}`,
        text: ''
      };
      curLines = [];
      continue;
    }
  }

  curLines.push(rawLine);
}

if (curChap) {
  curChap.text = curLines.join('\n').trim();
  if (curChap.text.length > 500) chapters.push(curChap);
}

console.log('Total Bab terdeteksi:', chapters.length);
console.log('Sample 10 Bab pertama:');
for (let i = 0; i < Math.min(10, chapters.length); i++) {
  console.log(`[${i+1}] ${chapters[i].title} (~${chapters[i].text.length} chars)`);
}
