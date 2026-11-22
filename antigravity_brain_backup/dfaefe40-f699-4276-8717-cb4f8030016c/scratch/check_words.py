with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_found.html", encoding="utf-8") as f:
    html = f.read()

import re
# check where Caliban or Abaddon appears
for word in ['Caliban', 'Abaddon', 'Leviathan Wakes', 'Tiamat', 'Cibola Burn', 'Nemesis Games', 'Babylon']:
    found = [m.start() for m in re.finditer(re.escape(word), html, re.I)]
    print(f"Word '{word}': {len(found)} times")
    if found:
        idx = found[0]
        print(html[max(0, idx-100):min(len(html), idx+300)])
        print("="*50)
