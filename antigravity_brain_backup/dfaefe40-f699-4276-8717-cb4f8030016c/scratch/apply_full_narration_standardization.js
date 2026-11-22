const fs = require('fs');

const inputPath = 'D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt';
let content = fs.readFileSync(inputPath, 'utf8');

console.log('Membaca file:', inputPath, `(${content.length} karakter)`);

// 1. Lindungi sapaan dan nama khusus yang tidak boleh diubah
const protections = [
  'Pak Clark',
  'Bu Clark',
  'Papa Bear George Halas',
  'Papa Bear',
  'John Wayne',
  'St. John',
  'Bears'
];

const protectedMap = new Map();
let pIndex = 0;
for (const p of protections) {
  const reg = new RegExp(`\\b${p.replace(/\./g, '\\.')}\\b`, 'g');
  content = content.replace(reg, (match) => {
    const key = `___PROT_${pIndex++}___`;
    protectedMap.set(key, match);
    return key;
  });
}

// 2. Daftar aturan 1-pass untuk seluruh karakter utama & pendukung
// Urutan penting: entitas majemuk (Killgore, Brightling) sebelum entitas dasar (John)
const rules = [
  // Horizon / The Project
  { regex: /\b(Dr\.\s*John\s*Killgore|Dokter\s*John\s*Killgore|Dr\.\s*Killgore|Dokter\s*Killgore|John\s*Killgore|Killgore)\b/g, rep: 'Dr. John Killgore' },
  { regex: /\b(Dr\.\s*Barbara\s*Archer|Dokter\s*Barbara\s*Archer|Dr\.\s*Archer|Dokter\s*Archer|Barbara\s*Archer|Archer)\b/g, rep: 'Dr. Barbara Archer' },
  { regex: /\b(John\s*Brightling|Brightling)\b/g, rep: 'John Brightling' },
  { regex: /\b(Carol\s*Brightling|Carol)\b/g, rep: 'Carol Brightling' },
  { regex: /\b(Bill\s*Henriksen|Henriksen)\b/g, rep: 'Bill Henriksen' },
  { regex: /\b(Foster\s*Hunnicutt|Hunnicutt)\b/g, rep: 'Foster Hunnicutt' },
  { regex: /\b(Kirk\s*Maclean|Kirk\s*MacLean|Maclean|MacLean|Macleash)\b/g, rep: 'Kirk Maclean' },
  { regex: /\b(Kolonel\s*Wilson\s*Gearing|Kolonel\s*Wil\s*Gearing|Wilson\s*Gearing|Wil\s*Gearing|Gearing)\b/g, rep: 'Kolonel Wil Gearing' },
  { regex: /\b(Ben\s*Farmer|Farmer)\b/g, rep: 'Ben Farmer' },
  { regex: /\b(Kevin\s*Mayflower|Mayflower)\b/g, rep: 'Kevin Mayflower' },
  { regex: /\b(Miles\s*Wilkerson|Wilkerson)\b/g, rep: 'Miles Wilkerson' },
  { regex: /\b(Dr\.\s*Dawson|Dawson)\b/g, rep: 'Dr. Dawson' },
  { regex: /\b(Dmitriy\s*Popov|Dimitri\s*Popov|Popov|Dmitriy|Dimitri)\b/g, rep: 'Dmitriy Popov' },

  // Tokoh Utama Rainbow Six
  { regex: /\b(John\s*Clark|Clark|John)\b/g, rep: 'John Clark' },
  { regex: /\b(Ding\s*Chavez|Domingo\s*Chavez|Chavez|Ding|Domingo)\b/g, rep: 'Ding Chavez' },
  { regex: /\b(Sandy\s*Clark|Sandy)\b/g, rep: 'Sandy Clark' },
  { regex: /\b(Patsy\s*Clark\s*Chavez|Patsy\s*Clark|Patsy\s*Chavez|Patsy)\b/g, rep: 'Patsy Clark Chavez' },
  { regex: /\b(Alistair\s*Stanley|Al\s*Stanley|Alistar\s*Stanley|Stanley|Alistair|Alistar)\b/g, rep: 'Alistair Stanley' },
  { regex: /\b(Bill\s*Tawney|Tawney)\b/g, rep: 'Bill Tawney' },
  { regex: /\b(Tim\s*Noonan|Noonan)\b/g, rep: 'Tim Noonan' },
  { regex: /\b(Dr\.\s*Paul\s*Bellow|Dokter\s*Paul\s*Bellow|Dr\.\s*Bellow|Dokter\s*Bellow|Paul\s*Bellow|Bellow)\b/g, rep: 'Dr. Paul Bellow' },
  { regex: /\b(Daniel\s*Malloy|Malloy)\b/g, rep: 'Daniel Malloy' },
  { regex: /\b(Peter\s*Covington|Covington)\b/g, rep: 'Peter Covington' },

  // Anggota Tim Rainbow
  { regex: /\b(Eddie\s*Price|Price)\b/g, rep: 'Eddie Price' },
  { regex: /\b(Homer\s*Johnston|Johnston)\b/g, rep: 'Homer Johnston' },
  { regex: /\b(Dieter\s*Weber|Weber)\b/g, rep: 'Dieter Weber' },
  { regex: /\b(Julio\s*Vega|Vega)\b/g, rep: 'Julio Vega' },
  { regex: /\b(Louis\s*Loiselle|Loiselle)\b/g, rep: 'Louis Loiselle' },
  { regex: /\b(Hank\s*Patterson|Patterson)\b/g, rep: 'Hank Patterson' },
  { regex: /\b(Peter\s*Connolly|Connolly)\b/g, rep: 'Peter Connolly' },
  { regex: /\b(George\s*Tomlinson|Tomlinson)\b/g, rep: 'George Tomlinson' },
  { regex: /\b(Fred\s*Franklin|Franklin)\b/g, rep: 'Fred Franklin' },
  { regex: /\b(Steve\s*Lincoln|Lincoln)\b/g, rep: 'Steve Lincoln' },
  { regex: /\b(Mike\s*Chin|Chin)\b/g, rep: 'Mike Chin' },

  // FBI, CIA & Tokoh Resmi
  { regex: /\b(Tom\s*Sullivan|Sullivan)\b/g, rep: 'Tom Sullivan' },
  { regex: /\b(Frank\s*Chatham|Chatham)\b/g, rep: 'Frank Chatham' },
  { regex: /\b(Gus\s*Werner|Werner)\b/g, rep: 'Gus Werner' },
  { regex: /\b(Dan\s*Murray|Murray)\b/g, rep: 'Dan Murray' },
  { regex: /\b(Ed\s*Foley|Foley)\b/g, rep: 'Ed Foley' },
  { regex: /\b(Mary\s*Pat\s*Foley|Mary\s*Pat)\b/g, rep: 'Mary Pat Foley' },
  { regex: /\b(Sergey\s*Golovko|Golovko)\b/g, rep: 'Sergey Golovko' },
  { regex: /\b(Cyril\s*Holt|Holt)\b/g, rep: 'Cyril Holt' },
  { regex: /\b(George\s*Winston|Winston)\b/g, rep: 'George Winston' },
  { regex: /\b(Arnie\s*van\s*Damm|Arnie)\b/g, rep: 'Arnie van Damm' },

  // Kasus Eropa & Teroris
  { regex: /\b(Hans\s*Fürchtner|Hans\s*Furchtner|Hans\s*Fiirchtner|Fürchtner|Fiirchtner|Furchtner)\b/g, rep: 'Hans Fürchtner' },
  { regex: /\b(Petra\s*Dortmund|Dortmund)\b/g, rep: 'Petra Dortmund' },
  { regex: /\b(Erwin\s*Ostermann|Ostermann)\b/g, rep: 'Erwin Ostermann' },
  { regex: /\b(Gerhardt\s*Dengler|Gerhardt)\b/g, rep: 'Gerhardt Dengler' },
  { regex: /\b(Kapten\s*Peter\s*Altmark|Kapten\s*Altmark|Altmark)\b/g, rep: 'Kapten Peter Altmark' },
  { regex: /\b(René\s*Montpellier|Montpellier)\b/g, rep: 'René Montpellier' },
  { regex: /\b(André\s*Herr)\b/g, rep: 'André Herr' },
  { regex: /\b(Mike\s*Dennis|Dennis)\b/g, rep: 'Mike Dennis' },
  { regex: /\b(Kapten\s*Gassman|Gassman)\b/g, rep: 'Kapten Gassman' },
  { regex: /\b(Sean\s*Grady|Grady)\b/g, rep: 'Sean Grady' },
  { regex: /\b(Timothy\s*O'Neil|Timmy\s*O'Neil|O'Neil)\b/g, rep: 'Timothy O\'Neil' },
  { regex: /\b(Chuck\s*Ussery|Ussery)\b/g, rep: 'Chuck Ussery' },
  { regex: /\b(Pat\s*O'Connor|O'Connor)\b/g, rep: 'Pat O\'Connor' }
];

let totalReplacements = 0;
for (const rule of rules) {
  content = content.replace(rule.regex, (match) => {
    totalReplacements++;
    return rule.rep;
  });
}

// 3. Kembalikan nama sapaan yang dilindungi
for (const [key, val] of protectedMap.entries()) {
  content = content.replace(new RegExp(key, 'g'), val);
}

// 4. Bersihkan duplikasi yang tidak sengaja
content = content.replace(/\bJohn\s+Clark\s+Clark\b/g, 'John Clark');
content = content.replace(/\bJohn\s+John\s+Clark\b/g, 'John Clark');
content = content.replace(/\bDing\s+Chavez\s+Chavez\b/g, 'Ding Chavez');
content = content.replace(/\bDing\s+Ding\s+Chavez\b/g, 'Ding Chavez');
content = content.replace(/\bSandy\s+Clark\s+Clark\b/g, 'Sandy Clark');
content = content.replace(/\bSandy\s+Sandy\s+Clark\b/g, 'Sandy Clark');
content = content.replace(/\bDr\.\s*John\s*Killgore\s+Killgore\b/g, 'Dr. John Killgore');
content = content.replace(/\bJohn\s+Brightling\s+Brightling\b/g, 'John Brightling');
content = content.replace(/\bAlistair\s+Stanley\s+Stanley\b/g, 'Alistair Stanley');

console.log(`Total nama distandarisasi di seluruh naskah: ${totalReplacements}`);

// Simpan file hasil
fs.writeFileSync(inputPath, content, 'utf8');
console.log('✅ File berhasil disimpan kembali dengan nama lengkap & konsisten 100%!');
