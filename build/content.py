"""The practice's content, read from the harvest of its live site (harvest/pages, harvest/images).

Nothing here is invented: facts are copied from the Contact Us, Meet The Team and home pages, and
every page body is the harvested copy, rendered block by block.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARVEST = ROOT / 'harvest'
OLD = 'https://www.porterfamilydentistry.com'

# ---------- Facts (harvest/pages/contact-us, meet-the-team, home) ----------
FACTS = {
    'name': 'Porter Family Dentistry',
    'legal': 'David L. Porter, D.D.S., P.C.',
    'tagline': 'We Treat You Like You Are Our Family!',
    'street': '1112 Indiana Avenue',
    'city': 'La Porte',
    'state': 'Indiana',
    'state_abbr': 'IN',
    'zip': '46350',
    'phone': '(219) 362-5205',
    'tel': '+12193625205',
    'fax': '(219) 362-2741',
    'email': 'drportermh@gmail.com',
    'founded': 1980,
    'geo': (41.60583, -86.71750),
    'maps': 'https://maps.google.com/maps?q=1112+Indiana+Avenue,La+Porte,Indiana,46350',
    'map_embed': ('https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1773.8861275180127!2d-86.71749875851494'
                  '!3d41.60582994067758!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x489fda9d40c90e5b'
                  '!2sPorter+Family+Dentistry!5e0!3m2!1sen!2sin!4v1551209056290'),
    'facebook': 'https://www.facebook.com/Porter-Family-Dentistry-889225141168109',
    'google': 'https://www.google.com/search?q=Porter+Family+Dentistry+Indiana',
    'carecredit_apply': 'https://www.carecredit.com/go/GCG545/',
    'carecredit_pay': 'https://www.carecredit.com/Pay/GCG545/',
    # Contact Us page. (The Appointment Request page says Friday 8:00am - 1:00pm: flagged for the office.)
    'hours': [
        ('Monday', '8:00am - 5:00pm', ('08:00', '17:00')),
        ('Tuesday', '8:00am - 5:00pm', ('08:00', '17:00')),
        ('Wednesday', 'Closed', None),
        ('Thursday', '8:00am - 5:00pm', ('08:00', '17:00')),
        ('Friday', '8:00am - 12:00pm', ('08:00', '12:00')),
        ('Saturday', 'Closed', None),
        ('Sunday', 'Closed', None),
    ],
    'emergency': '24/7 emergency services are available.',
    'areas': ['The Entire county of La Porte, IN', 'South Bend, IN', 'Plymouth, IN', 'Michigan City, IN',
              'Knox, IN and Starke County', 'New Carlisle, IN', 'New Buffalo, MI'],
}
WEEKDAY = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}


def hours_json():
    """{"1": ["08:00","17:00"], ...} keyed by weekday, 0 = Sunday, for the live open-now line."""
    return json.dumps({str(WEEKDAY[d]): list(t) for d, _, t in FACTS['hours'] if t}, separators=(',', ':'))


# ---------- Pages ----------
def path_of(url):
    p = url.replace(OLD, '') or '/'
    return p if p.endswith('/') else p + '/'


def load_pages():
    pages = {}
    for f in sorted((HARVEST / 'pages').glob('*.json')):
        if f.name.startswith('_'):
            continue
        d = json.loads(f.read_text(encoding='utf-8'))
        d['path'] = path_of(d['url'])
        pages[d['path']] = d
    return pages


def load_site():
    return json.loads((HARVEST / 'pages' / '_site.json').read_text(encoding='utf-8'))


# ---------- Links: old absolute URLs and the legacy .aspx pages map onto the new paths ----------
LEGACY = {'contactus.aspx': '/contact-us/', 'appointmentrequest.aspx': '/appointment-request/',
          'ourservices.aspx': '/our-services/', 'patientinformation.aspx': '/patient-information/',
          'financing.aspx': '/patient-information/financing/'}


def local(url):
    if not url:
        return url
    u = url.strip()
    if u.lower().startswith(('mailto:', 'tel:', '#')):
        return u
    if u.startswith(OLD) or u.startswith('/') and not u.startswith('//'):
        p = u.replace(OLD, '') or '/'
        tail = p.rstrip('/').rsplit('/', 1)[-1].lower()
        if tail in LEGACY:
            return LEGACY[tail]
        p = p.split('#')[0]
        return p if p.endswith('/') or '.' in p.rsplit('/', 1)[-1] else p + '/'
    return u


def is_external(url):
    return url.startswith(('http://', 'https://')) and not url.startswith(OLD)


# ---------- Inline markdown (as harvested) to HTML ----------
_LINK = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')


def md_inline(md):
    if md is None:
        return ''
    s = md.replace('\\*', '\x00').replace('\\_', '\x01')
    s = html.escape(s, quote=False)

    def link(m):
        text, href = m.group(1), html.unescape(m.group(2))
        href2 = local(href)
        ext = ' rel="noopener" target="_blank"' if is_external(href2) else ''
        return f'<a href="{html.escape(href2, quote=True)}"{ext}>{text}</a>'

    s = _LINK.sub(link, s)
    # the old editor left stray marks before a label's colon: ***Teeth polishing****:*** and ***Oral hygiene recommendations**:***
    s = re.sub(r'\*{3}([^*]+?)\*{2}(?:\*{2})?:\*{3}', r'***\1:***', s)
    s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s, flags=re.S)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s, flags=re.S)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s, flags=re.S)
    s = re.sub(r' {2,}\n', '<br>', s).replace('\n', '<br>')
    return s.replace('\x00', '*').replace('\x01', '_').strip()


def text_of(block):
    return block.get('md') if block.get('md') is not None else html.escape(block.get('text', ''), quote=False)


def plain(md):
    """Markdown to plain text (for meta descriptions and FAQ schema)."""
    s = _LINK.sub(r'\1', md or '')
    s = re.sub(r'[*_]{1,2}', '', s).replace('\\', '')
    return re.sub(r'\s+', ' ', s).strip()
