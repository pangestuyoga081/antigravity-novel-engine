import re

with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_found.html", encoding="utf-8") as f:
    html = f.read()

# Let's find all document links or media links
doc_pattern = re.findall(r'<a[^>]+href="([^"]*doc[^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"Found {len(doc_pattern)} doc links by regex:")
for href, inner in doc_pattern:
    text = re.sub(r'<[^>]+>', ' ', inner).strip()
    if 'Expanse' in text or any(k in text for k in ['Leviathan', 'Caliban', 'Abaddon', 'Cibola', 'Nemesis', 'Babylon', 'Persepolis', 'Tiamat']):
        print(f"BOOK: {text} -> {href}")

# Also search for all links mentioning Expanse
all_a = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"\nTotal links: {len(all_a)}")
for href, inner in all_a:
    text = re.sub(r'<[^>]+>', ' ', inner).strip()
    if any(k in text for k in ['Leviathan', 'Caliban', 'Abaddon', 'Cibola', 'Nemesis', 'Babylon', 'Persepolis', 'Tiamat', 'Expanse']):
        print(f"MATCH: {text} -> {href}")
