#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path

CSS_STYLE = """
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {
        content: "Seite " counter(page) " von " counter(pages);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #666;
    }
    @bottom-left {
        content: "Projektarbeit 3 – Dateiserver (Gruppe 3)";
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #2d3748;
    line-height: 1.6;
    font-size: 10.5pt;
}

h1 {
    color: #1a365d;
    border-bottom: 2px solid #2b6cb0;
    padding-bottom: 6px;
    margin-top: 0;
    font-size: 20pt;
}

h2 {
    color: #2b6cb0;
    margin-top: 18pt;
    font-size: 15pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
}

h3 {
    color: #2d3748;
    margin-top: 14pt;
    font-size: 12pt;
}

p {
    margin-bottom: 10pt;
}

code {
    background-color: #edf2f7;
    color: #805ad5;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 9.5pt;
}

pre {
    background-color: #1a202c;
    color: #e2e8f0;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    line-height: 1.4;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12pt;
    margin-bottom: 15pt;
    font-size: 10pt;
}

th, td {
    border: 1px solid #cbd5e0;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #2b6cb0;
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f7fafc;
}

blockquote {
    border-left: 4px solid #3182ce;
    background-color: #ebf8ff;
    margin: 12pt 0;
    padding: 8pt 12pt;
    color: #2c5282;
}

ul, ol {
    margin-left: 20px;
    margin-bottom: 10pt;
}

li {
    margin-bottom: 4pt;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20pt 0;
}

.box {
    border: 1px solid #e2e8f0;
    background-color: #f8fafc;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 15pt;
}
"""

def md_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    in_table = False
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        # Code block
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="{lang}">')
                in_code_block = True
            continue

        if in_code_block:
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(escaped)
            continue

        # Close table if needed
        if in_table and not stripped.startswith('|'):
            html_lines.append('</tbody></table>')
            in_table = False

        # Close list if needed
        if in_list and not (stripped.startswith('- ') or stripped.startswith('* ') or re.match(r'^\d+\.\s', stripped)):
            html_lines.append(f'</{list_type}>')
            in_list = False

        if not stripped:
            html_lines.append('')
            continue

        # Headers
        if stripped.startswith('# '):
            html_lines.append(f'<h1>{parse_inline(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h2>{parse_inline(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            html_lines.append(f'<h3>{parse_inline(stripped[4:])}</h3>')
        elif stripped.startswith('#### '):
            html_lines.append(f'<h4>{parse_inline(stripped[5:])}</h4>')

        # Horizontal rule
        elif stripped in ['---', '***', '___']:
            html_lines.append('<hr/>')

        # Tables
        elif stripped.startswith('|'):
            cells = [parse_inline(c.strip()) for c in stripped.split('|')[1:-1]]
            if '---' in stripped:
                continue
            if not in_table:
                html_lines.append('<table><thead><tr>')
                for c in cells:
                    html_lines.append(f'<th>{c}</th>')
                html_lines.append('</tr></thead><tbody>')
                in_table = True
            else:
                html_lines.append('<tr>')
                for c in cells:
                    html_lines.append(f'<td>{c}</td>')
                html_lines.append('</tr>')

        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_lines.append(f'<li>{parse_inline(stripped[2:])}</li>')
        elif re.match(r'^\d+\.\s', stripped):
            content = re.sub(r'^\d+\.\s', '', stripped)
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_lines.append(f'<li>{parse_inline(content)}</li>')

        # Blockquote
        elif stripped.startswith('> '):
            html_lines.append(f'<blockquote>{parse_inline(stripped[2:])}</blockquote>')

        # Paragraph
        else:
            html_lines.append(f'<p>{parse_inline(stripped)}</p>')

    if in_table:
        html_lines.append('</tbody></table>')
    if in_list:
        html_lines.append(f'</{list_type}>')

    body_content = '\n'.join(html_lines)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{CSS_STYLE}
</style>
</head>
<body>
{body_content}
</body>
</html>"""

def parse_inline(text):
    # Escape basic HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline Code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

def convert_file(md_path, pdf_path):
    print(f"Konvertiere {md_path} -> {pdf_path}...")
    md_content = Path(md_path).read_text(encoding='utf-8')
    html_content = md_to_html(md_content)
    
    tmp_html = Path(md_path).with_suffix('.tmp.html')
    tmp_html.write_text(html_content, encoding='utf-8')
    
    cmd = ['weasyprint', str(tmp_html), str(pdf_path)]
    subprocess.run(cmd, check=True)
    tmp_html.unlink()
    print(f"Erfolgreich erstellt: {pdf_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: build_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    convert_file(sys.argv[1], sys.argv[2])
