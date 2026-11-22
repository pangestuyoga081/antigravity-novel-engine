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
      const cleanText = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      if (cleanText.length > 500) {
        chapters.push({ id: ent.name, chars: cleanText.length, sample: cleanText.substring(0, 70) });
      }
    }
  }
}
scanDir(tempDir);
fs.rmSync(tempDir, { recursive: true, force: true });
chapters.sort((a,b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
console.log('Extracted chapters:', chapters.length);
chapters.forEach(c => console.log(' ', c.id, c.chars, c.sample));
