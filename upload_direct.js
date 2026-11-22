const https = require('https');
const fs = require('fs');
const path = require('path');

async function uploadCatbox(filePath) {
  const fileData = fs.readFileSync(filePath);
  const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
  const fileName = path.basename(filePath);

  const postDataStart = Buffer.from(
    '--' + boundary + '\r\n' +
    'Content-Disposition: form-data; name="reqtype"\r\n\r\n' +
    'fileupload\r\n' +
    '--' + boundary + '\r\n' +
    'Content-Disposition: form-data; name="fileToUpload"; filename="' + fileName + '"\r\n' +
    'Content-Type: application/epub+zip\r\n\r\n'
  );
  const postDataEnd = Buffer.from('\r\n--' + boundary + '--\r\n');
  const totalLength = postDataStart.length + fileData.length + postDataEnd.length;

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'catbox.moe',
      port: 443,
      path: '/user/api.php',
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Content-Length': totalLength,
        'User-Agent': 'Mozilla/5.0'
      }
    }, res => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => resolve(body.trim()));
    });
    req.on('error', reject);
    req.write(postDataStart);
    req.write(fileData);
    req.write(postDataEnd);
    req.end();
  });
}

(async () => {
  try {
    console.log('Uploading Metro 2033...');
    const url1 = await uploadCatbox('D:/JV/novel yoga/epubs/Metro 2033 (Illustrated ID-Direct).epub');
    console.log('Metro 2033 URL:', url1);
    console.log('Uploading Dune...');
    const url2 = await uploadCatbox('D:/JV/novel yoga/epubs/1_Dune_-_Frank_Herbert (Illustrated ID-Direct).epub');
    console.log('Dune URL:', url2);
  } catch (err) {
    console.error('Upload error:', err);
  }
})();
