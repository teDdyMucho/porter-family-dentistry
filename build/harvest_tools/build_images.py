"""Build harvest/images/manifest.json, a contact sheet, and downscaled full-page screenshots.

Run:  python -I -X utf8 build_images.py
"""
import json
import os
import re
from urllib.parse import urlparse, unquote

from PIL import Image, ImageDraw, ImageFont

H = r'C:\Users\Admin\Desktop\porter-family-dentistry\harvest'
CRAWL = os.path.join(H, 'raw', '_crawl')
IMG = os.path.join(H, 'images')
LOG = json.load(open(os.path.join(CRAWL, 'crawl_log.json'), encoding='utf-8'))
EX = {p['slug']: json.load(open(os.path.join(CRAWL, p['slug'] + '.extract.json'), encoding='utf-8')) for p in LOG['pages']}
OVR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image_overrides.json')
OVR = json.load(open(OVR_PATH, encoding='utf-8')) if os.path.exists(OVR_PATH) else {}


def fix(u):
    if not u:
        return u
    if u.startswith('//'):
        u = 'https:' + u
    x = urlparse(u)
    return x._replace(netloc=x.netloc.lower()).geturl()


# ---- usage index: url -> {pages:set, alts:set, areas:set, kinds:set, els:set}
use = {}


def add(u, slug, kind, area=None, alt=None, el=None, rendered=None):
    u = fix(u)
    if not u or u.startswith('data:'):
        return
    e = use.setdefault(u, {'pages': set(), 'alts': set(), 'areas': set(), 'kinds': set(), 'els': set(), 'rendered': set()})
    if slug:
        e['pages'].add(slug)
    e['kinds'].add(kind)
    if area:
        e['areas'].add(area)
    if alt is not None:
        e['alts'].add(alt)
    if el:
        e['els'].add(el)
    if rendered:
        e['rendered'].add(tuple(rendered))


for slug, ex in EX.items():
    for i in ex.get('images', []):
        add(i.get('best') or i.get('src'), slug, 'img', i.get('area'), i.get('alt'), None, (i.get('renderedWidth'), i.get('renderedHeight')))
    for b in ex.get('backgrounds', []):
        add(b['url'], slug, 'css-background', b['area'], None, b['el'] + (b.get('pseudo') or ''), (b.get('w'), b.get('h')))
    for ic in (ex.get('head') or {}).get('icons', []):
        add(ic['href'], slug, 'favicon/' + ic['rel'], 'head')
mob_path = os.path.join(CRAWL, '_home_mobile.extract.json')
if os.path.exists(mob_path):
    mob = json.load(open(mob_path, encoding='utf-8'))
    for i in mob.get('images', []):
        add(i.get('best') or i.get('src'), 'home (mobile 390px)', 'img', i.get('area'), i.get('alt'))
    for b in mob.get('backgrounds', []):
        add(b['url'], 'home (mobile 390px)', 'css-background', b['area'], None, b['el'])
css_only = {}
for c in LOG.get('cssRefs', []):
    css_only.setdefault(fix(c['url']), set()).add(os.path.basename(urlparse(c['css']).path) if not c['css'].startswith('inline') else c['css'])

# ---- role heuristics
TEAM_PAGES = {'our-practice__meet-the-team'}


def role_for(u, e, w, h):
    name = os.path.basename(unquote(urlparse(u).path)).lower()
    if u in OVR.get('roles', {}):
        return OVR['roles'][u]
    kinds = e['kinds'] if e else set()
    areas = e['areas'] if e else set()
    if any(k.startswith('favicon') for k in kinds) or 'favicon' in name:
        return 'icon (favicon / touch icon)'
    if w and h and max(w, h) <= 96:
        return 'icon'
    if 'hero-carousel' in areas:
        return 'hero (home slider background)'
    if 'hero-banner' in areas:
        return 'hero (interior page banner)'
    if e and e['pages'] & TEAM_PAGES and 'main' in areas:
        return 'team'
    if any(a.startswith('section-') for a in areas):
        areas = set(areas) | {'main'}
    if 'css-background' in kinds:
        return 'section background (template)'
    if not e:
        return 'template asset (referenced in CSS only, not shown)'
    return 'content image'


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')


def target_name(orig, u, e):
    fo = OVR.get('files', {}).get(orig, {})
    if fo.get('rename'):
        return fo['rename']
    if '/mediamed/thumbs/' in u:
        alt = sorted(a for a in (e['alts'] if e else []) if a)
        code, ext = os.path.splitext(orig)
        return f"video-thumb_{code}_{slugify(alt[0]) if alt else 'untitled'}{ext.lower()}"
    return orig


manifest = []
skipped = []
excluded = []
files_seen = set()
for d in LOG['downloads']:
    u = fix(d['url'])
    e = use.get(u)
    entry = {'sourceUrl': u}
    if not d.get('file'):
        entry.update({'localFile': None, 'downloadStatus': d.get('status'), 'error': d.get('error') or d.get('note')})
        if e or u in css_only:
            entry['usedOnPages'] = sorted(e['pages']) if e else []
            entry['note'] = 'could not download (referenced only by plugin/template CSS; not visible on the site)' if not e else 'could not download'
            manifest.append(entry)
        continue
    orig = os.path.basename(d['file'])
    if orig in OVR.get('skip', {}):
        p = os.path.join(H, d['file'])
        if os.path.exists(p):
            os.remove(p)
        excluded.append({'sourceUrl': u, 'reason': OVR['skip'][orig]})
        continue
    new = target_name(orig, u, e)
    old_path, path = os.path.join(H, d['file']), os.path.join(IMG, new)
    if new != orig and os.path.exists(old_path) and not os.path.exists(path):
        os.rename(old_path, path)
    if not os.path.exists(path):
        path = old_path
        new = orig
    files_seen.add(os.path.normcase(path))
    w = h = None
    fmt = mode = None
    try:
        with Image.open(path) as im:
            w, h = im.size
            fmt, mode = im.format, im.mode
    except Exception as ex:
        fmt = 'unreadable by Pillow (' + os.path.splitext(path)[1] + ')'
    if w is not None and w <= 2 and h <= 2:
        skipped.append({'sourceUrl': u, 'reason': f'{w}x{h} tracking/spacer pixel'})
        os.remove(path)
        continue
    entry.update({
        'localFile': 'images/' + new,
        'originalFilename': orig if new != orig else None,
        'pixelSize': [w, h] if w else None,
        'format': fmt, 'mode': mode, 'bytes': d.get('bytes'),
        'altText': sorted(a for a in (e['alts'] if e else []) if a is not None) or ([] if e else None),
        'altNote': None,
        'usedOnPages': sorted(e['pages']) if e else [],
        'usedAs': sorted(e['kinds']) if e else ['css-reference-only'],
        'areas': sorted(e['areas']) if e else [],
        'cssElements': sorted(e['els']) if e and e['els'] else None,
        'renderedSizes': sorted({f'{a}x{b}' for a, b in e['rendered'] if a}) if e and e['rendered'] else None,
        'referencedInCss': sorted(css_only.get(u, [])) or None,
        'role': role_for(u, e, w, h),
    })
    if e and 'img' in e['kinds'] and not any(a for a in e['alts']):
        entry['altNote'] = 'empty alt / no alt attribute'
    elif e and 'img' not in e['kinds']:
        entry['altNote'] = 'CSS background / link icon - no alt text'
    fo = OVR.get('files', {}).get(orig)
    if not fo and '/mediamed/thumbs/' in u:
        fo = OVR.get('mediamedThumbs')
    if fo:
        entry['role'] = fo.get('role', entry['role'])
        entry['realOrStock'] = fo.get('realOrStock')
        entry['assessment'] = fo.get('assessment')
    entry = {k: v for k, v in entry.items() if v is not None}
    manifest.append(entry)

ROLE_ORDER = ['team', 'hero (home slider background)', 'hero (interior page banner)', 'section background (template)', 'section background (CareCredit vendor page)',
              'badge', 'icon', 'icon (favicon / touch icon)', 'stock (MediaMed patient-education video thumbnail)', 'template asset (referenced in CSS only, not shown)']
manifest.sort(key=lambda m: (ROLE_ORDER.index(m['role']) if m.get('role') in ROLE_ORDER else 99, m.get('localFile') or ''))
summary = {}
for m in manifest:
    if m.get('localFile'):
        summary[m.get('role', '?')] = summary.get(m.get('role', '?'), 0) + 1
json.dump({'generated': 'by build_tools/harvest_tools/build_images.py from raw/_crawl/crawl_log.json + image_overrides.json (visual review)',
           'site': 'https://www.porterfamilydentistry.com/',
           'count': len([m for m in manifest if m.get('localFile')]),
           'countsByRole': summary,
           'logo': 'NONE - the site has no logo image; the header "logo" is live text (David L. Porter, D.D.S., P.C. / We Treat You Like You Are Our Family!).',
           'skippedTrackingPixels': skipped, 'excludedNonImages': excluded, 'images': manifest},
          open(os.path.join(IMG, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- contact sheet
cells = [m for m in manifest if m.get('localFile') and m.get('pixelSize')]
cw, ch, pad, lab = 260, 200, 10, 46
cols = 5
rows = (len(cells) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (cw + pad) + pad, rows * (ch + lab + pad) + pad), (235, 235, 235))
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('arial.ttf', 12)
except Exception:
    font = ImageFont.load_default()
for n, m in enumerate(cells):
    x = pad + (n % cols) * (cw + pad)
    y = pad + (n // cols) * (ch + lab + pad)
    try:
        with Image.open(os.path.join(H, m['localFile'])) as im:
            im = im.convert('RGBA')
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            im = bg.convert('RGB')
            im.thumbnail((cw, ch))
            sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    except Exception as ex:
        draw.text((x + 5, y + 5), 'cannot render', fill=(200, 0, 0), font=font)
    draw.rectangle([x - 1, y - 1, x + cw, y + ch], outline=(180, 180, 180))
    nm = os.path.basename(m['localFile'])
    draw.text((x, y + ch + 3), f"{n + 1}. {nm[:38]}", fill=(0, 0, 0), font=font)
    draw.text((x, y + ch + 18), f"{m['pixelSize'][0]}x{m['pixelSize'][1]}  {m.get('role', '')[:28]}", fill=(60, 60, 60), font=font)
    draw.text((x, y + ch + 32), (', '.join(m.get('usedOnPages', [])[:2]) or 'css only')[:44], fill=(90, 90, 90), font=font)
sheet.save(os.path.join(H, 'contact_sheet.jpg'), quality=88)
json.dump([{'n': i + 1, 'file': m['localFile'], 'size': m['pixelSize'], 'role': m.get('role')} for i, m in enumerate(cells)],
          open(os.path.join(CRAWL, 'contact_sheet_index.json'), 'w', encoding='utf-8'), indent=1)

# ---- downscale full-page screenshots
FULL = os.path.join(H, 'raw', '_shots_fullsize')
SHOTS = os.path.join(H, 'shots')
for f in sorted(os.listdir(FULL)) if os.path.isdir(FULL) else []:
    if not f.endswith('.png'):
        continue
    with Image.open(os.path.join(FULL, f)) as im:
        im = im.convert('RGB')
        scale = 0.5 if im.width > 600 else 1.0
        nw, nh = int(im.width * scale), int(im.height * scale)
        im = im.resize((nw, nh), Image.LANCZOS)
        out = f.replace('.png', '_50pct.jpg' if scale < 1 else '.jpg')
        im.save(os.path.join(SHOTS, out), quality=85)
        print('shot', out, nw, nh)
print('manifest images:', len(cells), 'skipped pixels:', len(skipped), 'not downloaded:', len([m for m in manifest if not m.get('localFile')]))
