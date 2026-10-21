"""Scan every crawled page's full rendered text + links for facts; report every occurrence with its URL.

Writes raw/_crawl/fact_scan.json and prints a summary. Run: python -I -X utf8 scan_facts.py
"""
import json
import os
import re
from collections import defaultdict

H = r'C:\Users\Admin\Desktop\porter-family-dentistry\harvest'
CRAWL = os.path.join(H, 'raw', '_crawl')
LOG = json.load(open(os.path.join(CRAWL, 'crawl_log.json'), encoding='utf-8'))
EX = {p['slug']: json.load(open(os.path.join(CRAWL, p['slug'] + '.extract.json'), encoding='utf-8')) for p in LOG['pages']}

PATTERNS = {
    'phone': re.compile(r'(?<!\d)(?:\+?1[\s.-]?)?\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'),
    'email': re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+'),
    'fax': re.compile(r'fax[^\n]{0,40}', re.I),
    'hours_line': re.compile(r'^.*\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\b.*\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.).*$|^.*\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\b.*\bclosed\b.*$', re.I | re.M),
    'hours_word': re.compile(r'^.*\b(?:hours|open|closed|appointment only)\b.*$', re.I | re.M),
    'address': re.compile(r'\b\d{2,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Avenue|Ave|Street|St|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Court|Ct|Highway|Hwy)\b\.?', re.M),
    'zip': re.compile(r'\b(?:Indiana|IN|Michigan|MI|Illinois|IL)\.?,?\s+\d{5}(?:-\d{4})?\b'),
    'emergency': re.compile(r'^.*emergenc.*$', re.I | re.M),
    'insurance': re.compile(r'^.*insurance.*$', re.I | re.M),
    'financing': re.compile(r'^.*(?:carecredit|care credit|financ|payment plan|lending|cherry|sunbit|alphaeon|proceed finance|visa|mastercard|discover|american express|cash|check).*$', re.I | re.M),
    'new_patient': re.compile(r'^.*new patient.*$', re.I | re.M),
    'years': re.compile(r'^.*\b(?:19[5-9]\d|20[0-2]\d|\d{1,3} years)\b.*$', re.I | re.M),
    'credentials': re.compile(r'^.*\b(?:D\.?D\.?S|D\.?M\.?D|FAGD|MAGD|RDH|CDA|EFDA|Dr\.)\b.*$', re.M),
    'towns': re.compile(r'\b(?:La ?Porte|LaPorte|Michigan City|Plymouth|Knox|South Bend|Valparaiso|Westville|Kingsbury|Rolling Prairie|Union Mills|Wanatah|Hanna|Stillwell|Kingsford Heights|Mishawaka|Chesterton|Portage|Merrillville|Lake of the Four Seasons|New Carlisle|Walkerton|Long Beach|Trail Creek|Michiana Shores|Pottawattamie Park|Fish Lake|Hamlet|North Liberty|Lakeville|Starke County|Marshall County|Porter County|La ?Porte County|St\. Joseph County)\b'),
    'tagline_like': re.compile(r'^.*\b(?:family|trust|smile|comfort|gentle|pain-?free|painless)\b.*$', re.I | re.M),
    'gentlewave': re.compile(r'^.*gentle ?wave.*$', re.I | re.M),
    'nitrous': re.compile(r'^.*(?:nitrous|sedation|laughing gas).*$', re.I | re.M),
}

res = defaultdict(lambda: defaultdict(set))  # kind -> value -> urls
for slug, ex in EX.items():
    url = ex['fetch']['finalUrl']
    texts = {'fullText': ex.get('fullText') or ''}
    # also hidden main-content text (collapsed FAQ answers etc.)
    texts['mainTextContent'] = ex.get('mainTextContent') or ''
    for fr in ex.get('frames', []):
        texts['iframe:' + fr['url'][:60]] = fr.get('text') or ''
    for src, t in texts.items():
        for k, rx in PATTERNS.items():
            for m in rx.finditer(t):
                v = m.group(0).strip()
                if k == 'phone' and len(re.sub(r'\D', '', v)) not in (10, 11):
                    continue
                if len(v) > 300:
                    v = v[:300] + '…'
                res[k][v].add(url if src == 'fullText' else f'{url} [{src}]')
    for l in ex.get('links', []):
        h = l.get('href') or ''
        if h.startswith('tel:'):
            res['tel_links'][h].add(url)
        elif h.startswith('mailto:'):
            res['mailto_links'][h].add(url)
        elif re.search(r'facebook|instagram|twitter|x\.com|youtube|linkedin|yelp|google\.[a-z]+/(?:maps|search)|maps\.google|healthgrades|zocdoc|pinterest|tiktok|nextdoor|bbb\.org|carecredit|lendingclub|demandforce|lighthouse|solutionreach|sesame|weave|revenuewell|birdeye|podium', h, re.I):
            res['external_profiles'][h].add(f"{url} [{l.get('area')}] text={l.get('text')!r}")
        elif re.search(r'\.pdf(\?|$)', h, re.I):
            res['pdf_links'][h].add(f"{url} text={l.get('text')!r}")
    for o in ex.get('onclickLinks', []):
        res['onclick_links'][o['onclick'][:200]].add(url)
    for m in ex.get('media', []):
        res['media'][f"{m.get('type')} {m.get('src')}"].add(url)

out = {k: {v: sorted(u) for v, u in sorted(d.items())} for k, d in res.items()}
json.dump(out, open(os.path.join(CRAWL, 'fact_scan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
n_pages = len(EX)
for k in ['phone', 'tel_links', 'email', 'mailto_links', 'fax', 'address', 'zip', 'hours_line', 'towns', 'external_profiles', 'pdf_links', 'onclick_links', 'media', 'credentials', 'gentlewave', 'nitrous', 'financing', 'insurance', 'emergency', 'new_patient', 'years', 'hours_word']:
    d = out.get(k, {})
    print(f'\n=== {k} ({len(d)} distinct)')
    for v, urls in d.items():
        short = [u.replace('https://www.porterfamilydentistry.com', '') for u in urls]
        cnt = len({u.split(' ')[0] for u in urls})
        where = 'ALL PAGES' if cnt == n_pages else ', '.join(short[:6]) + (f' … (+{len(short) - 6})' if len(short) > 6 else '')
        print(f'- [{cnt}p] {v!r}  @ {where}')
