const snippet = `Sandy terkekeh lalu balik fokus ke bukunya, berbarengan sama pramugari yang kembali mondar-mandir nawarin minuman. Clark beres baca *The Economist* lalu ganti ke majalah *Sports Illustrated*. Sialan, dia bakal ngelewatin babak penutup musim *football*.

Pramugari: "Pak Clark?"

Pramugari: "Bu Clark?"

Enaknya kelas satu tuh begini. Kru kabin beneran hafal nama lu. John ngerasa ada peningkatan signifikan di penerbangan sekarang.`;

// 1 pass token replacement
function fixClark(t) {
  // Lindungi Pak Clark dan Bu Clark
  t = t.replace(/\bPak Clark\b/g, '___PAK_CLARK___');
  t = t.replace(/\bBu Clark\b/g, '___BU_CLARK___');

  // Match John Clark ATAU Clark ATAU John
  t = t.replace(/\b(John\s+Clark|Clark|John)\b/g, 'John Clark');

  // Kembalikan sapaan
  t = t.replace(/___PAK_CLARK___/g, 'Pak Clark');
  t = t.replace(/___BU_CLARK___/g, 'Bu Clark');
  return t;
}

console.log('HASIL 1-PASS:');
console.log(fixClark(snippet));
