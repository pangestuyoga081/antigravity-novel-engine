import zipfile

with zipfile.ZipFile('D:/JV/novel yoga/epubs/Metro 2033 (Illustrated ID-Direct).epub') as z:
    text = z.read('OEBPS/text/chapter_09.xhtml').decode('utf-8')
    lines = text.split('\n')
    
    print('=== 1. Check Di mana-mana (Image 2) ===')
    for l in lines:
        if 'Di mana-mana terpampang' in l:
            print(repr(l[:160]))
            
    print('\n=== 2. Check Hunter & Artyom dialogues (Image 3) ===')
    for l in lines:
        if 'Ayo gerak' in l or 'Tudung... lepasin' in l:
            print(repr(l[:160]))
            
    print('\n=== 3. Check VDNKh aside (Image 1) ===')
    for l in lines:
        if '<aside' in l and 'VDNKh' in l:
            print(repr(l[:200]))
