const fs = require('fs');

const content = fs.readFileSync('D:/JV/novel yoga/Tom Clancy - 09. Rainbow six - vol. 1+2 (Terjemahan ID-Direct).txt', 'utf8');

const checks = [
  'Fiirchtner', 'Furchtner', 'Fürchtner',
  'Macleash', 'Maclean', 'MacLean',
  'Alistar', 'Alistair',
  'Dimitri', 'Dmitriy',
  'Wil Gearing', 'Wilson Gearing',
  'Baur', 'Bauer',
  'Ostermann', 'Dengler', 'Altmark',
  'Dortmund', 'Montpellier', 'Gassman',
  'Killgore', 'Archer', 'Henriksen', 'Brightling',
  'Hunnicutt', 'O\'Neil', 'Grady',
  'Chavez', 'Clark', 'Stanley', 'Noonan', 'Bellow',
  'Malloy', 'Johnston', 'Weber', 'Price', 'Pierce',
  'Vega', 'Loiselle', 'Connolly', 'Patterson'
];

for (const c of checks) {
  const reg = new RegExp(c, 'g');
  const count = (content.match(reg) || []).length;
  console.log(`${c.padEnd(16)}: ${count}`);
}
