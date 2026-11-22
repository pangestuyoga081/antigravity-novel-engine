import urllib.request
import re
import json

folder_id = "1DtsI_vvoqFxJqiBupyPRPdZO4LiMjuOK"
url = f"https://drive.google.com/drive/folders/{folder_id}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    print(f"HTML fetched, length: {len(html)}")
    with open(r"E:\antigravity-novel-engine\gdrive_folder.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    title = re.search(r'<title>(.*?)</title>', html)
    print("Page Title:", title.group(1) if title else "No title")
    
    # Extract JSON blobs containing files/items
    # Google Drive embeds items in window['_DRIVE_ivd'] or similar WIZ / AF_initDataCallback
    af_matches = re.findall(r'AF_initDataCallback\s*\(\s*\{[^\}]*?data:\s*(\[.*?\])\s*,\s*sideChannel', html, re.DOTALL)
    print(f"Found {len(af_matches)} AF_initDataCallback blobs")
    
    # search for filenames ending in .epub, .pdf, .mobi, etc.
    filenames = re.findall(r'[\'"]([^\'"]+?\.(?:epub|pdf|mobi|azw3|txt|zip|rar))[\'"]', html, re.I)
    unique_files = sorted(list(set(filenames)))
    print(f"Found {len(unique_files)} book/archive files in HTML:")
    for f in unique_files:
        print("  -", f)
        
except Exception as e:
    print("Error:", e)
