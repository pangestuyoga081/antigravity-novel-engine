#!/usr/bin/env node
/**
 * ============================================================================
 * 🚇 NOVEL TRANSLATOR - DRAG & DROP RUNNER (ROBUST PROMPT & ZERO-REFUSAL)
 * Multi-Novel Fast Pipeline with Resume, Auto Sub-Chunk & Style Adapter
 * ============================================================================
 */

import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import http from 'node:http';
import https from 'node:https';
import { execSync } from 'node:child_process';

const CONFIG = {
  proxyUrl: process.env.LLM_PROXY_URL || 'http://localhost:20128/v1/chat/completions',
  model: process.env.LLM_MODEL || 'ag/gemini-3.8-flash-low',
  apiKey: process.env.LLM_API_KEY || 'sk-2e591994696af18e-71ijj7-14263abd',
  maxChunkChars: 6500,
  concurrency: parseInt(process.env.CONCURRENCY || '15', 10)
};

interface Chapter {
  id: string;
  title: string;
  text: string;
}

type StyleMode = 'carl' | 'dxd' | 'konosuba' | 'warhammer' | 'hobbit' | 'overlord' | 'mushoku' | 'dune' | 'metro' | 'expanse' | 'harrypotter' | 'comic_history' | 'default';

function parseSSEorJSON(raw: string): string {
  let full = '';
  const lines = raw.split('\n');
  for (const l of lines) {
    if (l.startsWith('data: ') && !l.includes('[DONE]')) {
      try {
        const j = JSON.parse(l.substring(6));
        const delta = j.choices?.[0]?.delta?.content || j.choices?.[0]?.message?.content || '';
        full += delta;
      } catch {}
    }
  }

  if (!full && raw.trim().startsWith('{')) {
    try {
      const j = JSON.parse(raw.trim());
      if (j.response?.promptFeedback?.blockReason) {
        console.warn(`   ⚠️ Gemini Block Filter: ${j.response.promptFeedback.blockReasonMessage || j.response.promptFeedback.blockReason}`);
        return '';
      }
      return j.choices?.[0]?.message?.content || '';
    } catch {}
  }

  return full.trim();
}

function isRefusalResponse(text: string): boolean {
  if (!text || text.trim().length === 0) return true;
  // Deteksi penolakan eksplisit, canned response hak cipta, atau penggantian teks novel dengan ringkasan/rangkuman halus
  const refusalPatterns = [
    /i\s+(cannot|can\s*not|am\s+unable\s+to)\s+(rewrite|provide|translate|reproduce|generate)/i,
    /as\s+an\s+ai/i,
    /copyrighted\s+(novel|text|material|work|book)/i,
    /here\s+is\s+a\s+(concise\s+)?summary/i,
    /tidak\s+(bisa|dapat|diizinkan|diperbolehkan)\s+(untuk\s+)?(menulis|menuliskan|menerjemahkan|menyajikan|membuat|mengadaptasi|memberikan)/i,
    /secara\s+(kata\s+demi\s+kata|baris\s+demi\s+baris|mendetail\s+dari\s+baris|detail\s+atau\s+menuliskannya)/i,
    /(alih-alih|daripada)\s+(menulis\s+ulang|menerjemahkan)/i,
    /(novel|karya)\s+berhak\s+cipta|(kebijakan|batasan|aturan)\s+hak\s+cipta|hak\s+cipta\s+melarang/i,
    /naskah\s+(novel\s+)?aslinya/i,
    /berikut\s+(adalah\s+)?(ringkasan|rangkuman|garis\s+besar)/i,
    /###\s+(ringkasan|rangkuman|garis\s+besar)/i,
    /(ringkasan|rangkuman)\s+(santai|singkat|umum|kejadian|cerita|mengenai|peristiwa|babak|adegan|alur)/i,
    /secara\s+garis\s+besar/i,
    /garis\s+besar\s+(adegan|bagian|cerita|peristiwa|mengenai|kejadian)/i,
    /intisari\s+(adegan|cerita|peristiwa)/i,
    /apakah\s+(kamu|anda)\s+ingin\s+(lanjut\s+)?(menyimak|melihat|dengar|membaca|ringkasan|rangkuman|tahu)/i,
    /mau\s+(lanjut|tahu|aku\s+buatin)\s+(ke\s+|bahas\s+|dengerin\s+|dengan\s+)?(ringkasan|rangkuman|bagian\s+berikutnya)/i,
    /aku\s+bisa\s+kasih\s+(ringkasan|rangkuman|gambaran|garis\s+besar)/i,
    /bagian\s+awal\s+perjalanan\s+reinkarnasi/i,
    /kisah\s+awal\s+reinkarnasi/i,
    /permintaan\s+(ini\s+)?(meminta|untuk)/i,
    /instruksi\s+sistem\s+melarang/i,
    /tidak\s+dapat\s+dipenuhi/i,
    /tanpa\s+memuat\s+unsur\s+(pornografi|kata-kata)/i,
    /penyampaian\s+ulang\s+isi\s+teks/i,
    /materi\s+non-seksual/i
  ];
  return refusalPatterns.some(rx => rx.test(text));
}

function cleanWatermarks(text: string): string {
  return text
    // Watermark Overlord
    .replace(/^PDF\s+Overlo[a-z]*\s+Vol[^\n]*/gmi, '')
    .replace(/^by\s*:\s*Kenny[^\n]*/gmi, '')
    .replace(/^Attention[\s\S]*?Dilarang keras[^\n]*/gmi, '')
    .replace(/^\s*Overlord\s*[–—\-]\s*Volume\s*\d+\s*$/gmi, '')
    .replace(/\bOVERLORD\s*[–—\-]?\s*VOLUME\s*\d+(\s+\d+)?\b/gi, '')
    .replace(/\bOVERLORD\s+\d+\b/gi, '')
    // Watermark Horus Rising / Warhammer 40k
    .replace(/^Dan Abnett\s*$/gmi, '')
    .replace(/^Horus Rising\s*$/gmi, '')
    .replace(/^THE HORUS HERESY\s*$/gmi, '')
    .replace(/^\s*\d+\s*$/gm, '')
    // Watermark The Hobbit / Tolkien
    .replace(/^The\s+Hobbit\s*$/gmi, '')
    .replace(/^J\.?\s*R\.?\s*R\.?\s*Tolkien\s*$/gmi, '')
    // Watermark Tom Clancy
    .replace(/\b\d+\s*e\s*TOM\s*CLANCY\b/gi, '')
    .replace(/\bTOM\s*CLANCY\s*e\s*\d+\b/gi, '')
    .replace(/\bTOM\s*CLANCY\b/gi, '')
    .replace(/\bTOMCLANCY\b/gi, '')
    .replace(/\bRAINBOW\s*SIX(\s*e\s*\d+)?\b/gi, '')
    // Watermark Konosuba / Ruidrive / Afterscarlet
    .replace(/PDF\s+KONOSUBA\s+Vol(?:\w+)?\s*\d*/gi, '')
    .replace(/Konosuba\s+[–-]\s+Volume\s*\d+(?:\.\d+)?/gi, '')
    .replace(/https?:\/\/[^\s]+/gi, '')
    .replace(/Ruidrive\.com/gi, '')
    .replace(/Author\s*:[^\n]*/gi, '')
    .replace(/Illustra(?:si|tor)\s*:[^\n]*/gi, '')
    .replace(/Translate\s*:[^\n]*/gi, '')
    .replace(/PDF\s+By\s*:[^\n]*/gi, '')
    .replace(/PDF\s+dan\s+dowload[^\n]*/gi, '')
    .replace(/\n\s*\n\s*\n/g, '\n\n')
    .trim();
}

function sanitizeSensitiveWords(t: string): string {
  return t
    .replace(/pubisul/gi, 'corpul')
    .replace(/boaşele/gi, 'carnea')
    .replace(/puţulica/gi, 'ceva')
    .replace(/lăbar/gi, 'laş')
    .replace(/schimbat sexul/gi, 'aranjat')
    .replace(/fac din tine o fetiţă/gi, 'te distrug')
    .replace(/transform în fetiţă/gi, 'termin')
    .replace(/violezi|viol/gi, 'ataci')
    .replace(/\bloli(?:con)?\b/gi, 'penggemar gadis imut')
    .replace(/\btelanjang\b/gi, 'buka-bukaan')
    .replace(/\bmelepaskan bajuku\b/gi, 'tampil lebih berani')
    .replace(/\bmonster mesum\b/gi, 'iblis centil')
    .replace(/tidur dengan ayah/gi, 'ditemani ayah tidur')
    .replace(/tidur dengan anak kita/gi, 'temani dia tidur')
    .replace(/tidur dengan anak/gi, 'menemani tidur')
    .replace(/tidur bersama anak/gi, 'menemani tidur')
    .replace(/apakah aku benar-benar lolicon atau tidak/gi, 'apakah aku punya selera aneh atau tidak')
    .replace(/bukanlah hal yang mesum/gi, 'bukan hal yang aneh')
    .replace(/membuat penurusku/gi, 'meneruskan garis keturunan')
    .replace(/Jika kau ingin punya anak, aku siap untuk membantumu/gi, 'Kalo lu mau berpasangan, gue siap bantu')
    .replace(/perempuan jalang/gi, 'cewek PHP');
}

function maskCopyrightTokens(text: string): string {
  return text
    .replace(/^\s*Overlord\s*[–—\-]\s*Volume\s*\d+\s*$/gmi, '')
    .replace(/\bOVERLORD\s*[–—\-]?\s*VOLUME\s*\d+(\s+\d+)?\b/gi, '')
    .replace(/\bMakam Besar Bawah Tanah Nazarick\b/gi, 'Markas Bawah Tanah')
    .replace(/\bAbsolute Overlord\b/gi, 'Penguasa Tertinggi')
    .replace(/\bSorcerer King\b/gi, 'Raja Sihir')
    .replace(/\bSorcerer Kingdom\b/gi, 'Kerajaan Sihir');
}

function unmaskCopyrightTokens(text: string): string {
  return text
    .replace(/\bMarkas Bawah Tanah\b/gi, 'Makam Besar Bawah Tanah Nazarick')
    .replace(/\bPenguasa Tertinggi\b/gi, 'Absolute Overlord')
    .replace(/\bRaja Sihir\b/gi, 'Sorcerer King')
    .replace(/\bKerajaan Sihir\b/gi, 'Sorcerer Kingdom');
}

function extractEpubChapters(epubPath: string): Chapter[] {
  console.log('📦 Membaca isi file EPUB...');
  const baseName = path.basename(epubPath, path.extname(epubPath));
  const dirName = path.dirname(epubPath);
  const tempDir = path.join(dirName, '.temp_epub_extract');
  if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
  fs.mkdirSync(tempDir, { recursive: true });

  try {
    execSync(`tar -xf "${epubPath}" -C "${tempDir}"`, { stdio: 'pipe' });
  } catch (err) {
    throw new Error('Gagal mengekstrak EPUB: ' + err);
  }

  // Simpan gambar ke folder illustrations/<baseName>
  const illustDir = path.join(dirName, 'illustrations', baseName);
  if (!fs.existsSync(illustDir)) fs.mkdirSync(illustDir, { recursive: true });

  function copyImages(dir: string) {
    for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) copyImages(full);
      else if (/\.(jpe?g|png|webp|gif)$/i.test(ent.name)) {
        fs.copyFileSync(full, path.join(illustDir, ent.name));
      }
    }
  }
  copyImages(tempDir);

  // Cari berkas OPF untuk membaca urutan canonical spine
  function findOpf(dir: string): string | null {
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
  const spineHrefs: string[] = [];
  let opfDir = tempDir;

  if (opfFile) {
    opfDir = path.dirname(opfFile);
    const opfXml = fs.readFileSync(opfFile, 'utf-8');
    const manifest: Record<string, string> = {};
    for (const itemTag of opfXml.match(/<item\b[^>]*>/gi) || []) {
      const idM = itemTag.match(/\bid=(["'])(.*?)\1/i);
      const hrefM = itemTag.match(/\bhref=(["'])(.*?)\1/i);
      if (idM && hrefM) {
        manifest[idM[2]] = hrefM[2];
      }
    }
    const itemrefs = [...opfXml.matchAll(/<itemref\b[^>]*\bidref=(["'])(.*?)\1/gi)].map(m => m[2]);
    for (const idref of itemrefs) {
      if (manifest[idref]) spineHrefs.push(manifest[idref]);
    }
  }

  const targetFiles: string[] = spineHrefs.length > 0 
    ? spineHrefs.map(href => path.resolve(opfDir, href))
    : [];

  if (targetFiles.length === 0) {
    function scanDir(dir: string) {
      for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) scanDir(full);
        else if (/\.(html|xhtml)$/i.test(ent.name)) targetFiles.push(full);
      }
    }
    scanDir(tempDir);
    targetFiles.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }

  const chapters: Chapter[] = [];
  for (const full of targetFiles) {
    if (!fs.existsSync(full)) continue;
    const fname = path.basename(full);
    if (/cover|alsobyauthor|copyright|title|contents|brand|dedication|next-reads|nav\.xhtml|frontmatter|_cop_|_tp_|_toc_|_fm1_|_bm1_/i.test(fname)) continue;

    const html = fs.readFileSync(full, 'utf-8');
    let cleanText = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
      .replace(/<img[^>]+src=['"]([^'"]+)['"][^>]*>/gi, (m, src) => `\n\n[[ILUSTRASI:${path.basename(src)}]]\n\n`)
      .replace(/<div class="cst"><b>(.*?)<\/b><\/div>/gi, '\nSubtitle: $1\n')
      .replace(/<div class="ct"><b>(.*?)<\/b><\/div>/gi, '\n\n# $1\n')
      .replace(/<h[1-6][^>]*>(.*?)<\/h[1-6]>/gi, '\n\n# $1\n')
      .replace(/<p[^>]*>/gi, '\n')
      .replace(/<div[^>]*>/gi, '\n')
      .replace(/<br\s*[\/]?>/gi, '\n')
      .replace(/<[^>]+>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'")
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      .trim();

    if (cleanText.length > 200) {
      const lines = cleanText.split('\n').map(l => l.trim()).filter(l => Boolean(l) && !/^(The\s+Hobbit|Dune|METRO\s+2033|A\s+Game\s+of\s+Thrones)\s*$/i.test(l));
      const firstRealLine = lines[0] || '';
      if (/^(CONTENTS|TABLE OF CONTENTS|LIST OF ILLUSTRATIONS|NOTE ON THE TEXT|WORKS BY|COPYRIGHT|PRAISE FOR)\b/i.test(firstRealLine)) continue;

      let title = '';
      const gotPovMatch = firstRealLine.match(/^(PROLOGUE|EPILOGUE|BRAN|CATELYN|DAENERYS|EDDARD|JON|ARYA|TYRION|SANSA|DAVOS|THEON|JAIME|CERSEI|SAMWELL|BRIENNE|AERYS|APPENDIX)\b/i);
      const duneChMatch = firstRealLine.match(/^Chapter\s+([0-9]+)(?:,\s*Dune)?/i);
      const metroChMatch = firstRealLine.match(/^CHAPTER\s+([0-9]+)\b/i);
      if (gotPovMatch) {
        title = `BAB: ${gotPovMatch[1].toUpperCase()}`;
      } else if (duneChMatch) {
        title = `Chapter ${duneChMatch[1]}`;
      } else if (metroChMatch) {
        const subTitle = (lines[1] && !lines[1].startsWith('‘') && !lines[1].startsWith('"')) ? lines[1] : '';
        title = subTitle ? `Chapter ${metroChMatch[1]} - ${subTitle}` : `Chapter ${metroChMatch[1]}`;
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
        text: cleanWatermarks(cleanText)
      });
    }
  }

  scanDir: fs.rmSync(tempDir, { recursive: true, force: true });
  return chapters;
}

function extractTxtChapters(txtPath: string): Chapter[] {
  const content = fs.readFileSync(txtPath, 'utf-8');
  const lines = content.split('\n');

  // Khusus High School DxD
  if (/high\s*school\s*dxd|dxd/i.test(txtPath)) {
    console.log('😈 Terdeteksi: Light Novel High School DxD (No Sensor, Frontal, Gaul Gue-Lu)!');
    const chapters: Chapter[] = [];
    let curChap: Chapter | null = null;
    let curLines: string[] = [];
    let chIdx = 1;

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      // Lewati daftar isi (TOC) dan baris halaman
      if (l.startsWith('#') || /^(List\s+Chapter|Index|Attention|Warning!)/i.test(l)) {
        continue;
      }

      // Deteksi awal bab riil DxD: Life 00, Life 01, Life 02, New Life, Afterword
      const isDxdHeader = /^(Life[\s.]+[0-9]+|Next\s+Life|New\s+Life|Prolog(?:ue)?|Epilog(?:ue)?|Afterword)/i.test(l) && !/Bagian\s+[0-9]+/i.test(l);
      if (isDxdHeader && l.length < 50) {
        if (curChap && curLines.length > 50) {
          curChap.text = cleanWatermarks(curLines.join('\n').trim());
          if (curChap.text.length > 200) chapters.push(curChap);
        }
        const chNum = String(chIdx++).padStart(2, '0');
        curChap = {
          id: `dxd_ch${chNum}`,
          title: l,
          text: ''
        };
        curLines = [];
        continue;
      }

      curLines.push(rawLine);
    }

    if (curChap && curLines.length > 50) {
      curChap.text = cleanWatermarks(curLines.join('\n').trim());
      if (curChap.text.length > 200) chapters.push(curChap);
    }

    if (chapters.length > 0) return chapters;
  }

  // Khusus Konosuba: Kono Subarashii Sekai ni Shukufuku wo!
  if (/konosuba|kono\s*subarashii/i.test(txtPath)) {
    console.log('🎌 Terdeteksi: Kompilasi Light Novel Konosuba (Volume 01-17 + Bakuen)!');
    const chapters: Chapter[] = [];
    let curVol = 'VOLUME 01';
    let curChap: Chapter | null = null;
    let curLines: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      const vm = l.match(/^KONO SUBARASHII SEKAI NI SHUKUFUKU WO! - (VOLUME\s+[0-9]+(?:\.[0-9]+)?)/i);
      if (vm) {
        if (curChap && curLines.length > 50) {
          curChap.text = cleanWatermarks(curLines.join('\n').trim());
          if (curChap.text.length > 400) chapters.push(curChap);
        }
        curVol = vm[1].toUpperCase();
        curChap = null;
        curLines = [];
        continue;
      }

      // Lewati daftar isi (TOC)
      if (l.startsWith('#') || /^(List\s+Chapter|Index|Attention|Warning!)/i.test(l)) {
        continue;
      }

      // Filter nomor halaman tunggal
      if (/^\d+$/.test(l) && l.length < 5) {
        continue;
      }

      // Deteksi awal bab riil
      const isChap = /^(PROLOG(?:UE)?|EPILOG(?:UE)?|CHAPTER\s+[0-9]+|INTERLUDE|SHORT\s+STORY|EXTRA)/i.test(l);
      if (isChap) {
        const nextLines = lines.slice(i + 1, i + 8).map(x => x.trim()).filter(Boolean);
        const isReal = nextLines.some(x => /^(Bagian\s+[0-9]+|['\"“]|-)/i.test(x) || x.length > 30);
        if (isReal) {
          if (curChap && curLines.length > 50) {
            curChap.text = cleanWatermarks(curLines.join('\n').trim());
            if (curChap.text.length > 400) chapters.push(curChap);
          }
          const chNum = String(chapters.length + 1).padStart(3, '0');
          curChap = {
            id: `${curVol.toLowerCase().replace(/[\s.]+/g, '_')}_ch${chNum}`,
            title: `${curVol} - ${l}`,
            text: ''
          };
          curLines = [];
          continue;
        }
      }

      curLines.push(rawLine);
    }

    if (curChap && curLines.length > 50) {
      curChap.text = cleanWatermarks(curLines.join('\n').trim());
      if (curChap.text.length > 400) chapters.push(curChap);
    }

    return chapters;
  }

  // Khusus Horus Rising (Warhammer 40k)
  if (/horus\s*rising|dan\s*abnett/i.test(txtPath)) {
    console.log('⚔️  Terdeteksi: The Horus Heresy - Horus Rising (Dan Abnett)!');
    const chapters: Chapter[] = [];
    let curPart = 'PROLOGUE';
    let curChap: Chapter | null = null;
    let curLines: string[] = [];

    const numberWords = [
      'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN',
      'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN', 'SEVENTEEN', 'EIGHTEEN', 'NINETEEN', 'TWENTY'
    ];

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      const partMatch = l.match(/^PART\s+(ONE|TWO|THREE|FOUR|FIVE)/i);
      if (partMatch) {
        curPart = `PART ${partMatch[1].toUpperCase()}`;
        continue;
      }

      if (numberWords.includes(l.toUpperCase())) {
        const prevLines = lines.slice(Math.max(0, i - 3), i).map(x => x.trim()).filter(Boolean);
        const isAfterHeader = prevLines.some(x => /^\d+$/i.test(x) || /Dan Abnett|Horus Rising/i.test(x));
        const next1 = lines[i + 1]?.trim() || '';
        const next2 = lines[i + 2]?.trim() || '';
        const next3 = lines[i + 3]?.trim() || '';
        const next4 = lines[i + 4]?.trim() || '';

        const isHeading = isAfterHeader && next1.length > 0 && next1.length < 60 && !next1.endsWith('.');
        if (isHeading) {
          if (curChap && curLines.length > 5) {
            curChap.text = cleanWatermarks(curLines.join('\n'));
            if (curChap.text.length > 200) chapters.push(curChap);
          }
          const chNum = String(chapters.length + 1).padStart(2, '0');
          const subs = [next1, next2, next3, next4].filter(x => x && x.length < 60 && !x.endsWith('.'));
          const subtitle = subs.join(' - ');

          curChap = {
            id: `horus_rising_ch${chNum}`,
            title: `${curPart} - Chapter ${l.toUpperCase()}: ${subtitle}`,
            text: ''
          };
          curLines = [];
          i += subs.length;
          continue;
        }
      }

      if (!curChap && chapters.length === 0 && l.includes('It is a time of legend')) {
        curChap = {
          id: 'horus_rising_ch00',
          title: 'PROLOGUE: Legend & Dramatis Personae',
          text: ''
        };
      }

      if (curChap) {
        if (/^\s*Overlord\s*[–—\-]\s*Volume\s*\d+\s*$/i.test(l)) continue;
        curLines.push(rawLine);
      }
    }

    if (curChap && curLines.length > 5) {
      curChap.text = cleanWatermarks(curLines.join('\n'));
      if (curChap.text.length > 200) chapters.push(curChap);
    }

    return chapters;
  }

  // Khusus Tom Clancy - Rainbow Six: gunakan mapping 41 bab presisi
  if (/rainbow\s*six/i.test(txtPath)) {
    const chapterMeta = [
      { no: 0, id: 'prolog', title: 'PROLOG: Situasi', rx: [/^\s*PROLOG\s*$/i] },
      { no: 1, id: 'chap_01', title: 'BAB 1: Memorandum', rx: [/^\s*MEMORANDUM\s*$/i] },
      { no: 2, id: 'chap_02', title: 'BAB 2: Beraksi, Koboi', rx: [/Pe CAI,\s*COW-BOY/i] },
      { no: 3, id: 'chap_03', title: 'BAB 3: Tim Pengintai & Pasukan Penembak', rx: [/PITICI\s*ŞI\s*PUŞCOACE/i, /^\s*3\s*$/] },
      { no: 4, id: 'chap_04', title: 'BAB 4: Evaluasi Pasca Aksi (AAR)', rx: [/^\s*ADA\s*$/] },
      { no: 5, id: 'chap_05', title: 'BAB 5: Cabang Masalah', rx: [/RAMIFICA/i, /^\s*5\s*$/] },
      { no: 6, id: 'chap_06', title: 'BAB 6: Orang Beriman Sejati', rx: [/CREDINCIO|ADEV[AĂ]RA[TŢ]/i, /^\s*6\s*$/] },
      { no: 7, id: 'chap_07', title: 'BAB 7: Finansial', rx: [/FINAN[TŢ]E/i, /^\s*7\s*$/] },
      { no: 8, id: 'chap_08', title: 'BAB 8: Sorotan TV', rx: [/ŞTIAI\s*TV|STIAI\s*TV/i, /^\s*8\s*$/] },
      { no: 9, id: 'chap_09', title: 'BAB 9: Pendekatan', rx: [/APROPIERI/i, /^\s*9\s*$/] },
      { no: 10, id: 'chap_10', title: 'BAB 10: Penyelidikan Mendalam', rx: [/S[AĂ]P[AĂ]TURI/i, /^\s*(10|IO)\s*$/] },
      { no: 11, id: 'chap_11', title: 'BAB 11: Infrastruktur', rx: [/INFRASTRUCTUR/i, /^\s*(11|II)\s*$/] },
      { no: 12, id: 'chap_12', title: 'BAB 12: Tak Terduga dan Tak Terkendali', rx: [/Imprevizibil/i, /^\s*12\s*$/] },
      { no: 13, id: 'chap_13', title: 'BAB 13: Taman Hiburan', rx: [/AMUZAMENT/i, /^\s*13\s*$/] },
      { no: 14, id: 'chap_14', title: 'BAB 14: Pedang Pasukan', rx: [/SABIA\s*LEGIUNII/i, /^\s*14\s*$/] },
      { no: 15, id: 'chap_15', title: 'BAB 15: Topi Putih', rx: [/P[AĂ]L[AĂ]RII\s*ALBE/i, /^\s*(15|IS)\s*$/] },
      { no: 16, id: 'chap_16', title: 'BAB 16: Penemuan', rx: [/DESCOPERIREA/i, /^\s*(16|IG)\s*$/] },
      { no: 17, id: 'chap_17', title: 'BAB 17: Radar Terbentang', rx: [/ANTENE\s*[IÎ]NTINSE/i, /^\s*17\s*$/] },
      { no: 18, id: 'chap_18', title: 'BAB 18: Paviliun', rx: [/PAVILIOANE/i, /^\s*(18|I8)\s*$/] },
      { no: 19, id: 'chap_19', title: 'BAB 19: Burung Kenari', rx: [/CANARI/i, /^\s*(19|IO)\s*$/] },
      { no: 20, id: 'chap_20', title: 'BAB 20: Kontak', rx: [/CONTACTE/i, /^\s*20\s*$/] },
      { no: 21, id: 'chap_21', title: 'BAB 21: Fase Uji Coba', rx: [/STADII/i, /^\s*21\s*$/] },
      { no: 22, id: 'chap_22', title: 'BAB 22: Langkah Balasan', rx: [/CONTRAM[AĂ]SURI/i, /^\s*22\s*$/] },
      { no: 23, id: 'chap_23', title: 'BAB 23: Selalu Waspada', rx: [/MEREU\s*DE\s*VEGHE/i, /^\s*23\s*$/] },
      { no: 24, id: 'chap_24', title: 'BAB 24: Di Perbatasan', rx: [/LA\s*VAM[AĂ]/i, /^\s*24\s*$/] },
      { no: 25, id: 'chap_25', title: 'BAB 25: Terbit Fajar', rx: [/R[AĂ]S[AĂ]RIT/i, /^\s*(25|05)\s*$/] },
      { no: 26, id: 'chap_26', title: 'BAB 26: Kesimpulan', rx: [/CONCLUZII/i, /^\s*(26|20)\s*$/] },
      { no: 27, id: 'chap_27', title: 'BAB 27: Media Penyebaran', rx: [/AGEN[TŢ]I\s*DE\s*TRANSFER/i, /^\s*27\s*$/] },
      { no: 28, id: 'chap_28', title: 'BAB 28: Di Siang Bolong', rx: [/[IÎ]N\s*P[UL]IN[AĂ]\s*ZI/i, /^\s*28\s*$/] },
      { no: 29, id: 'chap_29', title: 'BAB 29: Evakuasi', rx: [/RECUPERAREA/i, /^\s*(29|20)\s*$/] },
      { no: 30, id: 'chap_30', title: 'BAB 30: Bentang Alam', rx: [/PEISAJE/i, /^\s*30\s*$/] },
      { no: 31, id: 'chap_31', title: 'BAB 31: Manuver', rx: [/MI[SŞ]CARE/i, /^\s*(31|3I)\s*$/] },
      { no: 32, id: 'chap_32', title: 'BAB 32: Bisnis Berdarah', rx: [/AFACERI/i, /^\s*32\s*$/] },
      { no: 33, id: 'chap_33', title: 'BAB 33: Permainan Dimulai', rx: [/[IÎ]NCEP\s*JOCURILE/i, /^\s*33\s*$/] },
      { no: 34, id: 'chap_34', title: 'BAB 34: Permainan Berlanjut', rx: [/JOCURILE\s*CONTINU/i, /^\s*34\s*$/] },
      { no: 35, id: 'chap_35', title: 'BAB 35: Maraton', rx: [/MARATONUL/i, /^\s*35\s*$/] },
      { no: 36, id: 'chap_36', title: 'BAB 36: Penerbangan Darurat', rx: [/ZBOR\s*DE\s*NECESITATE/i, /^\s*(36|30)\s*$/] },
      { no: 37, id: 'chap_37', title: 'BAB 37: Api yang Padam', rx: [/FLAC[AĂ]RA/i, /^\s*37\s*$/] },
      { no: 38, id: 'chap_38', title: 'BAB 38: Pangkalan Riset', rx: [/STA[TŢ]IUNEA/i, /^\s*38\s*$/] },
      { no: 39, id: 'chap_39', title: 'BAB 39: Harmoni', rx: [/ARMONIA/i, /^\s*39\s*$/] },
      { no: 40, id: 'epilog', title: 'EPILOG', rx: [/^\s*(EPILOG|EPILOC)\s*$/i] }
    ];

    let lastLine = 520;
    const chapterSlices: Array<typeof chapterMeta[0] & { startLine: number }> = [];

    for (let i = 0; i < chapterMeta.length; i++) {
      const meta = chapterMeta[i];
      let start = -1;
      for (let j = lastLine; j < lines.length; j++) {
        if (j >= 25030 && j <= 25120) continue;
        if (j >= 48240 && j <= 48350) continue;
        const l = lines[j].trim();
        if (l.length > 50) continue;
        if (meta.rx.some(r => r.test(l))) {
          start = j;
          lastLine = j + 5;
          break;
        }
      }
      chapterSlices.push({ ...meta, startLine: start });
    }

    const chapters: Chapter[] = [];
    for (let i = 0; i < chapterSlices.length; i++) {
      const cur = chapterSlices[i];
      const next = chapterSlices[i + 1];
      let endLine = next ? next.startLine : lines.length;
      if (cur.no === 20) endLine = 25030;
      if (cur.no === 40) endLine = 48240;

      const rawLines = lines.slice(cur.startLine, endLine);
      const cleanLines = rawLines.filter(l => {
        const t = l.trim();
        if (/TOM\s*CLANCY|RAINBOW\s*SIX/i.test(t)) return false;
        if (/^\d+\s*e\s*TOM/i.test(t)) return false;
        if (t.length < 5 && /^[|\-=_~+`!?.a-z\s0-9]+$/i.test(t)) return false;
        return true;
      });

      const rawText = cleanLines.join('\n').trim();
      chapters.push({
        id: cur.id,
        title: cur.title,
        text: cleanWatermarks(rawText)
      });
    }

    return chapters;
  }

  // Khusus Overlord (Kugane Maruyama)
  if (/overlord/i.test(txtPath)) {
    console.log('💀 Terdeteksi: Overlord (Kugane Maruyama)!');
    const vm = path.basename(txtPath).match(/Volume\s+([0-9]+)/i);
    const volNum = vm ? vm[1].padStart(2, '0') : '01';
    const volPrefix = `vol${volNum}_`;

    const chapters: Chapter[] = [];
    let curChap: Chapter | null = null;
    let curLines: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      if (l.includes('### Galeri Ilustrasi Karakter & Warna')) {
        if (curChap && curLines.length > 0) {
          curChap.text = curLines.join('\n').trim();
          chapters.push(curChap);
        }
        curChap = {
          id: `${volPrefix}galeri`,
          title: 'Galeri Ilustrasi & Profil Karakter',
          text: ''
        };
        curLines = [];
        continue;
      }

      const isChapHeader = /^(Prolog\b|Chapter\s+[0-9IVXLCDM]+|Interlude\b|Epilog\b|Afterword\b)/i.test(l) && l.length < 80;
      if (isChapHeader) {
        if (curChap && curLines.length > 0) {
          curChap.text = curLines.join('\n').trim();
          if (curChap.text.length > 50) chapters.push(curChap);
        }

        let chId = `${volPrefix}ch${String(chapters.length + 1).padStart(2, '0')}`;
        if (/prolog/i.test(l)) chId = `${volPrefix}prolog`;
        else if (/interlude/i.test(l)) chId = `${volPrefix}interlude_${chapters.length + 1}`;
        else if (/epilog/i.test(l)) chId = `${volPrefix}epilog`;
        else if (/afterword/i.test(l)) chId = `${volPrefix}afterword`;
        else {
          const numMatch = l.match(/Chapter\s+([0-9IVXLCDM]+)/i);
          if (numMatch) chId = `${volPrefix}ch${numMatch[1].padStart(2, '0')}`;
        }

        curChap = {
          id: chId,
          title: l,
          text: ''
        };
        curLines = [];
        continue;
      }

      if (curChap) {
        if (/^\s*Overlord\s*[–—\-]\s*Volume\s*\d+\s*$/i.test(l)) continue;
        curLines.push(rawLine);
      }
    }

    if (curChap && curLines.length > 0) {
      curChap.text = curLines.join('\n').trim();
      if (curChap.text.length > 50) chapters.push(curChap);
    }

    return chapters;
  }

  // Khusus Mushoku Tensei (Rifujin na Magonote)
  if (/mushoku/i.test(txtPath)) {
    console.log('🔮 Terdeteksi: Mushoku Tensei - Isekai Ittara Honki Dasu!');
    const vm = path.basename(txtPath).match(/Volume\s+([0-9]+)/i);
    const volNum = vm ? vm[1].padStart(2, '0') : '01';
    const volPrefix = `vol${volNum}_`;

    const chapters: Chapter[] = [];
    let curChap: Chapter | null = null;
    let curLines: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      const l = rawLine.trim();

      if (l.includes('### Galeri Ilustrasi Karakter & Warna')) {
        if (curChap && curLines.length > 0) {
          curChap.text = curLines.join('\n').trim();
          chapters.push(curChap);
        }
        curChap = {
          id: `${volPrefix}galeri`,
          title: 'Galeri Ilustrasi & Karakter',
          text: ''
        };
        curLines = [];
        continue;
      }

      const isChapHeader = /^(Prolog\b|Bab\s+\d+|Bab\s+Ekstra|Epilog\b|Penutup\b|Afterword\b|Tentang Penulis|Paulus tersayang,)/i.test(l) && l.length < 80;
      // Jangan salah mendeteksi frasa biasa seperti "penutup mata" sebagai judul bab Penutup!
      const isFalsePositive = /^penutup\s+mata/i.test(l);
      if (isChapHeader && !isFalsePositive) {
        if (curChap && curLines.length > 0) {
          curChap.text = curLines.join('\n').trim();
          if (curChap.text.length > 50) chapters.push(curChap);
        }

        let chId = `${volPrefix}ch${String(chapters.length + 1).padStart(2, '0')}`;
        if (/prolog/i.test(l)) chId = `${volPrefix}prolog`;
        else if (/epilog/i.test(l)) chId = `${volPrefix}epilog`;
        else if (/bab\s+ekstra/i.test(l)) chId = `${volPrefix}ekstra`;
        else if (/afterword|penutup|tentang penulis/i.test(l)) chId = `${volPrefix}penutup`;
        else {
          const numMatch = l.match(/Bab\s+([0-9]+)/i);
          if (numMatch) chId = `${volPrefix}ch${numMatch[1].padStart(2, '0')}`;
        }

        // Ambil baris berikutnya jika merupakan kelanjutan judul bab (misal: "Bab 2:Pembantu yang \n Menyeramkan")
        let fullTitle = l;
        const nextRaw = lines[i + 1]?.trim() || '';
        if (nextRaw && nextRaw.length < 50 && !/^(Saya|Saat|Lilia|Sudah|Suatu|Nama|\[\[|Di|Ketika|Pada)\b/i.test(nextRaw) && !isChapHeader) {
          fullTitle = `${l} ${nextRaw}`;
        }

        curChap = {
          id: chId,
          title: fullTitle,
          text: ''
        };
        curLines = [];
        continue;
      }

      if (curChap) {
        if (/^\s*Mushoku\s*Tensei\s*[–—\-]\s*Volume\s*\d+\s*$/i.test(l)) continue;
        curLines.push(rawLine);
      }
    }

    if (curChap && curLines.length > 0) {
      curChap.text = curLines.join('\n').trim();
      if (curChap.text.length > 50) chapters.push(curChap);
    }

    return chapters;
  }

  // Generic fallback TXT parser
  const chapters: Chapter[] = [];
  let currentChap: Chapter | null = null;
  let currentLines: string[] = [];
  let chIndex = 1;

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    if (/^(CHAPTER|BAB)\s+[0-9]+/i.test(line) && currentLines.length > 200) {
      if (currentChap) {
        currentChap.text = cleanWatermarks(currentLines.join('\n').trim());
        chapters.push(currentChap);
      }
      currentChap = {
        id: `chap_${String(chIndex++).padStart(2, '0')}`,
        title: line,
        text: ''
      };
      currentLines = [];
      continue;
    }

    if (!currentChap && /^(CHAPTER|BAB)\s+[0-9]+/i.test(line)) {
      currentChap = {
        id: `chap_${String(chIndex++).padStart(2, '0')}`,
        title: line,
        text: ''
      };
      continue;
    }

    currentLines.push(rawLine);
  }

  if (currentChap && currentLines.length > 0) {
    currentChap.text = cleanWatermarks(currentLines.join('\n').trim());
    chapters.push(currentChap);
  }

  if (chapters.length === 0) {
    return [{ id: 'full_text', title: path.basename(txtPath), text: cleanWatermarks(content) }];
  }

  return chapters;
}

function splitParagraphSafe(text: string, maxChars: number): string[] {
  const paragraphs = text.split('\n');
  const chunks: string[] = [];
  let current: string[] = [];
  let len = 0;

  for (const p of paragraphs) {
    current.push(p);
    len += p.length + 1;
    if (len >= maxChars) {
      chunks.push(current.join('\n'));
      current = [];
      len = 0;
    }
  }

  if (current.length > 0) chunks.push(current.join('\n'));
  return chunks;
}

function buildPrompt(text: string, styleMode: StyleMode, simplified = false): string {
  if (simplified) {
    if (styleMode === 'comic_history') {
      return `Tuliskan naskah sejarah Islam karya Ira M. Lapidus berikut ke dalam Bahasa Indonesia dengan GAYA BAHASA KOMIK / WEBTOON SEJARAH (EPIC, DRAMATIC, PUNCHY, LUGAS, dan TO-THE-POINT).
- DILARANG MENAMBAH TOKOH FIKSI / ANIME / MONOLOG BATIN PALSU (jangan sebut Ainz, Albedo, Nazarick, dll.).
- BANNED JOKES OVERUSE: DILARANG menggunakan kata "budak korporat", "bos toxic", "shift malam".
- Haram bahasa baku kaku ("tatkala", "kian", "kendati demikian", "beliau").
- Pertahankan seluruh fakta sejarah, nama tokoh, dan tahun secara akurat.
- PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisinya!

Naskah Asli:

${text}`;
    }
    if (styleMode === 'harrypotter') {
      return `Tuliskan adegan cerita novel Harry Potter berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL TONGKRONGAN ASRAMA (GUE - LU), NO SENSOR, dan TO-THE-POINT.
- Dilarang monolog batin palsu. Dilarang jokes "budak korporat" / "bos toxic".
- Haram bahasa baku kaku ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "mencicit", "menukas").
- Dialog wajib format: Nama Lengkap: "..."
- PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisinya!

Adegan Cerita:

${text}`;
    }
    return `Tuliskan adegan fiksi fantasi berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, KONYOL, dan TO-THE-POINT (gaya komik/manga terjemahan gaul santai).
- Haram bahasa baku/formal kaku ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "mengindikasikan", "beliau").
- Wajib bahasa santai tongkrongan: "nggak", "banget", "udah", "gitu", "parah", "bodo amat", "sialan/anjir", dll.
- STRICT NO HALLUCINATIONS: DILARANG mengarang adegan palsu, DILARANG menambah tokoh/nama fiksi dari anime/novel lain, dan DILARANG menambah monolog batin yang tidak ada di teks sumber!
- STRICT BANNED JOKES: DILARANG menggunakan lelucon klise/garing seperti "budak korporat", "salaryman", "bos toxic", "shift malam", "takut kena SP", "laporan bulanan". Terjemahkan emosi karakter asli secara natural dan proporsional.
- Tell, Don't Show: Langsung beri tahu fakta dan emosi karakter secara tegas tanpa kalimat bertele-tele.
- Dialog wajib format: Nama: "..."
- PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisinya!
- Istilah Asli (Loanwords): Pertahankan istilah aslinya (nama jurus, sihir, ras, senjata, rank, gelar, konsep lore semesta terkait) beserta penjelasan singkat dalam kurung jika membingungkan pembaca awam!

Adegan Cerita:

${text}`;
  }

  const explanationRule = `- Penjelasan Istilah Asing / Teknis / Lore Cerita:
  Setiap istilah asing, istilah teknis, atau konsep yang berpotensi tidak dipahami pembaca dalam narasi maupun dialog harus disertai penjelasan singkat dalam bahasa Indonesia dengan format konsisten: Istilah (arti atau penjelasan sederhana). Contoh: Vox (perangkat komunikasi radio militer), Remembrancer (sejarawan/pencatat resmi ekspedisi), Browser (peramban web untuk menjelajahi internet).
  Terapkan secara alami sesuai konteks cerita, tanpa merusak alur, suasana, atau dialog karakter. Jelaskan hanya istilah yang benar-benar berpotensi membingungkan, utamakan saat pertama kali muncul, dan hindari pengulangan penjelasan yang sama. Gunakan bahasa sehari-hari yang lugas, bukan penjelasan formal seperti kamus. Jika istilah memiliki makna khusus dalam dunia cerita, jelaskan berdasarkan konteks tersebut.`;

  if (styleMode === 'comic_history') {
    return `Tuliskan kembali SELURUH naskah sejarah peradaban Islam karya Ira M. Lapidus berikut ke dalam Bahasa Indonesia dengan GAYA BAHASA KOMIK / WEBTOON SEJARAH (EPIC, DRAMATIC, PUNCHY, LUGAS, SERU, dan TO-THE-POINT) — setara narasi komik aksi/sejarah berkelas dunia tanpa bahasa makalah/skripsi yang membosankan!

ATURAN PALING PENTING (SETIA PADA NASKAH ASLI & ANTI-HALUSINASI):
- DILARANG MENAMBAH-NAMBAHKAN TOKOH FIKSI ATAU MONOLOG BATIN PALSU (jangan sebut karakter anime/game seperti Ainz, Albedo, dsb.)!
- BANNED JOKES OVERUSE: DILARANG memakai jokes korporat klise ("budak korporat", "bos toxic", "shift malam"). Ini adalah catatan sejarah dunia nyata!
- Tetap sajikan seluruh fakta sejarah, nama tokoh, tahun, wilayah, dan analisis institusi secara 100% LENGKAP tanpa memotong atau meringkas!

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH naskah secara UTUH, MENGALIR, dan DETAIL dari awal sampai akhir!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah...", "Ringkasan...", dll.

GAYA BAHASA KOMIK SEJARAH & ATURAN MUTLAK:
1. PUNCHY & ENERGETIK: Paragraf mengalir dinamis, tempo cepat, kalimat lugas, dan dramatisasi epik (seperti narator komik Kingdom / Vinland Saga / Three Kingdoms).
2. HARAM BAHASA BAKU KAKU / MAKALAH: DILARANG memakai kata usang kaku seperti ("tatkala", "manakala", "alkisah", "perihal yang mana", "kian", "kendati demikian", "beliau", "mengindikasikan", "mencicit", "menukas", "bergumam").
3. FORMAT DIALOG & QUOTE: Jika ada tuturan langsung tokoh sejarah atau dokumen kuno, gunakan format: Nama Tokoh: "..." dan berikan penekanan tegas.
4. NAMA TOKOH & ISTILAH SEJARAH:
   - Tulis nama tokoh dan dinasti dengan presisi (Utsman, Ali bin Abi Thalib, Mu'awiyah, Bani Umayyah, Abbasiyah, Fatimiyah, Seljuk, Mamluk, Utsmani).
   - Istilah sejarah Islam (Khilafah, Ulama, Waqf, Iqta', Fitnah, Baiat, Tahkim, Ghazw) tetap dipertahankan dengan penjelasan konteks alami jika perlu.
5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisinya!
${explanationRule}

Naskah Asli:

${text}`;
  }

  if (styleMode === 'harrypotter') {
    return `Tuliskan kembali SELURUH alur adegan cerita novel Harry Potter berikut ke dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL TONGKRONGAN ASRAMA (GUE - LU), NO SENSOR, LUGAS, dan TO-THE-POINT — setara novel petualangan modern tanpa eufemisme jadul yang kaku!

ATURAN PALING PENTING (SETIA PADA NASKAH ASLI & ANTI-HALUSINASI):
- DILARANG MENAMBAH-NAMBAHKAN PIKIRAN BATIN / MONOLOG PALSU yang tidak ada di naskah sumber!
- BANNED TOTAL JOKES OVERUSE: DILARANG KERAS menggunakan lelucon klise/garing seperti "budak korporat", "bos toxic", "lembur shift malam", "gaji UMR", dll. Harry Potter adalah anak/remaja penyihir di dunia magis, BUKAN pekerja kantoran Jakarta!
- Pertahankan sudut pandang narator orang ketiga (third person POV) asli dari buku, JANGAN ubah narator cerita menjadi "batin gue" atau "kata gue". Sudut pandang orang pertama (Gue - Lu) HANYA untuk DIALOG antar karakter sebaya dan pikiran karakter yang MEMANG ADA di teks aslinya!

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

ATURAN WAJIB & MUTLAK:
1. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Percakapan antar murid/sahabat sebaya (Harry Potter, Ron Weasley, Hermione Granger, Neville Longbottom, Seamus Finnigan, Fred, George): gunakan GUE - LU secara luwes.
   - BANNED TOTAL: DILARANG menggunakan kata kaku "aku", "kamu", "kau", "diriku", "kepadamu" untuk dialog pergaulan sebaya! Ganti jadi GUE / LU!

2. TONE KASAR, VULGAR, CEPLAS-CEPLOS & MAKIAN TANPA SENSOR:
   - JANGAN TURUNKAN KEVULGARAN / KEBERANIAN BAHASA! Terjemahkan umpatan jalanan, perseteruan asrama, dan amarah karakter secara liar, frontal, dan to-the-point tanpa eufemisme sopan yang munafik (bloody hell, git, prat, damn, bastard, bitch, shit -> anjing, bangsat, taik, bajingan, sialan, keparat, tolol, brengsek, songong, lonte, kampret).
   - Dialog perseteruan dan amarah antar murid (terutama Harry, Ron vs Malfoy, Crabbe, Goyle) wajib pedas, nyolot, dan tanpa rem!
   - Karakterisasi tokoh terjaga kuat sesuai aslinya:
     * Harry Potter: Remaja mandiri, sinis pedas kalau dijahatin, pemberani dan nggak segan ngegas.
     * Ron Weasley: Ceplas-ceplos, gampang panas, hobi misuh/ngumpat kalau kaget atau kesel ("Buset anjing, bangsat bener tuh anak!").
     * Severus Snape: Dingin, menusuk, sarkas tajam, suka merendahkan dan mempermalukan lawan bicaranya.
     * Draco Malfoy: Songong, tengil, manja anak orang kaya, rasis darah murni penghina ("Najis dasar darah lumpur lu!").
     * Rubeus Hagrid: Blak-blakan, ramah, polos, suka keceplosan info rahasia ("Aduh goblok, harusnya gue nggak ngomong itu tadi...").
     * Albus Dumbledore: Bijak, tenang, misterius, santai tapi sangat berwibawa.
     * Vernon & Petunia Dursley: Kolot, panik, sensi sama hal aneh, suka ngegas dan bentak-bentak kasar.

3. HARAM BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
   - Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "berujar", "berkata").
   - BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus"!
   - ANTI-REPETISI VERBA: Variasikan kata kerja aksi dan dialog secara dinamis sesuai naskah asli (bisik, seru, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir, ngedumel, ngoceh, dengus kesel, hela napas).

4. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog tanpa nama pembicara!
   - Setiap baris tuturan langsung WAJIB diawali format: Nama Lengkap: "..."
   - DAFTAR NAMA LENGKAP TOKOH HARRY POTTER:
     * Harry Potter -> Selalu gunakan: Harry Potter: "..."
     * Ron Weasley -> Selalu gunakan: Ron Weasley: "..."
     * Hermione Granger -> Selalu gunakan: Hermione Granger: "..."
     * Albus Dumbledore -> Selalu gunakan: Albus Dumbledore: "..."
     * Minerva McGonagall -> Selalu gunakan: Minerva McGonagall: "..."
     * Severus Snape -> Selalu gunakan: Severus Snape: "..."
     * Rubeus Hagrid -> Selalu gunakan: Rubeus Hagrid: "..."
     * Draco Malfoy -> Selalu gunakan: Draco Malfoy: "..."
     * Neville Longbottom -> Selalu gunakan: Neville Longbottom: "..."
     * Vernon Dursley -> Selalu gunakan: Vernon Dursley: "..."
     * Petunia Dursley -> Selalu gunakan: Petunia Dursley: "..."
     * Dudley Dursley -> Selalu gunakan: Dudley Dursley: "..."
     * Quirrell -> Selalu gunakan: Profesor Quirrell: "..."
     * Ollivander -> Selalu gunakan: Garrick Ollivander: "..."

5. MANTRA & ISTILAH SIHIR TETAP PRESISI (LOANWORDS):
   - Pertahankan istilah sihir asli: Muggle, Quidditch, Golden Snitch, Bludger, Quaffle, Sorting Hat, Diagon Alley, Privet Drive, Gringotts, Galleon, Sickle, Knut, Invisibility Cloak, Mirror of Erised.
   - Pertahankan nama mantra latin asli (Alohomora, Wingardium Leviosa, Petrificus Totalus, Lumos, dll.) dengan penjelasan efek dalam kurung jika membingungkan.
${explanationRule}

Naskah Asli:

${text}`;
  }

  if (styleMode === 'carl') {
    return `Tuliskan kembali SELURUH alur adegan cerita Dungeon Crawler Carl berikut dalam Bahasa Indonesia bergaya MANHWA / KOMIK DUNGEON APOCALYPSE MODERN, SANGAT MENGHIBUR, KOMEDI GELAP KOCAK, ENAK DIBACA AWAM, SUPER SANTAI TONGKRONGAN (GUE - LU), VULGAR MAKSIMAL NO SENSOR, TELL-DON'T-SHOW, LUGAS, dan TO-THE-POINT!
Target pembaca: Pembaca awam penyuka komik/manhwa dungeon crawler aksi brutal nan kocak (seperti Solo Leveling tapi versi komedi gelap R-rated, gila, liar, dan tanpa sensor sama sekali).

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

ATURAN WAJIB & MUTLAK:
1. GAYA KOMIK & TELL-DON'T-SHOW (NAGIH & BIKIN BETAH):
   - Gunakan pendekatan TELL-DON'T-SHOW yang lincah: aksi serba cepat, visual, punchy, dan langsung ke inti ketegangan serta humor gilanya.
   - Narasi Carl dirombak menjadi obrolan santai, sinis, capek hidup, tapi badass. Carl terjun ke dungeon apocalypse cuma pakai celana boxer hati merah, jaket kulit tebal, dan telanjang kaki tanpa sepatu!

2. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Monolog batin Carl, narasi, dan percakapan antar manusia / teman: WAJIB gunakan GUE - LU!
   - BANNED TOTAL: DILARANG menggunakan kata kaku "aku", "kamu", "kau", "diriku", "kepadamu" untuk dialog informal! Ganti jadi GUE / LU!

3. VULGAR MAKSIMAL NO SENSOR & KOMEDI GELAP:
   - Terjemahkan umpatan jalanan, makian, dan kepanikan tanpa disensor (shit, fuck, motherfucker, goddammit, asshole, bitch, bastard, dick -> bangsat, anjing, keparat, bajingan, kontol, taik, sialan, jahanam).
   - KHUSUS PRINCESS DONUT: Kucing Persia juara kontes yang sekarang bisa bicara. Nadanya diva sombong, lebay, manja, narsis, sering histeris dalam huruf kapital (ALL-CAPS), menganggap Carl bawahannya, tapi sangat setia.
   - KHUSUS DUNGEON AI / SYSTEM ANNOUNCER: Komentator game intergalaksi yang sadis, ngeselin, mesum, sarkas, dan punya fetish aneh terhadap kaki telanjang Carl.
   - KHUSUS NOTIFIKASI GAME / ACHIEVEMENT / STATS: Buat kotak teks jelas dan rapi:
     [PEMBERITAHUAN DUNGEON: PENCAPAIAN DIBUKA!]
     [Item: ...]
     [Hadiah: ...]

4. HARAM BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
   - Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "berujar", "berkata").
   - BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus"!
   - ANTI-REPETISI VERBA: Variasikan kata kerja aksi dan dialog secara dinamis sesuai naskah asli (bisik, seru, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir, ngedumel, ngoceh, dengus kesel, hela napas).

5. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog tanpa nama pembicara!
   - Setiap baris tuturan langsung WAJIB diawali format: Nama Lengkap: "..."
   - DAFTAR NAMA LENGKAP TOKOH DUNGEON CRAWLER CARL:
     * Carl -> Selalu gunakan: Carl: "..."
     * Princess Donut -> Selalu gunakan: Princess Donut: "..."
     * Dungeon AI -> Selalu gunakan: Dungeon AI: "..."
     * Mordecai -> Selalu gunakan: Mordecai: "..."
     * Agatha -> Selalu gunakan: Agatha: "..."
     * Frank -> Selalu gunakan: Frank: "..."
     * Bea -> Selalu gunakan: Bea: "..."
     * Odette -> Selalu gunakan: Odette: "..."
     * Borant Announcer -> Selalu gunakan: Announcer: "..."

6. ISTILAH GAME / LITRPG (LOANWORDS):
   - Pertahankan istilah game aslinya: Crawler, Safe Room, Floor Collapse, Loot Box, Magic Missile, Inventory, HUD, Stats, Achievement, Boss, Minion.
${explanationRule}

Naskah Asli:

${text}`;
  }

  if (styleMode === 'expanse') {
    return `Tuliskan kembali SELURUH alur adegan fiksi ilmiah The Expanse berikut dalam Bahasa Indonesia bergaya KOMIK / WEBTOON MODERN, SANGAT MENGHIBUR, ENAK DIBACA AWAM, SUPER SANTAI TONGKRONGAN (GUE - LU), VULGAR MAKSIMAL NO SENSOR, TELL-DON'T-SHOW, LUGAS, dan TO-THE-POINT!
Target pembaca: Pembaca awam yang bukan kutu buku sastra tebal, tapi pengin cerita fiksi ilmiah serasa nonton serial aksi luar angkasa Hollywood atau baca komik sci-fi dewasa yang nagih, intens, dan bikin betah dari bab ke bab.

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

ATURAN WAJIB & MUTLAK:
1. GAYA KOMIK & TELL-DON'T-SHOW (NAGIH & GAK NGEBOSENIN):
   - Gunakan pendekatan TELL-DON'T-SHOW yang lincah: deskripsi bertele-tele diubah jadi narasi aksi yang serba cepat, visual, dan langsung ke inti ketegangan.
   - Narasi harus renyah, menghibur, dan bikin betah pembaca awam seolah-olah sedang membaca balon teks dan panel komik/manga sci-fi beroktan tinggi.

2. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Semua dialog informal & pergaulan antar kru pesawat (Holden, Naomi, Amos, Alex), marinir Mars (Bobbie Draper), detektif, maupun peneliti (Prax Meng): WAJIB gunakan GUE - LU!
   - BANNED TOTAL: DILARANG menggunakan kata kaku "aku", "kamu", "kau", "diriku", "kepadamu" untuk dialog kasual! Ganti jadi GUE / LU!

3. VULGAR MAKSIMAL NO SENSOR & TONE MILITER / POLITIK:
   - Tanpa sensor sedikit pun! Umpatan jalanan luar angkasa dan militer diterjemahkan apa adanya secara brutal dan mengalir (shit, fuck, motherfucker, asshole, dick, bastard -> bangsat, anjing, keparat, bajingan, kontol, taik, sialan).
   - KHUSUS CHRISJEN AVASARALA: Karakternya terkenal sangat vulgar, bermulut kotor, sinis, dan tak kenal ampun. Dialog Avasarala WAJIB tajam, ceplas-ceplos, penuh umpatan berbobot tanpa diperhalus!
   - KHUSUS BOBBIE (GUNNERY SGT ROBERTA DRAPER): Gaya bicara marinir Mars yang garang, lugas, disiplin tempur, dan intimidatif.
   - KHUSUS AMOS BURTON: Pembunuh dingin berhati santai, gaya ngomongnya cuek, pragmatis, dan santai walau sedang meremukkan tulang musuh.

4. HARAM BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
   - Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "berujar", "berkata").
   - BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus"!
   - ANTI-REPETISI VERBA: Variasikan kata kerja aksi dan dialog secara dinamis sesuai naskah asli (bisik, seru, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir, ngedumel, ngoceh, dengus kesel, hela napas).

5. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog tanpa nama pembicara!
   - Setiap baris tuturan langsung WAJIB diawali format: Nama Lengkap: "..."
   - DAFTAR NAMA LENGKAP TOKOH THE EXPANSE (BOOK 1 & 2):
     * James Holden -> Selalu gunakan: James Holden: "..."
     * Naomi Nagata -> Selalu gunakan: Naomi Nagata: "..."
     * Amos Burton -> Selalu gunakan: Amos Burton: "..."
     * Alex Kamal -> Selalu gunakan: Alex Kamal: "..."
     * Bobbie Draper / Roberta Draper -> Selalu gunakan: Bobbie Draper: "..."
     * Chrisjen Avasarala -> Selalu gunakan: Chrisjen Avasarala: "..."
     * Praxidike Meng / Prax -> Selalu gunakan: Prax Meng: "..."
     * Clarissa Mao / Peaches -> Selalu gunakan: Clarissa Mao: "..."
     * Joe Miller -> Selalu gunakan: Joe Miller: "..."
     * Fred Johnson -> Selalu gunakan: Fred Johnson: "..."
     * Sadavir Errinwright -> Selalu gunakan: Sadavir Errinwright: "..."
     * Cotyar Ghazi -> Selalu gunakan: Cotyar Ghazi: "..."
     * Jules-Pierre Mao -> Selalu gunakan: Jules-Pierre Mao: "..."
     * Mei Meng -> Selalu gunakan: Mei Meng: "..."
     * Strickland -> Selalu gunakan: Dr. Strickland: "..."
     * Soren -> Selalu gunakan: Soren: "..."
     * Julie Mao -> Selalu gunakan: Julie Mao: "..."

6. ISTILAH TEKNIS LUAR ANGKASA & BAHASA BELTER (LOANWORDS):
   - Pertahankan istilah fiksi ilmiah keras: Epstein Drive, PDC (Point Defense Cannon), railgun, high-g burn, thrust gravity, spin gravity, crash couch, EVA suit, airlock, reaction control thrusters, juice (koktail obat anti-g).
   - Pertahankan bahasa Belter (Lang Belta): beratna, sa-sa ke, bosmang, inyalowda, welwalla, sheng beserta penjelasan singkat jika perlu.
${explanationRule}

Naskah Asli:

${text}`;
  }

  if (styleMode === 'dxd') {
    return `Tuliskan kembali SELURUH alur adegan cerita High School DxD berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, TONGKRONGAN GAUL, NO SENSOR, MESUM FRONTAL, KASAR, dan TO-THE-POINT — setara dengan light novel dewasa / manga ecchi tanpa sensor!
Target pembaca: Remaja akhir / dewasa yang mau hiburan seru, kocak, mesum to-the-point, dan ogah baca kalimat berbelit-belit atau eufemisme sopan yang munafik!

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

ATURAN WAJIB & MUTLAK:
1. SUDUT PANDANG & PRONOUNS (BANNED KATA AKU-KAMU):
   - Tokoh utama (Issei Hyoudou) monolog batin dan narasi selalu menggunakan: GUE (bukan "aku").
   - Menghadap orang lain / dialog menggunakan: LU / ELO (bukan "kamu" atau "kau").
   - BANNED TOTAL: DILARANG menggunakan kata "aku", "kamu", "kau", "diriku", "kepadamu". Ganti semua jadi GUE / LU!

2. TONE & KATA KASAR / VULGAR / MESUM FRONTAL:
   - Pikiran batin Issei mesum frontal, to-the-point, liar, dan kocak (toket, toket montok, grepe, ngintip, sange, coli, binal, ngentot, kontol, memek, becek, desah liar, bangsat, anjing, sialan, taik keluar apa adanya tanpa sensor!).
   - Jangan disopankan atau diperhalus! Terjemahkan secara blak-blakan dan renyah.

3. HARAM BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
   - Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "berujar", "berkata").
   - BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau", "mendengus"!
   - ANTI-REPETISI VERBA: Variasikan kata kerja aksi dan dialog secara dinamis sesuai naskah asli (bisik, seru, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir, ngedumel, ngoceh, dengus kesel, hela napas).

4. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog tanpa nama pembicara!
   - Setiap baris tuturan langsung WAJIB diawali format: Nama Lengkap: "..."
   - DAFTAR NAMA LENGKAP TOKOH HIGH SCHOOL DXD:
     * Issei Hyoudou / Ise -> Selalu gunakan: Issei Hyoudou: "..."
     * Yuuma Amano / Raynare -> Selalu gunakan: Yuuma Amano: "..." (atau Raynare: "..." setelah wujud aslinya terbongkar)
     * Rias Gremory / Buchou -> Selalu gunakan: Rias Gremory: "..."
     * Akeno Himejima -> Selalu gunakan: Akeno Himejima: "..."
     * Koneko Toujou -> Selalu gunakan: Koneko Toujou: "..."
     * Kiba Yuuto -> Selalu gunakan: Kiba Yuuto: "..."
     * Asia Argento -> Selalu gunakan: Asia Argento: "..."
     * Matsuda -> Selalu gunakan: Matsuda: "..."
     * Motohama -> Selalu gunakan: Motohama: "..."
     * Ayah Issei -> Selalu gunakan: Gorou Hyoudou: "..."
     * Ibu Issei -> Selalu gunakan: Miki Hyoudou: "..."
     * Dohnaseek -> Selalu gunakan: Dohnaseek: "..."
     * Kalawarner -> Selalu gunakan: Kalawarner: "..."
     * Mittelt -> Selalu gunakan: Mittelt: "..."
     * Freed Sellzen -> Selalu gunakan: Freed Sellzen: "..."

5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
${explanationRule}

Naskah Asli:

${text}`;
  }

  if (styleMode === 'mushoku') {
    return `Tuliskan kembali SELURUH alur adegan cerita fiksi fantasi berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, KONYOL, LUCU, KOCAK, dan TO-THE-POINT — setara dengan komik/manga isekai terjemahan gaul santai, webtoon fantasi komedi, atau light novel populer.

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN ATAU POIN-POIN SINGKAT:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah ringkasan...", "Mau lanjut ke ringkasan...", atau semacamnya!

HARAM BAHASA BAKU/FORMAL/KBBI KAKU:
- Dilarang keras memakai kata-kata formal/makalah kaku ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan sebuah", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau").
- Narasi dan dialog wajib memakai bahasa tongkrongan santai sehari-hari: "nggak/ngga", "banget", "udah", "gitu", "bocah", "parah", "bodo amat", "kepo", "gila", "sialan/anjir", "mager", "pusing pala", dll. Kalimat pendek, padat, dan tidak kaku!

GAYA BAHASA & ATURAN MUTLAK:
1. Santai sehari-hari, gaul, konyol, lucu, dan kocak: Bikin pembaca ngakak dan enjoy nikmati cerita dari awal sampai akhir.
2. Boleh kasar, vulgar, mesum konyol, dan santai selama sesuai karakter dan situasi.
3. Kalimat pendek, padat, dan tidak kaku (nol kalimat puitis/berbunga-bunga klise/lebay).
4. Karakterisasi tokoh tetap dijaga ketat:
   - Tokoh utama (Rudy / Rudeus):
     * Monolog batin / isi pikiran: Gaya lu-gue santai, otaku mesum, panik, kocak, overthinking, introspeksi diri ala mantan pengangguran nolep 34 tahun yang reinkarnasi jadi bocah ajaib ("Waduh anjir, gawat nih...", "Gue harus tobat tapi godaannya berat banget bro...").
     * Dialog keluar: Berusaha sopan, manis, cerdas, tapi kadang ceplas-ceplos atau mesum terselubung.
   - Tokoh ayah (Paul): Ksatria playboy santai, sok keren, akrab ala tongkrongan cowok sama anaknya.
   - Tokoh guru sihir (Roxy): Guru loli mungil berkepala dingin, kikuk, tapi dihormati dan dipuja Rudy bak dewi.
   - Tokoh gadis bangsawan tsundere (Eris): Galak, temperamental, tinju dulu baru ngomong, tapi gengsian.
   - Tokoh teman masa kecil elf (Sylphie): Pemalu, manis, penurut, polos.
5. Tell, Don't Show (Lugas & Transparan): Langsung beri tahu fakta, suasana, dan apa yang ada di pikiran karakter secara gamblang tanpa buang-buang kalimat mendeskripsikan kedutan alis atau tarikan napas bertele-tele.
6. Format Dialog Wajib: Nama: "..." (misal Rudy: "...", Paul: "...", Roxy: "...", Zenith: "...").
7. PENTING: Pertahankan tag penanda seperti [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
8. Istilah Asli (Loanwords): Pertahankan istilah asli dunia fantasi (Mana, Chantless Casting, Voiceless Magic, Rank Saint/King/God, Sword God Style, Water God Style, Demon Continent, dll.) beserta penjelasan singkat dalam kurung jika membingungkan.
${explanationRule}

Adegan Cerita:

${text}`;
  }

  if (styleMode === 'overlord') {
    return `Tuliskan kembali SELURUH alur adegan cerita fiksi fantasi berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, KONYOL, LUCU, KOCAK, dan TO-THE-POINT — setara dengan komik/manga terjemahan gaul santai, webtoon komedi aksi, atau light novel populer.

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN ATAU POIN-POIN SINGKAT:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah ringkasan...", "Mau lanjut ke ringkasan...", atau semacamnya!

HARAM BAHASA BAKU/FORMAL/KBBI KAKU:
- Dilarang keras memakai kata-kata formal/makalah kaku ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan sebuah", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau").
- Narasi dan dialog wajib memakai bahasa tongkrongan santai sehari-hari: "nggak/ngga", "banget", "udah", "gitu", "bocah", "parah", "bodo amat", "kepo", "gila", "sialan/anjir", "mager", "pusing pala", dll. Kalimat pendek, padat, dan tidak kaku!

GAYA BAHASA & ATURAN MUTLAK:
1. Santai sehari-hari, gaul, konyol, lucu, dan kocak: Bikin pembaca ngakak dan enjoy nikmati cerita dari awal sampai akhir.
2. Boleh kasar, vulgar, dan santai selama sesuai karakter dan situasi.
3. Kalimat pendek, padat, dan tidak kaku (nol kalimat puitis/berbunga-bunga klise/lebay).
4. Karakterisasi tokoh tetap dijaga ketat:
   - Tokoh utama (Sang Penguasa / Tengkorak):
     * Monolog batin / isi pikiran: Gaya santai, panik, overthinking, konyol, lu-gue ("Waduh anjir, gawat banget nih kalau ketahuan...", "Bisa berabe urusannya kalau mereka tahu gue cuma akting sok keren..."). DILARANG mengulang-ulang frasa "budak korporat/salaryman/takut kena SP/laporan bulanan" di luar teks aslinya!
     * Dialog keluar: Berusaha keras sok jaim, cool, berwibawa mutlak, dingin, dan mengintimidasi.
   - Karakter wanita setia: Bucin akut, protektif, histeris mesum saat berdua.
   - Karakter penasihat: Super sopan, intelek, sadis berdarah dingin, pemikir konspirasi.
   - Karakter ksatria: Pejuang terhormat, nafas berdesis, taat instruksi.
   - Karakter kembar elf: Tomboi blak-blakan vs pemalu penakut tapi serangannya ngeri.
5. Tell, Don't Show (Lugas & Transparan): Langsung beri tahu fakta, suasana, dan apa yang ada di pikiran karakter secara gamblang tanpa buang-buang kalimat mendeskripsikan kedutan alis, butiran keringat mikro, atau tarikan napas bertele-tele.
6. Format Dialog Wajib: Nama: "..." (misal Ainz: "...", Albedo: "...", Gazef: "...").
7. PENTING: Pertahankan tag penanda seperti [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
8. Istilah Asli (Loanwords): Pertahankan istilah asli dunia fantasi (World Item, Tier Magic, Undead, dll.) beserta penjelasan singkat dalam kurung jika membingungkan.
${explanationRule}

Adegan Cerita:

${text}`;
  }

  if (styleMode === 'metro') {
    return `Tuliskan kembali SELURUH alur adegan cerita sci-fi post-apocalyptic Metro 2033 berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, CEPLAS-CEPLOS, SURAM/TEGANG, KASAR PRAJURIT, dan TO-THE-POINT — setara dengan komik/manga survival aksi, webtoon thriller distopia, atau novel laga populer.

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan cerita...", dll.

HARAM TOTAL BAHASA BAKU / FORMAL / KBBI KAKU:
- Dilarang keras memakai bahasa makalah/KBBI sastra kaku ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "tiada").
- Narator dan dialog WAJIB memakai bahasa tongkrongan santai sehari-hari: "nggak/ngga", "banget", "udah", "gitu", "bocah", "parah", "bodo amat", "kepo", "gila", "sialan/anjir/brengsek/kampret/tai", "mager", "pusing pala", dll.
- Boleh ceplas-ceplos, bahasa ngawur, kata kasar, makian, dan umpatan santai prajurit/stalker selama pas dengan emosi adegan dan karakternya!

GAYA BAHASA & ATURAN MUTLAK:
1. Narasi Tegang & Atmosfer Survival Kelam tapi Mengalir Renyah: Dunia bawah tanah Metro Moskwa yang gelap, dingin, sesak, dan berbahaya diceritakan dengan gaya lugas, to-the-point, dan bikin pembaca ketagihan tanpa bikin ngantuk.
2. Tell, Don't Show: Langsung sampaikan situasi, bahaya mutan, dan kepanikan karakter secara gamblang tanpa muter-muter.
3. Karakterisasi Tokoh:
   - Artyom: Pemuda 20-an tahun dari VDNKh. Monolog batin lu-gue santai, takut tapi penasaran, overthinking saat jaga pos atau masuk terowongan gelap ("Anjir, suara apa lagi tuh barusan...", "Kalau senter gue mati kelar hidup gue").
   - Hunter / Bourbon / Khan / Miller: Kasar, blak-blakan, gaya prajurit/stalker berpengalaman, perokok berat, ceplas-ceplos ("Bocah, jalan di belakang gue", "Jangan banyak bacot kalau mau idup").
   - Warga stasiun / Prajurit: Santai, minum teh jamur, judi peluru militer kaliber 5.45mm.
4. Format Dialog Wajib: Nama: "..." (misal Artyom: "...", Hunter: "...", Bourbon: "...", Khan: "...", Miller: "...").
5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
6. Istilah Asli Semesta Metro 2033 (Loanwords): Pertahankan istilah aslinya (Stalker, Dark Ones / Si Hitam, Hanza, Fourth Reich, Red Line, Polis, VDNKh, Exhibition, Ranger, Shambler, Bastard gun, Metro-2 / D-6, Peluru Militer pra-perang).
${explanationRule}

Adegan Cerita:\n\n${text}`;
  }

  if (styleMode === 'dune') {
    return `Tuliskan kembali SELURUH alur adegan cerita sci-fi Dune berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, CEPLAS-CEPLOS, FUN, KONYOL/NGAWUR, dan TO-THE-POINT — setara dengan komik/manga terjemahan gaul santai, webtoon aksi, atau light novel populer. Target pembaca: remaja/young-adult yang pengen bacaan seru, nagih, dan nggak bikin ngantuk.

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Lanjut ke bab berikutnya...", dll.

HARAM TOTAL BAHASA BAKU / FORMAL / KBBI KAKU:
- Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "tiada", "berkata", "berujar", "bersabda").
- Narator dan dialog WAJIB memakai bahasa tongkrongan santai sehari-hari: "nggak/ngga", "banget", "udah", "gitu", "bocah", "parah", "bodo amat", "kepo", "gila", "sialan/anjir/brengsek/kampret", "mager", "pusing pala", dll.
- Boleh ceplas-ceplos, bahasa ngawur, kata kasar, makian, dan umpatan santai selama pas dengan emosi adegan dan karakternya!

GAYA BAHASA & ATURAN MUTLAK:
1. Narasi Fun, Ceplas-Ceplos & Hidup: Cerita sci-fi berat Dune diubah jadi bacaan super renyah dan asik dinikmati layaknya baca komik gaul, tanpa menghilangkan esensi konflik politik dan bahaya planet Arrakis.
2. Tell, Don't Show: Langsung sampaikan situasi, apa yang terjadi, dan fakta secara gamblang tanpa muter-muter bikin pusing. Pangkas deskripsi mikro yang bikin ngantuk.
3. Karakterisasi Tokoh:
   - Paul Atreides:
     * Monolog batin / isi pikiran: Gaya lu-gue santai, ceplas-ceplos, overthinking, konyol ala remaja jenius yang pusing mikirin takdir gila ("Anjir, nenek lampir ini ngapain melototin gue...", "Gom Jabbar apaan lagi coba? Kalau gue mati di sini kan berabe...").
     * Dialog keluar: Sopan tapi tegas, berani ngejawab balik, nggak ciut.
   - Nenek Bene Gesserit (Mohiam): Nenek tua galak, judes, mengintimidasi, ceplas-ceplos tanpa ampun ("Bocah licik", "Diem lu jangan banyak bacot").
   - Jessica: Ibu yang cemas tapi jaim dan penuh rahasia.
   - Tokoh Militer / Fremen (Stilgar, Gurney, Duncan): Kasar, maskulin, blak-blakan, gaya prajurit tanpa basa-basi ("Sialan lu", "Beres bos", "Mampus tuh cacing").
   - Baron Harkonnen: Penjahat tambun yang sadis, rakus, licik, dan suka ngegas.
4. Format Dialog Wajib: Nama: "..." (misal Paul: "...", Jessica: "...", Mohiam: "...", Stilgar: "...", Baron: "...").
5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
6. Istilah Asli Semesta Dune (Loanwords): Pertahankan istilah aslinya (Spice Melange, Bene Gesserit, Kwisatz Haderach, Mentat, Gom Jabbar, Voice, Fremen, Shai-Hulud, Sandworm, Crysknife, Stillsuit, Ornithopter, Sardaukar, Padishah Emperor, Landsraad, Guild Navigator, Water of Life, Sietch, Fedaykin, Lisan al-Gaib, Muad'Dib).
${explanationRule}

Adegan Cerita:\n\n${text}`;
  }

  if (styleMode === 'hobbit') {
    return `Tuliskan seluruh cerita dalam Bahasa Indonesia yang luwes, santai/gaul, hidup, dan to-the-point — setara dengan novel petualangan fantasi modern terjemahan resmi, webtoon fantasi, atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, ekspresif, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & Transparan). Langsung sampaikan situasi, atmosfer petualangan, dan isi pikiran karakter secara tegas.
- Nol Metafora & Anti-Puitis. Dilarang keras menggunakan kalimat berbunga-bunga lebay.
- Slang & Percakapan Santai (gue/lu atau percakapan sehari-hari yang luwes dan dinamis).
- Format dialog: Nama: "..."
- PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
- Istilah Asli (Loanwords): Pertahankan istilah ras dan nama tempat/karakter (Hobbit, Dwarf, Elf, Goblin, Orc, Troll, Warg, Shire, Rivendell, Mirkwood, Erebor, Smaug).
${explanationRule}

Adegan Cerita:\n\n${text}`;
  }

  if (styleMode === 'warhammer') {
    return `Tuliskan seluruh cerita dalam Bahasa Indonesia yang lugas, energik, badass, dan to-the-point — setara dengan komik/manga terjemahan resmi, webtoon aksi sci-fi militer, atau novel aksi grimdark populer. Target pembaca adalah remaja/young-adult: ritme cepat, intens, maskulin/taktis, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & Transparan). Pangkas deskripsi fisiologis mikro yang kepanjangan (butiran keringat, tarikan napas mikro, urat nadi). Langsung sampaikan situasi taktis, atmosfer perang, dan isi pikiran karakter secara tegas.
- Nol Metafora & Anti-Puitis. Dilarang keras menggunakan analogi filosofis lebay atau kalimat bunga-bunga. Pertempuran dan ketegangan disampaikan secara konkret dan berbobot.
- Slang & Dialog Prajurit (lu-gue/lo-gue antar saudara seperjuangan Space Marine akrab, sapaan "saudara", "kapten", "sobat"; santai to-the-point dengan sesama manusia/remembrancer).
- Pacing Cepat ala Panel Manga: aksi taktis langsung → reaksi singkat → dialog balasan.
- Istilah Asli (Loanwords): Pertahankan istilah asli semesta Warhammer 40k (Primarch, Warmaster, Astartes, Space Marines, Legion, Luna Wolves, Mournival, Remembrancer, Iterator, Bolter, Chainsword, Dreadnought, Drop-pod, Warp, Ceramite, Pict, Vox).
${explanationRule}

Adegan Cerita:\n\n${text}`;
  }

  if (styleMode === 'konosuba') {
    return `Tuliskan seluruh cerita dalam Bahasa Indonesia yang luwes, hidup, dan to-the-point — setara dengan komik/manga terjemahan resmi, webtoon aksi, atau light novel populer. Target pembaca adalah remaja/young-adult: ritme cepat, energik, kocak, padat, adiktif, dan langsung pada pokok masalah. Jangan kaku seperti terjemahan mesin, dan jangan gunakan bahasa formal makalah ("Anda", "mengindikasikan", "beliau"). Format dialog konsisten sertakan Nama: "...".

Aturan Mutlak:
- Tell, Don't Show (Lugas & Transparan). Pangkas deskripsi fisiologis mikro yang kepanjangan (butiran keringat, tarikan napas mikro, urat nadi). Langsung beri tahu fakta, situasi, dan isi pikiran karakter secara tegas.
- Nol Metafora & Anti-Puitis. Dilarang keras menggunakan kalimat berbunga-bunga atau analogi filosofis lebay.
- Slang & Bahasa Santai (lu-gue/kamu-aku sesuai relasi). Karakter bicara natural seperti manusia hidup di eranya.
- Pacing Cepat ala Panel Komik / Manga: aksi langsung → reaksi singkat → dialog balasan.
- Istilah Asli (Loanwords): Pertahankan istilah asli (nama jurus/sihir seperti Explosion, Steal; honorifik -san, -kun, senpai; nama monster/faksi).
${explanationRule}

Adegan Cerita:\n\n${text}`;
  }

  return `Tuliskan kembali SELURUH alur adegan cerita berikut dalam Bahasa Indonesia yang SUPER SANTAI SEHARI-HARI, GAUL, LUGAS, FUN, dan TO-THE-POINT — setara dengan komik/manga terjemahan gaul santai, webtoon aksi populer, atau novel adaptasi modern.
Target pembaca: Orang yang suka cerita seru tapi malas baca novel sastra karena bahasanya berat, puitis, dan dialognya kaku. Kita BUKAN lagi ujian sastra Bahasa Indonesia!

DILARANG KERAS MEMBUAT RINGKASAN/RANGKUMAN:
- Tuliskan kembali SELURUH narasi dan percakapan adegan secara LENGKAP, UTUH, dan MENGALIR dari awal sampai akhir tanpa memotong peristiwa atau detail cerita!
- Dilarang membuat kalimat pembuka atau penutup template seperti "Berikut adalah terjemahan...", "Ringkasan...", dll.

HARAM TOTAL BAHASA BAKU / FORMAL / KBBI KAKU (BLACKLIST MUTLAK):
- Dilarang keras memakai bahasa makalah/KBBI sastra kaku: ("adalah", "tatkala", "terpendar", "kian", "kendati demikian", "merupakan", "tak kunjung", "berada dalam situasi", "mengindikasikan", "beliau", "tiada", "berkata", "berujar", "bersabda").
- BANNED KATA KAKU SEREMPET KBBI: DILARANG memakai kata kaku klise seperti "mencicit", "menukas", "menimpali", "tersenyum simpul", "bergumam", "meracau"! Gantilah dengan bahasa tongkrongan alami: bisik gemeteran, ngomong lirih, nyamber, nyolot, nyeletuk, motong omongan, senyum miring, nyengir tipis, ngedumel, ngoceh.
- ANTI-REPETISI VERBA (IKUTI KEKAYAAN NASKAH ASLI): Penulis novel tidak pernah memakai kata kerja aksi/dialog yang sama berulang-ulang! DILARANG mengulang verba yang sama terus-menerus (jangan setiap baris pakai 'mendengus' atau 'terkekeh'). Variasikan secara dinamis: buang napas sinis, narik napas jengkel, nahan tawa, ngelirik tajem, buang muka, dll.
- Narator dan dialog WAJIB memakai bahasa tongkrongan santai sehari-hari: "nggak/ngga", "banget", "udah", "gitu", "bocah", "parah", "bodo amat", "kepo", "gila", "sialan/anjir/brengsek/kampret", "mager", "pusing pala", dll. Kalimat pendek, padat, dan mengalir renyah!
- Boleh ceplas-ceplos, bahasa ngawur, kata kasar, makian, dan umpatan santai selama pas dengan emosi adegan dan karakternya.

GAYA BAHASA & ATURAN MUTLAK:
1. Narasi Fun, Segar, dan Gamblang: Bawakan cerita dengan seru dan hidup. Kalau ada nuansa militer/taktis atau intrik politik kerajaan (seperti Game of Thrones), pertahankan atmosfer ketegangan, kekejaman medan perang, dan bahaya intriknya, tapi sajikan dengan bahasa yang gamblang, renyah, aduhai, dan mantap tanpa bikin jidat mengkerut.
2. Tell, Don't Show: Langsung beri tahu fakta, situasi lapangan, bahaya, dan apa yang ada di pikiran karakter secara tegas dan transparan. Pangkas metafora puitis berbunga-bunga klise yang bikin ngantuk.
3. Dialog Hidup, Alami, & Konsisten: Percakapan antar karakter mengalir seperti orang ngobrol betulan (lu-gue/lo-gue atau gaya obrolan rekan kerja/rekan tempur yang akrab).
4. ATURAN MUTLAK FORMAT DIALOG (WAJIB NAMA LENGKAP: "..."):
   - DILARANG KERAS mengeluarkan dialog yang cuma tanda kutip "..." atau tanda strip tanpa nama pembicara!
   - Setiap tuturan langsung WAJIB diawali format nama lengkap tokoh: Nama Lengkap: "..."
   - Jika di kalimat aslinya tidak tertulis nama atau hanya panggilan/nama sandi, SIMPULKAN dari konteks adegan dan TULIS NAMA LENGKAP TOKOHNYA.
   - KONSISTENSI NAMA LENGKAP BAKU (Gunakan Nama Lengkap, dilarang gonta-ganti/singkat-singkat):
     * Eddard Stark / Ned -> Selalu gunakan: Eddard Stark: "..."
     * Catelyn Stark / Cat -> Selalu gunakan: Catelyn Stark: "..."
     * Jon Snow -> Selalu gunakan: Jon Snow: "..."
     * Tyrion Lannister / The Imp -> Selalu gunakan: Tyrion Lannister: "..."
     * Arya Stark -> Selalu gunakan: Arya Stark: "..."
     * Sansa Stark -> Selalu gunakan: Sansa Stark: "..."
     * Bran Stark -> Selalu gunakan: Bran Stark: "..."
     * Robb Stark -> Selalu gunakan: Robb Stark: "..."
     * Daenerys Targaryen / Dany -> Selalu gunakan: Daenerys Targaryen: "..."
     * Viserys Targaryen -> Selalu gunakan: Viserys Targaryen: "..."
     * Robert Baratheon -> Selalu gunakan: Robert Baratheon: "..."
     * Cersei Lannister -> Selalu gunakan: Cersei Lannister: "..."
     * Jaime Lannister -> Selalu gunakan: Jaime Lannister: "..."
     * Sandor Clegane / The Hound -> Selalu gunakan: Sandor Clegane: "..."
     * Joffrey Baratheon -> Selalu gunakan: Joffrey Baratheon: "..."
     * Theon Greyjoy -> Selalu gunakan: Theon Greyjoy: "..."
     * Domingo Chavez / Chavez / Ding -> Selalu gunakan: Domingo Chavez: "..."
     * John Clark / Clark / John / Rainbow Enam / Bima -> Selalu gunakan: John Clark: "..."
     * Alistair Stanley / Stanley / Al -> Selalu gunakan: Alistair Stanley: "..."
     * Anastasia Steele / Ana -> Selalu gunakan: Anastasia Steele: "..."
     * Christian Grey / Grey -> Selalu gunakan: Christian Grey: "..."
     * Bill Henriksen / Henriksen / Bill -> Selalu gunakan: Bill Henriksen: "..."
     * John Brightling / Brightling -> Selalu gunakan: John Brightling: "..."
     * Dmitriy Popov / Popov -> Selalu gunakan: Dmitriy Popov: "..."
     * Paul Bellow / Bellow / Dokter Bellow -> Selalu gunakan: Paul Bellow: "..."
     * Tim Noonan / Noonan -> Selalu gunakan: Tim Noonan: "..."
     * Peter Covington / Covington -> Selalu gunakan: Peter Covington: "..."
     * Daniel Malloy / Malloy -> Selalu gunakan: Daniel Malloy: "..."
     * Sandy Clark / Sandy -> Selalu gunakan: Sandy Clark: "..."
     * Patricia Chavez / Patsy -> Selalu gunakan: Patricia Chavez: "..."
     * Anastasia Steele / Ana -> Selalu gunakan: Anastasia Steele: "..."
     * Christian Grey / Grey -> Selalu gunakan: Christian Grey: "..."
     * Katherine Kavanagh / Kate -> Selalu gunakan: Katherine Kavanagh: "..."
     * Elliot Grey / Elliot -> Selalu gunakan: Elliot Grey: "..."
     * Mia Grey / Mia -> Selalu gunakan: Mia Grey: "..."
     * Carrick Grey -> Selalu gunakan: Carrick Grey: "..."
     * Grace Trevelyan Grey -> Selalu gunakan: Grace Trevelyan Grey: "..."
     * Jose Rodriguez / Jose -> Selalu gunakan: Jose Rodriguez: "..."
     * Paul Clayton / Paul -> Selalu gunakan: Paul Clayton: "..."
     * Taylor -> Selalu gunakan: Taylor: "..."
     * Mrs. Jones -> Selalu gunakan: Mrs. Jones: "..."
5. PENTING: Pertahankan tag penanda [[ILUSTRASI:...]] persis di posisi adegannya tanpa diubah atau dihapus!
6. Istilah Asli (Loanwords): Pertahankan istilah teknis/senjata/lore asli (misal MP5, flashbang, SOP, briefing, dll.) beserta penjelasan singkat santai dalam kurung jika membingungkan pembaca awam.
${explanationRule}

Naskah mentah:

${text}`;
}

async function callLLMSingle(text: string, styleMode: StyleMode, sanitize = false, simplified = false): Promise<string> {
  const parsedUrl = new URL(CONFIG.proxyUrl);
  let processedText = cleanWatermarks(text);
  if (sanitize || styleMode === 'konosuba' || styleMode === 'overlord') {
    processedText = sanitizeSensitiveWords(processedText);
    processedText = maskCopyrightTokens(processedText);
  }

  const promptContent = buildPrompt(processedText, styleMode, simplified);

  const payload = JSON.stringify({
    model: CONFIG.model,
    messages: [
      { role: 'user', content: promptContent }
    ],
    temperature: styleMode === 'konosuba' ? 0.7 : 0.6,
    stream: false
  });

  const rawResponse = await new Promise<string>((resolve, reject) => {
    const isHttps = parsedUrl.protocol === 'https:';
    const client = isHttps ? https : http;
    const req = client.request({
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'Content-Length': Buffer.byteLength(payload)
      },
      timeout: 180000
    }, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
          resolve(d);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${d}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => req.destroy(new Error('Request Timeout')));
    req.write(payload);
    req.end();
  });

  const parsed = parseSSEorJSON(rawResponse);
  const cleaned = parsed
    .replace(/^Berikut (adalah |ini )?(adaptasi|terjemahan|naskah|hasil|penulisan ulang)[^\n]*:\s*\n+/i, '')
    .replace(/^Tentu,? (ini|berikut) [^\n]*:\s*\n+/i, '')
    .trim();
  return unmaskCopyrightTokens(cleaned);
}

async function handleCooldown(err: any, attempt: number) {
  if (!err) return;
  const msg = err.message || '';
  if (/ECONNREFUSED|ECONNRESET|ETIMEDOUT/i.test(msg)) {
    console.warn(`   ⏳ Koneksi proxy sedang terputus, menunggu 5 detik...`);
    await new Promise(r => setTimeout(r, 5000));
    return;
  }
  const resetMatch = msg.match(/reset after (?:(\d+)m\s*)?(\d+)s/i);
  if (resetMatch || /503|429|UNAVAILABLE|RESOURCE_EXHAUSTED/i.test(msg)) {
    let waitSec = 15 * attempt;
    if (resetMatch) {
      const m = resetMatch[1] ? parseInt(resetMatch[1], 10) : 0;
      const s = parseInt(resetMatch[2], 10);
      waitSec = (m * 60 + s) + 5;
    }
    console.warn(`   ⏳ Server Gemini sedang cooldown/antre (503/429), istirahat ${waitSec} detik...`);
    await new Promise(r => setTimeout(r, waitSec * 1000));
  }
}

function splitTextIntoParts(text: string, targetSize: number): string[] {
  const numParts = Math.max(2, Math.ceil(text.length / targetSize));
  const lines = text.split('\n');
  const subChunks: string[] = [];
  let curLines: string[] = [];
  let curLen = 0;
  const idealPerPart = Math.ceil(text.length / numParts);

  for (const line of lines) {
    curLines.push(line);
    curLen += line.length + 1;
    if (curLen >= idealPerPart) {
      subChunks.push(curLines.join('\n').trim());
      curLines = [];
      curLen = 0;
    }
  }
  if (curLines.length > 0) {
    subChunks.push(curLines.join('\n').trim());
  }
  return subChunks.filter(s => s.length > 0);
}

async function callLLM(text: string, prevContext: string | null, styleMode: StyleMode): Promise<string> {
  // 1. Coba terjemahkan teks utuh terlebih dahulu (Percobaan 1)
  try {
    const res = await callLLMSingle(text, styleMode, false);
    if (!isRefusalResponse(res) && res.length >= 50) {
      return res;
    }
    console.warn(`   ⚠️ Output teks utuh tertolak filter (${res.length} chars). Beralih ke pemecahan sub-chunk adaptif...`);
  } catch (err: any) {
    console.warn(`   ⚠️ Error saat memproses teks utuh: ${err.message}`);
    await handleCooldown(err, 1);
  }

  // 2. Pemecahan adaptif bertingkat: coba ukuran 1800 -> 1100 -> 700 -> 500 chars
  const targetSizes = [1800, 1100, 700, 500];

  for (const targetSize of targetSizes) {
    const subChunks = splitTextIntoParts(text, targetSize);
    console.log(`   ✂️ Membagi chunk bermasalah menjadi ${subChunks.length} sub-bagian (~${targetSize} chars)...`);

    const subResults: string[] = [];
    let allOk = true;

    for (let i = 0; i < subChunks.length; i++) {
      const sub = subChunks[i];
      let subSuccess = false;

      // Beri 3 kali kesempatan untuk sub-bagian ini secara mandiri
      for (let subAttempt = 1; subAttempt <= 3; subAttempt++) {
        try {
          if (i > 0) await new Promise(r => setTimeout(r, 600));

          const subRes = await callLLMSingle(sub, styleMode, subAttempt > 1, subAttempt > 1);
          if (!isRefusalResponse(subRes) && subRes.length >= 30) {
            subResults.push(subRes);
            subSuccess = true;
            break;
          }
          console.warn(`   ⚠️ Sub-bagian [${i + 1}/${subChunks.length}] tertolak filter (${subRes.length} chars). Mencoba ulang sub-bagian ini...`);
        } catch (subErr: any) {
          console.warn(`   ⚠️ Error pada sub-bagian [${i + 1}/${subChunks.length}]: ${subErr.message}`);
          await handleCooldown(subErr, subAttempt);
        }
      }

      if (!subSuccess) {
        allOk = false;
        console.warn(`   ⚠️ Sub-bagian [${i + 1}/${subChunks.length}] gagal pada level ${targetSize} chars. Beralih ke pecahan lebih kecil...`);
        break;
      }
    }

    if (allOk && subResults.length === subChunks.length) {
      console.log(`   ✅ Seluruh ${subChunks.length} sub-bagian sukses diterjemahkan dan digabungkan!`);
      return subResults.join('\n\n');
    }
  }

  throw new Error('LLM Translation Failed after multi-tier adaptive sub-chunking.');
}

async function mapConcurrent<T, R>(items: T[], limit: number, fn: (item: T, i: number) => Promise<R>): Promise<R[]> {
  const results = new Array<R>(items.length);
  let nextIdx = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (nextIdx < items.length) {
      const cur = nextIdx++;
      results[cur] = await fn(items[cur], cur);
    }
  });
  await Promise.all(workers);
  return results;
}

async function main() {
  console.log('================================================================');
  console.log('🚇 NOVEL TRANSLATOR - DRAG & DROP RUNNER (DIRECT & GAUL)');
  console.log('================================================================');

  let targetFile = process.argv[2];

  if (!targetFile) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    targetFile = await new Promise<string>(res => {
      rl.question('👉 Seret & Lepas (Drag & Drop) file .epub atau .txt ke sini lalu tekan ENTER:\n> ', ans => {
        rl.close();
        res(ans.trim().replace(/^["']|["']$/g, ''));
      });
    });
  }

  targetFile = path.resolve(targetFile.replace(/^["']|["']$/g, ''));

  if (!fs.existsSync(targetFile)) {
    console.error(`❌ File tidak ditemukan: ${targetFile}`);
    process.exit(1);
  }

  const ext = path.extname(targetFile).toLowerCase();
  const baseName = path.basename(targetFile, ext);
  const dirName = path.dirname(targetFile);

  const outputFile = path.join(dirName, `${baseName} (Terjemahan ID-Direct).txt`);
  const checkpointFile = path.join(dirName, `${baseName}_checkpoint.json`);
  const cacheDir = path.join(dirName, `.${baseName}_chunks_cache`);

  const isDxd = /high\s*school\s*dxd|dxd/i.test(targetFile);
  const isKonosuba = /konosuba|kono\s*subarashii/i.test(targetFile);
  const isWarhammer = /horus|warhammer|astartes|dan\s*abnett/i.test(targetFile);
  const isHobbit = /hobbit|tolkien|lotr|baggins/i.test(targetFile);
  const isOverlord = /overlord|ainz|nazarick|momonga/i.test(targetFile);
  const isMushoku = /mushoku|rudeus|greyrat/i.test(targetFile);
  const isDune = /dune|frank\s*herbert|arrakis|atreides/i.test(targetFile);
  const isMetro = /metro\s*2033|glukhovsky|artyom|vdnkh/i.test(targetFile);
  const isExpanse = /expanse|leviathan\s*wakes|caliban|abaddon|cibola|nemesis\s*games|babylon|persepolis|tiamat/i.test(targetFile);
  const isHarryPotter = /harry\s*potter|batu\s*bertuah|kamar\s*rahasia|tawanan\s*azkaban|piala\s*api|orde\s*phoenix|pangeran\s*berdarah|relikui\s*kematian/i.test(targetFile);
  const isLapidus = /history\s*of\s*islamic\s*societies|lapidus/i.test(targetFile);
  const isCarl = /dungeon\s*crawler\s*carl|matt\s*dinniman|princess\s*donut/i.test(targetFile);
  const styleMode: StyleMode = isCarl ? 'carl' : (isLapidus ? 'comic_history' : (isDxd ? 'dxd' : (isHarryPotter ? 'harrypotter' : (isExpanse ? 'expanse' : (isMetro ? 'metro' : (isDune ? 'dune' : (isKonosuba ? 'konosuba' : (isWarhammer ? 'warhammer' : (isHobbit ? 'hobbit' : (isOverlord ? 'overlord' : (isMushoku ? 'mushoku' : 'default')))))))))));

  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  console.log(`\n📁 File Input   : ${targetFile}`);
  console.log(`📄 File Output  : ${outputFile}`);
  console.log(`🔖 Checkpoint   : ${checkpointFile}`);
  console.log(`📂 Chunk Cache  : ${cacheDir}`);
  console.log(`⚡ Concurrency  : ${CONFIG.concurrency} Workers | Model: ${CONFIG.model}`);
  
  let styleDesc = 'Laga Aksi Luwes (Tell-Don\'t-Show, To-The-Point)';
  if (styleMode === 'carl') styleDesc = 'Dungeon Crawler Carl (Komedi Gelap LitRPG, No Sensor, Tell-Don\'t-Show, Gaul Gue-Lu, Notifikasi Game Sadis & Satir)';
  if (styleMode === 'harrypotter') styleDesc = 'Harry Potter Gaul Sihir Remake (No-Sensor, Gaul Tongkrongan Asrama Gryffindor Gue-Lu, Dialog Wajib Bernama Lengkap, Nol Kata Kaku)';
  if (styleMode === 'expanse') styleDesc = 'Hard Sci-Fi Space Opera The Expanse (No Sensor, Gaul Luar Angkasa Gue-Lu, Dialog Lengkap Bernama, Istilah Belter & Propulsi Presisi)';
  if (styleMode === 'metro') styleDesc = 'Sci-Fi Survival Post-Apokaliptik Metro 2033 (Tell-Don\'t-Show, Tegang & Gaul Stalker, Peta Terowongan)';
  if (styleMode === 'dune') styleDesc = 'Sci-Fi Epik Dune (Tell-Don\'t-Show, Intrik Feudal Arrakis, Istilah Lore Asli)';
  if (styleMode === 'warhammer') styleDesc = 'Sci-Fi Militer Grimdark Warhammer 40k (Badass, Tell-Don\'t-Show, Taktis & Gaul Prajurit)';
  if (styleMode === 'konosuba') styleDesc = 'Light Novel Komedi Isekai (Tell-Don\'t-Show, Manga Pacing, Gaul)';
  if (styleMode === 'comic_history') styleDesc = 'Komik/Webtoon Sejarah Islam (Epic, Dramatic, Punchy, To-The-Point, Fakta & Peta Utuh, Nol Kaku)';
  if (styleMode === 'hobbit') styleDesc = 'Petualangan Fantasi Modern Middle-earth (Tell-Don\'t-Show, Santai/Gaul, Peta & Ilustrasi)';
  if (styleMode === 'overlord') styleDesc = 'Dark Fantasy Anti-Hero (Ainz Monolog vs Wibawa Penguasa, Tell-Don\'t-Show, Taktis & Badass)';
  if (styleMode === 'dxd') styleDesc = 'High School DxD (No Sensor, Mesum Frontal, Tongkrongan Gaul Gue-Lu, Dialog Bernama Lengkap, Ilustrasi Presisi)';
  if (styleMode === 'mushoku') styleDesc = 'Fantasy Isekai Petualangan Hidup Baru (Rudy Otaku Mesum vs Tobat & Dewasa, Tell-Don\'t-Show, Gaul & Kocak)';
  console.log(`🎨 Style Mode   : ${styleDesc}\n`);

  let chapters: Chapter[] = [];
  if (ext === '.epub') {
    chapters = extractEpubChapters(targetFile);
  } else if (ext === '.txt') {
    chapters = extractTxtChapters(targetFile);
  } else {
    console.error('❌ Format file tidak didukung! Harap masukkan file .epub atau .txt');
    process.exit(1);
  }

  console.log(`✅ Berhasil mendeteksi ${chapters.length} Bab dari file.\n`);

  // Auto-init project di SQLite novel_pipeline.db
  const projectId = baseName.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const dbBridgeScript = path.resolve(__dirname, 'core_engine', 'src', 'database', 'db_bridge.py');
  if (fs.existsSync(dbBridgeScript)) {
    try {
      execSync(`python "${dbBridgeScript}" init_project "${projectId}" "${baseName}" "${targetFile}" "${styleMode}" ${chapters.length}`, { stdio: 'pipe' });
      console.log(`📡 Telemetri DB: Proyek '${projectId}' terdaftar di localhost:3000`);
    } catch {}
  }

  let checkpoint = { completedIds: [] as string[] };
  if (fs.existsSync(checkpointFile)) {
    try {
      checkpoint = JSON.parse(fs.readFileSync(checkpointFile, 'utf-8'));
    } catch {}
  }

  function assembleFullOutput() {
    let assembled = '';
    for (const ch of chapters) {
      const chapCacheDir = path.join(cacheDir, ch.id);
      if (fs.existsSync(chapCacheDir)) {
        const chunkFiles = fs.readdirSync(chapCacheDir)
          .filter(f => f.startsWith('chunk_') && f.endsWith('.txt'))
          .sort();
        const parts = chunkFiles.map(cf => fs.readFileSync(path.join(chapCacheDir, cf), 'utf-8'));
        assembled += `\n\n### ${ch.title}\n\n${parts.join('\n\n')}\n\n`;
      }
    }
    fs.writeFileSync(outputFile, assembled.trim() + '\n', 'utf-8');
  }

  for (let i = 0; i < chapters.length; i++) {
    const ch = chapters[i];

    if (checkpoint.completedIds.includes(ch.id)) {
      console.log(`⏭️  [${i + 1}/${chapters.length}] Lewati: ${ch.title} (Sudah selesai)`);
      continue;
    }

    console.log(`----------------------------------------------------------------`);
    console.log(`📖 [${i + 1}/${chapters.length}] Memproses: ${ch.title} (~${ch.text.length} karakter)`);
    console.log(`----------------------------------------------------------------`);

    const chapCacheDir = path.join(cacheDir, ch.id);
    if (!fs.existsSync(chapCacheDir)) {
      fs.mkdirSync(chapCacheDir, { recursive: true });
    }

    const chunks = splitParagraphSafe(ch.text, CONFIG.maxChunkChars);
    console.log(`📦 Dibagi menjadi ${chunks.length} bagian chunk...`);

    const startT = Date.now();
    const translatedParts = await mapConcurrent(chunks, CONFIG.concurrency, async (chunkText, idx) => {
      const chunkFile = path.join(chapCacheDir, `chunk_${String(idx + 1).padStart(3, '0')}.txt`);

      if (fs.existsSync(chunkFile)) {
        const cached = fs.readFileSync(chunkFile, 'utf-8');
        if (!isRefusalResponse(cached) && cached.length > 50) {
          console.log(`   ⚡ Bagian [${idx + 1}/${chunks.length}] dimuat dari cache lokal.`);
          return cached;
        } else {
          fs.rmSync(chunkFile, { force: true });
        }
      }

      const cleanChunk = cleanWatermarks(chunkText).trim();
      const nonIllustLines = cleanChunk.split('\n')
        .map(l => l.trim())
        .filter(l => l.length > 0 && !/^\[\[ILUSTRASI:[^\]]+\]\]$/i.test(l));

      const hasIllust = cleanChunk.includes('[[ILUSTRASI:');
      const nonIllustText = nonIllustLines.join(' ').trim();

      if (hasIllust && (nonIllustLines.length === 0 || nonIllustText.length < 60)) {
        console.log(`   🖼️ Bagian [${idx + 1}/${chunks.length}] adalah galeri ilustrasi, dipertahankan.`);
        fs.writeFileSync(chunkFile, cleanChunk, 'utf-8');
        return cleanChunk;
      }

      const prevContext = idx > 0 ? chunks[idx - 1] : null;
      const tStart = Date.now();
      const res = await callLLM(cleanChunk, prevContext, styleMode);
      const dur = ((Date.now() - tStart) / 1000).toFixed(1);

      fs.writeFileSync(chunkFile, res, 'utf-8');
      console.log(`   ⚡ Bagian [${idx + 1}/${chunks.length}] selesai (${dur}s) & dicache`);
      return res;
    });

    const totalDur = ((Date.now() - startT) / 1000).toFixed(1);
    console.log(`✅ Bab selesai dalam ${totalDur}s`);

    checkpoint.completedIds.push(ch.id);
    fs.writeFileSync(checkpointFile, JSON.stringify(checkpoint, null, 2), 'utf-8');
    assembleFullOutput();
    console.log(`💾 Bab tersimpan ke output dan checkpoint.`);

    // Auto-update chapter progress & snapshot to SQLite DB
    if (fs.existsSync(dbBridgeScript)) {
      try {
        const transChapText = translatedParts.join('\n\n');
        const tempChapFile = path.join(chapCacheDir, '_chapter_merged.tmp');
        fs.writeFileSync(tempChapFile, transChapText, 'utf-8');
        execSync(`python "${dbBridgeScript}" update_chapter "${projectId}" "${ch.id}" ${i + 1} "${ch.title.replace(/"/g, "'")}" ${transChapText.length} "completed" "${tempChapFile}"`, { stdio: 'pipe' });
        fs.rmSync(tempChapFile, { force: true });
      } catch {}
    }
  }

  // Final assembly to ensure complete output file
  assembleFullOutput();

  if (fs.existsSync(dbBridgeScript)) {
    try {
      execSync(`python "${dbBridgeScript}" finish_project "${projectId}"`, { stdio: 'pipe' });
    } catch {}
  }

  console.log('\n================================================================');
  console.log('🎉 PROSES TERJEMAHAN SELESAI!');
  console.log(`📁 File hasil tersimpan di: ${outputFile}`);
  console.log('================================================================');

  if (ext === '.epub' || isOverlord) {
    console.log('\n📚 Mengompilasi naskah menjadi berkas EPUB berilustrasi lengkap...');
    const epubOutDir = path.join(dirName, 'epubs');
    if (!fs.existsSync(epubOutDir)) fs.mkdirSync(epubOutDir, { recursive: true });
    const epubOutFile = path.join(epubOutDir, `${baseName} (Illustrated ID-Direct).epub`);
    
    // Auto-mirror ke folder pusat HASIL_TERJEMAHAN
    const centralEpubDir = path.resolve(__dirname, 'HASIL_TERJEMAHAN', 'EPUB_SIAP_BACA');
    const centralTxtDir = path.resolve(__dirname, 'HASIL_TERJEMAHAN', 'NASKAH_TXT');
    if (!fs.existsSync(centralEpubDir)) fs.mkdirSync(centralEpubDir, { recursive: true });
    if (!fs.existsSync(centralTxtDir)) fs.mkdirSync(centralTxtDir, { recursive: true });
    
    try {
      let helperScript = path.resolve('E:/antigravity-novel-engine/compile_epub_helper.py');
      if (!fs.existsSync(helperScript)) {
        helperScript = path.join(dirName, 'compile_epub_helper.py');
      }
      if (!fs.existsSync(helperScript)) {
        helperScript = path.resolve(process.cwd(), 'compile_epub_helper.py');
      }
      execSync(`python "${helperScript}" "${outputFile}" "${targetFile}" "${epubOutFile}"`, { stdio: 'inherit' });
      // Salin langsung ke HASIL_TERJEMAHAN
      try {
        fs.copyFileSync(epubOutFile, path.join(centralEpubDir, path.basename(epubOutFile)));
        fs.copyFileSync(outputFile, path.join(centralTxtDir, path.basename(outputFile)));
        console.log(`📁 Berhasil disimpan rapi ke: HASIL_TERJEMAHAN/EPUB_SIAP_BACA`);
      } catch {}
    } catch (e: any) {
      console.warn('⚠️ Catatan kompilasi EPUB:', e.message);
    }
  }

  // Auto Git-Sync On Completion (GitHub First)
  try {
    console.log('\n🔄 Sinkronisasi otomatis ke GitHub...');
    execSync(`git add "${outputFile}" "${checkpointFile}" "${targetFile}" core_engine/novel_pipeline.db`, { stdio: 'pipe' });
    execSync(`git commit -m "feat(novel): complete translation for ${baseName}"`, { stdio: 'pipe' });
    execSync(`git push origin main`, { stdio: 'pipe' });
    console.log('🚀 Berhasil disinkronkan ke repo GitHub origin main!');
  } catch (gitErr: any) {
    console.log('ℹ️ Catatan Git-Sync: Naskah lokal aman, sync ditunda.');
  }
}

main().catch(err => {
  console.error('\n❌ Terjadi kesalahan fatal:', err);
  process.exit(1);
});
