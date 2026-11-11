#!/usr/bin/env python3
"""Generator de site static pentru Editura TehnoPress. Fara dependente externe (doar Python 3)."""
import json, re, html, shutil, unicodedata
from pathlib import Path

ROOT = Path(__file__).parent; OUT = ROOT / 'public'
SITE = 'Editura TehnoPress'
E = html.escape

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:80] or 'x'

def load(folder):
    items = []
    for f in sorted((ROOT / 'content' / folder).glob('*.md')):
        t = f.read_text(encoding='utf-8').lstrip()
        meta, end = json.JSONDecoder().raw_decode(t)
        meta['body'] = t[end:].strip(); meta['slug'] = f.stem
        items.append(meta)
    return items

def safe_url(u):
    u = (u or '').strip()
    return u if re.match(r'^(https?://|mailto:|/|#)', u) else '#'

def inline(t):
    t = E(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{E(safe_url(html.unescape(m.group(2))))}">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    return re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<em>\1</em>', t)

def md(text):
    out = []
    for block in re.split(r'\n\s*\n', text.strip()):
        b = block.strip()
        if not b: continue
        m = re.match(r'(#{1,4})\s+(.*)', b)
        if m: out.append(f'<h{len(m.group(1))+1}>{inline(m.group(2))}</h{len(m.group(1))+1}>')
        elif all(re.match(r'[-*]\s+', l) for l in b.split('\n')):
            items = [inline(re.sub(r'^[-*]\s+', '', l)) for l in b.split('\n')]
            out.append('<ul>' + ''.join('<li>' + i + '</li>' for i in items) + '</ul>')
        else: out.append('<p>' + inline(b).replace('\n', '<br>') + '</p>')
    return '\n'.join(out)

def write(path, content):
    p = OUT / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')

NAV = [('/', 'Acasă'), ('/carti/', 'Cărți'), ('/autori/', 'Autori'), ('/despre/', 'Despre noi'), ('/contact/', 'Contact')]

def page(title, body, path, desc='', og=''):
    nav = ''.join(f'<a href="{u}"{" aria-current=page" if u == path or (u != "/" and path.startswith(u)) else ""}>{n}</a>' for u, n in NAV)
    full = SITE if title == SITE else f'{title} · {SITE}'
    return f'''<!doctype html><html lang="ro"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full)}</title><meta name="description" content="{E(desc or 'Editura TehnoPress, Iași: monografii, cărți despre Iași, literatură, filozofie și cărți tehnice.')}">
{f'<meta property="og:image" content="{E(og)}">' if og else ''}<link rel="stylesheet" href="/css/style.css"></head>
<body><header class="top"><a class="brand" href="/">Tehno<span>Press</span><small>Editură · Iași</small></a><nav>{nav}</nav></header>
<main>{body}</main>
<footer><p>© {SITE}, Iași. Toate drepturile rezervate.</p><p><a href="/contact/">Contact</a></p></footer>
<script src="/js/search.js" defer></script></body></html>'''

def card(b):
    cov = f'<img src="{E(b["cover"])}" alt="Coperta: {E(b["title"])}" loading="lazy">' if b.get('cover') else '<div class="nocover"></div>'
    hay = slugify(' '.join([b['title'], b.get('author', ''), b.get('collection', '')])).replace('-', ' ')
    return (f'<a class="card" href="/carti/{b["slug"]}/" data-q="{E(hay)}" data-col="{E(b.get("collection", ""))}">{cov}'
            f'<h3>{E(b["title"])}</h3><p>{E(b.get("author", ""))}</p></a>')

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(ROOT / 'static', OUT)
    books = load('carti'); authors = load('autori'); cols = load('colectii')
    pages = {p['slug']: p for p in load('pagini')}
    by_date = sorted(books, key=lambda b: (b.get('date') or '', b['title']), reverse=True)
    recent = [b for b in by_date if b.get('featured')] + [b for b in by_date if not b.get('featured')]
    aslug = {a['title']: slugify(a['title']) for a in authors}
    cslug = {c['title']: slugify(c['title']) for c in cols}

    # Acasa
    col_links = ''.join(f'<a href="/colectii/{cslug[c["title"]]}/">{E(c["title"])}</a>' for c in cols)
    write('index.html', page(SITE, f'''<section class="hero"><h1>Cărți care au rămas.</h1>
<p>Monografii, cărți despre Iași, literatură, filozofie și lucrări tehnice, publicate la Iași.</p><p><a class="btn" href="/carti/">Vezi catalogul</a></p></section>
<h2>Apariții recente</h2><div class="grid">{''.join(card(b) for b in recent[:8])}</div>
<h2>Colecții</h2><p class="chips">{col_links}</p>''', '/'))

    # Catalog
    opts = ''.join(f'<option>{E(c["title"])}</option>' for c in cols)
    write('carti/index.html', page('Cărți', f'''<h1>Catalogul de cărți</h1>
<div class="filters"><input id="q" type="search" placeholder="Caută după titlu, autor sau colecție" aria-label="Căutare">
<select id="col" aria-label="Colecție"><option value="">Toate colecțiile</option>{opts}</select></div>
<p id="count" class="muted"></p><div class="grid" id="list">{''.join(card(b) for b in sorted(books, key=lambda b: b['title'].lower()))}</div>''', '/carti/'))

    # Carte
    for b in books:
        rows = [('Autor', f'<a href="/autori/{aslug[b["author"]]}/">{E(b["author"])}</a>' if b.get('author') in aslug else E(b.get('author', ''))),
                ('Colecție', f'<a href="/colectii/{cslug[b["collection"]]}/">{E(b["collection"])}</a>' if b.get('collection') in cslug else ''),
                ('Anul apariției', E((b.get('date') or '')[:4])), ('Pagini', E(str(b.get('pages') or ''))),
                ('Format', E(b.get('format', ''))), ('Copertă', E(b.get('binding', ''))), ('ISBN', E(b.get('isbn', '')))]
        dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows if v and v not in ('0',))
        files = ''.join(f'<a class="btn alt" href="{E(safe_url(b[k]))}">{label}</a>' for k, label in (('toc_pdf', 'Cuprins (PDF)'), ('excerpt_pdf', 'Fragment (PDF)')) if b.get(k))
        cov = f'<img class="big" src="{E(b["cover"])}" alt="Coperta: {E(b["title"])}">' if b.get('cover') else ''
        flag = '<p class="flag">Tiraj epuizat</p>' if b.get('out_of_print') else ''
        write(f'carti/{b["slug"]}/index.html', page(b['title'], f'''<article class="book"><div>{cov}</div><div><h1>{E(b["title"])}</h1>{flag}
{md(b['body'])}<dl>{dl}</dl><p>{files}</p><p><a href="/carti/">← Toate cărțile</a></p></div></article>''', f'/carti/{b["slug"]}/',
            (re.sub(r'[*#]', '', b['body'])[:155] if b['body'] else ''), b.get('cover', '')))

    # Autori
    write('autori/index.html', page('Autori', '<h1>Autori</h1><ul class="plain">' + ''.join(
        f'<li><a href="/autori/{aslug[a["title"]]}/">{E(a["title"])}</a></li>' for a in sorted(authors, key=lambda a: a['title'].lower())) + '</ul>', '/autori/'))
    for a in authors:
        bk = [b for b in books if b.get('author') == a['title']]
        write(f'autori/{aslug[a["title"]]}/index.html', page(a['title'], f'<h1>{E(a["title"])}</h1>{md(a["body"])}<h2>Cărți</h2><div class="grid">{"".join(card(b) for b in bk)}</div>', '/autori/'))

    # Colectii
    for c in cols:
        bk = [b for b in books if b.get('collection') == c['title']]
        write(f'colectii/{cslug[c["title"]]}/index.html', page(c['title'], f'<h1>{E(c["title"])}</h1>{md(c["body"])}<div class="grid">{"".join(card(b) for b in bk) or "<p class=muted>Nu există încă titluri în această colecție.</p>"}</div>', '/carti/'))

    # Pagini simple
    d = pages.get('despre', {'title': 'Despre noi', 'body': ''})
    write('despre/index.html', page(d['title'], f'<h1>{E(d["title"])}</h1>{md(d["body"])}', '/despre/'))
    c = pages.get('contact', {'title': 'Contact', 'body': ''})
    form = '''<form name="contact" method="POST" action="/multumim/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><p hidden><label>Nu completa: <input name="bot-field"></label></p>
<label>Nume<input name="nume" required maxlength="100"></label><label>E-mail<input type="email" name="email" required maxlength="120"></label>
<label>Mesaj<textarea name="mesaj" rows="6" required maxlength="3000"></textarea></label><button class="btn" type="submit">Trimite mesajul</button></form>'''
    write('contact/index.html', page(c['title'], f'<h1>{E(c["title"])}</h1>{md(c["body"])}{form}', '/contact/'))
    write('multumim/index.html', page('Mulțumim', '<h1>Mulțumim!</h1><p>Mesajul a fost trimis. Vă răspundem cât mai curând.</p>', '/contact/'))
    write('404.html', page('Pagina nu există', '<h1>Pagina nu a fost găsită</h1><p><a href="/">Înapoi la prima pagină</a></p>', ''))
    write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /admin/\n')
    print('OK:', len(books), 'carti,', len(authors), 'autori,', len(cols), 'colectii')

main()
