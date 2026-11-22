with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\post_block.html", encoding="utf-8") as f:
    block = f.read()

import re
# check all onclick, data-, or class
classes = set(re.findall(r'class="([^"]+)"', block))
print("Classes:", list(classes)[:10])

# search for Caliban or Leviathan
for word in ['Leviathan', 'Caliban', 'Tiamat']:
    print(f"Contains {word}:", word in block)
    if word in block:
        idx = block.find(word)
        print("AROUND:", repr(block[max(0, idx-50):min(len(block), idx+150)]))
