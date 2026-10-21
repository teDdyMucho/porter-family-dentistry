"""Builds the Porter Family Dentistry site from the harvest of its live site.

    python -I build/build.py

Reads harvest/pages/*.json and harvest/images/, writes site/ (static, Vercel-ready: open the repo
in Vercel with Output Directory "site"). Every page keeps its old URL, the legacy .aspx URLs redirect,
and every page passes through house_text() on its way out (website-builder house rule 1).
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import (FACTS, HARVEST, OLD, ROOT, WEEKDAY, hours_json, is_external, load_pages,  # noqa: E402
                     load_site, local, md_inline, plain, text_of)
from house_text import house_text  # noqa: E402

SITE = ROOT / 'site'
IMG = SITE / 'assets' / 'img'
GS_LOCKUP = Path.home() / '.claude/skills/website-builder/assets/ground-standard/ground-standard-agency-lockup-dark.png'
YEAR = date.today().year
e = lambda s: html.escape(str(s), quote=True)  # noqa: E731

PAGES = load_pages()
SITEDATA = load_site()
_desc_count = {}
for _p in PAGES.values():
    _desc_count[_p.get('metaDescription')] = _desc_count.get(_p.get('metaDescription'), 0) + 1

# ---------- Icons: one stroke weight everywhere ----------
_I = {
    'phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    'pin': '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'down': '<path d="M6 9l6 6 6-6"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'close': '<path d="M6 6l12 12M18 6L6 18"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 7 8.5-7"/>',
    'fax': '<path d="M7 9V3.5h10V9"/><rect x="3.5" y="9" width="17" height="9" rx="2"/><path d="M7 15h10v5.5H7z"/>',
    'alert': '<path d="M12 3l9.5 17h-19L12 3z"/><path d="M12 10v4M12 17.5v.01"/>',
    'heart': '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7a4.3 4.3 0 0 1 7.5 2.8C19.5 15.4 12 20 12 20z"/>',
    'shield': '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6L12 3z"/><path d="M9 12l2 2 4-4"/>',
    'smile': '<circle cx="12" cy="12" r="9"/><path d="M8.5 14.5a4.5 4.5 0 0 0 7 0M9 9.5v.01M15 9.5v.01"/>',
    'tooth': '<path d="M7.5 3.5c1.6 0 2.7 1 4.5 1s2.9-1 4.5-1c2.6 0 4 2.3 3.5 5.2-.4 2.2-1.4 3.6-1.8 6-.4 2.6-1 5.8-2.6 5.8-1.9 0-1.6-5.3-3.6-5.3s-1.7 5.3-3.6 5.3c-1.6 0-2.2-3.2-2.6-5.8-.4-2.4-1.4-3.8-1.8-6-.5-2.9.9-5.2 3.6-5.2z"/>',
    'play': '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5 3.5-5 3.5z"/>',
    'star': '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z" fill="currentColor"/>',
    'facebook': '<path d="M14 21v-7.5h2.5L17 10.5h-3V8.7c0-.9.3-1.5 1.6-1.5H17V4.6A20 20 0 0 0 14.8 4.5C12.6 4.5 11 5.9 11 8.3v2.2H8.5v3H11V21"/>',
    'google': '<path d="M19.5 12.2h-7.3M19.5 12.2a7.5 7.5 0 1 1-2.2-5.5"/>',
}


def icon(name, cls=''):
    classes = ('i ' + cls).strip()
    return (f'<svg class="{classes}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{_I[name]}</svg>')


# ---------- Images: copy what the pages use, crop the hero arches ----------
USED = {}


def asset(local_file):
    """harvest/images/<file> -> /assets/img/<file> (copied once; big JPEGs re-compressed)."""
    if not local_file:
        return None
    name = Path(local_file).name
    if name not in USED:
        src = HARVEST / local_file if (HARVEST / local_file).exists() else HARVEST / 'images' / name
        dst = IMG / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in ('.jpg', '.jpeg') and src.stat().st_size > 160_000:
            ImageOps.exif_transpose(Image.open(src)).convert('RGB').save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
        else:
            shutil.copyfile(src, dst)
        with Image.open(dst) as im:
            USED[name] = im.size
    return f'/assets/img/{name}'


def size(url):
    return USED.get(Path(url).name, (None, None))


def crop(local_file, out_name, ratio, focus, width):
    """A portrait crop of a harvested photo for an arched frame (ratio = w/h)."""
    src = HARVEST / 'images' / Path(local_file).name
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    W, H = im.size
    cw, ch = (round(H * ratio), H) if W / H > ratio else (W, round(W / ratio))
    x = min(max(round(focus[0] * W - cw / 2), 0), W - cw)
    y = min(max(round(focus[1] * H - ch / 2), 0), H - ch)
    im = im.crop((x, y, x + cw, y + ch))
    if im.width > width:
        im = im.resize((width, round(width / ratio)), Image.LANCZOS)
    dst = IMG / out_name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
    USED[out_name] = im.size
    return f'/assets/img/{out_name}'


def img(src, alt, cls='', lazy=True, sizes=None):
    w, h = size(src)
    attrs = f' width="{w}" height="{h}"' if w else ''
    if lazy:
        attrs += ' loading="lazy"'
    if cls:
        attrs += f' class="{cls}"'
    if sizes:
        attrs += f' sizes="{sizes}"'
    return f'<img src="{e(src)}" alt="{e(alt)}"{attrs}>'


# ---------- Navigation (the live site's own menu, Patient Reviews grouped with Testimonials) ----------
def node(n):
    return {'label': n['label'], 'href': local(n['href']), 'children': [node(c) for c in n.get('children', [])]}


TREE = [node(n) for n in SITEDATA['navTree']]
BY = {n['label']: n for n in TREE}
PRACTICE, SERVICES, INFO = BY['Our Practice'], BY['Our Services'], BY['Patient Information']
REVIEWS = BY['Patient Reviews']
CATEGORIES = SERVICES['children']
LABEL = {}


def _index(nodes, parent=None):
    for n in nodes:
        LABEL[n['href']] = n['label']
        n['parent'] = parent
        _index(n['children'], n)


_index(TREE)
PARENT = {}
for n in TREE:
    def _p(x, par):
        PARENT.setdefault(x['href'], par['href'] if par else None)
        for c in x['children']:
            _p(c, x)
    _p(n, None)


def section_of(path):
    for top in (PRACTICE, SERVICES, INFO):
        if path.startswith(top['href']):
            return top['href']
    return {'/patient-reviews/': PRACTICE['href']}.get(path, path)


def crumbs_for(path):
    trail, p = [], path
    while p and p != '/':
        trail.insert(0, (LABEL.get(p) or heading_of(PAGES[p]) if p in PAGES else p, p))
        p = PARENT.get(p) or (p.rstrip('/').rsplit('/', 1)[0] + '/' if p.count('/') > 2 else None)
    return [('Home', '/')] + trail


def heading_of(page):
    return page.get('pageHeading') or page['title']


# Duplicate articles (same text under two categories) point their canonical at the first one.
CANONICAL = {}
_seen = {}
for p in PAGES.values():
    h = p.get('contentHash')
    if h in _seen and p['path'] != '/':
        CANONICAL[p['path']] = _seen[h]
    else:
        _seen.setdefault(h, p['path'])
# Same article under two categories with the same title (a comma or capital apart): same canonical.
_by_title = {}
for p in sorted(PAGES.values(), key=lambda q: q['path']):
    prim = _by_title.setdefault(p['title'], p['path'])
    if prim != p['path'] and p['path'] not in CANONICAL:
        CANONICAL[p['path']] = CANONICAL.get(prim, prim)
for p in PAGES.values():
    if p.get('duplicateOf'):
        prim = next((q['path'] for q in PAGES.values() if q['slug'] == p['duplicateOf']), None)
        if prim:
            CANONICAL[p['path']] = prim


# ---------- Page chrome ----------
def strip():
    f = FACTS
    return f'''<div class="strip">
  <div class="wrap strip__inner">
    <div class="strip__group">
      <a class="strip__item strip__item--hide-sm" href="{e(f['maps'])}" target="_blank" rel="noopener">{icon('pin')}{e(f['street'])}, {e(f['city'])}</a>
      <a class="strip__item" href="tel:{f['tel']}">{icon('phone')}{e(f['phone'])}</a>
    </div>
    <div class="strip__group strip__group--secondary">
      <span class="strip__item" data-status><span class="status-dot" aria-hidden="true"></span><span data-status-text>Office hours below</span></span>
      <a class="strip__item" href="/our-services/dental-emergencies/">{icon('alert')}24/7 emergency services</a>
    </div>
  </div>
</div>'''


def nav_dropdown(top, current, label=None, extra=None):
    links = [f'<a class="panel__all" href="{top["href"]}">{e(top["label"])}</a>']
    links += [f'<a href="{c["href"]}">{e(c["label"])}</a>' for c in top['children']]
    if extra:
        links += [f'<a href="{x["href"]}">{e(x["label"])}</a>' for x in extra]
    cur = ' is-current' if current == top['href'] else ''
    pid = 'panel-' + re.sub(r'\W+', '-', top['label'].lower())
    return f'''<li class="nav__item{cur}" data-dropdown>
        <button class="nav__trigger" type="button" aria-expanded="false" aria-controls="{pid}">{e(label or top['label'])}{icon('down')}</button>
        <div class="panel" id="{pid}">{''.join(links)}</div>
      </li>'''


def nav_services(current):
    cols = []
    for c in CATEGORIES:
        kids = ''.join(f'<li><a href="{k["href"]}">{e(k["label"])}</a></li>' for k in c['children'])
        cols.append(f'<div class="mega__col"><h3><a href="{c["href"]}">{e(c["label"])}</a></h3>{f"<ul>{kids}</ul>" if kids else ""}</div>')
    cur = ' is-current' if current == SERVICES['href'] else ''
    return f'''<li class="nav__item{cur}" data-dropdown>
        <button class="nav__trigger" type="button" aria-expanded="false" aria-controls="panel-services">Our Services{icon('down')}</button>
        <div class="panel panel--mega" id="panel-services">
          <div class="mega">{''.join(cols)}</div>
          <div class="mega__foot"><p>Not sure what you need? We'll talk it through.</p><a class="link" href="{SERVICES['href']}">All services {icon('arrow')}</a></div>
        </div>
      </li>'''


def header(current):
    return f'''<header class="site-header">
  {strip()}
  <div class="bar">
    <div class="wrap bar__inner">
      <a class="brand" href="/" aria-label="{e(FACTS['legal'])}, home">
        <span class="brand__name">{e(FACTS['legal'])}</span>
        <span class="brand__tag">{e(FACTS['tagline'])}</span>
      </a>
      <nav aria-label="Main">
        <ul class="nav" role="list">
          {nav_dropdown(PRACTICE, current, extra=[REVIEWS])}
          {nav_services(current)}
          {nav_dropdown(INFO, current)}
          <li class="nav__item"><a class="nav__link" href="/contact-us/"{' aria-current="page"' if current == '/contact-us/' else ''}>Contact Us</a></li>
        </ul>
      </nav>
      <div class="bar__actions">
        <a class="btn btn--primary btn--sm" href="/appointment-request/">{icon('calendar')}Request an Appointment</a>
        <button class="menu-btn" type="button" aria-expanded="false" aria-controls="drawer">{icon('menu')}Menu</button>
      </div>
    </div>
  </div>
</header>'''


def drawer():
    def group(top, extra=None):
        items = [top] + top['children'] + (extra or [])
        lis = ''.join(f'<li><a href="{x["href"]}">{e(x["label"] if x is not top else "All of " + x["label"])}</a></li>' for x in items)
        return f'<details><summary>{e(top["label"])}{icon("down")}</summary><ul>{lis}</ul></details>'
    return f'''<div class="drawer" id="drawer" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="drawer__head">
    <a class="brand" href="/"><span class="brand__name">{e(FACTS['legal'])}</span></a>
    <button class="drawer__close" type="button" data-drawer-close aria-label="Close menu">{icon('close')}</button>
  </div>
  <nav class="drawer__body" aria-label="Menu">
    <a href="/">Home</a>
    {group(PRACTICE, [REVIEWS])}
    {group(SERVICES)}
    {group(INFO)}
    <a href="/contact-us/">Contact Us</a>
  </nav>
  <div class="drawer__foot">
    <a class="btn btn--ghost" href="tel:{FACTS['tel']}">{icon('phone')}Call</a>
    <a class="btn btn--primary" href="/appointment-request/">Request</a>
  </div>
</div>'''


def hours_table():
    rows = ''.join(f'<tr data-day="{WEEKDAY[d]}"><th scope="row">{d}</th><td>{e(t)}</td></tr>' for d, t, _ in FACTS['hours'])
    return f'<table class="hours"><caption class="sr-only">Consultation hours</caption><tbody>{rows}</tbody></table>'


def footer():
    f = FACTS
    def col(title, items):
        return f'<div><h2>{e(title)}</h2><ul role="list">' + ''.join(f'<li><a href="{x["href"]}">{e(x["label"])}</a></li>' for x in items) + '</ul></div>'
    practice = [PRACTICE] + PRACTICE['children'] + [REVIEWS]
    info = [INFO] + INFO['children'] + [{'label': 'Appointment Request', 'href': '/appointment-request/'}, {'label': 'Contact Us', 'href': '/contact-us/'}]
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__contact">
        <p class="brand__name">{e(f['name'])}</p>
        <p class="brand__tag">{e(f['legal'])}</p>
        <address>{e(f['street'])}<br>{e(f['city'])}, {e(f['state'])} {e(f['zip'])}</address>
        <a class="footer__phone" href="tel:{f['tel']}">{e(f['phone'])}</a>
        <p class="footer__meta">Fax: {e(f['fax'])}<br><a href="mailto:{f['email']}">{e(f['email'])}</a></p>
        <div class="footer__social">
          <a href="{e(f['facebook'])}" target="_blank" rel="noopener" aria-label="Porter Family Dentistry on Facebook">{icon('facebook')}</a>
          <a href="{e(f['google'])}" target="_blank" rel="noopener" aria-label="Porter Family Dentistry on Google">{icon('google')}</a>
        </div>
      </div>
      <div class="footer__cols">
        {col('Our Practice', practice)}
        {col('Our Services', [SERVICES] + CATEGORIES)}
        {col('Patients', info)}
      </div>
    </div>
    <div class="footer__bar">
      <p>© {YEAR} {e(f['legal'])}. {e(f['emergency'])}</p>
      <a class="gs-credit" href="https://www.groundstandard.com">
        <span>Backed by</span>
        <img src="/assets/img/ground-standard-agency-lockup-dark.png" alt="Ground Standard Agency" width="1920" height="197" loading="lazy">
      </a>
    </div>
  </div>
</footer>
<div class="call-bar" aria-label="Quick actions">
  <a class="btn btn--ghost" href="tel:{f['tel']}">{icon('phone')}Call</a>
  <a class="btn btn--primary" href="/appointment-request/">{icon('calendar')}Request</a>
</div>'''


def jsonld_dentist():
    f = FACTS
    spec = []
    for d, _, t in f['hours']:
        if t:
            spec.append({'@type': 'OpeningHoursSpecification', 'dayOfWeek': d, 'opens': t[0], 'closes': t[1]})
    return {
        '@context': 'https://schema.org', '@type': 'Dentist', '@id': OLD + '/#practice',
        'name': f['name'], 'alternateName': f['legal'], 'slogan': f['tagline'], 'url': OLD + '/',
        'image': OLD + '/assets/img/og.jpg', 'logo': OLD + '/assets/img/icon_favicon_touch-icon_tooth.png',
        'telephone': f['phone'], 'faxNumber': f['fax'], 'email': f['email'], 'foundingDate': str(f['founded']),
        'address': {'@type': 'PostalAddress', 'streetAddress': f['street'], 'addressLocality': f['city'],
                    'addressRegion': f['state_abbr'], 'postalCode': f['zip'], 'addressCountry': 'US'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': f['geo'][0], 'longitude': f['geo'][1]},
        'openingHoursSpecification': spec, 'hasMap': f['maps'], 'sameAs': [f['facebook']],
        'areaServed': f['areas'], 'paymentAccepted': 'Cash, Check, Debit Card, Credit Card, CareCredit',
        'employee': {'@type': 'Person', 'name': 'Dr. David L. Porter', 'jobTitle': 'Dentist',
                     'alumniOf': ['Wabash College', 'Indiana University']},
    }


def shell(page_path, title, description, body, current, extra_ld=(), og_image='/assets/img/og.jpg', robots=None):
    canon = CANONICAL.get(page_path, page_path)
    page = PAGES.get(page_path)
    if page and _desc_count.get(description, 0) > 1:
        description = first_sentence(page, 155) or description
    lds = [jsonld_dentist(), *extra_ld]
    ld = ''.join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{f'<meta name="robots" content="{robots}">' if robots else f'<link rel="canonical" href="{OLD}{canon}">'}
<meta name="theme-color" content="#fbf7f2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(FACTS['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{OLD}{canon}">
<meta property="og:image" content="{OLD}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/icon_favicon_touch-icon_tooth.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/icon_favicon_touch-icon_tooth.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,400;0,500;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500..800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/styles.css">
<script>document.documentElement.classList.add('js');if(/[?&]nomotion\\b/.test(location.search))document.documentElement.classList.add('nomotion');</script>{ld}
</head>
<body data-hours='{hours_json()}' data-tz="America/Chicago">
<a class="skip" href="#main">Skip to content</a>
{header(current)}
{drawer()}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
'''


# ---------- Block rendering ----------
def render_list(b, tag):
    out = []
    for it in b.get('items', []):
        inner = md_inline(text_of(it))
        kids = it.get('children') or it.get('items')
        if kids:
            inner += render_list({'items': kids}, tag)
        out.append(f'<li>{inner}</li>')
    return f'<{tag}>' + ''.join(out) + f'</{tag}>'


def render_blocks(blocks, skip_heading=True):
    out, skipped = [], not skip_heading
    for b in blocks:
        t = b['type']
        if t == 'h2' and not skipped:
            skipped = True
            continue
        if t in ('h2', 'h3', 'h4'):
            if b.get('text', '').strip():
                out.append(f'<{t}>{md_inline(text_of(b))}</{t}>')
        elif t == 'p':
            s = md_inline(text_of(b))
            if s:
                out.append(f'<p>{s}</p>')
        elif t in ('ul', 'ol'):
            if b.get('items'):
                out.append(render_list(b, t))
        elif t == 'blockquote':
            out.append(f'<blockquote>{md_inline(text_of(b))}</blockquote>')
        elif t == 'img' and b.get('localFile'):
            src = asset(b['localFile'])
            tag = img(src, b.get('alt') or BADGE_ALT.get(Path(b['localFile']).name, ''))
            href = b.get('href')
            out.append(f'<p class="prose-img"><a href="{e(local(href))}" target="_blank" rel="noopener">{tag}</a></p>' if href else f'<p class="prose-img">{tag}</p>')
        elif t in ('iframe', 'embed') and b.get('src'):
            out.append(f'<div class="embed"><iframe src="{e(b["src"])}" title="CareCredit payment calculator" loading="lazy"></iframe></div>')
        elif t == 'map' and b.get('src'):
            out.append(f'<div class="map"><iframe src="{e(b["src"])}" title="Map to {e(FACTS["name"])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>')
        elif t == 'field' and b.get('buttonText') == 'Map & Directions':
            out.append(f'<p><a class="btn btn--ghost btn--sm" href="{e(FACTS["maps"])}" target="_blank" rel="noopener">{icon("pin")}Map &amp; Directions</a></p>')
        elif t == 'hr':
            out.append('<hr>')
    return '\n'.join(out)


def first_sentence(page, limit=150):
    for b in page['blocks']:
        md = (b.get('md') or '').strip()
        if b['type'] == 'p' and len(b.get('text', '').strip()) >= 50 and not (md.startswith('**') and md.endswith('**')):
            s = plain(text_of(b))
            m = re.match(r'(.+?[.!?])(\s|$)', s)
            s = m.group(1) if m else s
            return s if len(s) <= limit else s[:limit].rsplit(' ', 1)[0] + '…'
    return ''


# Badges carry information (which cards are accepted), so they get words when the old site gave none
BADGE_ALT = {
    'badge_card_mastercard.png': 'Mastercard', 'badge_card_visa.png': 'Visa', 'badge_card_discover.png': 'Discover',
    'badge_card_amex.png': 'American Express', 'badge_carecredit-logo.png': 'CareCredit',
    'badge_carecredit-logo-tagline.png': 'CareCredit', 'badge_carecredit_apply-now-button.png': 'Apply now for CareCredit',
    'badge_carecredit_pay-bill-button.jpg': 'Pay your CareCredit bill',
}

# ---------- Building blocks ----------
BANNER_ALT = {'banner2.jpg': 'A smiling patient', 'banner8.jpg': 'Smiling patients'}


def page_head(page, title, lead=None):
    crumbs = crumbs_for(page['path'])
    lis = ''.join(f'<li><a href="{h}">{e(t)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{e(t)}</li>'
                  for i, (t, h) in enumerate(crumbs))
    banner = (page.get('hero') or {}).get('banner') or {}
    ban = asset(banner.get('localFile')) if banner.get('localFile') else None
    band = f'<div class="wrap"><div class="transom">{img(ban, "", lazy=False)}</div></div>' if ban else ''
    return f'''<section class="page-head">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="wrap">
    <nav aria-label="Breadcrumb"><ol class="crumbs">{lis}</ol></nav>
    <h1>{e(title)}</h1>
    {f'<p class="lead">{lead}</p>' if lead else ''}
  </div>
  {band}
</section>'''


def aside(page):
    sec = section_of(page['path'])
    top = {PRACTICE['href']: PRACTICE, SERVICES['href']: SERVICES, INFO['href']: INFO}.get(sec)
    nav = ''
    if top:
        items = [top] + (CATEGORIES if top is SERVICES else top['children'] + ([REVIEWS] if top is PRACTICE else []))
        if top is SERVICES:
            par = PARENT.get(page['path'])
            cat = next((c for c in CATEGORIES if page['path'] == c['href'] or par == c['href']), None)
            if cat and cat['children']:
                items = [cat] + cat['children']
        cur = ' aria-current="page"'
        lis = ''.join(f'<li><a href="{x["href"]}"{cur if x["href"] == page["path"] else ""}>{e(x["label"])}</a></li>' for x in items)
        nav = f'<div class="aside__box"><h2>In this section</h2><ul class="aside__nav" role="list">{lis}</ul></div>'
    return f'''<aside class="aside" aria-label="More">
  {nav}
  <div class="aside__box aside__cta">
    <h2>Schedule your visit</h2>
    <p>Please contact our office by phone or complete an online appointment request.</p>
    <a class="phone" href="tel:{FACTS['tel']}">{e(FACTS['phone'])}</a>
    <a class="btn btn--primary" href="/appointment-request/">{icon('calendar')}Request an Appointment</a>
  </div>
  <div class="aside__box">
    <h2>Consultation hours</h2>
    {hours_table()}
    <p class="aside__note">{e(FACTS['emergency'])}</p>
  </div>
</aside>'''


def closer(title='The first step towards a beautiful, healthy smile is to schedule an appointment.',
           text='Please contact our office by phone or complete an online appointment request. Our scheduling coordinator will contact you to confirm your appointment.'):
    return f'''<section class="section">
  <div class="wrap">
    <div class="closer" data-reveal>
      <h2>{e(title)}</h2>
      <p>{e(text)}</p>
      <div class="closer__cta">
        <a class="btn btn--primary" href="/appointment-request/">{icon('calendar')}Request an Appointment</a>
        <a class="btn btn--ghost" href="tel:{FACTS['tel']}">{icon('phone')}Call {e(FACTS['phone'])}</a>
      </div>
    </div>
  </div>
</section>'''


def breadcrumb_ld(page):
    crumbs = crumbs_for(page['path'])
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': t, 'item': OLD + h} for i, (t, h) in enumerate(crumbs)]}


# ---------- Page types ----------
TESTIMONIALS = []


def harvest_testimonials():
    p = PAGES['/our-practice/testimonials/']
    quote = None
    for b in p['blocks']:
        if b['type'] == 'blockquote':
            quote = plain(text_of(b))
        elif b['type'] == 'p' and quote:
            TESTIMONIALS.append((quote, plain(text_of(b))))
            quote = None


def quote_cards(items):
    cards = []
    for q, who in items:
        cards.append(f'''<figure class="quote-card" data-reveal>
        <blockquote>{e(q)}</blockquote>
        <figcaption>{e(who)}</figcaption>
      </figure>''')
    return '<div class="quotes">' + ''.join(cards) + '</div>'


def article_page(page):
    title = heading_of(page)
    kids = [c for c in (next((n for n in CATEGORIES if n['href'] == page['path']), {}) or {}).get('children', [])]
    src = page['blocks']
    if kids:
        kid_hrefs = {k['href'] for k in kids}
        def is_kid_list(b):
            hrefs = [local(l.get('href')) for it in b.get('items', []) for l in it.get('links', [])]
            return b['type'] == 'ul' and hrefs and all(h in kid_hrefs for h in hrefs)
        src = [b for b in src if not is_kid_list(b) and plain(text_of(b)).rstrip(':') != 'Related Pages']
    blocks = render_blocks(src)
    kids_html = ''
    if kids:
        cards = ''.join(f'''<article class="card" data-reveal>
          <span class="card__icon">{icon('tooth')}</span>
          <h3><a class="card__link" href="{k['href']}">{e(k['label'])}</a></h3>
          <p>{e(first_sentence(PAGES[k['href']]) if k['href'] in PAGES else '')}</p>
          <span class="card__more">Read more {icon('arrow')}</span>
        </article>''' for k in kids)
        kids_html = f'<div class="grid kids" style="--cols:2">{cards}</div>'
    body = f'''{page_head(page, title)}
<section class="section">
  <div class="wrap article">
    <div>
      <div class="prose">{blocks}</div>
      {kids_html}
    </div>
    {aside(page)}
  </div>
</section>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or first_sentence(page),
                 body, section_of(page['path']), extra_ld=[breadcrumb_ld(page)])


def services_hub(page):
    bl = page['blocks']
    # intro: everything up to the nested list of categories, which becomes the category grid
    cut = next((i for i, b in enumerate(bl) if b['type'] == 'ul' and any('our-services/endodontics' in (l.get('href') or '')
                for it in b.get('items', []) for l in it.get('links', []))), len(bl))
    intro = render_blocks(bl[:cut])
    cards = []
    for c in CATEGORIES:
        kids = ''.join(f'<li><a href="{k["href"]}">{e(k["label"])}</a></li>' for k in c['children'])
        lead = first_sentence(PAGES[c['href']], 130) if c['href'] in PAGES else ''
        cards.append(f'''<article class="card cat" data-reveal>
          <span class="card__icon">{icon('tooth')}</span>
          <h3><a href="{c['href']}">{e(c['label'])}</a></h3>
          <p>{e(lead)}</p>
          {f'<ul class="cat__list" role="list">{kids}</ul>' if kids else f'<a class="link" href="{c["href"]}">Read more {icon("arrow")}</a>'}
        </article>''')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap article">
    <div class="prose">{intro}</div>
    {aside(page)}
  </div>
</section>
<section class="section room--linen">
  <div class="wrap">
    <header class="head"><p class="eyebrow">Our Services</p><h2>Everything we do, by specialty</h2></header>
    <div class="grid" style="--cols:3">{''.join(cards)}</div>
  </div>
</section>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, SERVICES['href'], extra_ld=[breadcrumb_ld(page)])


def team_page(page):
    bl = page['blocks']
    group = next(b for b in bl if b['type'] == 'img' and 'group' in (b.get('localFile') or ''))
    intro = next(b for b in bl if b['type'] == 'p')
    people, cur = [], None
    for b in bl:
        if b['type'] == 'h2' and b['text'] != heading_of(page):
            cur = {'name': b['text'], 'role': '', 'bio': [], 'photo': None}
            people.append(cur)
        elif cur and b['type'] in ('h3', 'h4'):
            cur['role'] = b['text']
        elif cur and b['type'] == 'p':
            cur['bio'].append(md_inline(text_of(b)))
    head = next(b for b in bl if b['type'] == 'img' and 'headshot' in (b.get('localFile') or ''))
    people[0]['photo'] = asset(head['localFile'])
    gsrc = asset(group['localFile'])
    cards = []
    for p in people:
        photo = (f'<div class="frame frame--arch person__photo">{img(p["photo"], p["name"])}</div>' if p['photo']
                 else f'<div class="person__mono" aria-hidden="true">{e("".join(w[0] for w in p["name"].split()[:2]))}</div>')
        cards.append(f'''<article class="person" data-reveal>
        {photo}
        <div class="person__body">
          <h2>{e(p['name'])}</h2>
          {f'<p class="role">{e(p["role"])}</p>' if p['role'] else ''}
          <div class="prose">{''.join(f'<p>{x}</p>' for x in p['bio'])}</div>
        </div>
      </article>''')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="frame frame--wide" data-reveal>{img(gsrc, 'The Porter Family Dentistry team')}</div>
      <div class="split__copy"><p class="lead">{md_inline(text_of(intro))}</p></div>
    </div>
  </div>
</section>
<section class="section room--linen">
  <div class="wrap people">{''.join(cards)}</div>
</section>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, PRACTICE['href'], extra_ld=[breadcrumb_ld(page)])


def testimonials_page(page):
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap">
    {quote_cards(TESTIMONIALS)}
    <p class="after-quotes"><a class="link" href="/patient-reviews/">Write a review {icon('arrow')}</a></p>
  </div>
</section>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, PRACTICE['href'], extra_ld=[breadcrumb_ld(page)])


def faq_page(page):
    bl = page['blocks']
    intro_end = next(i for i, b in enumerate(bl) if b['type'] == 'h3')
    intro = render_blocks(bl[:intro_end])
    items, cur = [], None
    for b in bl[intro_end:]:
        if b['type'] == 'h3':
            cur = {'q': b['text'], 'blocks': []}
            items.append(cur)
        elif cur:
            cur['blocks'].append(b)
    det = []
    for i, it in enumerate(items):
        det.append(f'''<details{' open' if i == 0 else ''}>
        <summary>{e(it['q'])}{icon('arrow')}</summary>
        <div class="faq__body"><div><div class="prose">{render_blocks(it['blocks'], skip_heading=False)}</div></div></div>
      </details>''')
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': it['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': ' '.join(
            plain(text_of(b)) if b['type'] != 'ul' else ' '.join(plain(text_of(x)) for x in b.get('items', [])) for b in it['blocks'])}}
        for it in items]}
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap article">
    <div>
      <div class="prose">{intro}</div>
      <div class="faq">{''.join(det)}</div>
    </div>
    {aside(page)}
  </div>
</section>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, INFO['href'], extra_ld=[breadcrumb_ld(page), ld])


def videos_page(page):
    bl = page['blocks']
    first_h3 = next(i for i, b in enumerate(bl) if b['type'] == 'h3')
    intro = render_blocks(bl[:first_h3])
    groups, cur = [], None
    for b in bl[first_h3:]:
        if b['type'] == 'h3':
            cur = {'title': b['text'], 'items': []}
            groups.append(cur)
        elif b['type'] == 'ul' and cur:
            for it in b['items']:
                link = (it.get('links') or [{}])[0].get('href')
                thumb = (it.get('media') or [{}])[0].get('localFile')
                cur['items'].append((it['text'], link, asset(thumb) if thumb else None))
        elif b['type'] == 'p' and groups:
            groups[-1].setdefault('after', []).append(md_inline(text_of(b)))
    secs = []
    for g in groups:
        cards = ''.join(f'''<li><button class="video" type="button" data-video="{e(src)}" data-title="{e(t)}">
            <span class="video__thumb">{img(th, '') if th else ''}<span class="video__play">{icon('play')}</span></span>
            <span class="video__title">{e(t)}</span></button></li>''' for t, src, th in g['items'] if src)
        secs.append(f'<section class="video-group" data-reveal><h2>{e(g["title"])}</h2><ul class="videos" role="list">{cards}</ul></section>')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap">
    <div class="prose">{intro}</div>
    {''.join(secs)}
  </div>
</section>
<dialog class="player" id="player" aria-label="Dental video">
  <div class="player__bar"><p class="player__title" id="playerTitle"></p><button class="drawer__close" type="button" data-player-close aria-label="Close video">{icon('close')}</button></div>
  <video id="playerVideo" controls playsinline preload="none"></video>
</dialog>
{closer()}'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, INFO['href'], extra_ld=[breadcrumb_ld(page)])


# ---------- Forms (the live site's own fields, labels and messages) ----------
def field(name, label, kind='text', required=False, error=None, hint=None, auto=None, rows=None):
    req = ' required' if required else ''
    star = ' <span class="req" aria-hidden="true">*</span>' if required else ''
    ac = f' autocomplete="{auto}"' if auto else ''
    fid = 'f-' + name
    err = f'<p class="field__error" id="{fid}-err">{e(error)}</p>' if error else ''
    described = f' aria-describedby="{fid}-err"' if error else ''
    if kind == 'textarea':
        control = f'<textarea id="{fid}" name="{name}"{req}{described}></textarea>'
    else:
        im = ' inputmode="tel"' if kind == 'tel' else ''
        control = f'<input id="{fid}" name="{name}" type="{kind}"{req}{ac}{described}{im}>'
    hint_html = f'<p class="hint">{e(hint)}</p>' if hint else ''
    return f'<div class="field"><label for="{fid}">{e(label)}{star}</label>{hint_html}{control}{err}</div>'


def choices(name, legend, options, kind='checkbox', required=False, error=None):
    opts = ''.join(f'<label><input type="{kind}" name="{name}" value="{e(o)}">{e(o)}</label>' for o in options)
    err = f'<p class="field__error">{e(error)}</p>' if error else ''
    return f'<div class="field"{" data-required" if required else ""}><fieldset><legend>{e(legend)}</legend><div class="choices">{opts}</div></fieldset>{err}</div>'


def form(kind, inner, submit, subject, success, note=''):
    return f'''<form class="form" data-form data-kind="{kind}" data-endpoint="" data-mailto="{FACTS['email']}" data-subject="{e(subject)}"
      data-success="{e(success)}" data-phone="{e(FACTS['phone'])}" novalidate>
      {inner}
      {note}
      <div><button class="btn btn--primary" type="submit">{e(submit)}</button></div>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>'''


def appointment_page(page):
    bl = page['blocks']
    def keep(b):
        t = plain(text_of(b)) if b['type'] == 'p' else ''
        return b['type'] != 'form' and not t.startswith('Consultation Hours') and 'Items in bold are required' not in t
    intro = render_blocks([b for b in bl if keep(b)])
    inner = (f'<div class="form__row">{field("name", "Name", required=True, error="Please enter your name", auto="name")}'
             f'{field("email", "Email", "email", error="Please fill in phone or email address!", auto="email")}</div>'
             f'<div class="form__row">{field("phone", "Phone", "tel", error="Please fill in phone or email address!", auto="tel")}'
             f'{field("heard", "How did you hear about us?")}</div>'
             + choices('current_patient', 'Are you a current patient?', ['Yes', 'No'], 'radio')
             + choices('days', 'Preferred day(s) of the week for an appointment?', ['Any Day', 'Monday', 'Tuesday', 'Thursday', 'Friday'])
             + choices('times', 'Preferred time(s) for an appointment?', ['Any Time', 'Morning', 'Afternoon'])
             + field('nature', 'Please describe the nature of your appointment (e.g., consultation, check-up, etc.)', 'textarea'))
    note = '<p class="form__note">Please do not use this form to cancel or change an existing appointment.</p>'
    f = form('appointment', inner.replace('data-form', ''), 'Request My Appointment', 'Appointment request',
             'Thank you. Our scheduling coordinator will contact you to confirm your appointment.', note)
    f = f.replace('data-form data-kind="appointment"', 'data-form data-kind="appointment" data-one-of="email,phone"')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap article">
    <div><div class="prose">{intro}</div>{f}</div>
    {aside(page)}
  </div>
</section>'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, '/appointment-request/', extra_ld=[breadcrumb_ld(page)])


def contact_page(page):
    bl = page['blocks']
    form_i = next(i for i, b in enumerate(bl) if b['type'] == 'form')
    info = render_blocks([b for b in bl[:form_i] if b['type'] not in ('map',) and not (b['type'] == 'h2' and b['text'] == 'Contact Us')], skip_heading=False)
    msg_label = 'Type your message here:'
    inner = (f'<div class="form__row">{field("name", "Name", required=True, error="Please enter a name!", auto="name")}'
             f'{field("phone", "Phone", "tel", error="Email or Phone Required", auto="tel")}</div>'
             f'{field("email", "Email", "email", error="Email or Phone Required", auto="email")}'
             + field('message', msg_label, 'textarea', hint='Messages sent using this form are not considered private. Avoid sending confidential information via email.'))
    f = form('contact', inner, 'Send My Message', 'Message from the website', 'Thank you. We will get back to you soon.')
    f = f.replace('data-form data-kind="contact"', 'data-form data-kind="contact" data-one-of="email,phone"')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap contact">
    <div class="prose contact__info">{info}</div>
    <div class="contact__side">
      <div class="map"><iframe src="{e(FACTS['map_embed'])}" title="Map to {e(FACTS['name'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <div class="aside__box"><h2>Consultation hours</h2>{hours_table()}<p class="aside__note">{e(FACTS['emergency'])}</p></div>
    </div>
  </div>
</section>
<section class="section room--linen">
  <div class="wrap narrow">
    <header class="head"><p class="eyebrow">Contact Us</p><h2>Send us a message</h2>
      <p class="lead">We encourage you to contact us with any questions or comments you may have. Please call our office or use the quick contact form below.</p></header>
    {f}
  </div>
</section>'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, '/contact-us/', extra_ld=[breadcrumb_ld(page)])


def reviews_page(page):
    stars = ''.join(f'<label><input type="radio" name="rating" value="{n}"><span>{n} star{"s" if n > 1 else ""}</span></label>' for n in range(5, 0, -1))
    inner = (f'<div class="field"><fieldset><legend>Your Star Rating</legend><p class="hint">Click on a star to change your rating 1 – 5, where 5 = great! and 1 = really bad</p>'
             f'<div class="choices rating">{stars}</div></fieldset></div>'
             + field('review', 'Your Review', 'textarea', required=True, error='Comment is Required', hint='Leave a comment to share your experience with others.')
             + f'<div class="form__row">{field("name", "Name", required=True, error="Name is Required", auto="name")}'
             f'{field("city", "City", required=True, error="City is Required", auto="address-level2")}</div>'
             + field('email', 'Email', 'email', required=True, error='Email is Required', auto='email'))
    f = form('review', inner, 'Submit My Review', 'Patient review', 'Thank you for sharing your experience!')
    body = f'''{page_head(page, heading_of(page))}
<section class="section">
  <div class="wrap split split--top">
    <div>
      <h2 class="h3">Write your Review:</h2>
      {f}
    </div>
    <div class="share">
      <p class="lead">Please take a moment to share your review on our social networks:</p>
      <div class="share__links">
        <a class="btn btn--ghost" href="{e(FACTS['google'])}" target="_blank" rel="noopener">{icon('google')}Google</a>
        <a class="btn btn--ghost" href="{e(FACTS['facebook'])}" target="_blank" rel="noopener">{icon('facebook')}Facebook</a>
      </div>
      {quote_cards(TESTIMONIALS[:2])}
    </div>
  </div>
</section>'''
    return shell(page['path'], page['title'], page.get('metaDescription') or '', body, PRACTICE['href'], extra_ld=[breadcrumb_ld(page)])


# ---------- Home ----------
def home_page(page):
    f = FACTS
    bl = page['blocks']
    paras = [b for b in bl if b['type'] == 'p']
    svc_list = next(b for b in bl if b['type'] == 'ul')
    lead = plain(text_of(paras[0])).split('. ')[0] + '.'

    arches = [
        crop('team_dr-david-l-porter_headshot.jpg', 'arch-dr-porter.jpg', 3 / 3.6, (.5, .45), 275),
        crop('hero-slide3_cover3_stock-family.jpg', 'arch-family.jpg', 4 / 4.4, (.74, .5), 700),
        crop('hero-slide1_cover1_stock-smiling-woman.jpg', 'arch-smile.jpg', 3 / 3.4, (.72, .5), 600),
        crop('hero-slide2_cover2_stock-smiling-man-hat.jpg', 'arch-man.jpg', 2 / 2.9, (.6, .45), 460),
    ]
    alts = ['Dr. David L. Porter', 'A smiling family', 'A smiling patient', 'A smiling patient']
    arch_html = ''.join(f'<div class="frame frame--arch">{img(s, a, lazy=False)}</div>' for s, a in zip(arches, alts))

    # the services the home page lists, each with the first sentence of its own page
    cards = []
    for it in svc_list['items']:
        href = local((it.get('links') or [{}])[0].get('href'))
        label = it['text'].strip()
        target = PAGES.get(href)
        desc = first_sentence(target, 120) if target and href != '/our-services/' else 'Endodontics, periodontics, prosthodontics, restorations and more.'
        cards.append(f'''<article class="card" data-reveal>
          <span class="card__icon">{icon('tooth')}</span>
          <h3><a class="card__link" href="{href}">{e(label)}</a></h3>
          <p>{e(desc)}</p>
          <span class="card__more">Learn more {icon('arrow')}</span>
        </article>''')

    team = PAGES['/our-practice/meet-the-team/']
    bio = [b for b in team['blocks'] if b['type'] == 'p']
    dr = [md_inline(text_of(b)) for b in bio if 'Dr. Porter' in b.get('text', '') or 'David L. Porter received' in b.get('text', '')]
    practice = PAGES['/our-practice/']
    pb = practice['blocks']

    def practice_section(name):
        for i, b in enumerate(pb):
            if b['type'] == 'p' and plain(text_of(b)) == name and i + 1 < len(pb):
                return plain(text_of(pb[i + 1]))
        return ''
    values = [('heart', 'Our Philosophy', practice_section('Our Philosophy')),
              ('smile', 'A Positive Experience', practice_section('A Positive Experience')),
              ('shield', 'Uncompromising Safety', practice_section('Uncompromising Safety'))]
    value_cards = ''.join(f'''<article class="value" data-reveal>
        <span class="card__icon">{icon(i)}</span><h3>{e(t)}</h3><p>{e(x)}</p></article>''' for i, t, x in values)

    info = PAGES['/patient-information/']
    pay = next((plain(text_of(info['blocks'][i + 1])) for i, b in enumerate(info['blocks'])
                if b['type'] == 'p' and plain(text_of(b)) == 'Payment Options'), '')
    insurance = next((plain(text_of(b)) for b in PAGES['/our-services/']['blocks']
                      if b['type'] == 'p' and 'insurance' in b.get('text', '')), '')
    badges = ''.join(img(asset(f'images/{n}'), a) for n, a in [('badge_card_mastercard.png', 'Mastercard'), ('badge_card_visa.png', 'Visa'),
                                                                 ('badge_card_discover.png', 'Discover'), ('badge_card_amex.png', 'American Express')])
    cc = img(asset('images/badge_carecredit-logo.png'), 'CareCredit')
    areas = ''.join(f'<li>{e(a)}</li>' for a in f['areas'])

    body = f'''<section class="hero">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="wrap">
    <div class="hero__copy">
      <p class="eyebrow">{e(f['name'])} · {e(f['city'])}, {e(f['state'])}</p>
      <h1 class="hero__title">We treat you like you are <em>our family!</em></h1>
      <p class="lead hero__lead">{e(lead)}</p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="/appointment-request/">{icon('calendar')}Request an Appointment</a>
        <a class="btn btn--ghost" href="tel:{f['tel']}">{icon('phone')}Call {e(f['phone'])}</a>
      </div>
      <p class="hero__facts">
        <span data-status>{icon('clock')}<span data-status-text>Consultation hours below</span></span>
        <span>{icon('pin')}{e(f['street'])}, {e(f['city'])}</span>
        <span>{icon('alert')}{e(f['emergency'])}</span>
      </p>
    </div>
    <div class="arches" aria-hidden="false">{arch_html}</div>
  </div>
</section>

<section class="proof" aria-label="At a glance">
  <div class="wrap proof__list">
    <div data-reveal><strong>{f['founded']}</strong><span>Dr. Porter opened his office</span></div>
    <div data-reveal><strong>177</strong><span>years of combined staff experience</span></div>
    <div data-reveal><strong>24/7</strong><span>emergency services available</span></div>
    <div data-reveal><strong>{len(f['areas'])}</strong><span>communities in our service area</span></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split split--top">
      <header class="head">
        <p class="eyebrow">Welcome</p>
        <h2>Comfort that goes beyond pain‑free dentistry</h2>
      </header>
      <div class="prose welcome">{''.join(f'<p>{md_inline(text_of(b))}</p>' for b in paras[:2])}</div>
    </div>
    <div class="grid services" style="--cols:3">{''.join(cards)}</div>
  </div>
</section>

<section class="section room--linen">
  <div class="wrap split">
    <div class="frame frame--arch portrait" data-reveal>{img(asset('images/team_dr-david-l-porter_headshot.jpg'), 'Dr. David L. Porter')}</div>
    <div class="split__copy" data-reveal>
      <p class="eyebrow">Meet the dentist</p>
      <h2>Dr. David L. Porter</h2>
      <div class="prose">{''.join(f'<p>{x}</p>' for x in dr[1:3])}</div>
      <a class="link" href="/our-practice/meet-the-team/">Meet the team {icon('arrow')}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <header class="head head--row">
      <div><p class="eyebrow">Our Practice</p><h2>Our philosophy is to care for you like family</h2></div>
      <a class="link" href="/our-practice/">About our practice {icon('arrow')}</a>
    </header>
    <div class="values">{value_cards}</div>
  </div>
</section>

<section class="section room--sage">
  <div class="wrap">
    <header class="head head--row">
      <div><p class="eyebrow">Testimonials</p><h2>It feels like family</h2></div>
      <a class="link" href="/our-practice/testimonials/">Read all testimonials {icon('arrow')}</a>
    </header>
    {quote_cards([TESTIMONIALS[i] for i in (0, 3, 5)])}
  </div>
</section>

<section class="section">
  <div class="wrap split split--top">
    <div class="split__copy" data-reveal>
      <p class="eyebrow">Patient Information</p>
      <h2>Payment options and insurance</h2>
      <div class="prose"><p>{e(pay)}</p><p>{e(insurance)}</p></div>
      <div class="badges">{badges}</div>
      <a class="link" href="/patient-information/">Patient information {icon('arrow')}</a>
    </div>
    <div class="carecredit" data-reveal>
      {cc}
      <p>We are pleased to accept the CareCredit healthcare credit card, so you can pay for treatment in convenient monthly payments.</p>
      <a class="btn btn--ghost btn--sm" href="/patient-information/financing/">Financing with CareCredit {icon('arrow')}</a>
    </div>
  </div>
</section>

<section class="section room--linen" id="visit">
  <div class="wrap visit">
    <div data-reveal>
      <p class="eyebrow">Office Location</p>
      <h2>Visit us in La Porte</h2>
      <address class="visit__address">{e(f['street'])}<br>{e(f['city'])}, {e(f['state'])} {e(f['zip'])}</address>
      <p class="visit__links"><a class="link" href="{e(f['maps'])}" target="_blank" rel="noopener">Map &amp; Directions {icon('arrow')}</a>
        <a class="link" href="tel:{f['tel']}">{e(f['phone'])}</a></p>
      <h3>Consultation Hours</h3>
      {hours_table()}
      <p class="aside__note">{e(f['emergency'])}</p>
    </div>
    <div data-reveal>
      <div class="map"><iframe src="{e(f['map_embed'])}" title="Map to {e(f['name'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <h3 class="areas__title">Service Areas</h3>
      <ul class="areas" role="list">{areas}</ul>
    </div>
  </div>
</section>
{closer()}'''
    return shell('/', page['title'], page.get('metaDescription') or lead, body, '/')


def not_found():
    body = f'''<section class="hero hero--404">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="wrap hero__copy">
    <p class="eyebrow">Page not found</p>
    <h1 class="hero__title">This page isn't here.</h1>
    <p class="lead hero__lead">The page you were looking for has moved or no longer exists. These are the pages most patients look for:</p>
    <div class="hero__cta">
      <a class="btn btn--primary" href="/appointment-request/">{icon('calendar')}Request an Appointment</a>
      <a class="btn btn--ghost" href="/our-services/">Our Services</a>
      <a class="btn btn--ghost" href="/contact-us/">Contact Us</a>
    </div>
  </div>
</section>'''
    return shell('/404.html', f'Page not found | {FACTS["name"]}', 'This page is not here. Find our services, request an appointment or contact Porter Family Dentistry in La Porte, IN.',
                 body, '', robots='noindex')


# ---------- Write the site ----------
def write(path, html_text):
    out = SITE / path.strip('/') / 'index.html' if not path.endswith('.html') else SITE / path.strip('/')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(house_text(html_text), encoding='utf-8')


def main():
    for d in (SITE / 'assets' / 'img',):
        if d.exists():
            shutil.rmtree(d)
    for p in SITE.glob('**/index.html'):
        p.unlink()
    IMG.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(GS_LOCKUP, IMG / GS_LOCKUP.name)
    asset('images/icon_favicon_touch-icon_tooth.png')
    harvest_testimonials()

    special = {'/': home_page, '/our-services/': services_hub, '/our-practice/meet-the-team/': team_page,
               '/our-practice/testimonials/': testimonials_page, '/patient-information/faqs/': faq_page,
               '/patient-information/dental-videos/': videos_page, '/appointment-request/': appointment_page,
               '/contact-us/': contact_page, '/patient-reviews/': reviews_page}
    for path, page in PAGES.items():
        write(path, special.get(path, article_page)(page))
    write('/404.html', not_found())

    # Redirects for every legacy URL the old site answered on (Vercel and Netlify)
    redirects = {}
    def first_url(r):
        if isinstance(r, dict):
            return r.get('from') or r.get('url')
        if isinstance(r, (list, tuple)):
            return r[0] if r else None
        return r
    for p in PAGES.values():
        for u in list(p.get('requestedAs', [])) + [first_url(r) for r in p.get('redirects', [])]:
            if not isinstance(u, str) or not u:
                continue
            old = u.replace(OLD, '')
            if old.lower().endswith('.aspx') and old != p['path']:
                redirects[old] = p['path']
    for old, new in {'/patient-information/Financing.aspx': '/patient-information/financing/', '/Financing.aspx': '/patient-information/financing/',
                     '/AppointmentRequest.aspx': '/appointment-request/', '/ContactUs.aspx': '/contact-us/',
                     '/OurServices.aspx': '/our-services/', '/PatientInformation.aspx': '/patient-information/',
                     '/ada.aspx': '/'}.items():
        redirects.setdefault(old, new)
    vercel = {'$schema': 'https://openapi.vercel.sh/vercel.json', 'framework': None, 'outputDirectory': 'site',
              'trailingSlash': True, 'redirects': [{'source': s, 'destination': d, 'permanent': True} for s, d in sorted(redirects.items())]}
    (ROOT / 'vercel.json').write_text(json.dumps(vercel, indent=2) + '\n', encoding='utf-8')
    (SITE / '_redirects').write_text(''.join(f'{s} {d} 301\n' for s, d in sorted(redirects.items())), encoding='utf-8')

    urls = ''.join(f'  <url><loc>{OLD}{p}</loc></url>\n' for p in sorted(PAGES) if p not in CANONICAL)
    (SITE / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding='utf-8')
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {OLD}/sitemap.xml\n', encoding='utf-8')
    print(f'{len(PAGES) + 1} pages, {len(USED)} images, {len(redirects)} redirects, {len(CANONICAL)} canonical duplicates')


if __name__ == '__main__':
    main()
