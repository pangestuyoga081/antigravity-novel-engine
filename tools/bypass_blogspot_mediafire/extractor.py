#!/usr/bin/env python3
"""
Ruidrive & Ruisafe Link Extractor
Bypasses safelinks and extracts direct download links from Ruidrive series pages.
Requires only Python 3 standard library.
"""

import sys
import re
import json
import base64
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_html(url: str) -> Optional[str]:
    """Fetches HTML content with custom user-agent."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] Gagal mengambil {url}: {e}", file=sys.stderr)
        return None

def decode_ruisafe(url: str) -> str:
    """Decodes a ruisafe safelink URL if it contains a base64 encoded 'url' query param."""
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    if 'url' in qs:
        b64 = qs['url'][0]
        # Add padding if needed
        b64 += '=' * (-len(b64) % 4)
        try:
            return base64.b64decode(b64).decode('utf-8', errors='ignore')
        except Exception:
            pass
    return url

def extract_label_from_page(html: str) -> Optional[str]:
    """Finds the series label feed from Ruidrive main page."""
    # Look for script feed pattern: /feeds/posts/default/-/<LABEL>?...
    match = re.search(r'/feeds/posts/default/-/([^?\'"]+)\?[^"\']*callback=showrecentposts', html)
    if match:
        return urllib.parse.unquote(match.group(1))
    
    # Alternative search for feeds
    match = re.search(r'/feeds/posts/default/-/([^?\'"]+)', html)
    if match:
        label = urllib.parse.unquote(match.group(1))
        if not label.startswith('$') and label != "":
            return label
    return None

def get_volume_posts(domain: str, label: str) -> List[Tuple[float, str, str, str]]:
    """
    Fetches all posts tagged with `label` from Blogger JSON feed.
    Returns list of (volume_float, volume_str, title, post_url).
    """
    encoded_label = urllib.parse.quote(label)
    feed_url = f"https://{domain}/feeds/posts/default/-/{encoded_label}?orderby=published&alt=json&max-results=999"
    
    req = urllib.request.Request(feed_url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"[-] Gagal memuat feed {feed_url}: {e}", file=sys.stderr)
        return []

    entries = data.get('feed', {}).get('entry', [])
    posts = []

    for e in entries:
        title = e.get('title', {}).get('$t', '')
        links = e.get('link', [])
        alt_link = next((l.get('href') for l in links if l.get('rel') == 'alternate'), '')
        
        # Check volume number in title
        m = re.search(r'Volume\s+([\d\.]+)', title, re.I)
        if m:
            vol_str = m.group(1)
            try:
                vol_num = float(vol_str)
            except ValueError:
                vol_num = 999.0
            posts.append((vol_num, vol_str, title, alt_link))
        else:
            # Maybe it's a volume without "Volume" keyword or side story
            posts.append((999.0, "Extra", title, alt_link))

    posts.sort(key=lambda x: x[0])
    return posts

def extract_download_links(post_html: str) -> Dict[str, str]:
    """Extracts direct download links from volume post HTML."""
    found = {}
    matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', post_html, re.DOTALL | re.IGNORECASE)
    
    for href, text in matches:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        href_clean = href.replace('&amp;', '&').strip()
        
        # Check if it's already a safelink
        if 'ruisafe' in href_clean:
            href_clean = decode_ruisafe(href_clean)
            
        target_hosts = ['Mediafire', 'Google Drive', 'Mega', 'Terabox', 'Krakenfiles', 'drop.download']
        for host in target_hosts:
            host_key = host.lower().replace(' ', '')
            if host.lower() in clean_text.lower() or host_key in href_clean.lower():
                if 'ruidrive' not in href_clean and 'blogspot.com' not in href_clean:
                    found[host] = href_clean
    return found

def process_series(url: str):
    """Processes an entire series from Ruidrive main series URL."""
    print(f"[*] Menganalisis: {url}")
    html = fetch_html(url)
    if not html:
        print("[-] Gagal mengambil halaman.")
        return

    domain = urllib.parse.urlparse(url).netloc or "www.ruidrive.com"
    label = extract_label_from_page(html)
    if not label:
        print("[-] Label seri tidak ditemukan di halaman.")
        return

    print(f"[+] Label seri terdeteksi: '{label}'")
    posts = get_volume_posts(domain, label)
    print(f"[+] Ditemukan {len(posts)} volume.")

    results = []
    for vol_num, vol_str, title, post_url in posts:
        print(f"[*] Memproses Vol {vol_str}: {post_url}")
        post_html = fetch_html(post_url)
        links = extract_download_links(post_html) if post_html else {}
        results.append({
            'vol': vol_str,
            'title': title,
            'post_url': post_url,
            'links': links
        })

    # Output formatted results
    print("\n" + "="*50)
    print("KUMPULAN MEDIAFIRE (READY TO COPY):")
    print("="*50)
    for r in results:
        mf = r['links'].get('Mediafire')
        if mf:
            print(mf)

    print("\n" + "="*50)
    print("DETAIL PER VOLUME:")
    print("="*50)
    for r in results:
        print(f"\n[Volume {r['vol']}] {r['title']}")
        print(f"Halaman: {r['post_url']}")
        for host, link in r['links'].items():
            print(f"  - {host}: {link}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <ruidrive_series_url>")
        print("Example: python extractor.py https://www.ruidrive.com/2021/10/kono-subarashii-sekai-ni-shukufuku-wo.html")
        sys.exit(1)

    input_url = sys.argv[1].strip()
    if 'ruisafe' in input_url:
        print("[+] Direct Link:", decode_ruisafe(input_url))
    else:
        process_series(input_url)
