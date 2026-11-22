const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const epubPath = 'd:/JV/novel yoga/1_Dune_-_Frank_Herbert.epub';
const tempDir = path.join(path.dirname(epubPath), '.temp_test_dune_final');
if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
fs.mkdirSync(tempDir, { recursive: true });
execSync(`tar -xf "${epubPath}" -C "${tempDir}"`, { stdio: 'pipe' });

function findOpf(dir) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      const res = findOpf(full);
      if (res) return res;
    } else if (ent.name.endsWith('.opf')) {
      return full;
    }
  }
  return null;
}

const opfFile = findOpf(tempDir);
const spineHrefs = [];
let opfDir = tempDir;

if (opfFile) {
  opfDir = path.dirname(opfFile);
  const opfXml = fs.readFileSync(opfFile, 'utf-8');
  const manifest = {};
  for (const itemTag of opfXml.match(/<item\b[^>]*>/gi) || []) {
    const idM = itemTag.match(/\bid=["']([^"']+)["']/i);
    const hrefM = itemTag.match(/\bhref=["']([^"']+)["']/i);
    if (idM && hrefM) {
      manifest[idM[1]] = hrefM[1];
    }
  }
  const itemrefs = [...opfXml.matchAll(/<itemref\b[^>]*\bidref=["']([^"']+)["']/gi)].map(m => m[1]);
  for (const idref of itemrefs) {
    if (manifest[idref]) spineHrefs.push(manifest[idref]);
  }
}

const chapters = [];
const targetFiles = spineHrefs.map(href => path.resolve(opfDir, href));

for (const full of targetFiles) {
  if (!fs.existsSync(full)) continue;
  const fname = path.basename(full);
  if (/cover|alsobyauthor|copyright|title\.xhtml|dedication|next-reads|nav\.xhtml|frontmatter/i.test(fname)) continue;

  const html = fs.readFileSync(full, 'utf-8');
  let cleanText = html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
    .replace(/<img[^>]+src=['"]([^'"]+)['"][^>]*>/gi, (m, src) => `\n\n[[ILUSTRASI:${path.basename(src)}]]\n\n`)
    .replace(/<h[1-6][^>]*>(.*?)<\/h[1-6]>/gi, '\n\n# $1\n')
    .replace(/<[^>]+>/g, '\n')
    .replace(/\n\s*\n/g, '\n\n')
    .trim();

  if (cleanText.length > 200) {
    const lines = cleanText.split('\n').map(l => l.trim()).filter(l => Boolean(l) && !/^(The\s+Hobbit|Dune)\s*$/i.test(l));
    const firstRealLine = lines[0] || '';
    if (/^(CONTENTS|TABLE OF CONTENTS|LIST OF ILLUSTRATIONS|NOTE ON THE TEXT|WORKS BY|COPYRIGHT|PRAISE FOR)\b/i.test(firstRealLine)) continue;

    let title = '';
    const duneChMatch = firstRealLine.match(/^Chapter\s+([0-9]+)(?:,\s*Dune)?/i);
    if (duneChMatch) {
      title = `Chapter ${duneChMatch[1]}`;
    } else {
      const chIdx = lines.findIndex(l => /^Chapter\b/i.test(l));
      if (chIdx !== -1) {
        const chNum = lines[chIdx + 1] || '';
        const chName = lines[chIdx + 2] || '';
        title = `Chapter ${chNum}: ${chName}`;
      } else if (/Author[’']s Note/i.test(html) || /languages and letters/i.test(html)) {
        title = "Catatan Penulis (Author's Note: Runes & Languages)";
      } else {
        for (const l of lines.slice(0, 5)) {
          const cleanL = l.replace(/^#+\s*/, '').trim();
          if (/^(Chapter|Bab|Part|Book|Appendix)\b/i.test(cleanL)) {
            title = cleanL;
            break;
          }
        }
        if (!title) {
          title = lines.slice(0, 2).map(l => l.replace(/^#+\s*/, '').trim()).join(' - ') || fname;
        }
      }
    }

    chapters.push({
      id: path.basename(full, path.extname(full)),
      title,
      chars: cleanText.length
    });
  }
}

fs.rmSync(tempDir, { recursive: true, force: true });
console.log('Total extracted spine chapters:', chapters.length);
chapters.forEach((c, i) => {
  if (i < 5 || i >= chapters.length - 8) {
    console.log(`  [${i+1}] ${c.id} (${c.chars} chars): ${c.title}`);
  } else if (i === 5) {
    console.log('  ... and Chapter 06 to 48 ...');
  }
});
