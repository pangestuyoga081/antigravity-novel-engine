const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt', 'utf8');

// Contoh baris dari awal file yang ditanyakan user:
const snippet = `Sandy terkekeh lalu balik fokus ke bukunya, berbarengan sama pramugari yang kembali mondar-mandir nawarin minuman. Clark beres baca *The Economist* lalu ganti ke majalah *Sports Illustrated*. Sialan, dia bakal ngelewatin babak penutup musim *football*. Olahraga itu selalu dia pantau seumur hidupnya, bahkan pas lagi tugas operasi tempur. Tim Bears lagi gila-gilaan bangkitnya. Dia tumbuh besar di era Papa Bear George Halas dan julukan "Monsters of the Midway", bahkan sering ngayal bisa jadi atlet pro. Pas SMA dia lumayan jago jadi *linebacker*, dan Universitas Indiana sempet naksir berat sama dia (ditambah kemampuan renangnya yang hebat). Tapi akhirnya dia milih bodo amat sama kuliah dan gabung Angkatan Laut kayak bapaknya dulu. Bedanya, dia tembus Navy SEAL, bukan terombang-ambing di laut kayak sarden dalam kaleng kayak bapaknya...

Pramugari nyamperin bawa buku menu makan malam.

Pramugari: "Pak Clark?"

Pramugari: "Bu Clark?"

Enaknya kelas satu tuh begini. Kru kabin beneran hafal nama lu. John ngerasa ada peningkatan signifikan di penerbangan sekarang. Dia udah terbang jutaan mil bareng maskapai lain, tapi belakangan cuma terbang bareng British Airways yang dapet kontrak gede dari pemerintah Inggris.`;

console.log('--- SEBELUM ---');
console.log(snippet);

console.log('\n--- JIKA KONSISTEN John Clark & Sandy Clark ---');
let modified = snippet
  .replace(/\bClark\b/g, 'John Clark')
  .replace(/\bJohn\b/g, 'John Clark')
  .replace(/\bJohn John Clark\b/g, 'John Clark')
  .replace(/\bPak John Clark\b/g, 'Pak Clark')
  .replace(/\bBu John Clark\b/g, 'Bu Clark')
  .replace(/\bSandy\b/g, 'Sandy Clark')
  .replace(/\bSandy Sandy Clark\b/g, 'Sandy Clark');

console.log(modified);
