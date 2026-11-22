const fs = require('fs');

const inputPath = 'D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt';
let content = fs.readFileSync(inputPath, 'utf8');

// 1. Pemetaan Speaker Dialog Lengkap & Kanonik
const speakerRules = [
  // Rainbow Six Command & Staff
  { match: /^(?:\*{0,2})(?:Clark|John|John Clark)(?:\*{0,2}):/gm, replace: 'John Clark:' },
  { match: /^(?:\*{0,2})(?:Chavez|Ding|Domingo|Domingo Chavez|Ding Chavez)(?:\*{0,2}):/gm, replace: 'Ding Chavez:' },
  { match: /^(?:\*{0,2})(?:Stanley|Alistair|Al Stanley|Alistair Stanley)(?:\*{0,2}):/gm, replace: 'Alistair Stanley:' },
  { match: /^(?:\*{0,2})(?:Tawney|Bill Tawney)(?:\*{0,2}):/gm, replace: 'Bill Tawney:' },
  { match: /^(?:\*{0,2})(?:Noonan|Tim|Tim Noonan)(?:\*{0,2}):/gm, replace: 'Tim Noonan:' },
  { match: /^(?:\*{0,2})(?:Bellow|Paul|Dr\. Bellow|Dokter Bellow|Paul Bellow)(?:\*{0,2}):/gm, replace: 'Dr. Paul Bellow:' },
  { match: /^(?:\*{0,2})(?:Malloy|Daniel|Bear|Daniel Malloy)(?:\*{0,2}):/gm, replace: 'Daniel Malloy:' },
  { match: /^(?:\*{0,2})(?:Covington|Peter Covington)(?:\*{0,2}):/gm, replace: 'Peter Covington:' },

  // Rainbow Six Team Members
  { match: /^(?:\*{0,2})(?:Price|Eddie|Eddie Price)(?:\*{0,2}):/gm, replace: 'Eddie Price:' },
  { match: /^(?:\*{0,2})(?:Johnston|Homer|Homer Johnston)(?:\*{0,2}):/gm, replace: 'Homer Johnston:' },
  { match: /^(?:\*{0,2})(?:Weber|Dieter|Dieter Weber)(?:\*{0,2}):/gm, replace: 'Dieter Weber:' },
  { match: /^(?:\*{0,2})(?:Vega|Julio|Oso|Julio Vega)(?:\*{0,2}):/gm, replace: 'Julio Vega:' },
  { match: /^(?:\*{0,2})(?:Loiselle|Louis|Louis Loiselle)(?:\*{0,2}):/gm, replace: 'Louis Loiselle:' },
  { match: /^(?:\*{0,2})(?:Patterson|Hank|Hank Patterson)(?:\*{0,2}):/gm, replace: 'Hank Patterson:' },
  { match: /^(?:\*{0,2})(?:Connolly|Peter Connolly)(?:\*{0,2}):/gm, replace: 'Peter Connolly:' },
  { match: /^(?:\*{0,2})(?:Tomlinson|George Tomlinson)(?:\*{0,2}):/gm, replace: 'George Tomlinson:' },
  { match: /^(?:\*{0,2})(?:Pierce|Mike Pierce)(?:\*{0,2}):/gm, replace: 'Mike Pierce:' },
  { match: /^(?:\*{0,2})(?:Franklin|Fred|Fred Franklin)(?:\*{0,2}):/gm, replace: 'Fred Franklin:' },
  { match: /^(?:\*{0,2})(?:Lincoln|Steve|Steve Lincoln)(?:\*{0,2}):/gm, replace: 'Steve Lincoln:' },
  { match: /^(?:\*{0,2})(?:Chin|Mike Chin)(?:\*{0,2}):/gm, replace: 'Mike Chin:' },
  { match: /^(?:\*{0,2})(?:Nuncio|Angelo Nuncio)(?:\*{0,2}):/gm, replace: 'Angelo Nuncio:' },
  { match: /^(?:\*{0,2})(?:De la Cruz|Patricio de la Cruz)(?:\*{0,2}):/gm, replace: 'Patricio de la Cruz:' },
  { match: /^(?:\*{0,2})(?:Woods|Dave Woods)(?:\*{0,2}):/gm, replace: 'Dave Woods:' },

  // Keluarga Clark & Chavez
  { match: /^(?:\*{0,2})(?:Sandy|Sandy Clark)(?:\*{0,2}):/gm, replace: 'Sandy Clark:' },
  { match: /^(?:\*{0,2})(?:Patsy|Patsy Clark|Patsy Chavez|Patsy Clark Chavez)(?:\*{0,2}):/gm, replace: 'Patsy Clark Chavez:' },

  // FBI, CIA, Intelijen & Pejabat
  { match: /^(?:\*{0,2})(?:Sullivan|Tom Sullivan)(?:\*{0,2}):/gm, replace: 'Tom Sullivan:' },
  { match: /^(?:\*{0,2})(?:Chatham|Frank Chatham)(?:\*{0,2}):/gm, replace: 'Frank Chatham:' },
  { match: /^(?:\*{0,2})(?:Werner|Gus|Gus Werner)(?:\*{0,2}):/gm, replace: 'Gus Werner:' },
  { match: /^(?:\*{0,2})(?:Murray|Dan|Dan Murray)(?:\*{0,2}):/gm, replace: 'Dan Murray:' },
  { match: /^(?:\*{0,2})(?:Liz Murray)(?:\*{0,2}):/gm, replace: 'Liz Murray:' },
  { match: /^(?:\*{0,2})(?:Foley|Ed|Ed Foley)(?:\*{0,2}):/gm, replace: 'Ed Foley:' },
  { match: /^(?:\*{0,2})(?:Mary Pat|Mary Pat Foley)(?:\*{0,2}):/gm, replace: 'Mary Pat Foley:' },
  { match: /^(?:\*{0,2})(?:Golovko|Sergey|Sergey Golovko)(?:\*{0,2}):/gm, replace: 'Sergey Golovko:' },
  { match: /^(?:\*{0,2})(?:Holt|Cyril Holt)(?:\*{0,2}):/gm, replace: 'Cyril Holt:' },
  { match: /^(?:\*{0,2})(?:Winston|George Winston)(?:\*{0,2}):/gm, replace: 'George Winston:' },
  { match: /^(?:\*{0,2})(?:Arnie|Arnie van Damm)(?:\*{0,2}):/gm, replace: 'Arnie van Damm:' },
  { match: /^(?:\*{0,2})(?:Waterhouse|Mark Waterhouse)(?:\*{0,2}):/gm, replace: 'Mark Waterhouse:' },
  { match: /^(?:\*{0,2})(?:Martin Cooper)(?:\*{0,2}):/gm, replace: 'Martin Cooper:' },
  { match: /^(?:\*{0,2})(?:Sinclair|Gordon Sinclair)(?:\*{0,2}):/gm, replace: 'Gordon Sinclair:' },
  { match: /^(?:\*{0,2})(?:Senator Hawking)(?:\*{0,2}):/gm, replace: 'Senator Hawking:' },

  // Horizon / The Project Antagonis
  { match: /^(?:\*{0,2})(?:Popov|Dimitri|Dmitriy|Ilich|Serov|Dmitriy Popov)(?:\*{0,2}):/gm, replace: 'Dmitriy Popov:' },
  { match: /^(?:\*{0,2})(?:Brightling|John Brightling)(?:\*{0,2}):/gm, replace: 'John Brightling:' },
  { match: /^(?:\*{0,2})(?:Carol|Carol Brightling)(?:\*{0,2}):/gm, replace: 'Carol Brightling:' },
  { match: /^(?:\*{0,2})(?:Killgore|Dokter Killgore|Dr\. Killgore|John Killgore)(?:\*{0,2}):/gm, replace: 'Dr. John Killgore:' },
  { match: /^(?:\*{0,2})(?:Archer|Barbara|Dokter Archer|Dr\. Archer|Barbara Archer)(?:\*{0,2}):/gm, replace: 'Dr. Barbara Archer:' },
  { match: /^(?:\*{0,2})(?:Henriksen|Bill|Bill Henriksen)(?:\*{0,2}):/gm, replace: 'Bill Henriksen:' },
  { match: /^(?:\*{0,2})(?:Hunnicutt|Foster|Foster Hunnicutt)(?:\*{0,2}):/gm, replace: 'Foster Hunnicutt:' },
  { match: /^(?:\*{0,2})(?:Maclean|Kirk|MacLean|Kirk Maclean|Kirk MacLean|Macleash)(?:\*{0,2}):/gm, replace: 'Kirk Maclean:' },
  { match: /^(?:\*{0,2})(?:Gearing|Wil|Wil Gearing|Wilson Gearing|Kolonel Wilson Gearing)(?:\*{0,2}):/gm, replace: 'Kolonel Wil Gearing:' },
  { match: /^(?:\*{0,2})(?:Farmer|Ben|Ben Farmer)(?:\*{0,2}):/gm, replace: 'Ben Farmer:' },
  { match: /^(?:\*{0,2})(?:Mayflower|Kevin|Kevin Mayflower)(?:\*{0,2}):/gm, replace: 'Kevin Mayflower:' },
  { match: /^(?:\*{0,2})(?:Wilkerson|Miles|Miles Wilkerson)(?:\*{0,2}):/gm, replace: 'Miles Wilkerson:' },
  { match: /^(?:\*{0,2})(?:Dawson|Dr\. Dawson)(?:\*{0,2}):/gm, replace: 'Dr. Dawson:' },
  { match: /^(?:\*{0,2})(?:Mary Bannister|Mary)(?:\*{0,2}):/gm, replace: 'Mary Bannister:' },
  { match: /^(?:\*{0,2})(?:Anne Pretloe)(?:\*{0,2}):/gm, replace: 'Anne Pretloe:' },

  // Teroris Lapangan & Sandera / Tokoh Terkait
  { match: /^(?:\*{0,2})(?:Fiirchtner|Hans Fürchtner|Hans Furchtner|Fürchtner|Hans)(?:\*{0,2}):/gm, replace: 'Hans Fürchtner:' },
  { match: /^(?:\*{0,2})(?:Petra|Petra Dortmund)(?:\*{0,2}):/gm, replace: 'Petra Dortmund:' },
  { match: /^(?:\*{0,2})(?:Ostermann|Erwin|Erwin Ostermann)(?:\*{0,2}):/gm, replace: 'Erwin Ostermann:' },
  { match: /^(?:\*{0,2})(?:Gerhardt|Gerhardt Dengler)(?:\*{0,2}):/gm, replace: 'Gerhardt Dengler:' },
  { match: /^(?:\*{0,2})(?:Altmark|Kapten Altmark)(?:\*{0,2}):/gm, replace: 'Kapten Peter Altmark:' },
  { match: /^(?:\*{0,2})(?:René|René Montpellier)(?:\*{0,2}):/gm, replace: 'René Montpellier:' },
  { match: /^(?:\*{0,2})(?:André|André Herr)(?:\*{0,2}):/gm, replace: 'André Herr:' },
  { match: /^(?:\*{0,2})(?:Mike Dennis|Dennis)(?:\*{0,2}):/gm, replace: 'Mike Dennis:' },
  { match: /^(?:\*{0,2})(?:Gassman|Kapten Gassman)(?:\*{0,2}):/gm, replace: 'Kapten Gassman:' },
  { match: /^(?:\*{0,2})(?:Grady|Sean|Sean Grady)(?:\*{0,2}):/gm, replace: 'Sean Grady:' },
  { match: /^(?:\*{0,2})(?:O'Neil|Timothy|Timothy O'Neil|Timmy|Timmy O'Neil)(?:\*{0,2}):/gm, replace: 'Timothy O\'Neil:' },
  { match: /^(?:\*{0,2})(?:Roddy Sands)(?:\*{0,2}):/gm, replace: 'Roddy Sands:' },
  { match: /^(?:\*{0,2})(?:Chuck Ussery|Ussery|Chuck)(?:\*{0,2}):/gm, replace: 'Chuck Ussery:' },
  { match: /^(?:\*{0,2})(?:Pat O'Connor|O'Connor)(?:\*{0,2}):/gm, replace: 'Pat O\'Connor:' }
];

let speakerChangeCount = 0;
for (const rule of speakerRules) {
  content = content.replace(rule.match, (match) => {
    speakerChangeCount++;
    return rule.replace;
  });
}

console.log(`Speaker dialog diganti/dinormalkan: ${speakerChangeCount} kali.`);

// 2. Pembersihan Typo OCR & Konsistensi Nama di Narasi
const narrationRules = [
  { match: /\bFiirchtner\b/g, replace: 'Fürchtner' },
  { match: /\bHans Fiirchtner\b/g, replace: 'Hans Fürchtner' },
  { match: /\bMacleash\b/g, replace: 'Maclean' },
  { match: /\bMacLean\b/g, replace: 'Maclean' },
  { match: /\bKirk MacLean\b/g, replace: 'Kirk Maclean' },
  { match: /\bAlistar Stanley\b/g, replace: 'Alistair Stanley' },
  { match: /\bAlistar\b/g, replace: 'Alistair' },
  { match: /\bDimitri Popov\b/g, replace: 'Dmitriy Popov' },
  { match: /\bDimitri\b/g, replace: 'Dmitriy' },
  { match: /\bKolonel Wilson Gearing\b/g, replace: 'Kolonel Wil Gearing' },
  { match: /\bWilson Gearing\b/g, replace: 'Wil Gearing' },
  { match: /\bBob Auckland\b/g, replace: 'Bob Aukland' },
  { match: /\bAuckland\b/g, replace: 'Aukland' }
];

let narrationChangeCount = 0;
for (const rule of narrationRules) {
  content = content.replace(rule.match, (match) => {
    narrationChangeCount++;
    return rule.replace;
  });
}

console.log(`Perbaikan konsistensi narasi: ${narrationChangeCount} kali.`);

// Simpan file hasil normalisasi
fs.writeFileSync(inputPath, content, 'utf8');
console.log('✅ File berhasil disimpan kembali dengan nama lengkap & konsisten!');
