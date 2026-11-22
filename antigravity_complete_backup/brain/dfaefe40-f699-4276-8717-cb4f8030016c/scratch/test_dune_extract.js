const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const epubPath = 'd:/JV/novel yoga/1_Dune_-_Frank_Herbert.epub';
const tempDir = path.join(path.dirname(epubPath), '.temp_test_dune');
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
      const cleanText = html.replace(/<[^>]+>/g, '\n').replace(/\n\s*\n/g, '\n').trim();
      const lines = cleanText.split('\n').map(l => l.trim()).filter(Boolean);
      if (cleanText.length > 500) {
        let title = lines.slice(0, 2).join(' - ');
        chapters.push({ id: ent.name, title, chars: cleanText.length });
      }
    }
  }
}
scanDir(tempDir);
fs.rmSync(tempDir, { recursive: true, force: true });
chapters.sort((a,b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
console.log('Total chapters extracted:', chapters.length);
chapters.slice(0, 15).forEach(c => console.log(' ', c.id, c.chars, c.title));
if (chapters.length > 15) {
  console.log(' ... and', chapters.length - 15, 'more');
  chapters.slice(-5).forEach(c => console.log(' ', c.id, c.chars, c.title));
}
