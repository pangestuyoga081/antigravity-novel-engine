import zipfile, re, os, xml.etree.ElementTree as ET

epub_path = r"d:\JV\novel yoga\The Hobbit - Tolkien, J. R. R._5022.epub"
with zipfile.ZipFile(epub_path, 'r') as z:
    opf_name = [n for n in z.namelist() if n.endswith('.opf')][0]
    opf_dir = os.path.dirname(opf_name)
    opf_tree = ET.fromstring(z.read(opf_name))
    
    ns = {'opf': 'http://www.idpf.org/2007/opf'}
    manifest = {}
    for item in opf_tree.findall('.//opf:item', ns):
        manifest[item.attrib['id']] = item.attrib['href']
        
    spine = []
    for itemref in opf_tree.findall('.//opf:itemref', ns):
        spine.append(manifest[itemref.attrib['idref']])
        
    print(f"Total spine items: {len(spine)}")
    for idx, href in enumerate(spine):
        full_path = os.path.normpath(os.path.join(opf_dir, href)).replace('\\', '/')
        if full_path not in z.namelist():
            for n in z.namelist():
                if n.endswith(href):
                    full_path = n
                    break
        content = z.read(full_path).decode('utf-8', errors='ignore')
        m_h = re.search(r'<h[1-4][^>]*>(.*?)</h[1-4]>', content, re.DOTALL | re.IGNORECASE)
        htxt = re.sub(r'<[^>]+>', ' ', m_h.group(1)).strip() if m_h else ''
        imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', content, re.IGNORECASE)
        clean_text = re.sub(r'<[^>]+>', ' ', content)
        clean_text = ' '.join(clean_text.split())
        if len(clean_text) > 100 or imgs:
            print(f"[{idx+1:02d}] {full_path} | H: {htxt[:35]} | Imgs: {len(imgs)} | chars: {len(clean_text)}")
            if imgs:
                print(f"     Imgs: {imgs}")
