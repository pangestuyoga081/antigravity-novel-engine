const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8089;
const epubDir = 'D:/JV/novel yoga/epubs';

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  
  if (urlPath === '/' || urlPath === '') {
    const files = fs.readdirSync(epubDir).filter(f => f.endsWith('.epub') || f.endsWith('.txt'));
    let html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Download Novel EPUB</title>
  <style>
    body { font-family: -apple-system, sans-serif; padding: 20px; background: #121212; color: #eee; }
    h1 { color: #e67e22; font-size: 22px; }
    ul { list-style: none; padding: 0; }
    li { margin: 12px 0; background: #1e1e1e; padding: 15px; border-radius: 8px; border: 1px solid #333; }
    a { color: #3498db; text-decoration: none; font-size: 17px; font-weight: bold; display: block; word-break: break-all; }
    .size { color: #aaa; font-size: 13px; margin-top: 6px; }
    .btn { display: inline-block; margin-top: 10px; background: #27ae60; color: white; padding: 8px 16px; border-radius: 6px; font-size: 14px; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>
  <h1>📚 Download Novel EPUB</h1>
  <p>Pilih file di bawah ini untuk langsung download ke HP Android:</p>
  <ul>`;

    files.forEach(f => {
      const stat = fs.statSync(path.join(epubDir, f));
      const mb = (stat.size / (1024*1024)).toFixed(2);
      html += `
    <li>
      <a href="/download/${encodeURIComponent(f)}">${f}</a>
      <div class="size">Ukuran: ${mb} MB</div>
      <a class="btn" href="/download/${encodeURIComponent(f)}" download>⬇️ Download ke HP</a>
    </li>`;
    });

    html += `
  </ul>
</body>
</html>`;
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(html);
  }

  if (urlPath.startsWith('/download/')) {
    const fileName = path.basename(urlPath.replace('/download/', ''));
    const filePath = path.join(epubDir, fileName);
    if (fs.existsSync(filePath)) {
      const stat = fs.statSync(filePath);
      res.writeHead(200, {
        'Content-Type': 'application/epub+zip',
        'Content-Length': stat.size,
        'Content-Disposition': `attachment; filename="${encodeURIComponent(fileName)}"`
      });
      return fs.createReadStream(filePath).pipe(res);
    }
  }

  res.writeHead(404);
  res.end('Not Found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server download aktif di port ${PORT}`);
});
