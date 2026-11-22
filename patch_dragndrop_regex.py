with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "r", encoding="utf-8") as f:
    code = f.read()

# Update header detection regex
old_header_regex = "const isDxdHeader = /^(Life\\s+[0-9]+|New\\s+Life|Afterword)/i.test(l) && !/Bagian\\s+[0-9]+/i.test(l);"
new_header_regex = "const isDxdHeader = /^(Life[\\s.]+[0-9]+|Next\\s+Life|New\\s+Life|Prolog(?:ue)?|Epilog(?:ue)?|Afterword)/i.test(l) && !/Bagian\\s+[0-9]+/i.test(l);"
code = code.replace(old_header_regex, new_header_regex)

# Remove border lines '======' from output
old_assemble = "assembled += `\\n\\n${'='.repeat(70)}\\n### ${ch.title}\\n${'='.repeat(70)}\\n\\n${parts.join('\\n\\n')}\\n\\n`;"
new_assemble = "assembled += `\\n\\n### ${ch.title}\\n\\n${parts.join('\\n\\n')}\\n\\n`;"
code = code.replace(old_assemble, new_assemble)

with open(r"D:\JV\novel yoga\translate-novel-dragndrop.ts", "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied to dragndrop.ts successfully!")
