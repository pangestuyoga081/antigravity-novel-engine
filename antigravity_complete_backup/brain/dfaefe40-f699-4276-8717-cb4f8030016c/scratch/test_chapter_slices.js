const fs = require('fs');

const lines = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2.txt', 'utf8').split('\n');

const chapterMeta = [
  { no: 0, id: 'prolog', title: 'PROLOG: Situasi', rx: [/^\s*PROLOG\s*$/i] },
  { no: 1, id: 'chap_01', title: 'BAB 1: Memorandum', rx: [/^\s*MEMORANDUM\s*$/i] },
  { no: 2, id: 'chap_02', title: 'BAB 2: Beraksi, Koboi', rx: [/Pe CAI,\s*COW-BOY/i] },
  { no: 3, id: 'chap_03', title: 'BAB 3: Tim Pengintai & Pasukan Penembak', rx: [/PITICI\s*ŞI\s*PUŞCOACE/i, /^\s*3\s*$/] },
  { no: 4, id: 'chap_04', title: 'BAB 4: Evaluasi Pasca Aksi (AAR)', rx: [/^\s*ADA\s*$/] },
  { no: 5, id: 'chap_05', title: 'BAB 5: Cabang Masalah', rx: [/RAMIFICA/i, /^\s*5\s*$/] },
  { no: 6, id: 'chap_06', title: 'BAB 6: Orang Beriman Sejati', rx: [/CREDINCIO|ADEV[AĂ]RA[TŢ]/i, /^\s*6\s*$/] },
  { no: 7, id: 'chap_07', title: 'BAB 7: Finansial', rx: [/FINAN[TŢ]E/i, /^\s*7\s*$/] },
  { no: 8, id: 'chap_08', title: 'BAB 8: Sorotan TV', rx: [/ŞTIAI\s*TV|STIAI\s*TV/i, /^\s*8\s*$/] },
  { no: 9, id: 'chap_09', title: 'BAB 9: Pendekatan', rx: [/APROPIERI/i, /^\s*9\s*$/] },
  { no: 10, id: 'chap_10', title: 'BAB 10: Penyelidikan Mendalam', rx: [/S[AĂ]P[AĂ]TURI/i, /^\s*(10|IO)\s*$/] },
  { no: 11, id: 'chap_11', title: 'BAB 11: Infrastruktur', rx: [/INFRASTRUCTUR/i, /^\s*(11|II)\s*$/] },
  { no: 12, id: 'chap_12', title: 'BAB 12: Tak Terduga dan Tak Terkendali', rx: [/Imprevizibil/i, /^\s*12\s*$/] },
  { no: 13, id: 'chap_13', title: 'BAB 13: Taman Hiburan', rx: [/AMUZAMENT/i, /^\s*13\s*$/] },
  { no: 14, id: 'chap_14', title: 'BAB 14: Pedang Pasukan', rx: [/SABIA\s*LEGIUNII/i, /^\s*14\s*$/] },
  { no: 15, id: 'chap_15', title: 'BAB 15: Topi Putih', rx: [/P[AĂ]L[AĂ]RII\s*ALBE/i, /^\s*(15|IS)\s*$/] },
  { no: 16, id: 'chap_16', title: 'BAB 16: Penemuan', rx: [/DESCOPERIREA/i, /^\s*(16|IG)\s*$/] },
  { no: 17, id: 'chap_17', title: 'BAB 17: Radar Terbentang', rx: [/ANTENE\s*[IÎ]NTINSE/i, /^\s*17\s*$/] },
  { no: 18, id: 'chap_18', title: 'BAB 18: Paviliun', rx: [/PAVILIOANE/i, /^\s*(18|I8)\s*$/] },
  { no: 19, id: 'chap_19', title: 'BAB 19: Burung Kenari', rx: [/CANARI/i, /^\s*(19|IO)\s*$/] },
  { no: 20, id: 'chap_20', title: 'BAB 20: Kontak', rx: [/CONTACTE/i, /^\s*20\s*$/] },
  { no: 21, id: 'chap_21', title: 'BAB 21: Fase Uji Coba', rx: [/STADII/i, /^\s*21\s*$/] },
  { no: 22, id: 'chap_22', title: 'BAB 22: Langkah Balasan', rx: [/CONTRAM[AĂ]SURI/i, /^\s*22\s*$/] },
  { no: 23, id: 'chap_23', title: 'BAB 23: Selalu Waspada', rx: [/MEREU\s*DE\s*VEGHE/i, /^\s*23\s*$/] },
  { no: 24, id: 'chap_24', title: 'BAB 24: Di Perbatasan', rx: [/LA\s*VAM[AĂ]/i, /^\s*24\s*$/] },
  { no: 25, id: 'chap_25', title: 'BAB 25: Terbit Fajar', rx: [/R[AĂ]S[AĂ]RIT/i, /^\s*(25|05)\s*$/] },
  { no: 26, id: 'chap_26', title: 'BAB 26: Kesimpulan', rx: [/CONCLUZII/i, /^\s*(26|20)\s*$/] },
  { no: 27, id: 'chap_27', title: 'BAB 27: Media Penyebaran', rx: [/AGEN[TŢ]I\s*DE\s*TRANSFER/i, /^\s*27\s*$/] },
  { no: 28, id: 'chap_28', title: 'BAB 28: Di Siang Bolong', rx: [/[IÎ]N\s*P[UL]IN[AĂ]\s*ZI/i, /^\s*28\s*$/] },
  { no: 29, id: 'chap_29', title: 'BAB 29: Evakuasi', rx: [/RECUPERAREA/i, /^\s*(29|20)\s*$/] },
  { no: 30, id: 'chap_30', title: 'BAB 30: Bentang Alam', rx: [/PEISAJE/i, /^\s*30\s*$/] },
  { no: 31, id: 'chap_31', title: 'BAB 31: Manuver', rx: [/MI[SŞ]CARE/i, /^\s*(31|3I)\s*$/] },
  { no: 32, id: 'chap_32', title: 'BAB 32: Bisnis Berdarah', rx: [/AFACERI/i, /^\s*32\s*$/] },
  { no: 33, id: 'chap_33', title: 'BAB 33: Permainan Dimulai', rx: [/[IÎ]NCEP\s*JOCURILE/i, /^\s*33\s*$/] },
  { no: 34, id: 'chap_34', title: 'BAB 34: Permainan Berlanjut', rx: [/JOCURILE\s*CONTINU/i, /^\s*34\s*$/] },
  { no: 35, id: 'chap_35', title: 'BAB 35: Maraton', rx: [/MARATONUL/i, /^\s*35\s*$/] },
  { no: 36, id: 'chap_36', title: 'BAB 36: Penerbangan Darurat', rx: [/ZBOR\s*DE\s*NECESITATE/i, /^\s*(36|30)\s*$/] },
  { no: 37, id: 'chap_37', title: 'BAB 37: Api yang Padam', rx: [/FLAC[AĂ]RA/i, /^\s*37\s*$/] },
  { no: 38, id: 'chap_38', title: 'BAB 38: Pangkalan Riset', rx: [/STA[TŢ]IUNEA/i, /^\s*38\s*$/] },
  { no: 39, id: 'chap_39', title: 'BAB 39: Harmoni', rx: [/ARMONIA/i, /^\s*39\s*$/] },
  { no: 40, id: 'epilog', title: 'EPILOG', rx: [/^\s*(EPILOG|EPILOC)\s*$/i] }
];

let lastLine = 520;
const chapterSlices = [];

for (let i = 0; i < chapterMeta.length; i++) {
  const meta = chapterMeta[i];
  let start = -1;
  for (let j = lastLine; j < lines.length; j++) {
    if (j >= 25030 && j <= 25120) continue;
    if (j >= 48240 && j <= 48350) continue;
    const l = lines[j].trim();
    if (l.length > 50) continue;
    if (meta.rx.some(r => r.test(l))) {
      start = j;
      lastLine = j + 5;
      break;
    }
  }
  chapterSlices.push({ ...meta, startLine: start });
}

for (let i = 0; i < chapterSlices.length; i++) {
  const cur = chapterSlices[i];
  const next = chapterSlices[i + 1];
  let endLine = next ? next.startLine : lines.length;
  // Jika ini bab 20 (terakhir di Vol 1), akhiri sebelum Cuprins Vol 1
  if (cur.no === 20) endLine = 25030;
  // Jika ini Epilog, akhiri sebelum Cuprins Vol 2
  if (cur.no === 40) endLine = 48240;

  const rawLines = lines.slice(cur.startLine, endLine);
  // Bersihkan watermark
  const cleanLines = rawLines.filter(l => {
    const t = l.trim();
    if (/^(TOM CLANCY\b|RAINBOW SIX\b|\d+\s+e\s+TOM CLANCY|\bRAINBOW SIX\s+e\s+\d+)/i.test(t)) return false;
    if (t.length < 5 && /^[|\-=_~+`!?.a-z\s]+$/i.test(t)) return false;
    return true;
  });
  const text = cleanLines.join('\n').trim();
  console.log(`${cur.id}: ${cur.title} | Baris ${cur.startLine}-${endLine} | Panjang: ${text.length} chars (~${Math.ceil(text.length / 8000)} chunks)`);
}
