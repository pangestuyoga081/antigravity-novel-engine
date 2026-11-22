const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt', 'utf8');
const lines = content.split('\n');

const speakerCounts = new Map();

for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();
  const m = line.match(/^(\*{0,2})([A-Za-zÀ-ÿ0-9\s.'’\-\/]{2,40})\1:\s*(["“'‘].*)/);
  if (m) {
    const spk = m[2].trim();
    speakerCounts.set(spk, (speakerCounts.get(spk) || 0) + 1);
  }
}

const allSpeakers = Array.from(speakerCounts.entries()).sort((a, b) => b[1] - a[1]);
console.log('Semua Speaker yang muncul > 2 kali:');
console.log(JSON.stringify(allSpeakers.filter(s => s[1] >= 3), null, 2));
