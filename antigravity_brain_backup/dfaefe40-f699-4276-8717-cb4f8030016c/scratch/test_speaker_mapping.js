const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt', 'utf8');
const lines = content.split('\n');

// Peta konversi nama speaker dialog sepotong -> Nama Lengkap Kanonik
const speakerMap = {
  // Rainbow Six Command
  'Clark': 'John Clark',
  'John': 'John Clark',
  'John Clark': 'John Clark',
  'Chavez': 'Ding Chavez',
  'Ding': 'Ding Chavez',
  'Domingo': 'Ding Chavez',
  'Domingo Chavez': 'Ding Chavez',
  'Ding Chavez': 'Ding Chavez',
  'Stanley': 'Alistair Stanley',
  'Alistair': 'Alistair Stanley',
  'Al Stanley': 'Alistair Stanley',
  'Alistair Stanley': 'Alistair Stanley',
  'Tawney': 'Bill Tawney',
  'Bill Tawney': 'Bill Tawney',
  'Noonan': 'Tim Noonan',
  'Tim Noonan': 'Tim Noonan',
  'Bellow': 'Dr. Paul Bellow',
  'Paul Bellow': 'Dr. Paul Bellow',
  'Dokter Bellow': 'Dr. Paul Bellow',
  'Dr. Bellow': 'Dr. Paul Bellow',
  'Covington': 'Peter Covington',
  'Peter Covington': 'Peter Covington',
  'Malloy': 'Daniel Malloy',
  'Daniel Malloy': 'Daniel Malloy',
  'Bear': 'Daniel Malloy',

  // Anggota Tim Rainbow
  'Eddie Price': 'Eddie Price',
  'Price': 'Eddie Price',
  'Johnston': 'Homer Johnston',
  'Homer Johnston': 'Homer Johnston',
  'Homer': 'Homer Johnston',
  'Weber': 'Dieter Weber',
  'Dieter Weber': 'Dieter Weber',
  'Dieter': 'Dieter Weber',
  'Vega': 'Julio Vega',
  'Julio Vega': 'Julio Vega',
  'Oso': 'Julio Vega',
  'Loiselle': 'Louis Loiselle',
  'Louis Loiselle': 'Louis Loiselle',
  'Patterson': 'Hank Patterson',
  'Hank Patterson': 'Hank Patterson',
  'Connolly': 'Peter Connolly',
  'Peter Connolly': 'Peter Connolly',
  'Tomlinson': 'George Tomlinson',
  'George Tomlinson': 'George Tomlinson',
  'Pierce': 'Mike Pierce',
  'Mike Pierce': 'Mike Pierce',
  'Franklin': 'Fred Franklin',
  'Fred Franklin': 'Fred Franklin',
  'Lincoln': 'Steve Lincoln',
  'Steve Lincoln': 'Steve Lincoln',
  'Chin': 'Mike Chin',
  'Mike Chin': 'Mike Chin',
  'Nuncio': 'Angelo Nuncio',
  'Angelo Nuncio': 'Angelo Nuncio',
  'De la Cruz': 'Patricio de la Cruz',
  'Dave Woods': 'Dave Woods',

  // Keluarga & Rekan
  'Sandy': 'Sandy Clark',
  'Sandy Clark': 'Sandy Clark',
  'Patsy': 'Patsy Clark Chavez',
  'Patsy Clark': 'Patsy Clark Chavez',
  'Patsy Chavez': 'Patsy Clark Chavez',

  // FBI & CIA & Intelijen
  'Sullivan': 'Tom Sullivan',
  'Tom Sullivan': 'Tom Sullivan',
  'Chatham': 'Frank Chatham',
  'Frank Chatham': 'Frank Chatham',
  'Werner': 'Gus Werner',
  'Gus Werner': 'Gus Werner',
  'Gus': 'Gus Werner',
  'Dan Murray': 'Dan Murray',
  'Murray': 'Dan Murray',
  'Liz Murray': 'Liz Murray',
  'Foley': 'Ed Foley',
  'Ed Foley': 'Ed Foley',
  'Ed': 'Ed Foley',
  'Mary Pat': 'Mary Pat Foley',
  'Mary Pat Foley': 'Mary Pat Foley',
  'Golovko': 'Sergey Golovko',
  'Sergey Golovko': 'Sergey Golovko',
  'Cyril Holt': 'Cyril Holt',
  'Holt': 'Cyril Holt',

  // The Project / Horizon
  'Popov': 'Dmitriy Popov',
  'Dmitriy Popov': 'Dmitriy Popov',
  'Dimitri': 'Dmitriy Popov',
  'Ilich': 'Dmitriy Popov',
  'Brightling': 'John Brightling',
  'John Brightling': 'John Brightling',
  'Carol': 'Carol Brightling',
  'Carol Brightling': 'Carol Brightling',
  'Killgore': 'Dr. John Killgore',
  'Dokter Killgore': 'Dr. John Killgore',
  'John Killgore': 'Dr. John Killgore',
  'Dr. Killgore': 'Dr. John Killgore',
  'Archer': 'Dr. Barbara Archer',
  'Barbara Archer': 'Dr. Barbara Archer',
  'Dokter Archer': 'Dr. Barbara Archer',
  'Dr. Archer': 'Dr. Barbara Archer',
  'Henriksen': 'Bill Henriksen',
  'Bill Henriksen': 'Bill Henriksen',
  'Hunnicutt': 'Foster Hunnicutt',
  'Foster Hunnicutt': 'Foster Hunnicutt',
  'Foster': 'Foster Hunnicutt',
  'Maclean': 'Kirk Maclean',
  'Kirk Maclean': 'Kirk Maclean',
  'MacLean': 'Kirk Maclean',
  'Kirk MacLean': 'Kirk Maclean',
  'Macleash': 'Kirk Maclean',
  'Kirk': 'Kirk Maclean',
  'Gearing': 'Kolonel Wil Gearing',
  'Wil Gearing': 'Kolonel Wil Gearing',
  'Kolonel Wilson Gearing': 'Kolonel Wil Gearing',
  'Farmer': 'Ben Farmer',
  'Ben Farmer': 'Ben Farmer',
  'Mayflower': 'Kevin Mayflower',
  'Kevin Mayflower': 'Kevin Mayflower',
  'Wilkerson': 'Miles Wilkerson',
  'Miles Wilkerson': 'Miles Wilkerson',
  'Miles': 'Miles Wilkerson',
  'Dawson': 'Dr. Dawson',
  'Mary Bannister': 'Mary Bannister',
  'Mary': 'Mary Bannister',
  'Anne Pretloe': 'Anne Pretloe',

  // Teroris Lapangan & Tokoh Kasus
  'Fiirchtner': 'Hans Fürchtner',
  'Hans Fürchtner': 'Hans Fürchtner',
  'Hans Furchtner': 'Hans Fürchtner',
  'Fürchtner': 'Hans Fürchtner',
  'Petra': 'Petra Dortmund',
  'Petra Dortmund': 'Petra Dortmund',
  'Ostermann': 'Erwin Ostermann',
  'Erwin Ostermann': 'Erwin Ostermann',
  'Erwin': 'Erwin Ostermann',
  'Gerhardt': 'Gerhardt Dengler',
  'Altmark': 'Kapten Peter Altmark',
  'Kapten Altmark': 'Kapten Peter Altmark',
  'René': 'René Montpellier',
  'René Montpellier': 'René Montpellier',
  'André': 'André Herr',
  'André Herr': 'André Herr',
  'Mike Dennis': 'Mike Dennis',
  'Dennis': 'Mike Dennis',
  'Gassman': 'Kapten Gassman',
  'Kapten Gassman': 'Kapten Gassman',
  'Grady': 'Sean Grady',
  'Sean Grady': 'Sean Grady',
  'Sean': 'Sean Grady',
  'O\'Neil': 'Timothy O\'Neil',
  'Timothy O\'Neil': 'Timothy O\'Neil',
  'Timmy O\'Neil': 'Timothy O\'Neil',
  'Timothy': 'Timothy O\'Neil',
  'Timmy': 'Timothy O\'Neil',
  'Roddy Sands': 'Roddy Sands',
  'Chuck Ussery': 'Chuck Ussery',
  'Ussery': 'Chuck Ussery',
  'Pat O\'Connor': 'Pat O\'Connor',
  'O\'Connor': 'Pat O\'Connor',

  // Pemerintahan AS
  'George Winston': 'George Winston',
  'Winston': 'George Winston',
  'Arnie': 'Arnie van Damm',
  'Arnie van Damm': 'Arnie van Damm',
  'Senator Hawking': 'Senator Hawking',
  'Mark Waterhouse': 'Mark Waterhouse',
  'Martin Cooper': 'Martin Cooper',
  'Gordon Sinclair': 'Gordon Sinclair'
};

let matchCount = 0;
let updatedLines = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const m = line.match(/^(\*{0,2})([A-Za-zÀ-ÿ0-9\s.'’\-\/]{2,40})\1:\s*(["“'‘].*)/);
  if (m) {
    const rawSpk = m[2].trim();
    if (speakerMap[rawSpk]) {
      matchCount++;
      if (rawSpk !== speakerMap[rawSpk]) {
        updatedLines++;
      }
    }
  }
}

console.log(`Total dialog match: ${matchCount}`);
console.log(`Total baris dialog yang akan diperbarui nama lengkapnya: ${updatedLines}`);
