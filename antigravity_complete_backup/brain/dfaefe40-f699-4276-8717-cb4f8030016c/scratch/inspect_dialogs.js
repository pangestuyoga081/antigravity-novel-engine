const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt', 'utf8');
const lines = content.split('\n');

console.log('Total baris:', lines.length);

const speakers = new Map();
const dialogSamples = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();
  
  // Deteksi berbagai pola dialog:
  // 1. Nama: "..."
  // 2. **Nama**: "..."
  // 3. Nama: “...”
  // 4. — "..." atau tag dialog
  const m1 = line.match(/^(\*{0,2})([A-Za-zÀ-ÿ0-9\s.'’\-\/]{2,40})\1:\s*(["“'‘].*)/);
  if (m1) {
    const spk = m1[2].trim();
    speakers.set(spk, (speakers.get(spk) || 0) + 1);
    if (dialogSamples.length < 30) {
      dialogSamples.push({ lineNum: i + 1, speaker: spk, text: line });
    }
    continue;
  }

  // Cek apakah ada kutip dialog biasa atau dash dialog
  if (line.startsWith('—') || line.startsWith('-') || line.startsWith('"') || line.startsWith('“')) {
    if (dialogSamples.length < 30) {
      dialogSamples.push({ lineNum: i + 1, speaker: 'NO_PREFIX', text: line });
    }
  }
}

console.log('Total speaker prefix ditemukan:', speakers.size);
const sorted = Array.from(speakers.entries()).sort((a, b) => b[1] - a[1]);
console.log('Top 40 speakers:');
console.log(sorted.slice(0, 40));

console.log('\nSample dialog lines:');
for (const s of dialogSamples.slice(0, 20)) {
  console.log(`L${s.lineNum} [${s.speaker}]: ${s.text}`);
}
