const fs = require('fs');

function standardizeNarration(text) {
  // Lindungi nama yang sudah lengkap dengan token sementara agar tidak tertimpa berulang kali
  const placeholders = [];
  function protect(pattern) {
    text = text.replace(pattern, (match) => {
      const id = `__PROTECTED_${placeholders.length}__`;
      placeholders.push({ id, match });
      return id;
    });
  }

  // 1. Lindungi nama-nama yang SUDAH lengkap
  protect(/\bJohn Clark\b/g);
  protect(/\bDing Chavez\b/g);
  protect(/\bDomingo Chavez\b/g);
  protect(/\bSandy Clark\b/g);
  protect(/\bPatsy Clark Chavez\b/g);
  protect(/\bPatsy Clark\b/g);
  protect(/\bPatsy Chavez\b/g);
  protect(/\bAlistair Stanley\b/g);
  protect(/\bAl Stanley\b/g);
  protect(/\bBill Tawney\b/g);
  protect(/\bTim Noonan\b/g);
  protect(/\bDr\. Paul Bellow\b/g);
  protect(/\bDokter Paul Bellow\b/g);
  protect(/\bDaniel Malloy\b/g);
  protect(/\bPeter Covington\b/g);
  protect(/\bEddie Price\b/g);
  protect(/\bHomer Johnston\b/g);
  protect(/\bDieter Weber\b/g);
  protect(/\bJulio Vega\b/g);
  protect(/\bLouis Loiselle\b/g);
  protect(/\bHank Patterson\b/g);
  protect(/\bPeter Connolly\b/g);
  protect(/\bGeorge Tomlinson\b/g);
  protect(/\bMike Pierce\b/g);
  protect(/\bFred Franklin\b/g);
  protect(/\bSteve Lincoln\b/g);
  protect(/\bMike Chin\b/g);
  protect(/\bTom Sullivan\b/g);
  protect(/\bFrank Chatham\b/g);
  protect(/\bGus Werner\b/g);
  protect(/\bDan Murray\b/g);
  protect(/\bEd Foley\b/g);
  protect(/\bMary Pat Foley\b/g);
  protect(/\bSergey Golovko\b/g);
  protect(/\bCyril Holt\b/g);
  protect(/\bGeorge Winston\b/g);
  protect(/\bArnie van Damm\b/g);
  protect(/\bDmitriy Popov\b/g);
  protect(/\bJohn Brightling\b/g);
  protect(/\bCarol Brightling\b/g);
  protect(/\bDr\. John Killgore\b/g);
  protect(/\bDokter John Killgore\b/g);
  protect(/\bDr\. Barbara Archer\b/g);
  protect(/\bDokter Barbara Archer\b/g);
  protect(/\bBill Henriksen\b/g);
  protect(/\bFoster Hunnicutt\b/g);
  protect(/\bKirk Maclean\b/g);
  protect(/\bKolonel Wil Gearing\b/g);
  protect(/\bBen Farmer\b/g);
  protect(/\bKevin Mayflower\b/g);
  protect(/\bMiles Wilkerson\b/g);
  protect(/\bMary Bannister\b/g);
  protect(/\bAnne Pretloe\b/g);
  protect(/\bHans Fürchtner\b/g);
  protect(/\bPetra Dortmund\b/g);
  protect(/\bErwin Ostermann\b/g);
  protect(/\bGerhardt Dengler\b/g);
  protect(/\bKapten Peter Altmark\b/g);
  protect(/\bRené Montpellier\b/g);
  protect(/\bAndré Herr\b/g);
  protect(/\bMike Dennis\b/g);
  protect(/\bKapten Gassman\b/g);
  protect(/\bSean Grady\b/g);
  protect(/\bTimothy O'Neil\b/g);

  // Lindungi juga sapaan hormat khusus
  protect(/\bPak Clark\b/g);
  protect(/\bBu Clark\b/g);
  protect(/\bPapa Bear\b/g);
  protect(/\bPapa Bear George Halas\b/g);
  protect(/\bJohn Wayne\b/g);

  // 2. Sekarang standarisasikan sebutan tunggal/sepotong di narasi menjadi NAMA LENGKAP
  // John Clark: 'Clark' atau 'John' mandiri -> 'John Clark'
  text = text.replace(/\bClark\b/g, 'John Clark');
  // Hati-hati kata 'John' mandiri (karena Killgore dan Brightling sudah dilindungi di step 1)
  text = text.replace(/\bJohn\b/g, 'John Clark');

  // Ding Chavez: 'Chavez' atau 'Ding' atau 'Domingo' mandiri -> 'Ding Chavez'
  text = text.replace(/\bChavez\b/g, 'Ding Chavez');
  text = text.replace(/\bDing\b/g, 'Ding Chavez');
  text = text.replace(/\bDomingo\b/g, 'Ding Chavez');

  // Alistair Stanley: 'Stanley' atau 'Alistair' mandiri -> 'Alistair Stanley'
  text = text.replace(/\bStanley\b/g, 'Alistair Stanley');
  text = text.replace(/\bAlistair\b/g, 'Alistair Stanley');

  // Dmitriy Popov: 'Popov' atau 'Dmitriy' atau 'Dimitri' mandiri -> 'Dmitriy Popov'
  text = text.replace(/\bPopov\b/g, 'Dmitriy Popov');
  text = text.replace(/\bDmitriy\b/g, 'Dmitriy Popov');
  text = text.replace(/\bDimitri\b/g, 'Dmitriy Popov');

  // John Brightling: 'Brightling' mandiri -> 'John Brightling'
  text = text.replace(/\bBrightling\b/g, 'John Brightling');

  // Killgore: 'Killgore' mandiri -> 'Dr. John Killgore'
  text = text.replace(/\bKillgore\b/g, 'Dr. John Killgore');
  text = text.replace(/\bDokter Dr\. John Killgore\b/g, 'Dr. John Killgore');

  // Archer: 'Archer' mandiri -> 'Dr. Barbara Archer'
  text = text.replace(/\bArcher\b/g, 'Dr. Barbara Archer');
  text = text.replace(/\bDokter Dr\. Barbara Archer\b/g, 'Dr. Barbara Archer');

  // Bellow: 'Bellow' mandiri -> 'Dr. Paul Bellow'
  text = text.replace(/\bBellow\b/g, 'Dr. Paul Bellow');
  text = text.replace(/\bDokter Dr\. Paul Bellow\b/g, 'Dr. Paul Bellow');

  // Henriksen: 'Henriksen' mandiri -> 'Bill Henriksen'
  text = text.replace(/\bHenriksen\b/g, 'Bill Henriksen');

  // Noonan: 'Noonan' mandiri -> 'Tim Noonan'
  text = text.replace(/\bNoonan\b/g, 'Tim Noonan');

  // Malloy: 'Malloy' mandiri -> 'Daniel Malloy'
  text = text.replace(/\bMalloy\b/g, 'Daniel Malloy');

  // Price: 'Price' mandiri -> 'Eddie Price'
  text = text.replace(/\bPrice\b/g, 'Eddie Price');

  // Johnston: 'Johnston' mandiri -> 'Homer Johnston'
  text = text.replace(/\bJohnston\b/g, 'Homer Johnston');

  // Weber: 'Weber' mandiri -> 'Dieter Weber'
  text = text.replace(/\bWeber\b/g, 'Dieter Weber');

  // Vega: 'Vega' mandiri -> 'Julio Vega'
  text = text.replace(/\bVega\b/g, 'Julio Vega');

  // Loiselle: 'Loiselle' mandiri -> 'Louis Loiselle'
  text = text.replace(/\bLoiselle\b/g, 'Louis Loiselle');

  // Patterson: 'Patterson' mandiri -> 'Hank Patterson'
  text = text.replace(/\bPatterson\b/g, 'Hank Patterson');

  // Connolly: 'Connolly' mandiri -> 'Peter Connolly'
  text = text.replace(/\bConnolly\b/g, 'Peter Connolly');

  // Tomlinson: 'Tomlinson' mandiri -> 'George Tomlinson'
  text = text.replace(/\bTomlinson\b/g, 'George Tomlinson');

  // Hunnicutt: 'Hunnicutt' mandiri -> 'Foster Hunnicutt'
  text = text.replace(/\bHunnicutt\b/g, 'Foster Hunnicutt');

  // Maclean: 'Maclean' mandiri -> 'Kirk Maclean'
  text = text.replace(/\bMaclean\b/g, 'Kirk Maclean');

  // Gearing: 'Gearing' mandiri -> 'Kolonel Wil Gearing'
  text = text.replace(/\bGearing\b/g, 'Kolonel Wil Gearing');

  // Fürchtner: 'Fürchtner' mandiri -> 'Hans Fürchtner'
  text = text.replace(/\bFürchtner\b/g, 'Hans Fürchtner');

  // Dortmund: 'Dortmund' mandiri -> 'Petra Dortmund'
  text = text.replace(/\bDortmund\b/g, 'Petra Dortmund');

  // Ostermann: 'Ostermann' mandiri -> 'Erwin Ostermann'
  text = text.replace(/\bOstermann\b/g, 'Erwin Ostermann');

  // Grady: 'Grady' mandiri -> 'Sean Grady'
  text = text.replace(/\bGrady\b/g, 'Sean Grady');

  // O'Neil: 'O\'Neil' mandiri -> 'Timothy O\'Neil'
  text = text.replace(/\bO'Neil\b/g, 'Timothy O\'Neil');

  // Sullivan: 'Sullivan' mandiri -> 'Tom Sullivan'
  text = text.replace(/\bSullivan\b/g, 'Tom Sullivan');

  // Chatham: 'Chatham' mandiri -> 'Frank Chatham'
  text = text.replace(/\bChatham\b/g, 'Frank Chatham');

  // Werner: 'Werner' mandiri -> 'Gus Werner'
  text = text.replace(/\bWerner\b/g, 'Gus Werner');

  // Murray: 'Murray' mandiri -> 'Dan Murray'
  text = text.replace(/\bMurray\b/g, 'Dan Murray');

  // Foley: 'Foley' mandiri -> 'Ed Foley'
  text = text.replace(/\bFoley\b/g, 'Ed Foley');

  // Altmark: 'Altmark' mandiri -> 'Kapten Peter Altmark'
  text = text.replace(/\bAltmark\b/g, 'Kapten Peter Altmark');

  // Tawney: 'Tawney' mandiri -> 'Bill Tawney'
  text = text.replace(/\bTawney\b/g, 'Bill Tawney');

  // Covington: 'Covington' mandiri -> 'Peter Covington'
  text = text.replace(/\bCovington\b/g, 'Peter Covington');

  // Sandy: 'Sandy' mandiri -> 'Sandy Clark'
  text = text.replace(/\bSandy\b/g, 'Sandy Clark');

  // Patsy: 'Patsy' mandiri -> 'Patsy Clark Chavez'
  text = text.replace(/\bPatsy\b/g, 'Patsy Clark Chavez');

  // 3. Kembalikan semua teks yang dilindungi
  for (let i = placeholders.length - 1; i >= 0; i--) {
    const p = placeholders[i];
    text = text.replace(p.id, p.match);
  }

  // Bersihkan potensi duplikasi jika ada yang terlewat
  text = text.replace(/\bJohn John Clark\b/g, 'John Clark');
  text = text.replace(/\bJohn Clark John Clark\b/g, 'John Clark');
  text = text.replace(/\bDing Ding Chavez\b/g, 'Ding Chavez');
  text = text.replace(/\bDing Chavez Ding Chavez\b/g, 'Ding Chavez');
  text = text.replace(/\bSandy Sandy Clark\b/g, 'Sandy Clark');

  return text;
}

// Uji pada snippet user
const snippet = `Sandy terkekeh lalu balik fokus ke bukunya, berbarengan sama pramugari yang kembali mondar-mandir nawarin minuman. Clark beres baca *The Economist* lalu ganti ke majalah *Sports Illustrated*. Sialan, dia bakal ngelewatin babak penutup musim *football*. Olahraga itu selalu dia pantau seumur hidupnya, bahkan pas lagi tugas operasi tempur. Tim Bears lagi gila-gilaan bangkitnya. Dia tumbuh besar di era Papa Bear George Halas dan julukan "Monsters of the Midway", bahkan sering ngayal bisa jadi atlet pro. Pas SMA dia lumayan jago jadi *linebacker*, dan Universitas Indiana sempet naksir berat sama dia (ditambah kemampuan renangnya yang hebat). Tapi akhirnya dia milih bodo amat sama kuliah dan gabung Angkatan Laut kayak bapaknya dulu. Bedanya, dia tembus Navy SEAL, bukan terombang-ambing di laut kayak sarden dalam kaleng kayak bapaknya...

Pramugari nyamperin bawa buku menu makan malam.

Pramugari: "Pak Clark?"

Pramugari: "Bu Clark?"

Enaknya kelas satu tuh begini. Kru kabin beneran hafal nama lu. John ngerasa ada peningkatan signifikan di penerbangan sekarang. Dia udah terbang jutaan mil bareng maskapai lain, tapi belakangan cuma terbang bareng British Airways yang dapet kontrak gede dari pemerintah Inggris.`;

console.log('HASIL UJI NORMALISASI CERDAS SNIPPET:');
console.log(standardizeNarration(snippet));
