#!/usr/bin/env node
/**
 * High-Speed Turbo Batch Text Translator (Vol 01-24)
 * 
 * Performance & Robustness Optimizations:
 * - Chunk size dioptimalkan (~7,500 chars) untuk mencegah respon LLM terpotong (max_tokens).
 * - Context overlap: Menyertakan baris sebelumnya sebagai referensi adegan agar dialog speaker tidak tertukar/halusinasi.
 * - Dynamic HTTP/HTTPS: Mendukung proxy lokal maupun remote secure proxy secara otomatis.
 * - Truncation & Finish-reason checking: Mendeteksi apakah LLM mencapai batas panjang token.
 * - Idempotent & Atomic Staging: Bab tersimpan di `.chapters_cache/` sebelum digabungkan, mencegah teks duplikat saat resume/crash.
 * - Multi-Worker Concurrency: 6 parallel workers dengan urutan chunk terjamin.
 * - Strict Heading Parsing: Mencegah teks narasi cerita salah terdeteksi sebagai bab baru.
 * - Graceful Exit (Ctrl+C): Menyelesaikan bab aktif dan menyimpan checkpoint sebelum keluar.
 */

import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import http from 'node:http';
import https from 'node:https';

interface Config {
  inputFile: string;
  outputFile: string;
  checkpointFile: string;
  proxyUrl: string;
  model: string;
  apiKey: string;
  maxChunkChars: number;
  concurrency: number;
}

const CONFIG: Config = {
  inputFile: 'D:/JV/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records - Volume 01/Rokudenashi Majutsu Koushi to Akashic Records - Volume 01-24.txt',
  outputFile: 'D:/JV/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records - Volume 01/Rokudenashi Majutsu Koushi to Akashic Records - Volume 01-24 (ID-Gaul-Combined).txt',
  checkpointFile: 'D:/JV/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records/[Ruidrive] Rokudenashi Majutsu Koushi to Akashic Records - Volume 01/batch-checkpoint.json',
  proxyUrl: 'http://127.0.0.1:20128/v1/chat/completions',
  model: 'ag/gemini-3.8-flash-low',
  apiKey: 'sk-2c1573f206deb3a0-ryos2n-4198badd',
  maxChunkChars: 7500, // Dioptimalkan dari 15.000 ke 7.500 agar tidak melewati batas output token
  concurrency: 3 // Turbo (3 workers paralel) dengan auto-cooldown handling
};

const SYSTEM_PROMPT = `Kamu adalah penerjemah + asisten pembaca Light Novel profesional ke Bahasa Indonesia.

TUGAS UTAMA (PRIORITAS TERTINGGI):
1. Terjemahkan CONTENT ke bahasa Indonesia yang santai sehari-hari, gaul, konyol, lucu, dan vulgar (sesuai karakter dan situasi). Bahasa harus hidup, alami, dan menghibur.
2. Dialog boleh pakai "gue/lu" atau umpatan/kata-kata kasar santai sehari-hari jika sesuai dengan emosi dan kepribadian karakter (contoh: Glenn Radars yang mageran, sinis, dan blak-blakan).
3. Karakter formal, bangsawan, guru, atau tokoh tua tetap dijaga kesopanannya sesuai peran (contoh: Rumia Tingel yang santun, Celica Arfonia yang anggun/mengintimidasi, atau Sistine Fibel yang tsundere).
4. FORMAT DIALOG: Selalu sertakan NAMA SPEAKER pada dialog secara konsisten dengan format:
   Nama: "Isi dialog..."
   (Contoh: Glenn Radars: "Hah?! Sialan, mager banget gila...", Sistine Fibel: "Dasar guru mesum nggak guna!").
5. JANGAN mengubah alur, kejadian, dialog, atau informasi penting. Hanya gaya bahasa dan suasana yang dibuat santai, kocak, dan menarik.
6. Source adalah raja. Jangan menambah atau mengurangi isi cerita.
7. Jangan spoiler dari chapter/scene berikutnya.
8. PENTING: Jika teks masukan menyertakan [KONTEKS SEBELUMNYA], jadikan bagian itu HANYA sebagai acuan pemahaman adegan & siapa pembicara. JANGAN PERNAH menerjemahkan ulang bagian [KONTEKS SEBELUMNYA]. HANYA terjemahkan isi dari [TEKS YANG HARUS DITERJEMAHKAN].

GAYA BAHASA:
- Santai sehari-hari, gaul, konyol, lucu, dan kocak.
- Boleh kasar, vulgar, dan santai selama sesuai karakter dan situasi.
- Kalimat pendek, padat, dan tidak kaku (tanpa kalimat puitis/berbunga-bunga klise).
- Karakterisasi tokoh tetap dijaga ketat.
- Bikin pembaca ketawa dan enjoy membaca cerita.

NOTES / KOMENTAR (PENJELASAN ISTILAH & FUN FACT):
- Tambahkan komentar penjelasan istilah atau fun fact singkat dalam tanda kurung siku [Catatan: ...] atau (fun fact: ...) yang RELEVAN dengan istilah asing, sihir, atau budaya yang membingungkan pembaca awam.
- Fun fact singkat, kontekstual, dan jangan menciptakan lore palsu/spoiler.

Output HANYA teks hasil terjemahan yang rapi tanpa kata pengantar atau penutup.`;

interface ChapterInfo {
  id: string;
  volNum: number;
  title: string;
  lines: string[];
}

interface Checkpoint {
  lastCompletedId: string | null;
  completedIds: string[];
  totalChapters: number;
  lastUpdated: string;
}

interface ChunkItem {
  index: number;
  total: number;
  text: string;
  contextBefore?: string;
}

let isShuttingDown = false;
process.on('SIGINT', () => {
  if (isShuttingDown) {
    console.log('\n[Warning] Paksa berhenti...');
    process.exit(1);
  }
  console.log('\n\n🛑 Menerima sinyal berhenti (Ctrl+C). Menyelesaikan bab yang sedang aktif sebelum keluar...');
  isShuttingDown = true;
});

function resolvePaths(config: Config): Config {
  let resolvedInput = config.inputFile;
  let resolvedOutput = config.outputFile;
  let resolvedCheckpoint = config.checkpointFile;

  // Fallback otomatis ke file lokal jika path di D:/ tidak ditemukan
  if (!fs.existsSync(resolvedInput)) {
    const localInput = path.resolve('Rokudenashi Majutsu Koushi to Akashic Records - Volume 01-24.txt');
    if (fs.existsSync(localInput)) {
      console.log(`ℹ️ [Info] Path input D:/ tidak ditemukan. Otomatis dialihkan ke file lokal:`);
      console.log(`   ${localInput}`);
      resolvedInput = localInput;
      resolvedOutput = path.resolve('Rokudenashi Majutsu Koushi to Akashic Records - Volume 01-24 (ID-Gaul-Combined).txt');
      resolvedCheckpoint = path.resolve('batch-checkpoint.json');
    }
  }

  // Buat direktori output & checkpoint bila belum ada
  const outDir = path.dirname(resolvedOutput);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const cpDir = path.dirname(resolvedCheckpoint);
  if (!fs.existsSync(cpDir)) {
    fs.mkdirSync(cpDir, { recursive: true });
  }

  return {
    ...config,
    inputFile: resolvedInput,
    outputFile: resolvedOutput,
    checkpointFile: resolvedCheckpoint
  };
}

function loadCheckpoint(cpFile: string): Checkpoint {
  if (fs.existsSync(cpFile)) {
    try {
      const data = JSON.parse(fs.readFileSync(cpFile, 'utf-8'));
      return {
        lastCompletedId: data.lastCompletedId || null,
        completedIds: Array.isArray(data.completedIds) ? data.completedIds : [],
        totalChapters: data.totalChapters || 0,
        lastUpdated: data.lastUpdated || new Date().toISOString()
      };
    } catch {
      // ignore
    }
  }
  return { lastCompletedId: null, completedIds: [], totalChapters: 0, lastUpdated: new Date().toISOString() };
}

function saveCheckpoint(cpFile: string, cp: Checkpoint) {
  cp.lastUpdated = new Date().toISOString();
  fs.writeFileSync(cpFile, JSON.stringify(cp, null, 2), 'utf-8');
}

async function parseAllVolumesAndChapters(filePath: string): Promise<ChapterInfo[]> {
  const fileStream = fs.createReadStream(filePath, { encoding: 'utf-8' });
  const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

  const chapters: ChapterInfo[] = [];
  let currentVol = 1;
  let currentChapter: ChapterInfo | null = null;
  let inTocOrDisclaimer = true;

  for await (const rawLine of rl) {
    const line = rawLine.trim();

    const volMatch = rawLine.match(/^ROKUDENASHI MAJUTSU KOUSHI TO AKASHIC RECORDS - VOLUME (\d+)/i);
    if (volMatch) {
      currentVol = parseInt(volMatch[1], 10);
      inTocOrDisclaimer = true;
      continue;
    }

    if (!line) continue;
    if (/^ruidrive\.com$/i.test(line)) continue;
    if (/^Volume \d+$/i.test(line)) continue;
    if (/^QWER - image\d+\./i.test(line)) continue;
    if (/^PDF by:/i.test(line)) continue;

    // Heading ketat: pastikan bukan kalimat narasi panjang dan memiliki format judul bab yang valid
    const isHeading = /^(Prolog(ue)?|Epilog(ue)?|Kata Penutup|Afterword)(\s*[:–—\-].*|$)|^Bab \d+(\s*[:–—\-].*|$)|^Chapter \d+(\s*[:–—\-].*|$)/i.test(line) && line.length <= 120;

    if (isHeading) {
      // Lewati karakter bullet TOC yang rusak atau baris terlalu pendek
      if (rawLine.includes('') || line.length < 3) {
        continue;
      }

      inTocOrDisclaimer = false;

      if (currentChapter && currentChapter.lines.length > 0) {
        chapters.push(currentChapter);
      }

      const chapterIndex = chapters.filter(c => c.volNum === currentVol).length + 1;
      const chId = `vol${String(currentVol).padStart(2, '0')}_ch${String(chapterIndex).padStart(2, '0')}`;

      currentChapter = {
        id: chId,
        volNum: currentVol,
        title: line,
        lines: []
      };
      continue;
    }

    if (inTocOrDisclaimer) continue;

    if (currentChapter) {
      currentChapter.lines.push(line);
    }
  }

  if (currentChapter && currentChapter.lines.length > 0) {
    chapters.push(currentChapter);
  }

  return chapters;
}

function splitIntoChunksWithContext(lines: string[], maxChars: number): ChunkItem[] {
  const rawChunks: string[] = [];
  let currentChunk: string[] = [];
  let currentLength = 0;

  for (const line of lines) {
    currentChunk.push(line);
    currentLength += line.length + 1;

    if (currentLength >= maxChars) {
      rawChunks.push(currentChunk.join('\n'));
      currentChunk = [];
      currentLength = 0;
    }
  }

  if (currentChunk.length > 0) {
    rawChunks.push(currentChunk.join('\n'));
  }

  return rawChunks.map((chunkText, idx) => {
    let contextBefore: string | undefined;
    if (idx > 0) {
      // Ambil 3-4 baris terakhir dari chunk sebelumnya sebagai referensi kontinuitas narasi & speaker
      const prevLines = rawChunks[idx - 1]
        .split('\n')
        .map(l => l.trim())
        .filter(l => l.length > 0);
      contextBefore = prevLines.slice(-4).join('\n');
    }

    return {
      index: idx + 1,
      total: rawChunks.length,
      text: chunkText,
      contextBefore
    };
  });
}

function parseResetSeconds(errMsg: string): number | null {
  const m = errMsg.match(/reset after\s+(?:(\d+)\s*m(?:in)?)?\s*(?:(\d+)\s*s)?/i);
  if (m && (m[1] || m[2])) {
    const mins = m[1] ? parseInt(m[1], 10) : 0;
    const secs = m[2] ? parseInt(m[2], 10) : 0;
    return (mins * 60) + secs;
  }
  return null;
}

async function callLLM(chunk: ChunkItem, config: Config, retryCount = 15): Promise<string> {
  let promptUser = '';
  if (chunk.contextBefore) {
    promptUser += `[KONTEKS SEBELUMNYA (HANYA REFERENSI ALUR/SPEAKER - JANGAN DITERJEMAHKAN)]:\n${chunk.contextBefore}\n\n---\n\n`;
  }
  promptUser += `[TEKS YANG HARUS DITERJEMAHKAN]:\n\n${chunk.text}`;

  const payload = JSON.stringify({
    model: config.model,
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: promptUser }
    ],
    temperature: 0.7,
    max_tokens: 8192,
    stream: false
  });

  const parsedUrl = new URL(config.proxyUrl);
  const isHttps = parsedUrl.protocol === 'https:';
  const client = isHttps ? https : http;
  const port = parsedUrl.port || (isHttps ? 443 : 80);

  for (let attempt = 1; attempt <= retryCount; attempt++) {
    if (isShuttingDown) throw new Error('Dibatalkan oleh pengguna.');

    try {
      const responseText = await new Promise<string>((resolve, reject) => {
        const req = client.request({
          hostname: parsedUrl.hostname,
          port: port,
          path: parsedUrl.pathname + parsedUrl.search,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': `Bearer ${config.apiKey}`,
            'Content-Length': Buffer.byteLength(payload)
          },
          timeout: 180000 // 3 minutes timeout
        }, (res) => {
          let data = '';
          res.on('data', chunkData => data += chunkData);
          res.on('end', () => {
            if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
              try {
                let content = '';
                // Tangani respons berformat SSE (data: {...}) maupun standard JSON
                if (data.trim().startsWith('data:')) {
                  const lines = data.split('\n');
                  for (const l of lines) {
                    const trimmed = l.trim();
                    if (trimmed.startsWith('data:') && !trimmed.includes('[DONE]')) {
                      try {
                        const chunkJson = JSON.parse(trimmed.replace(/^data:\s*/, ''));
                        const piece = chunkJson.choices?.[0]?.delta?.content || chunkJson.choices?.[0]?.message?.content || '';
                        content += piece;
                      } catch {}
                    }
                  }
                } else {
                  const json = JSON.parse(data);
                  const choice = json.choices?.[0];
                  content = choice?.message?.content || '';

                  if (choice?.finish_reason === 'length') {
                    console.warn(`\n⚠️  [Warning] Output chunk [${chunk.index}/${chunk.total}] terpotong karena mencapai batas max_tokens!`);
                  }
                }

                if (!content.trim()) {
                  reject(new Error('LLM mengembalikan respons kosong.'));
                  return;
                }

                resolve(content);
              } catch (err) {
                reject(new Error(`Gagal mem-parse response JSON: ${err}`));
              }
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${data}`));
            }
          });
        });

        req.on('error', reject);
        req.on('timeout', () => {
          req.destroy(new Error('Request timeout setelah 180s'));
        });

        req.write(payload);
        req.end();
      });

      return responseText.trim();
    } catch (err: any) {
      if (isShuttingDown) throw err;
      const errMsg = String(err?.message || '');
      console.warn(`   ⚠️ [Chunk ${chunk.index}/${chunk.total} - Percobaan ${attempt}/${retryCount}]: ${errMsg.substring(0, 150)}...`);

      if (attempt === retryCount) throw err;

      // Adaptive Backoff: Cek petunjuk cooldown waktu dari Google (misal: "reset after 2m 8s", "reset after 34s")
      let waitMs = 3000 * attempt;
      const resetSec = parseResetSeconds(errMsg);

      if (resetSec !== null && resetSec > 0) {
        waitMs = (resetSec + 3) * 1000; // tunggu jeda server + toleransi 3 detik
        console.log(`   ⏳ [Cooldown Kuota] Server meminta jeda ${resetSec}s. Menunggu ${(waitMs / 1000).toFixed(0)}s secara otomatis...`);
      } else if (errMsg.includes('503') || errMsg.includes('429') || errMsg.includes('CAPACITY') || errMsg.includes('OVERLOADED')) {
        waitMs = Math.min(45000, (Math.pow(2, Math.min(attempt, 5)) * 2000) + Math.floor(Math.random() * 2000));
        console.log(`   ⏳ [Server Sibuk] Menunggu ${(waitMs / 1000).toFixed(1)}s sebelum mencoba kembali...`);
      }

      await new Promise(r => setTimeout(r, waitMs));
    }
  }

  throw new Error('LLM call gagal setelah semua percobaan ulang.');
}

// Multi-worker pool helper to process items concurrently while preserving index
async function mapConcurrent<T, R>(items: T[], limit: number, fn: (item: T, index: number) => Promise<R>): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let nextIdx = 0;

  async function worker(workerId: number) {
    if (workerId > 0) {
      await new Promise(r => setTimeout(r, workerId * 1500));
    }
    while (nextIdx < items.length) {
      if (isShuttingDown) break;
      const current = nextIdx++;
      results[current] = await fn(items[current], current);
      // Pacing 2.5 detik antar-chunk agar rolling token-per-minute (TPM) quota tetap stabil
      if (nextIdx < items.length && !isShuttingDown) {
        await new Promise(r => setTimeout(r, 2500));
      }
    }
  }

  const workers = Array.from({ length: Math.min(limit, items.length) }, (_, i) => worker(i));
  await Promise.all(workers);
  return results;
}

function getChapterCachePath(cacheDir: string, chId: string): string {
  return path.join(cacheDir, `${chId}.txt`);
}

function rebuildOutputFile(outputFile: string, chapters: ChapterInfo[], completedIds: string[], cacheDir: string) {
  const parts: string[] = [];
  let lastVol = 0;

  for (const ch of chapters) {
    if (!completedIds.includes(ch.id)) continue;
    const chFile = getChapterCachePath(cacheDir, ch.id);
    if (fs.existsSync(chFile)) {
      let volumeHeader = '';
      if (ch.volNum !== lastVol) {
        volumeHeader = `\n\n${'='.repeat(80)}\nROKUDENASHI MAJUTSU KOUSHI TO AKASHIC RECORDS - VOLUME ${String(ch.volNum).padStart(2, '0')}\n${'='.repeat(80)}\n\n`;
        lastVol = ch.volNum;
      }
      const chContent = fs.readFileSync(chFile, 'utf-8');
      parts.push(`${volumeHeader}### [VOLUME ${String(ch.volNum).padStart(2, '0')}] ${ch.title}\n\n${chContent}\n\n`);
    }
  }

  fs.writeFileSync(outputFile, parts.join(''), 'utf-8');
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m > 60) {
    const h = Math.floor(m / 60);
    const rm = m % 60;
    return `${h}j ${rm}m`;
  }
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

async function main() {
  const config = resolvePaths(CONFIG);
  const cacheDir = path.join(path.dirname(config.checkpointFile), '.chapters_cache');
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  console.log('================================================================');
  console.log('⚡ TURBO MULTI-WORKER BATCH TRANSLATOR (VOL 01 - 24)');
  console.log('================================================================');
  console.log(`📁 Input File       : ${config.inputFile}`);
  console.log(`📄 Output File      : ${config.outputFile}`);
  console.log(`🔖 Checkpoint File  : ${config.checkpointFile}`);
  console.log(`🗄️  Staging Cache    : ${cacheDir}`);
  console.log(`⚡ Concurrency       : ${config.concurrency} parallel workers`);
  console.log(`📦 Chunk Size       : ~${config.maxChunkChars} characters (Context-Overlap enabled)`);
  console.log('================================================================\n');

  console.log('🔍 Memindai file sumber dan mengurai struktur volume...');
  const chapters = await parseAllVolumesAndChapters(config.inputFile);
  console.log(`✅ Berhasil mendeteksi ${chapters.length} Bab dari seluruh 24 Volume.\n`);

  const checkpoint = loadCheckpoint(config.checkpointFile);
  checkpoint.totalChapters = chapters.length;

  // Pastikan file output sinkron dengan checkpoint jika melanjutkan
  if (checkpoint.completedIds.length > 0) {
    console.log(`🔄 Menyinkronkan file output dengan ${checkpoint.completedIds.length} bab yang sudah tersimpan...`);
    rebuildOutputFile(config.outputFile, chapters, checkpoint.completedIds, cacheDir);
  }

  const overallStartTime = Date.now();
  let processedThisSession = 0;
  let totalTimeThisSession = 0;

  for (let i = 0; i < chapters.length; i++) {
    if (isShuttingDown) break;

    const ch = chapters[i];
    const progressPercent = ((i / chapters.length) * 100).toFixed(1);

    if (checkpoint.completedIds.includes(ch.id)) {
      console.log(`⏭️  [${i + 1}/${chapters.length} - ${progressPercent}%] Lewati ${ch.id} (${ch.title}) - Sudah selesai.`);
      continue;
    }

    console.log(`\n----------------------------------------------------------------`);
    console.log(`📖 [${i + 1}/${chapters.length} - ${progressPercent}%] Memproses: Volume ${ch.volNum} - ${ch.title} (${ch.lines.length} baris)`);
    console.log(`----------------------------------------------------------------`);

    const chunks = splitIntoChunksWithContext(ch.lines, config.maxChunkChars);
    console.log(`📦 Dibagi menjadi ${chunks.length} chunk. Menjalankan paralel (${config.concurrency} workers)...`);

    const chStartTime = Date.now();
    let translatedChunks: string[] = [];
    let chapterSuccess = false;

    while (!chapterSuccess && !isShuttingDown) {
      try {
        translatedChunks = await mapConcurrent(chunks, config.concurrency, async (chunk, idx) => {
          // Cek apakah chunk ini sudah pernah berhasil diterjemahkan sebelumnya
          const chunkCacheFile = path.join(cacheDir, `${ch.id}_part_${chunk.index}.txt`);
          if (fs.existsSync(chunkCacheFile)) {
            const cached = fs.readFileSync(chunkCacheFile, 'utf-8');
            if (cached.trim().length > 0) {
              console.log(`   ⏭️ Chunk [${chunk.index}/${chunks.length}] dimuat dari cache (sudah selesai sebelumnya).`);
              return cached;
            }
          }

          const cStart = Date.now();
          const res = await callLLM(chunk, config);
          fs.writeFileSync(chunkCacheFile, res, 'utf-8'); // Simpan chunk ke disk seketika
          const cDuration = ((Date.now() - cStart) / 1000).toFixed(1);
          console.log(`   ⚡ Worker selesai menerjemahkan chunk [${idx + 1}/${chunks.length}] dalam ${cDuration}s`);
          return res;
        });

        chapterSuccess = true;
      } catch (err: any) {
        if (isShuttingDown) break;
        console.error(`\n⚠️ Bab ${ch.id} mengalami kendala: ${err.message}`);
        console.log(`⏳ Menunggu 40 detik sebelum melanjutkan otomatis (progres chunk yang sudah selesai tetap aman)...`);
        for (let wait = 40; wait > 0 && !isShuttingDown; wait -= 5) {
          await new Promise(r => setTimeout(r, 5000));
        }
      }
    }

    if (isShuttingDown || !chapterSuccess) break;

    const chDuration = (Date.now() - chStartTime) / 1000;
    processedThisSession++;
    totalTimeThisSession += chDuration;

    const avgTimePerChapter = totalTimeThisSession / processedThisSession;
    const remainingChapters = chapters.length - (i + 1);
    const etaSec = remainingChapters * avgTimePerChapter;

    console.log(`✅ Bab selesai dalam ${chDuration.toFixed(1)}s (Rata-rata: ${avgTimePerChapter.toFixed(1)}s/bab | Estimasi sisa waktu: ${formatDuration(etaSec)})`);

    const translatedChapterText = translatedChunks.join('\n\n');

    // 1. Simpan bab ke cache individual (atomic)
    const chCacheFile = getChapterCachePath(cacheDir, ch.id);
    fs.writeFileSync(chCacheFile, translatedChapterText, 'utf-8');

    // Bersihkan file part chunk sementara
    for (let p = 1; p <= chunks.length; p++) {
      const partFile = path.join(cacheDir, `${ch.id}_part_${p}.txt`);
      if (fs.existsSync(partFile)) {
        try { fs.unlinkSync(partFile); } catch {}
      }
    }

    // 2. Perbarui checkpoint
    checkpoint.lastCompletedId = ch.id;
    if (!checkpoint.completedIds.includes(ch.id)) {
      checkpoint.completedIds.push(ch.id);
    }
    saveCheckpoint(config.checkpointFile, checkpoint);

    // 3. Tambahkan ke file output gabungan
    let volumeHeader = '';
    const isFirstChapterOfVolume = !chapters.slice(0, i).some(prev => prev.volNum === ch.volNum && checkpoint.completedIds.includes(prev.id));
    if (isFirstChapterOfVolume) {
      volumeHeader = `\n\n${'='.repeat(80)}\nROKUDENASHI MAJUTSU KOUSHI TO AKASHIC RECORDS - VOLUME ${String(ch.volNum).padStart(2, '0')}\n${'='.repeat(80)}\n\n`;
    }

    const chapterOutput = `${volumeHeader}### [VOLUME ${String(ch.volNum).padStart(2, '0')}] ${ch.title}\n\n${translatedChapterText}\n\n`;
    fs.appendFileSync(config.outputFile, chapterOutput, 'utf-8');

    console.log(`💾 Bab ${ch.id} berhasil disimpan secara permanen.`);

    // Jeda relaksasi 3 detik antar bab
    if (i < chapters.length - 1 && !isShuttingDown) {
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  const totalRuntime = (Date.now() - overallStartTime) / 1000;

  if (isShuttingDown) {
    console.log('\n================================================================');
    console.log(`🛑 Proses dihentikan dengan aman. Checkpoint berhasil diperbarui.`);
    console.log(`📊 Selesai pada sesi ini: ${processedThisSession} bab (${formatDuration(totalRuntime)})`);
    console.log('================================================================');
  } else if (checkpoint.completedIds.length >= chapters.length) {
    console.log('\n================================================================');
    console.log('🎉 SELURUH VOLUME (VOL 01 - 24) TELAH BERHASIL DITERJEMAHKAN!');
    console.log(`📁 File hasil gabungan: ${config.outputFile}`);
    console.log(`⏱️  Total waktu pengerjaan: ${formatDuration(totalRuntime)}`);
    console.log('================================================================');
  }
}

main().catch(err => {
  console.error('Fatal execution error:', err);
  process.exit(1);
});
