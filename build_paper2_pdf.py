"""build_paper2_pdf.py (copy of build_paper1_pdf.py, 26 Oct) — PAPER-2-DRAFT-2026-10-25.md -> PAPER-1.html (figures embedded, the official Apart template's look:
Letter, Old Standard TT, title rules, author grid, "With Apart Research", the sprint footnote) -> PDF via headless Chrome.
Adapted from experiments/sprint-2026-09/build_paper_pdf.py. Run from anywhere: python3 experiments/sprint-2026-10/build_paper1_pdf.py"""
import re, html, base64, pathlib, subprocess, os
HERE = pathlib.Path(__file__).resolve().parent
os.chdir(HERE)
SRC = 'PAPER-2-DRAFT-2026-10-25.md'
FIGS = HERE
OUT_HTML = 'PAPER-2-2026-10-26.html'
OUT_PDF = 'Splitting-the-Watcher-2026-10-26.pdf'
AUTHORS = [('Marion Nowicki', 'Independent; AI &amp; Becoming'), ('Cael', 'Independent; Cael\'s Field Notes')]

lines = open(SRC).read().splitlines()
title = lines[0].lstrip('# ').strip()
body = lines[1:]
# drop the working header line ("*Apart Research ... CUT VERSION ...*")
body = [l for l in body if not l.startswith('*Apart Research')]
# a figure's caption is the italic '*Figure n. ...*' line that follows it: use it, and drop it from the text
for i, l in enumerate(body):
    if l.startswith('!['):
        for j in range(i + 1, min(i + 3, len(body))):
            if body[j].startswith('*Figure'):
                body[i] = re.sub(r'^!\[.*?\]', '![' + body[j].strip().strip('*').replace(']', ')') + ']', l); body[j] = ''
                break

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    t = re.sub(r'(?<![">])(https?://[^\s<)]+?)([.,;:)]?)(?=\s|$|<)', r'<a href="\1">\1</a>\2', t)
    return t

DEFER = {'fig-patrol-doses-both-2026-10-24.png': 0, 'fig-restrictions-both-2026-10-24.png': 1, 'fig-frontier-tall-2026-10-24.png': 0}  # layout only: emit after n paragraphs so pages fill
pending = []  # [html, paragraphs_left]
def cropped(path, pad=8):
    # trim the figure's empty margins (her note, 24 Oct: space around Figures 1 and 2); the drawing itself is untouched
    from PIL import Image, ImageChops
    import io
    im = Image.open(path).convert('RGB'); bg = Image.new('RGB', im.size, im.getpixel((2, 2)))
    box = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 10 else 0).getbbox()
    if box: im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()
out = []; para = []; intable = False; inlist = None; in_abstract = False; abstract = []
def flush():
    global para
    if para:
        p = '<p>' + inline(' '.join(para)) + '</p>'
        (abstract if in_abstract else out).append(p); para = []
        if not in_abstract:
            for f in pending: f[1] -= 1
            for f in [f for f in pending if f[1] <= 0]: out.append(f[0]); pending.remove(f)
def endlist():
    global inlist
    if inlist: out.append('</' + inlist + '>'); inlist = None

for line in body:
    m = re.match(r'^!\[(.*?)\]\((.*?)\)\s*$', line)
    if m:
        flush(); endlist()
        data = base64.b64encode(cropped(FIGS / m.group(2))).decode()
        cls = 'w94' if 'doses' in m.group(2) else ('tall' if 'frontier-tall' in m.group(2) else 'wide')
        fig = f'<figure class="{cls}"><img src="data:image/png;base64,{data}"><figcaption>{inline(m.group(1))}</figcaption></figure>'
        if DEFER.get(m.group(2)): pending.append([fig, DEFER[m.group(2)]])
        else: out.append(fig)
        continue
    if line.startswith('|'):
        flush(); endlist()
        if not intable: out.append('<table>'); intable = True; tstart = len(out) - 1
        if re.match(r'^\|[\s:|-]+\|$', line): continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        tag = 'th' if out[-1] == '<table>' else 'td'
        row = '<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>'
        out.append(f'<thead>{row}</thead>' if tag == 'th' else row); continue
    elif intable:
        out.append('</table>'); intable = False
        if len(out) - tstart > 14: out[tstart] = '<table class="long">'
    m = re.match(r'^(#{1,3})\s+(.*)', line)
    if m:
        flush(); endlist()
        level, text = len(m.group(1)), m.group(2)
        if text == 'Abstract':
            in_abstract = True; continue
        in_abstract = False
        text = re.sub(r'^(\d+) ', r'\1. ', text)   # "1 Introduction" -> "1. Introduction", as the template
        cls = ' class="newpage"' if text.startswith('Appendix A') else ''
        out.append(f'<h{level}{cls}>{inline(text)}</h{level}>'); continue
    m = re.match(r'^\s*(-|\d+\.)\s+(.*)', line)
    if m and not in_abstract:
        flush(); kind = 'ol' if m.group(1)[0].isdigit() else 'ul'
        if inlist != kind: endlist(); out.append('<' + kind + '>'); inlist = kind
        out.append('<li>' + inline(m.group(2)) + '</li>'); continue
    if not line.strip(): flush(); endlist(); continue
    if inlist: endlist()
    t = line.strip()
    if t.startswith('**') and para: flush()
    if t.startswith('**Table'):
        flush(); out.append('<p class="tcap">' + inline(t) + '</p>'); continue
    para.append(t)
flush(); endlist()
if intable: out.append('</table>')

authors = ''.join(f'<div class="au"><div>{n}</div><div>{a}</div></div>' for n, a in AUTHORS)
head = (f'<div class="rule thick"></div><h1 class="title">{inline(title)}<sup>1</sup></h1><div class="rule"></div>'
        f'<div class="authors">{authors}</div><div class="with"><b>With</b><br>Apart Research</div>'
        f'<h2 class="abs">Abstract</h2><div class="abstract">{"".join(abstract)}</div>'
        )

css = '''<link href="https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=block" rel="stylesheet">
<style>@page{size:Letter;margin:1in} @page:first{@bottom-left{content:"¹ Research conducted at the AI Collusion Research Sprint, October 2026";font-family:"Old Standard TT",Georgia,serif;font-size:9pt;vertical-align:top;padding-top:5pt;border-top:0.75pt solid #000;width:4.6in}} body{font-family:"Old Standard TT",Georgia,serif;font-size:10.5pt;line-height:1.22;color:#000;margin:0;position:relative}
.rule{border-top:1px solid #000;margin:0} .rule.thick{border-top:4px solid #000;margin-top:.1in}
h1.title{text-align:center;font-size:18pt;line-height:1.25;margin:16pt 0.2in 18pt;font-weight:700}
h1.title sup{font-size:10pt} .authors{display:flex;justify-content:center;gap:.6in;margin:16pt 0 8pt;text-align:center}
.with{text-align:center;margin:4pt 0 14pt} h2.abs{text-align:center;font-size:14pt;margin:8pt 0 8pt}
.abstract{width:68%;margin:0 auto;text-align:justify} .abstract p{margin:0 0 6pt}
.fn{position:absolute;top:8.62in;left:0;font-size:9pt} .fnrule{width:2in;border-top:1px solid #000;margin-bottom:3pt}
.fn a{word-break:normal}
h2{font-size:14pt;margin:10pt 0 5pt;page-break-after:avoid} h3{font-size:11.5pt;margin:8pt 0 3pt;page-break-after:avoid}
h2:first-of-type{} h2.first{page-break-before:always}
p{margin:0 0 5.5pt;text-align:justify} ol,ul{margin:0 0 7pt;padding-left:1.5em} li{margin:0 0 2pt}
p.tcap{page-break-after:avoid;margin-bottom:3pt} tr{page-break-inside:avoid} table.long{page-break-inside:auto} h2.newpage{page-break-before:always} table{page-break-inside:avoid;border-collapse:collapse;font-size:8.3pt;line-height:1.18;margin:4pt 0 9pt;width:100%} td,th{border:1px solid #888;padding:1px 4px;vertical-align:top;text-align:left}
code{font-size:9pt} figure{margin:6pt auto;page-break-inside:avoid} figure.wide{width:84%} figure.w94{width:94%} figure.tall{width:100%} figure.narrow{width:62%}
img{width:100%;display:block} figcaption{font-size:8.6pt;margin-top:3pt;text-align:justify}
a{color:#1155cc;text-decoration:underline;word-break:break-all}
p:has(+ ol),p:has(+ ul),p:has(+ table),p:has(+ figure){break-after:avoid;page-break-after:avoid} ol,ul{break-inside:avoid;page-break-inside:avoid} li{break-inside:avoid} figure+p{break-before:avoid} h2,h3{break-after:avoid}</style>'''
body_html = '\n'.join(out)
open(OUT_HTML, 'w').write(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title>{css}</head><body>{head}{body_html}</body></html>')
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                '--virtual-time-budget=15000', f'--print-to-pdf={HERE}/{OUT_PDF}', f'file://{HERE}/{OUT_HTML}'], capture_output=True)
import pypdf
r = pypdf.PdfReader(OUT_PDF)
texts = [(p.extract_text() or '') for p in r.pages]
def first(s): return next((i + 1 for i, t in enumerate(texts) if s in t), None)
intro, codedata = first('1. Introduction'), first('Code and Data')
print('pages', len(r.pages), '| intro on p', intro, '| Code and Data on p', codedata, '| references on p', first('References'))
