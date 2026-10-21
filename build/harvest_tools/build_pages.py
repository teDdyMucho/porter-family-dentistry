"""Turn raw crawl extractions into harvest/pages/<slug>.json + .md, plus _site.json/.md and _index.json.

Run:  python -I -X utf8 build_pages.py
"""
import hashlib
import json
import os
import re
from urllib.parse import urlparse, unquote

H = r'C:\Users\Admin\Desktop\porter-family-dentistry\harvest'
CRAWL = os.path.join(H, 'raw', '_crawl')
PAGES = os.path.join(H, 'pages')
os.makedirs(PAGES, exist_ok=True)

LOG = json.load(open(os.path.join(CRAWL, 'crawl_log.json'), encoding='utf-8'))
EX = {p['slug']: json.load(open(os.path.join(CRAWL, p['slug'] + '.extract.json'), encoding='utf-8')) for p in LOG['pages']}
ORDER = [p['slug'] for p in LOG['pages']]


def fix(u):
    if not u:
        return u
    if u.startswith('//'):
        u = 'https:' + u
    try:
        x = urlparse(u)
        return x._replace(netloc=x.netloc.lower()).geturl()
    except Exception:
        return u


def key_of(u):
    x = urlparse(u)
    return 'https://' + x.netloc.lower() + x.path.lower() + (('?' + x.query) if x.query else '')


def npath(u):
    x = urlparse(u)
    p = x.path.lower()
    return p if p.endswith('/') or '.' in p.rsplit('/', 1)[-1] else p + '/'


DL = {}
_man = os.path.join(H, 'images', 'manifest.json')
if os.path.exists(_man):  # final (renamed) local files from build_images.py
    for m in json.load(open(_man, encoding='utf-8'))['images']:
        if m.get('localFile'):
            DL[fix(m['sourceUrl'])] = m['localFile']
else:
    for d in LOG['downloads']:
        if d.get('file'):
            DL[fix(d['url'])] = d['file']


def local(u):
    f = DL.get(fix(u))
    return f


# ---------------- nav ----------------
HOME = EX.get('home')
NAV = HOME['nav'] if HOME else []
NAV_INDEX = {}


def flatten(nodes, parents=()):
    for n in nodes:
        yield n, list(parents)
        if n.get('children'):
            yield from flatten(n['children'], parents + (n['label'],))


for n, parents in flatten(NAV):
    if n.get('href'):
        NAV_INDEX.setdefault(npath(n['href']), []).append({'label': n['label'], 'parents': parents, 'menuPath': ' > '.join(parents + [n['label']])})

# ---------------- fetch / alias bookkeeping ----------------
REQ = {}      # slug -> list of requested urls
CHAINS = {}   # slug -> list of redirect chains
for f in LOG['fetches']:
    s = f.get('slug') or f.get('aliasOf')
    if not s:
        continue
    REQ.setdefault(s, []).append(f['requested'])
    hops = [(h['status'], h['url']) for h in f['nav'] if h['status'] != 202]
    if any(300 <= st < 400 for st, _ in hops):
        CHAINS.setdefault(s, []).append([f'{st} {u}' for st, u in hops])

LINKED = LOG['linkedFrom']


def inbound(slug, final):
    keys = {key_of(final)} | {key_of(u) for u in REQ.get(slug, [])}
    src = []
    for k in keys:
        for e in LINKED.get(k, []):
            src.append(e)
    pages = sorted({e['from'] for e in src if e.get('from') and not str(e['from']).startswith('sitemap')})
    in_content = sorted({e['from'] for e in src if e.get('area') == 'main'})
    via_sitemap = any(str(e.get('from', '')).startswith('sitemap') for e in src)
    return {'linkingPages': len(pages), 'linkedFromContentOf': in_content, 'inSitemap': via_sitemap}


# ---------------- block cleaning ----------------
WORD = re.compile(r"[A-Za-z0-9]+(?:[’'.\-][A-Za-z0-9]+)*")


def clean_img(b):
    best = fix(b.get('best') or b.get('src'))
    o = {'type': 'img', 'src': best}
    if b.get('src') and fix(b['src']) != best:
        o['srcAttr'] = fix(b['src'])
    o['alt'] = b.get('alt')
    if b.get('title'):
        o['title'] = b['title']
    o['width'] = b.get('naturalWidth')
    o['height'] = b.get('naturalHeight')
    o['renderedSize'] = [b.get('renderedWidth'), b.get('renderedHeight')]
    if b.get('href'):
        o['href'] = b['href']
    if b.get('hidden'):
        o['hidden'] = True
    if b.get('svg'):
        o['svg'] = True
    lf = local(best) if best else None
    if lf:
        o['localFile'] = lf
    return o


def clean_media(b):
    o = {'type': b['type'], 'tag': b.get('tag'), 'src': b.get('src')}
    for k in ('title', 'width', 'height', 'poster', 'sources', 'tracks', 'params', 'flashvars', 'name', 'dataSetup', 'mime'):
        if b.get(k):
            o[k] = b[k]
    o['renderedSize'] = [b.get('renderedWidth'), b.get('renderedHeight')]
    if b.get('hidden'):
        o['hidden'] = True
    return o


_USED_LABEL_BLOCKS = set()


def field_label(fields_by_i, fi, prev_block):
    """Visible label for a control: <label for>, then a short 'Label:'/'Question?' paragraph right before it
    (each paragraph claimed once), then the placeholder, then nearby text."""
    f = fields_by_i.get(fi)
    if not f:
        return None
    for k in ('labelFor', 'wrapLabel', 'ariaLabel'):
        if f.get(k) and f['type'] not in ('radio', 'checkbox'):
            return f[k]
    if prev_block and prev_block.get('type') == 'p' and id(prev_block) not in _USED_LABEL_BLOCKS:
        t = prev_block.get('text', '')
        if len(t) < 160 and (t.rstrip().endswith((':', '?')) or not f.get('placeholder')):
            _USED_LABEL_BLOCKS.add(id(prev_block))
            return t
    if f.get('placeholder'):
        return f['placeholder']
    if f.get('rowLabel'):
        return f['rowLabel']
    if f.get('prevText'):
        return f['prevText']
    return None


def group_key(f):
    n = f.get('name') or f.get('id') or ''
    if f['type'] in ('radio', 'checkbox'):
        return re.sub(r'\$\d+$', '', n)
    return n


def resolve_fields(ex, blocks_area='main'):
    """Return structured, human-readable fields for the controls of one area, in DOM order."""
    fields = [f for f in ex.get('fields', []) if f.get('area') == blocks_area]
    by_i = {f['i']: f for f in ex.get('fields', [])}
    # previous block for each field marker (label paragraph) -- scan main blocks recursively
    prev_for = {}

    def scan(blocks, prev=None):
        for b in blocks:
            if b.get('type') == 'field':
                prev_for[b['field']['i']] = prev
            for it in b.get('items', []) or []:
                scan(it.get('media', []) or [], prev)
            for row in b.get('rows', []) or []:
                for c in row:
                    scan(c.get('media', []) or [], prev)
            if b.get('type') in ('p', 'h2', 'h3', 'h4'):
                prev = b
            if b.get('type') == 'table':
                pass
    if blocks_area == 'main':
        scan(ex.get('blocks', []))
    out = []
    groups = {}
    for f in fields:
        honeypot = (not f.get('visible')) and f['type'] == 'text' and (str(f.get('name', '')).endswith('hurl') or 'qcformemailcheck' in str(f.get('cls', '')))
        if f['type'] in ('radio', 'checkbox'):
            gk = group_key(f)
            if gk not in groups:
                pb = prev_for.get(f['i'])
                # radio/checkbox inputs are visually replaced by styled labels, so judge visibility by the group's label paragraph
                vis = (not pb.get('hidden')) if pb else bool(f.get('visible'))
                g = {'label': field_label(by_i, f['i'], pb), 'type': f['type'] + '-group', 'name': gk, 'options': [], 'required': False, 'visibleOnLoad': vis}
                if f['type'] == 'radio' and g['label'] in (None, f.get('optionLabel')):
                    g['label'] = None
                groups[gk] = g
                out.append(g)
            g = groups[gk]
            g['options'].append({'label': f.get('optionLabel') or f.get('labelFor'), 'checkedByDefault': bool(f.get('checked'))})
            if f.get('validators'):
                g['validators'] = f['validators']
            continue
        o = {
            'label': field_label(by_i, f['i'], prev_for.get(f['i'])) if f['type'] not in ('button', 'submit') else None,
            'type': f['type'], 'name': f.get('name'), 'id': f.get('id'),
        }
        if f.get('placeholder'):
            o['placeholder'] = f['placeholder']
        if f.get('value'):
            o['buttonText'] = f['value']
        if f.get('options'):
            o['options'] = f['options']
        if f.get('rows'):
            o['rows'] = f['rows']
        if f.get('maxlength'):
            o['maxlength'] = f['maxlength']
        o['required'] = bool(f.get('required'))
        if f.get('prevTextBold'):
            o['labelBold'] = True
        if f.get('validators'):
            o['validators'] = [{'message': v.get('message'), 'kind': v.get('fn') or v.get('clientfn')} for v in f['validators']]
            if any((v.get('clientfn') or '') == 'ValidateInputs' for v in f['validators']):
                o['requiredNote'] = 'phone OR email required (at least one)'
        o['visibleOnLoad'] = bool(f.get('visible'))
        if honeypot:
            o['honeypot'] = True
        out.append(o)
    return out


def clean_blocks(blocks, ex):
    out = []
    by_i = {f['i']: f for f in ex.get('fields', [])}
    for b in blocks:
        t = b.get('type')
        if t == 'img' and b.get('svg'):
            continue  # inline SVG icons (e.g. the review page's star-rating widget) — not content images
        if t == 'img':
            out.append(clean_img(b))
        elif t in ('video', 'map', 'iframe', 'embed', 'audio'):
            out.append(clean_media(b))
        elif t in ('ul', 'ol'):
            out.append(clean_list(b, ex))
        elif t == 'table':
            rows = []
            for r in b['rows']:
                cells = []
                for c in r:
                    cc = {'text': c['text'], 'md': c['md']}
                    if c.get('links'):
                        cc['links'] = c['links']
                    if c.get('media'):
                        cc['media'] = clean_blocks(c['media'], ex)
                    if c.get('th'):
                        cc['th'] = True
                    if c.get('colspan'):
                        cc['colspan'] = c['colspan']
                    cells.append(cc)
                rows.append(cells)
            o = {'type': 'table', 'rows': rows}
            if b.get('hidden'):
                o['hidden'] = True
            out.append(o)
        elif t == 'field':
            f = by_i.get(b['field']['i'], {})
            out.append({'type': 'field', 'fieldType': f.get('type'), 'name': f.get('name'), 'optionLabel': f.get('optionLabel') if f.get('type') in ('radio', 'checkbox') else None, 'buttonText': f.get('value'), 'visibleOnLoad': bool(f.get('visible'))})
        elif t == 'hr':
            out.append({'type': 'hr'})
        else:
            o = {'type': t, 'text': b.get('text', '')}
            if b.get('md') and b['md'] != b.get('text'):
                o['md'] = b['md']
            if b.get('lines'):
                o['lines'] = b['lines']
            if b.get('links'):
                o['links'] = [{'text': l['text'], 'href': l['href'], **({'target': l['target']} if l.get('target') else {})} for l in b['links']]
            if b.get('media'):
                o['media'] = clean_blocks(b['media'], ex)
            if b.get('hidden'):
                o['hidden'] = True
            if b.get('cls'):
                o['class'] = b['cls']
            out.append(o)
    return out


def clean_list(b, ex):
    items = []
    for it in b['items']:
        o = {'text': it['text']}
        if it.get('md') and it['md'] != it['text']:
            o['md'] = it['md']
        if it.get('links'):
            o['links'] = [{'text': l['text'], 'href': l['href']} for l in it['links']]
        if it.get('media'):
            o['media'] = clean_blocks(it['media'], ex)
        if it.get('children'):
            o['children'] = [clean_list(c, ex) for c in it['children']]
        if it.get('hidden'):
            o['hidden'] = True
        items.append(o)
    return {'type': b['type'], 'items': items}


def wrap_form(blocks, fields):
    """Wrap the run of blocks from the first to the last form control into one {type: form} block."""
    idx = [i for i, b in enumerate(blocks) if b['type'] == 'field' or (b['type'] == 'table' and any(m.get('type') == 'field' for r in b['rows'] for c in r for m in c.get('media', [])))]
    if not idx:
        return blocks
    # a stand-alone button (e.g. contact page "Map & Directions") does not start a form
    start = [i for i in idx if not (blocks[i]['type'] == 'field' and blocks[i].get('fieldType') in ('button', 'submit', 'image'))]
    if not start:
        return blocks
    a, z = start[0], idx[-1]
    names = set()
    for b in blocks[a:z + 1]:
        if b['type'] == 'field':
            names.add(b.get('name') or '')
        for r in b.get('rows', []) or []:
            for c in r:
                for m in c.get('media', []) or []:
                    if m.get('type') == 'field':
                        names.add(m.get('name') or '')
    fields = [f for f in fields if (f.get('name') or '') in names or (f['type'].endswith('-group') and any(n.startswith(f.get('name') or '\x00') for n in names))]
    # pull the label paragraph immediately before the first control into the form
    if a > 0 and blocks[a - 1]['type'] == 'p' and len(blocks[a - 1]['text']) < 160:
        a -= 1
    form = {'type': 'form', 'fields': fields, 'content': blocks[a:z + 1]}
    return blocks[:a] + [form] + blocks[z + 1:]


def texts(blocks):
    for b in blocks:
        t = b['type']
        if t in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'):
            yield b.get('text', '')
        elif t in ('ul', 'ol'):
            yield from list_texts(b)
        elif t == 'table':
            for r in b['rows']:
                for c in r:
                    yield c['text']
        elif t == 'form':
            yield from texts(b['content'])


def list_texts(b):
    for it in b['items']:
        yield it['text']
        for c in it.get('children', []) or []:
            yield from list_texts(c)


# ---------------- markdown ----------------
def md_inline(b):
    s = b.get('md') or b.get('text') or ''
    return s.replace('\n', '  \n')


def md_list(b, depth=0):
    lines = []
    for n, it in enumerate(b['items'], 1):
        bullet = f'{n}.' if b['type'] == 'ol' else '-'
        pad = '   ' * depth
        txt = (it.get('md') or it.get('text') or '').replace('\n', '  \n' + pad + '  ')
        hid = ' *(hidden on load)*' if it.get('hidden') else ''
        lines.append(f'{pad}{bullet} {txt}{hid}')
        for m in it.get('media', []) or []:
            lines.append(pad + '  ' + md_media(m))
        for c in it.get('children', []) or []:
            lines.extend(md_list(c, depth + 1))
    return lines


def rel_img(f):
    return '../' + f if f else None


def md_media(m):
    t = m['type']
    if t == 'img':
        loc = rel_img(m.get('localFile')) or m.get('src')
        alt = m.get('alt') or ''
        cap = f"{m.get('width')}x{m.get('height')}px" if m.get('width') else ''
        link = f" (links to {m['href']})" if m.get('href') else ''
        return f"![{alt}]({loc}) <sub>{os.path.basename(m.get('localFile') or m.get('src') or '')} · {cap} · alt=\"{alt}\"{link}</sub>"
    if t == 'field':
        return f"`[{m.get('fieldType')}{': ' + m['optionLabel'] if m.get('optionLabel') else ''}{': ' + m['buttonText'] if m.get('buttonText') else ''}]`"
    if t in ('video', 'map', 'iframe', 'embed', 'audio'):
        title = m.get('title') or ''
        return f"[{t.upper()} embed{': ' + title if title else ''}]({m.get('src')})"
    return f'[{t}]'


def md_form(b):
    lines = ['', '**Form fields** (in order):', '']
    for f in b['fields']:
        if f.get('honeypot'):
            lines.append(f"- *(hidden anti-spam honeypot field `{f.get('name')}` — not shown to users)*")
            continue
        if f['type'] in ('button', 'submit'):
            lines.append(f"- Button: **{f.get('buttonText')}**")
            continue
        req = 'required' if f.get('required') else (f['requiredNote'] if f.get('requiredNote') else 'optional')
        extra = []
        if f.get('labelBold'):
            extra.append('label shown in bold')
        if f.get('validators'):
            extra.append('validation: ' + '; '.join(f"\"{v['message']}\"" for v in f['validators'] if v.get('message')))
        if not f.get('visibleOnLoad'):
            extra.append('hidden until revealed by another answer')
        if f.get('placeholder'):
            extra.append(f"placeholder \"{f['placeholder']}\"")
        opts = ''
        if f.get('options'):
            opts = ' — options: ' + ', '.join((('[x] ' if o.get('checkedByDefault') or o.get('selected') else '') + str(o.get('label') or o.get('text'))) for o in f['options'] if 'optgroup' not in o)
        lines.append(f"- **{f.get('label') or '(no label)'}** — {f['type']}, {req}{opts}{(' (' + '; '.join(extra) + ')') if extra else ''}")
    lines.append('')
    lines.append('Form content as displayed:')
    lines.append('')
    lines.extend(md_blocks(b['content']))
    return lines


def md_blocks(blocks):
    lines = []
    last_opt = None
    for b in blocks:
        t = b['type']
        hid = ' *(hidden on load)*' if b.get('hidden') else ''
        if t == 'p' and last_opt and b.get('text') == last_opt:
            last_opt = None
            continue  # option label already shown inside the field marker
        last_opt = b.get('optionLabel') if t == 'field' else None
        if t in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            lines += ['', '#' * int(t[1]) + ' ' + (b.get('md') or b['text']) + hid, '']
        elif t == 'p':
            lines += [md_inline(b) + hid, '']
        elif t in ('ul', 'ol'):
            lines += md_list(b) + ['']
        elif t == 'blockquote':
            lines += ['> ' + l if l else '>' for l in (b.get('md') or b['text']).split('\n')] + ['']
        elif t == 'table':
            rows = b['rows']
            w = max(len(r) for r in rows) if rows else 0
            if rows:
                def cell(c):
                    s = (c.get('md') or c['text']).replace('\n', '<br>').replace('|', '\\|')
                    for m in c.get('media', []) or []:
                        s += ' ' + md_media(m)
                    return s
                lines.append('| ' + ' | '.join(cell(c) for c in rows[0]) + ' |' * (1) + '')
                lines.append('|' + '---|' * len(rows[0]))
                for r in rows[1:]:
                    lines.append('| ' + ' | '.join(cell(c) for c in r) + ' |')
                lines.append('')
        elif t == 'hr':
            lines += ['---', '']
        elif t == 'form':
            lines += md_form(b)
        else:
            lines += [md_media(b), '']
    return lines


# ---------------- per page ----------------
hashes = {}
index = []
for slug in ORDER:
    ex = EX[slug]
    f = ex['fetch']
    final = f['finalUrl']
    head = ex.get('head', {})
    blocks = clean_blocks(ex.get('blocks', []), ex)
    main_fields = resolve_fields(ex, 'main')
    blocks = wrap_form(blocks, main_fields)
    body_texts = [t for t in texts(blocks)]
    words = sum(len(WORD.findall(t)) for t in body_texts)
    # duplicate detection on whitespace-normalised text (ignores line-break/paragraph differences)
    h = hashlib.sha1(re.sub(r'\s+', ' ', ' '.join(body_texts[1:] if body_texts else [])).strip().encode('utf-8')).hexdigest()[:12]
    dup = hashes.get(h) if body_texts[1:] else None
    hashes.setdefault(h, slug)
    nav = NAV_INDEX.get(npath(final), [])
    hero = ex.get('hero', {})
    hero_out = {}
    if hero.get('carousel'):
        hero_out['carousel'] = [{
            'slide': s['index'], 'leadIn': s['leadIn'], 'heading': s['heading'], 'phone': s['phone'], 'phoneHref': s.get('phoneHref'),
            'backgroundImage': fix((re.search(r'url\("?([^")]+)', s.get('bgImage') or '') or [None, None])[1]),
            'backgroundLocalFile': local((re.search(r'url\("?([^")]+)', s.get('bgImage') or '') or [None, None])[1]),
        } for s in hero['carousel']]
    if hero.get('banner') and hero['banner'].get('img'):
        hero_out['banner'] = clean_img(hero['banner']['img'])
    page_imgs = []
    for im in ex.get('images', []):
        best = fix(im.get('best') or im.get('src'))
        page_imgs.append({'src': best, 'alt': im.get('alt'), 'area': im.get('area'), 'size': [im.get('naturalWidth'), im.get('naturalHeight')], 'localFile': local(best)})
    for bg in ex.get('backgrounds', []):
        page_imgs.append({'src': fix(bg['url']), 'alt': None, 'area': bg['area'], 'cssBackgroundOf': bg['el'] + (bg.get('pseudo') or ''), 'localFile': local(bg['url'])})
    media = [clean_media(m) | {'area': m.get('area')} for m in ex.get('media', [])]
    frames = [{'url': fr['url'], 'name': fr['name'], 'text': fr['text']} for fr in ex.get('frames', [])]
    other_forms = {}
    for fld in ex.get('fields', []):
        if fld['area'] not in ('main', 'header'):
            other_forms.setdefault(fld['area'], True)
    rec = {
        'slug': slug,
        'url': f['requested'],
        'finalUrl': final,
        'status': f.get('status'),
        'requestedAs': sorted(set(REQ.get(slug, []))),
        'redirects': CHAINS.get(slug, []),
        'title': head.get('title'),
        'metaDescription': (head.get('descriptions') or [None])[0],
        'metaDescriptionsAll': head.get('descriptions') if len(head.get('descriptions') or []) > 1 else None,
        'metaKeywords': (head.get('keywords') or [None])[0] or None,
        'canonical': head.get('canonical'),
        'h1': [x['text'] for x in ex.get('h1', [])] or None,
        'h1Note': None if ex.get('h1') else 'No <h1> element on the page; the page heading is <h2 class="section-heading">.',
        'pageHeading': ex.get('sectionHeading'),
        'nav': nav or None,
        'navNote': None if nav else 'Not in the main navigation menu.',
        'inbound': inbound(slug, final),
        'hero': hero_out or None,
        'blocks': blocks,
        'wordCount': words,
        'contentHash': h,
        'duplicateOf': dup,
        'media': media or None,
        'iframesText': frames or None,
        'sharedSections': {
            'contactQuickForm': bool((ex.get('pluginContact') or {}).get('rendered')),
            'testimonialsCarousel': bool((ex.get('pluginTestimonials') or {}).get('items')),
            'officeLocation': bool((ex.get('pluginAddress') or {}).get('text')),
            'phoneBar': bool(ex.get('phonebar')),
        },
        'images': page_imgs,
        'extractionErrors': ex.get('errors') or None,
    }
    rec = {k: v for k, v in rec.items() if v is not None}
    json.dump(rec, open(os.path.join(PAGES, slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # markdown
    L = [f"# {head.get('title')}", '']
    L.append(f"- **URL:** {final}")
    if rec.get('requestedAs') and rec['requestedAs'] != [final]:
        L.append(f"- **Also reached via:** {', '.join(u for u in rec['requestedAs'] if u != final)}")
    L.append(f"- **Meta description:** {rec.get('metaDescription') or '(none)'}")
    L.append(f"- **H1:** {', '.join(rec['h1']) if rec.get('h1') else '(none — page heading is an h2: ' + str(ex.get('sectionHeading')) + ')'}")
    L.append(f"- **Nav:** {'; '.join(n['menuPath'] for n in nav) if nav else 'not in main menu'}")
    L.append(f"- **Words (main content):** {words}")
    if dup:
        L.append(f"- **Duplicate content of:** `{dup}`")
    L.append('')
    if hero_out.get('carousel'):
        L.append('## [Hero carousel]')
        for s in hero_out['carousel']:
            L.append(f"- Slide {s['slide']}: lead-in \"{s['leadIn']}\" / heading \"{s['heading'].replace(chr(10), ' ')}\" / \"{s['phone']}\" — background `{os.path.basename(s['backgroundLocalFile'] or s['backgroundImage'] or '')}`")
        L.append('')
    if hero_out.get('banner'):
        L.append('## [Page banner]')
        L.append(md_media(hero_out['banner']))
        L.append('')
    L.append('---')
    L += md_blocks(blocks)
    if media:
        L += ['', '---', '**Embedded media on page:**', '']
        for m in media:
            L.append(f"- {m['type']} ({m.get('area')}): {m.get('src')} {('— ' + m['title']) if m.get('title') else ''}")
    sh = [k for k, v in rec['sharedSections'].items() if v]
    L += ['', '---', f"*Shared site sections also shown on this page (content in `_site.md`): {', '.join(sh) if sh else 'none'}*", '']
    md = '\n'.join(L)
    md = re.sub(r'\n{3,}', '\n\n', md)
    open(os.path.join(PAGES, slug + '.md'), 'w', encoding='utf-8').write(md)
    index.append({'slug': slug, 'url': final, 'status': f.get('status'), 'title': head.get('title'), 'pageHeading': ex.get('sectionHeading'),
                  'nav': '; '.join(n['menuPath'] for n in nav) if nav else None, 'words': words,
                  'mainImages': sum(1 for b in ex.get('blocks', []) if b.get('type') == 'img' and not b.get('svg')) + sum(1 for b in ex.get('blocks', []) if b.get('type') in ('ul', 'ol') for it in b['items'] for m in it.get('media', []) or [] if m.get('type') == 'img'),
                  'bannerImage': os.path.basename(hero_out['banner']['src']) if hero_out.get('banner') else ('carousel' if hero_out.get('carousel') else None),
                  'duplicateOf': dup, 'contentHash': h, 'requestedAs': rec.get('requestedAs'), 'redirects': rec.get('redirects'),
                  'media': len(media), 'forms': any(b['type'] == 'form' for b in blocks), 'inbound': rec['inbound']})

json.dump(index, open(os.path.join(PAGES, '_index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------- site-wide chrome ----------------
site = {}
if HOME:
    site['header'] = HOME.get('header')
    site['navTree'] = NAV
    site['pluginContact'] = HOME.get('pluginContact')
    site['pluginContactFields'] = resolve_fields(HOME, 'plugin-contact')
    site['pluginTestimonials'] = HOME.get('pluginTestimonials')
    site['pluginAddress'] = HOME.get('pluginAddress')
    site['footer'] = {k: v for k, v in (HOME.get('footer') or {}).items() if k != 'html'}
    site['favicon'] = HOME['head'].get('icons')
    site['fontsLoaded'] = HOME.get('fontsLoaded')
    site['styleSamples'] = HOME.get('styleSamples')
    site['adaWidget'] = 'Fixed bottom-left round button (background rgb(0,61,104) = #003D68) linking to /ada.aspx "Accessibility Mode". Not crawled: following it switches the session into the accessibility template.'
for slug in ORDER:
    pb = EX[slug].get('phonebar')
    if pb:
        site['phoneBar'] = pb
        break
for slug in ORDER:
    ss = EX[slug].get('styleSamples') or {}
    if slug != 'home' and 'banner' in ss:
        site['styleSamplesInterior'] = ss
        site['interiorPageExample'] = slug
        break
json.dump(site, open(os.path.join(PAGES, '_site.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

S = ['# Site-wide sections (header, nav, shared plugins, footer)', '']
if HOME:
    S += ['## Header / logo (text logo — no logo image)', '']
    for c in HOME['header']['compTitles']:
        S.append(f"- `{c['cls']}`: \"{c['text']}\"")
    S += ['', 'Header icon buttons (mobile/compact header):', '']
    for m in HOME['header']['menuIcons']:
        S.append(f"- `{m['id']}` → {m.get('href') or m.get('onclick')}")
    S += ['', '## Main navigation menu', '']

    def navmd(nodes, d=0):
        for n in nodes:
            S.append('  ' * d + f"- {n['label']} → {n['href']}")
            if n.get('children'):
                navmd(n['children'], d + 1)
    navmd(NAV)
    if site.get('phoneBar'):
        S += ['', '## Phone bar under the banner (interior pages)', '']
        for p in site['phoneBar']:
            S.append(f"- \"{p['text']}\" → {', '.join(p['links'])}")
    pc = HOME.get('pluginContact') or {}
    S += ['', '## "Contact Us" quick-contact section (home page and some interior pages)', '', f"**{pc.get('heading')}**", '', str(pc.get('intro')), '']
    for fl in site['pluginContactFields']:
        if fl.get('honeypot'):
            S.append(f"- *(hidden honeypot `{fl['name']}`)*")
        elif fl['type'] in ('button', 'submit'):
            S.append(f"- Button: **{fl.get('buttonText')}**")
        else:
            S.append(f"- {fl.get('placeholder') or fl.get('label')} — {fl['type']}{', required' if fl.get('required') else ''}{(' — ' + '; '.join(v['message'] for v in fl.get('validators', []) if v.get('message'))) if fl.get('validators') else ''}")
    pt = HOME.get('pluginTestimonials') or {}
    S += ['', f"## \"{pt.get('heading')}\" carousel (shared section)", '']
    for it in pt.get('items', []):
        S += ['> ' + l for l in (it['quote'] or '').split('\n')]
        S += [f"— {it['source']}", '']
    S.append(f"Button: \"{pt.get('moreText')}\" → {pt.get('moreLink')}")
    pa = HOME.get('pluginAddress') or {}
    S += ['', f"## \"{pa.get('heading')}\" (shared section)", '']
    for o in pa.get('offices', []):
        S += [f"- City label: {o['cityName']}", f"- Address: {o['address']}, {o['city']} {o['zip']}", f"- Phone: {o['phoneLabel']}", f"- \"{o['mapText']}\" link → {o['mapUrl']}"]
    ft = HOME.get('footer') or {}
    S += ['', '## Footer', '', f"Text: \"{ft.get('text') or ''}\" (no text — icons only)", '']
    for l in ft.get('links', []):
        S.append(f"- icon `{os.path.basename(unquote(l.get('img') or ''))}` → {l['href']}")
    S += ['', '## Accessibility widget', '', site['adaWidget'], '']
open(os.path.join(PAGES, '_site.md'), 'w', encoding='utf-8').write('\n'.join(S))
print('pages written:', len(index))
