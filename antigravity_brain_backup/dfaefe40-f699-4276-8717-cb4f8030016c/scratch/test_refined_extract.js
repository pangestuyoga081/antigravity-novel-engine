const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const epubPath = 'd:/JV/novel yoga/The Hobbit - Tolkien, J. R. R._5022.epub';
const tempDir = path.join(path.dirname(epubPath), '.temp_test_extract');
if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
fs.mkdirSync(tempDir, { recursive: true });
execSync(`tar -xf "${epubPath}" -C "${tempDir}"`, { stdio: 'pipe' });

const chapters = [];
function scanDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) scanDir(full);
    else if (/\.(html|xhtml)$/i.test(ent.name)) {
      if (/cover|toc|bookmark|titlepage|copyright/i.test(ent.name)) continue;
      const html = fs.readFileSync(full, 'utf-8');
      let cleanText = html.replace(/<[^>]+>/g, '\n').replace(/\n\s*\n/g, '\n').trim();
      const lines = cleanText.split('\n').map(l => l.trim()).filter(l => Boolean(l) && !/^The\s+Hobbit\s*$/i.test(l));
      const firstRealLine = lines[0] || '';
      if (/^(CONTENTS|TABLE OF CONTENTS|LIST OF ILLUSTRATIONS|NOTE ON THE TEXT|WORKS BY|COPYRIGHT)\b/i.test(firstRealLine)) continue;
      if (cleanText.length > 500) {
        let title = '';
        const chIdx = lines.findIndex(l => /^Chapter\b/i.test(l));
        if (chIdx !== -1) {
          const chNum = lines[chIdx + 1] || '';
          const chName = lines[chIdx + 2] || '';
          title = `Chapter ${chNum}: ${chName}`;
        } else if (/Author[’']s Note/i.test(html) || /languages and letters/i.test(html)) {
          title = "Catatan Penulis (Author's Note: Runes & Languages)";
        } else {
          title = lines.slice(0, 2).join(' - ');
        }
        chapters.push({ id: ent.name, title });
      }
    }
  }
}
scanDir(tempDir);
fs.rmSync(tempDir, { recursive: true, force: true });
chapters.sort((a,b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
console.log('Total valid chapters:', chapters.length);
chapters.forEach((c, i) => console.log(`  [${i+1}] ${c.id}: ${c.title}`));
