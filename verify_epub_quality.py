import zipfile

with zipfile.ZipFile('D:/JV/novel yoga/epubs/Metro 2033 (Illustrated ID-Direct).epub') as z:
    for ch_file in ['chapter_01.xhtml', 'chapter_02.xhtml']:
        text = z.read('OEBPS/text/' + ch_file).decode('utf-8')
        lines = text.split('\n')
        print(f'=== {ch_file} ===')
        
        # Check dialogue
        dial_lines = [l for l in lines if 'class="dialogue"' in l][:4]
        for dl in dial_lines:
            print('DIAL:', dl[:140])
            
        # Check aside
        asides = [l for l in lines if '<aside' in l][:3]
        for a in asides:
            print('ASIDE:', a[:140])

    # Check TOC
    toc = z.read('OEBPS/toc.ncx').decode('utf-8')
    import re
    navpoints = re.findall(r'<navLabel><text>(.*?)</text></navLabel>', toc)
    print(f'\nTotal TOC items: {len(navpoints)}')
    for np in navpoints:
        print(' -', np)
