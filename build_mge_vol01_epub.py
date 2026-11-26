import os
import re
import json
import html
import zipfile
import sys
import yaml

sys.path.insert(0, r"D:\JV\novel yoga")
from core_engine.src.qa_gate.validator import EPUBValidator

CHECKPOINT_PATH = r"D:\JV\novel yoga\.mge_v1_checkpoint.json"
ILLUST_DIR = r"D:\JV\novel yoga\illustrations\Monster_Girl_Encyclopedia_Vol_01"
PROFILE_PATH = r"D:\JV\novel yoga\core_engine\config\profiles\monster_girl_encyclopedia.yaml"
OUT_EPUB = r"D:\JV\novel yoga\epubs\Monster_Girl_Encyclopedia_Vol_01 (Illustrated ID-Direct).epub"
FINAL_EPUB = r"D:\JV\novel yoga\HASIL_TERJEMAHAN\EPUB_SIAP_BACA\Monster_Girl_Encyclopedia_Vol_01 (Illustrated ID-Direct).epub"

CSS_CONTENT = """@charset "utf-8";
body {
    margin: 4% 6%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.7;
    color: inherit;
    background-color: transparent;
}
h1, h2, h3, h4 {
    color: #b91c1c;
    margin-top: 1.3em;
    margin-bottom: 0.5em;
    font-weight: 800;
}
h1 { font-size: 1.65em; border-bottom: 2px solid rgba(185, 28, 28, 0.6); padding-bottom: 0.2em; }
h2 { font-size: 1.3em; }
h3 { font-size: 1.1em; }
p { margin: 0.65em 0; }
hr { border: none; border-top: 1px dashed rgba(148, 163, 184, 0.45); margin: 1.2em 0; }
.illustration-container {
    text-align: center;
    margin: 1em 0 1.3em 0;
    page-break-inside: avoid;
}
.illustration-container img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.22);
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 0.92em;
}
th, td {
    border: 1px solid rgba(148, 163, 184, 0.45);
    padding: 6px 8px;
    text-align: left;
}
th {
    background-color: rgba(185, 28, 28, 0.85);
    color: #fff;
}
ul, ol { margin: 0.6em 0; padding-left: 1.5em; }
li { margin: 0.3em 0; }
.lore-ref {
    color: inherit;
    text-decoration: underline dotted #0284c7;
    font-weight: 600;
}
.footnotes-section {
    margin-top: 2em;
    border-top: 1px dashed rgba(148, 163, 184, 0.4);
    padding-top: 0.8em;
}
aside.footnote {
    margin: 0.5em 0;
    padding: 0.45em 0.8em;
    font-size: 0.88em;
    line-height: 1.5;
    background-color: rgba(2, 132, 199, 0.06);
    border-left: 3px solid #0284c7;
    border-radius: 4px;
    color: inherit;
}
"""

def load_lore():
    lore = {}
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for lw in data.get("loanwords", []):
        if "(" in lw and ")" in lw:
            lore[lw.split("(")[0].strip()] = "📖 " + lw.split("(")[1].replace(")", "").strip()
    for loc in data.get("locations_and_factions", []):
        if "(" in loc and ")" in loc:
            lore[loc.split("(")[0].strip()] = "🏛️ " + loc.split("(")[1].replace(")", "").strip()
    return lore

def inline_fmt(text: str, lore_map: dict, footnotes: list, fn_counter: list) -> str:
    esc = html.escape(text)
    esc = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", esc)
    esc = re.sub(r"\*(.*?)\*", r"<em>\1</em>", esc)
    for term, desc in sorted(lore_map.items(), key=lambda x: len(x[0]), reverse=True):
        if len(term) >= 4 and not any(f[2] == term for f in footnotes):
            fn_id = f"fn_{fn_counter[0]}"
            fn_ref_id = f"fnref_{fn_counter[0]}"
            rep = f'<a id="{fn_ref_id}" href="#{fn_id}" class="lore-ref" epub:type="noteref">{term}</a>'
            pat = re.compile(r'(<a\b[^>]*>.*?</a>)|(\b' + re.escape(term) + r'\b)', re.DOTALL)
            replaced = False
            def cb(m):
                nonlocal replaced
                if m.group(1):
                    return m.group(1)
                if not replaced:
                    replaced = True
                    return rep
                return m.group(0)
            new_esc = pat.sub(cb, esc)
            if replaced:
                esc = new_esc
                footnotes.append((fn_id, fn_ref_id, term, desc))
                fn_counter[0] += 1
    return esc

def md_to_xhtml_body(raw_entry: str, lore_map: dict) -> tuple:
    lines = raw_entry.splitlines()
    title = ""
    body_lines = []
    for i, l in enumerate(lines):
        s = l.strip()
        if i == 0 and s.startswith("### "):
            title = re.sub(r"\s*\(Hal\.\s*\d+\)\s*$", "", s[4:].strip())
            continue
        body_lines.append(l)

    html_parts = []
    footnotes = []
    fn_counter = [1]
    in_ul = False
    table_rows = []

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        html_parts.append("<table>")
        for r_idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                continue
            tag = "th" if r_idx == 0 else "td"
            html_parts.append("<tr>" + "".join(f"<{tag}>{inline_fmt(c, lore_map, footnotes, fn_counter)}</{tag}>" for c in cells) + "</tr>")
        html_parts.append("</table>")
        table_rows = []

    for line in body_lines:
        s = line.strip()
        if not s:
            flush_ul()
            flush_table()
            continue

        img_m = re.match(r"^\[\[ILUSTRASI:(.*?)\]\]$", s)
        if img_m:
            flush_ul()
            flush_table()
            fn = os.path.basename(img_m.group(1).strip())
            html_parts.append(f'<div class="illustration-container"><img src="../images/{fn}" alt="{html.escape(fn)}" /></div>')
            continue

        if s.startswith("|") and "|" in s[1:]:
            flush_ul()
            table_rows.append(s)
            continue
        else:
            flush_table()

        if re.match(r"^-{3,}$", s):
            flush_ul()
            html_parts.append("<hr/>")
            continue

        h_m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if h_m:
            flush_ul()
            lvl = min(4, len(h_m.group(1)))
            ht = inline_fmt(h_m.group(2).strip(), lore_map, footnotes, fn_counter)
            html_parts.append(f"<h{lvl}>{ht}</h{lvl}>")
            continue

        li_m = re.match(r"^[\*\-•]\s+(.*)$", s)
        if li_m:
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{inline_fmt(li_m.group(1).strip(), lore_map, footnotes, fn_counter)}</li>")
            continue

        flush_ul()
        html_parts.append(f"<p>{inline_fmt(s, lore_map, footnotes, fn_counter)}</p>")

    flush_ul()
    flush_table()

    if footnotes:
        html_parts.append('<div class="footnotes-section">')
        for fn_id, _, _, desc in footnotes:
            html_parts.append(f'<aside id="{fn_id}" class="footnote" epub:type="footnote">{html.escape(desc)}</aside>')
        html_parts.append("</div>")

    return title, "\n".join(html_parts)

def main():
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        done_map = json.load(f)
    lore_map = load_lore()

    pages = []
    for p_num in range(1, 242):
        raw = done_map.get(str(p_num), f"[[ILUSTRASI:page_{p_num:03d}.jpg]]")
        title, body_html = md_to_xhtml_body(raw, lore_map)
        disp_title = title if title and not title.startswith("Halaman ") else f"Halaman {p_num}"
        if title and not title.startswith("Halaman "):
            body_html = f"<h1>{html.escape(title)}</h1>\n" + body_html
        pages.append((f"page_{p_num:03d}.xhtml", disp_title, body_html))

    os.makedirs(os.path.dirname(OUT_EPUB), exist_ok=True)
    with zipfile.ZipFile(OUT_EPUB, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/epub+zip" /></rootfiles></container>'.replace("application/epub+zip", "application/oebps-package+xml"), compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/css/stylesheet.css", CSS_CONTENT, compress_type=zipfile.ZIP_DEFLATED)

        manifest_items, spine_items, nav_points, nav_lis = [], [], [], []
        for idx, (fname, title, body_html) in enumerate(pages):
            xhtml = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="../css/stylesheet.css"/></head>
<body>
{body_html}
</body>
</html>'''
            z.writestr(f"OEBPS/text/{fname}", xhtml, compress_type=zipfile.ZIP_DEFLATED)
            manifest_items.append(f'<item id="p_{idx+1}" href="text/{fname}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="p_{idx+1}"/>')
            nav_points.append(f'<navPoint id="np_{idx+1}" playOrder="{idx+1}"><navLabel><text>{html.escape(title)}</text></navLabel><content src="text/{fname}"/></navPoint>')
            nav_lis.append(f'<li><a href="text/{fname}">{html.escape(title)}</a></li>')

        manifest_imgs = []
        cover_id = "img_1"
        for idx, fn in enumerate(sorted(os.listdir(ILLUST_DIR))):
            if fn.lower().endswith(".jpg"):
                z.write(os.path.join(ILLUST_DIR, fn), f"OEBPS/images/{fn}", compress_type=zipfile.ZIP_STORED)
                iid = f"img_{idx+1}"
                props = ' properties="cover-image"' if fn == "page_001.jpg" else ""
                if fn == "page_001.jpg":
                    cover_id = iid
                manifest_imgs.append(f'<item id="{iid}" href="images/{fn}" media-type="image/jpeg"{props}/>')

        uid = "urn:uuid:mge-vol-01-id-direct-kenkou-cross"
        z.writestr("OEBPS/toc.ncx", f'<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{uid}"/><meta name="dtb:depth" content="1"/></head><docTitle><text>Monster Girl Encyclopedia Vol. 1 (ID-Direct)</text></docTitle><navMap>{"".join(nav_points)}</navMap></ncx>', compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", f'<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Daftar Isi</title></head><body><nav epub:type="toc" id="toc"><h1>Daftar Isi</h1><ol>{"".join(nav_lis)}</ol></nav></body></html>', compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", f'<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/opf" unique-identifier="BookID" version="3.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Monster Girl Encyclopedia Vol. 1 (ID-Direct)</dc:title><dc:creator>Kenkou Cross</dc:creator><dc:language>id</dc:language><dc:identifier id="BookID">{uid}</dc:identifier><meta name="cover" content="{cover_id}"/></metadata><manifest><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="css/stylesheet.css" media-type="text/css"/>{"".join(manifest_items)}{"".join(manifest_imgs)}</manifest><spine toc="ncx">{"".join(spine_items)}</spine></package>', compress_type=zipfile.ZIP_DEFLATED)

    ok, errs, stats = EPUBValidator.validate_epub(OUT_EPUB)
    print(f"Built: {OUT_EPUB} ({os.path.getsize(OUT_EPUB)/(1024*1024):.2f} MB)")
    print("QA GATE:", "PASS" if ok else f"FAIL ({len(errs)})", stats)
    if errs:
        for e in errs[:10]: print(" -", e)

if __name__ == "__main__":
    main()
