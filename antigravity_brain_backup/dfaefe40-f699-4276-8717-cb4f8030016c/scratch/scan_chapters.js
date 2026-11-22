const fs = require('fs');

const lines = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2.txt', 'utf8').split('\n');

const chapters = [
  { no: 0, title: 'PROLOG', rx: [/^\s*PROLOG\s*$/i] },
  { no: 1, title: '1. Memorandum', rx: [/^\s*MEMORANDUM\s*$/i] },
  { no: 2, title: '2. Pe cai, cow-boy', rx: [/Pe CAI,\s*COW-BOY/i] },
  { no: 3, title: '3. Pitici şi puşcoace', rx: [/PITICI\s*ŞI\s*PUŞCOACE/i, /^\s*3\s*$/] },
  { no: 4, title: '4. ADA', rx: [/^\s*ADA\s*$/] },
  { no: 5, title: '5. Ramificații', rx: [/RAMIFICA/i, /^\s*5\s*$/] },
  { no: 6, title: '6. Credincioşi adevăraţi', rx: [/Credincio|adevarat/i, /^\s*6\s*$/] },
  { no: 7, title: '7. Finanțe', rx: [/FINAN/i, /^\s*7\s*$/] },
  { no: 8, title: '8. Știai TV', rx: [/ŞTIAI\s*TV|STIAI\s*TV/i, /^\s*8\s*$/] },
  { no: 9, title: '9. Apropieri', rx: [/APROPIERI/i, /^\s*9\s*$/] },
  { no: 10, title: '10. Săpături', rx: [/S[AĂ]P[AĂ]TURI/i, /^\s*(10|IO)\s*$/] },
  { no: 11, title: '11. Infrastructură', rx: [/INFRASTRUCTUR/i, /^\s*(11|II)\s*$/] },
  { no: 12, title: '12. Imprevizibil, incontrolabil', rx: [/Imprevizibil/i, /^\s*12\s*$/] },
  { no: 13, title: '13. Amuzament', rx: [/AMUZAMENT/i, /^\s*13\s*$/] },
  { no: 14, title: '14. Sabia legiunii', rx: [/SABIA\s*LEGIUNII/i, /^\s*14\s*$/] },
  { no: 15, title: '15. Pălării albe', rx: [/P[AĂ]L[AĂ]RII\s*ALBE/i, /^\s*(15|IS)\s*$/] },
  { no: 16, title: '16. Descoperirea', rx: [/DESCOPERIREA/i, /^\s*(16|IG)\s*$/] },
  { no: 17, title: '17. Antene întinse', rx: [/ANTENE\s*[IÎ]NTINSE/i, /^\s*17\s*$/] },
  { no: 18, title: '18. Pavilioane', rx: [/PAVILIOANE/i, /^\s*(18|I8)\s*$/] },
  { no: 19, title: '19. Canari', rx: [/CANARI/i, /^\s*(19|IO)\s*$/] },
  { no: 20, title: '20. Contacte', rx: [/CONTACTE/i, /^\s*20\s*$/] },
  { no: 21, title: '21. Stadii', rx: [/STADII/i, /^\s*21\s*$/] },
  { no: 22, title: '22. Contramăsuri', rx: [/CONTRAM[AĂ]SURI/i, /^\s*22\s*$/] },
  { no: 23, title: '23. Mereu de veghe', rx: [/MEREU\s*DE\s*VEGHE/i, /^\s*23\s*$/] },
  { no: 24, title: '24. La vamă', rx: [/LA\s*VAM[AĂ]/i, /^\s*24\s*$/] },
  { no: 25, title: '25. Răsărit de soare', rx: [/R[AĂ]S[AĂ]RIT/i, /^\s*(25|05)\s*$/] },
  { no: 26, title: '26. Concluzii', rx: [/CONCLUZII/i, /^\s*(26|20)\s*$/] },
  { no: 27, title: '27. Agenţi de transfer', rx: [/AGEN[TŢ]I/i, /^\s*27\s*$/] },
  { no: 28, title: '28. În plină zi', rx: [/[IÎ]N\s*P[UL]IN[AĂ]\s*ZI/i, /^\s*28\s*$/] },
  { no: 29, title: '29. Recuperarea', rx: [/RECUPERAREA/i, /^\s*(29|20)\s*$/] },
  { no: 30, title: '30. Peisaje', rx: [/PEISAJE/i, /^\s*30\s*$/] },
  { no: 31, title: '31. Mişcare', rx: [/MI[SŞ]CARE/i, /^\s*(31|3I)\s*$/] },
  { no: 32, title: '32. Afaceri sîngeroase', rx: [/AFACERI/i, /^\s*32\s*$/] },
  { no: 33, title: '33. Încep jocurile', rx: [/[IÎ]NCEP\s*JOCURILE/i, /^\s*33\s*$/] },
  { no: 34, title: '34. Jocurile continuă', rx: [/JOCURILE\s*CONTINU/i, /^\s*34\s*$/] },
  { no: 35, title: '35. Maratonul', rx: [/MARATONUL/i, /^\s*35\s*$/] },
  { no: 36, title: '36. Zbor de necesitate', rx: [/ZBOR\s*DE\s*NECESITATE/i, /^\s*(36|30)\s*$/] },
  { no: 37, title: '37. Flacăra care se stinge', rx: [/FLAC[AĂ]RA/i, /^\s*37\s*$/] },
  { no: 38, title: '38. Staţiunea ştiinţifică', rx: [/STA[TŢ]IUNEA/i, /^\s*38\s*$/] },
  { no: 39, title: '39. Armonia', rx: [/ARMONIA/i, /^\s*39\s*$/] },
  { no: 40, title: 'EPILOG', rx: [/^\s*(EPILOG|EPILOC)\s*$/i] }
];

let lastLine = 520;
const found = [];

for (let ch of chapters) {
  let bestLine = -1;
  let bestText = '';
  for (let i = lastLine; i < lines.length; i++) {
    if (i >= 25030 && i <= 25120) continue;
    if (i >= 48240 && i <= 48350) continue;

    const l = lines[i].trim();
    if (l.length > 50) continue;

    const match = ch.rx.some(r => r.test(l));
    if (match) {
      bestLine = i + 1;
      bestText = l;
      lastLine = i + 5;
      break;
    }
  }
  found.push({ no: ch.no, title: ch.title, line: bestLine, text: bestText });
}

console.log('HASIL SCAN BAB:');
for (const f of found) {
  console.log(`Bab ${f.no.toString().padStart(2, '0')} (${f.title}): Line ${f.line} -> "${f.text}"`);
}
const missing = found.filter(f => f.line === -1);
console.log(`Missing chapters: ${missing.length}`);
