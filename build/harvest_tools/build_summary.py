"""Write harvest/SUMMARY.md from pages/_index.json, images/manifest.json and the crawl log.

Run:  python -I -X utf8 build_summary.py
"""
import json
import os
from collections import Counter

H = r'C:\Users\Admin\Desktop\porter-family-dentistry\harvest'
IX = json.load(open(os.path.join(H, 'pages', '_index.json'), encoding='utf-8'))
MAN = json.load(open(os.path.join(H, 'images', 'manifest.json'), encoding='utf-8'))
LOG = json.load(open(os.path.join(H, 'raw', '_crawl', 'crawl_log.json'), encoding='utf-8'))
BASE = 'https://www.porterfamilydentistry.com'

CLASS = {
    'home': ('PRACTICE', 'All copy written for the practice (welcome, service list, service area, 35 yrs / 177 yrs claims).'),
    'appointment-request': ('MIXED', 'ProSites appointment form + practice hours ("Consultation Hours") and notes.'),
    'contact-us': ('PRACTICE', 'Address, phone, fax, email, service areas, hours, map; form is the template quick-contact.'),
    'our-practice': ('MIXED', 'Our Mission / Our Goal / Our Philosophy are practice-written; Our High Standards / Uncompromising Safety / A Positive Experience are shared ProSites-Officite boilerplate (verified on other sites).'),
    'our-practice__meet-the-team': ('MIXED', 'Dr. Porter + Cheryl Grace bios are practice-written; intro paragraph is boilerplate (verified on other sites).'),
    'our-practice__testimonials': ('PRACTICE', '6 patient testimonials (initials only).'),
    'our-services': ('PRACTICE', 'Intro "Get treated like family…" + "Comprehensive Preventative Family Dentistry" list are practice-written (no verbatim match elsewhere); the category directory below is auto-generated from the menu.'),
    'patient-information': ('MIXED', 'ProSites default text (Appointment, Payment Options, first insurance sentence — found on other ProSites/Officite sites) + practice lines ("ALL insurance plans… every last penny"), card logos.'),
    'patient-information__dental-videos': ('VENDOR', 'ProSites/MediaMed licensed video library (44 listings / 34 videos).'),
    'patient-information__faqs': ('VENDOR', 'ProSites FAQ library, 13 Q&As (5,000+ words).'),
    'patient-information__financing': ('VENDOR', 'ProSites CareCredit page (only practice-specific item: merchant code GCG545 in the links).'),
    'patient-reviews': ('VENDOR', 'ProSites "write a review" widget; shows no reviews.'),
}


def cls(slug):
    if slug in CLASS:
        return CLASS[slug]
    return ('VENDOR', 'ProSites patient-education library article.')


L = []
w = L.append
pages = sorted(IX, key=lambda p: p['url'])
n_dup = sum(1 for p in pages if p.get('duplicateOf'))
fetches = LOG['fetches']
aliases = [f for f in fetches if f.get('aliasOf')]
imgs = [m for m in MAN['images'] if m.get('localFile')]
roles = Counter(m['role'] for m in imgs)

w('# Harvest summary — porterfamilydentistry.com (David L. Porter, D.D.S., P.C., La Porte, IN)')
w('')
w('Phase 1 (Intake) harvest, 2026-10-22. Rule: "the client is paying for a better site, not new content" — everything below is what the current site actually says and shows.')
w('')
w('## At a glance')
w('')
w(f'- **{len(pages)} unique pages** crawled (all HTTP 200), from {len(fetches)} fetches: {len(aliases)} legacy/relative `.aspx` URLs 301-redirect onto existing pages. The XML sitemap lists exactly the same 46 URLs; no orphan pages found.')
w(f'- **Copy:** {sum(1 for p in pages if cls(p["slug"])[0] == "PRACTICE")} pages are practice-written, {sum(1 for p in pages if cls(p["slug"])[0] == "MIXED")} mix template text with practice edits, and {sum(1 for p in pages if cls(p["slug"])[0] == "VENDOR")} are generic ProSites library pages (all 34 service pages, FAQs, videos, financing, reviews widget). The 35-page service tree contains 3 exact duplicate pairs, 3 pairs that differ by a single comma/capital, and 2 lightly reworded variants (see Anything odd).')
w(f'- **Images:** {len(imgs)} files downloaded. Only **2 real photos of the practice** — Dr. Porter\'s headshot (275x385) and a 10-person staff group photo (646x399), both small. **0 office/building/operatory photos.** Everything else is template stock (3 home hero slides + 8 interior banners + textures), vendor badges/thumbnails or icons. **No logo image exists** (the logo is styled text).')
w('- **Key facts:** 1112 Indiana Avenue, La Porte, Indiana 46350 · (219) 362-5205 · fax (219) 362-2741 · drportermh@gmail.com · Mon & Tue 8:00am-5:00pm, Wed closed, Thu 8:00am-5:00pm, Fri 8:00am-12:00pm **or** 1:00pm (pages disagree), Sat & Sun closed, "24/7 emergency services are available." · Dr. David L. Porter (D.D.S., office opened 1980) · Cheryl Grace, Office Manager · CareCredit (merchant GCG545) · Facebook page.')
w('- **No patient forms/PDFs, no in-network insurance list, no third-party reviews, no office photos, no other dentists or hygienists named.**')
w('')
w('## Where things are')
w('')
w('| Path | What |')
w('|---|---|')
for a, b in [
    ('harvest/pages/<slug>.json', 'Per page: url, final url, redirects/aliases, title, meta description, h1 (none exist), page heading, nav placement, hero/banner, ordered content blocks (h2/h3/p/ul/ol/blockquote/img/table/form/video/map with exact text, list structure, inline links), images used, shared sections shown, word count, duplicate flag.'),
    ('harvest/pages/<slug>.md', 'Same content as readable Markdown (images point at ../images/).'),
    ('harvest/pages/_site.md / _site.json', 'Site-wide chrome captured once: header text logo + tagline, full nav tree, phone bar, shared "Contact Us" quick form, shared Testimonials carousel, "Office Location" strip, footer, accessibility widget, style samples.'),
    ('harvest/pages/_index.json', 'Machine-readable page inventory (the table below).'),
    ('harvest/facts.md', 'All facts with source URLs: names, doctor, team, address/phones/fax/email, hours (both versions), service area, social, emergency, insurance/financing, new-patient info, every testimonial, every FAQ (verbatim), video list, all form fields, map embed, brand colours/fonts, taglines, conflicts.'),
    ('harvest/images/ + manifest.json', f'{len(imgs)} images with source URL, local file, pixel size, alt text, pages using it, role and a real-vs-stock assessment.'),
    ('harvest/contact_sheet.jpg', 'Contact sheet of every downloaded image (numbered, with size/role).'),
    ('harvest/shots/', 'Desktop 1440x900 first screens + 50%-downscaled full pages for home, meet-the-team, our-services, a service page (root-canal-therapy), patient-information, contact-us; home slide-1 first screen; 390px mobile first screen + full page of home; contact map close-up.'),
    ('harvest/raw/', 'Rendered HTML of every page, raw extraction JSON (`_crawl/*.extract.json`), crawl log, robots.txt, sitemap.xml, site-map page, all CSS files (`raw/css/`), full-size full-page screenshots (`_shots_fullsize/`).'),
    ('harvest/docs/', 'Empty — the site links no PDFs or documents.'),
    ('build/harvest_tools/', 'Scripts: crawl.mjs (+ extract_inpage.js), build_pages.py, build_images.py (+ image_overrides.json), build_facts.py, build_summary.py, scan_facts.py, probe_variants.mjs, reshoot.mjs.'),
]:
    w(f'| `{a}` | {b} |')
w('')

# ---------------- inventory
w('## Page inventory')
w('')
w('Words = main-content words (page heading through last paragraph; excludes header, nav, footer and the shared sections). Imgs = content images in the main column (banner not counted). Copy: PRACTICE = written for this practice, MIXED = template + practice edits, VENDOR = generic ProSites library text.')
w('')
w('| # | URL | Title tag | Nav section | Words | Imgs | Banner | Copy | Notes |')
w('|---|---|---|---|---|---|---|---|---|')
for i, p in enumerate(pages, 1):
    path = p['url'].replace(BASE, '')
    c, note = cls(p['slug'])
    extra = []
    if p.get('duplicateOf'):
        extra.append(f"**exact duplicate of** `{[q['url'].replace(BASE, '') for q in pages if q['slug'] == p['duplicateOf']][0]}`")
    if p.get('requestedAs') and [u for u in p['requestedAs'] if u != p['url']]:
        extra.append('also reached via ' + ', '.join('`' + u.replace(BASE, '') + '`' for u in p['requestedAs'] if u != p['url']) + ' (301)')
    if p['media']:
        extra.append(f"{p['media']} embed(s)")
    if p['forms']:
        extra.append('form')
    nav = p['nav'] or '(not in menu)'
    banner = p['bannerImage'] or ''
    ttl = p['title'].replace('|', '\\|')
    w(f"| {i} | `{path}` | {ttl} | {nav} | {p['words']} | {p['mainImages']} | {banner} | {c} | {note if c != 'VENDOR' or p['slug'] in CLASS else ''}{' · ' if extra and (c != 'VENDOR' or p['slug'] in CLASS) else ''}{' · '.join(extra)} |")
w('')
tot = sum(p['words'] for p in pages)
by = Counter()
for p in pages:
    by[cls(p['slug'])[0]] += p['words']
w(f'Total main-content words: {tot:,} — VENDOR {by["VENDOR"]:,} ({by["VENDOR"] * 100 // tot}%), MIXED {by["MIXED"]:,}, PRACTICE {by["PRACTICE"]:,}. Note that MIXED pages are partly boilerplate, so the practice-written total is lower still (roughly 1,200 words).')
w('')

# ---------------- practice vs vendor
w('## Practice-specific vs generic vendor copy')
w('')
w('The site is a ProSites (Henry Schein) "litesite" template. ProSites ships a library of patient-education articles that thousands of dental sites reuse word-for-word. On this site:')
w('')
w('- **Practice-written (keep, it is the client\'s voice):** home Welcome text and service list; Our Services intro ("Get treated like family at our unique dental practice." + the "Comprehensive Preventative Family Dentistry" list); Our Practice → Our Mission, Our Goal, Our Philosophy; Dr. Porter and Cheryl Grace bios; the 6 testimonials; contact details, service-area list and Consultation Hours; the second Dental Insurance paragraph ("We are able to work with ALL insurance plans… every last penny…"); hero slogans and the header tagline "We Treat You Like You Are Our Family!".')
w('- **Template boilerplate on otherwise custom pages:** Our Practice → Our High Standards, Uncompromising Safety, A Positive Experience (verbatim on other Officite/ProSites practices, e.g. a Bowman Y Shin DMD page); Meet the Team intro paragraph ("At the core of our dental practice…", near-identical on my.officite.com staff pages); Patient Information → Appointment, Payment Options and the first Dental Insurance sentence (found on another Officite site); appointment/contact form wording.')
w('- **Generic vendor library (38 pages):** every page under /our-services/ except the index (34) — the 6 category intros (Endodontics, Cleanings & Prevention, Cosmetic Dentistry, Periodontics, Restorations, Prosthodontics) plus Dental Anxiety and Fear, Dental Emergencies and all 26 procedure articles; FAQs (13 Q&As); Dental Videos (MediaMed); Financing (CareCredit); Patient Reviews widget. Spot-check: the Root Canal Therapy text ("Root canal therapy is needed when the nerve of a tooth is affected by decay or infection…") appears verbatim on other practices\' sites (e.g. Moore Dentistry, a Montrose clinic). NiteWhite ACP is manufacturer copy. None of these pages mention Dr. Porter, La Porte or anything practice-specific, apart from generic "contact our office" lines.')
w('- Practical consequence: the rebuild\'s real source material is roughly 1,200 words of practice copy + facts; the 34 service articles plus the FAQ, video and CareCredit pages are interchangeable boilerplate (and ProSites-licensed). Whether to carry them over verbatim is a decision for the PRD, not something to rewrite here.')
w('')

# ---------------- facts table
w('## Facts table (details and sources in facts.md)')
w('')
w('| Fact | Value | Source page |')
w('|---|---|---|')
for r in [
    ('Name in header / title tags', 'David L. Porter, D.D.S., P.C.', 'all pages'),
    ('Trading name in copy', 'Porter Family Dentistry (also "David L. Porter Family Dentistry"; Google pin "David L. Porter DDS")', '/, /contact-us/, /our-practice/'),
    ('Tagline', 'We Treat You Like You Are Our Family!', 'header, all pages'),
    ('Dentist', 'Dr. David L. Porter, D.D.S. — Wabash College (Bachelor\'s), Indiana University (dental degree); opened office 1980; ADA, NW Indiana Dental Assn., Chicago Dental Society, BBB, La Porte Chamber; La Porte Planning & Zoning Commission', '/our-practice/meet-the-team/'),
    ('Team', 'Cheryl Grace — Office Manager (37 years). No one else named. Group photo shows 10 unnamed staff.', '/our-practice/meet-the-team/'),
    ('Address', '1112 Indiana Avenue, La Porte, Indiana 46350', 'all pages'),
    ('Phone', '(219) 362-5205 (only number on the site)', 'all pages'),
    ('Fax', '(219) 362-2741', '/contact-us/'),
    ('Email', 'drportermh@gmail.com', '/contact-us/'),
    ('Hours', 'Mon & Tue 8:00am-5:00pm; Wed Closed; Thu 8:00am-5:00pm; Fri 8:00am-12:00pm (contact) / 8:00am-1:00pm (appointment page); Sat & Sun Closed; "24/7 emergency services are available."', '/contact-us/, /appointment-request/'),
    ('Service area', 'The Entire county of La Porte, IN; South Bend, IN; Plymouth, IN; Michigan City, IN; Knox, IN and Starke County; New Carlisle, IN; New Buffalo, MI', '/contact-us/ (home lists fewer)'),
    ('Emergencies', '"24/7 emergency services are available." vs "Dental Emergencies (For Patients of Record)"', '/contact-us/, /appointment-request/ vs /'),
    ('Insurance', 'Not in-network with any insurer ("At no time has Dr. Porter acquiesced to becoming an “in-network” dentist…"), but "able to work with ALL insurance plans"', '/our-practice/, /patient-information/'),
    ('Payment', 'Cash, personal checks, debit cards, most major credit cards (MasterCard, Visa, Discover, AmEx logos); payment expected at time of service', '/patient-information/'),
    ('Financing', 'CareCredit — apply https://www.carecredit.com/go/GCG545/ , pay https://www.carecredit.com/Pay/GCG545/', '/patient-information/financing/'),
    ('Social', 'Facebook https://www.facebook.com/Porter-Family-Dentistry-889225141168109 ; "Google" icon is only a Google search link', 'footer, all pages'),
    ('Map', 'Google Maps embed, 41.6058299, -86.7174988, place CID 0x489fda9d40c90e5b', '/contact-us/'),
    ('Testimonials', '6, initials only (JG, YS, AK, BR, YT, NC)', '/our-practice/testimonials/'),
    ('FAQs', '13 generic Q&As', '/patient-information/faqs/'),
    ('Videos', '44 listings / 34 MediaMed videos (ProSites-hosted mp4) + CareCredit promo video', '/patient-information/dental-videos/, /patient-information/financing/'),
    ('Forms', 'Appointment request (9 fields + Send Request), contact quick-form (on 40 pages), patient review form', 'see facts.md §16'),
    ('Brand colours', 'Plum #5A3944 (logo, links), #4A313A (nav), mauve #735660 (buttons, phone bar, headings), #8A6E78 (tagline), #543641 (dropdown), body text #5D5050, taupe #D4CCC2', 'computed styles'),
    ('Fonts', 'Open Sans (body), Montserrat (nav/headings), Source Sans Pro (logo text); hero declares Droid Serif / Crimson Text but they never load (falls back to Times)', 'computed styles'),
    ('Patient forms / PDFs', 'MISSING — none on the site', '—'),
]:
    w(f'| {r[0]} | {r[1]} | {r[2]} |')
w('')

# ---------------- images
w('## Image inventory and verdict')
w('')
w('| Role | Count | Files | Quality / verdict |')
w('|---|---|---|---|')
groups = [
    ('team', 'REAL. Dr. Porter headshot 275x385 (no larger original exists on the CDN) and staff group photo 646x399. Usable small only; commission a new shoot for any hero/large use.'),
    ('hero (home slider background)', 'STOCK — ProSites template 2283 defaults (smiling woman / man in straw hat / family), 2000x1002. Shared by every site on this template; not the practice.'),
    ('hero (interior page banner)', 'STOCK — template banner set banner1-8, 1900x350, rotated across interior pages.'),
    ('section background (template)', 'Template textures: beige paper 2000x1002, wood + blossoms 2000x1500, 25x25 tile.'),
    ('section background (CareCredit vendor page)', 'Vendor stock (cut-out woman 1715x1880, blurred operatory 1051x622).'),
    ('badge', 'CareCredit logos/buttons and 64x64 card logos (MasterCard, Visa, Discover, AmEx).'),
    ('icon', 'Social icons (Facebook x2, Google), 48-75px.'),
    ('icon (favicon / touch icon)', 'Generic ProSites tooth icon 114x114 (declared favicon) + generic /favicon.ico. Not a practice logo.'),
    ('stock (MediaMed patient-education video thumbnail)', '142x80 thumbnails of the licensed video library — too small to reuse.'),
    ('template asset (referenced in CSS only, not shown)', 'Not displayed on the site (fancybox sprite, unused CareCredit stock couple).'),
]
for role, verdict in groups:
    files = [os.path.basename(m['localFile']) for m in imgs if m['role'] == role]
    shown = ', '.join(f'`{f}`' for f in files[:4]) + (f' … (+{len(files) - 4})' if len(files) > 4 else '')
    w(f'| {role} | {len(files)} | {shown} | {verdict} |')
other = [m for m in imgs if m['role'] not in dict(groups)]
for m in other:
    w(f'| {m["role"]} | 1 | `{os.path.basename(m["localFile"])}` | {m.get("assessment", "")} |')
w('')
w(f'**Verdict:** {len(imgs)} images, but only **2 usable real photos of the practice/team** (both low resolution) and **0 photos of the office, building, reception or operatories**. {roles["hero (home slider background)"] + roles["hero (interior page banner)"]} hero/banner images and the section backgrounds are template stock; {roles["stock (MediaMed patient-education video thumbnail)"]} are vendor video thumbnails; the rest are badges and icons. There is **no logo file** — only styled text. The rebuild will need a photo shoot (team, Dr. Porter, exterior, reception, treatment rooms) and a logo decision. Alt text: 10 of the 11 non-video content images have empty or missing alt.')
w('')
w('Contact sheet: `harvest/contact_sheet.jpg`. Per-image detail: `harvest/images/manifest.json`.')
w('')

# ---------------- odd
w('## Anything odd')
w('')
dups = [(p['url'].replace(BASE, ''), [q['url'].replace(BASE, '') for q in pages if q['slug'] == p['duplicateOf']][0]) for p in pages if p.get('duplicateOf')]
w('- **Duplicate service pages (same ProSites article under two menu parents):**')
for a, b in dups:
    w(f'  - exact duplicate (identical text): `{b}` = `{a}`')
w('  - same article, one-character edit: `/our-services/prosthodontics/crowns-caps/` vs `/our-services/restorations/crowns-caps/` ("At your second appointment your" vs "…appointment, your"); `/our-services/cosmetic-dentistry/dentures-partial-dentures/` vs `/our-services/prosthodontics/dentures-partial-dentures/` ("A partial denture" vs "A Partial denture"); `/our-services/prosthodontics/fixed-bridges/` vs `/our-services/restorations/fixed-bridges/` ("many years, however they" vs "many years; however, they").')
w('  - lightly reworded variants: `/our-services/cosmetic-dentistry/porcelain-crowns-caps/` ≈ crowns-caps (98% same; adds "because they resemble your natural teeth", has the typo "color or your teeth"); `/our-services/cosmetic-dentistry/porcelain-fixed-bridges/` ≈ fixed-bridges (97% same; adds "Porcelain fixed bridges are most popular because they resemble your natural teeth.", has the typo "consists to two crowns").')
w('  - Net: the 35-page service tree holds 29 distinct texts and about 27 distinct topics. On the home page, "GentleWave Root Canal Treatment" links to /endodontics/root-canal-retreatment/ and "Porcelain Crowns" to /restorations/crowns-caps/.')
w('- **Legacy `.aspx` URLs** — content links still point at old WebForms URLs that 301 to the new paths: ' + ', '.join(f'`{f["requested"].replace(BASE, "")}` → `{[q["url"].replace(BASE, "") for q in pages if q["slug"] == f["aliasOf"]][0]}`' for f in aliases) + '. Relative links such as "AppointmentRequest.aspx" on the FAQ page resolve under the current folder (e.g. `/patient-information/faqs/AppointmentRequest.aspx`) and only work because ProSites redirects them. Keep 301s for these in the rebuild.')
w('- **Conflicting facts:** Friday hours (12:00pm vs 1:00pm); 24/7 emergencies vs "For Patients of Record"; "35 years of service" vs "opened his office in 1980"; not in-network vs "accept all dental insurance plans"; three different service-area lists; degree named "Doctor of Dental Science". See facts.md §0.')
w('- **No `<h1>` on any page** — every page heading is an `<h2 class="section-heading">`; titles follow two patterns ("David L. Porter, D.D.S., P.C. - X" for main pages, "X | La Porte, Indiana | Porter Family Dentistry" for service pages).')
w('- **Hero fonts never load:** the slider asks for "Droid Serif" and "Crimson Text", but no such font is loaded, so the hero renders in Times New Roman.')
w('- **"Office Location" strip is empty on /contact-us/** (0px tall) and the quick-contact section is hidden on 6 pages; both are intentional template behaviour.')
w('- **Hidden content:** FAQ answers are collapsed accordions and the dental-video lists are collapsed by category. Both were captured and are flagged `hidden: true` in the JSON. The appointment form has conditional fields.')
w('- **Home "Additional Services" / "New patients click here" / "contact us" links** use legacy .aspx URLs; "GentleWave Root Canal Treatment" links to the *Retreatment* page; "Porcelain Crowns" links to /restorations/crowns-caps/ although a /cosmetic-dentistry/porcelain-crowns-caps/ page exists.')
w('- **Services claimed without pages:** implant-supported dentures, nitrous oxide, GentleWave.')
w('- **Third-party/vendor dependencies that will not move:** ProSites MediaMed videos (video.prosites.com), the CareCredit promo video and calculator iframe, the ProSites review widget, the ADA "Accessibility Mode" (/ada.aspx, not crawled because it flips the session into an alternate template), and Matomo analytics (analytics.prosites.com, site 13255).')
w('- **Bot protection / robots:** AWS WAF JavaScript challenge (first response HTTP 202, then a JS-set `aws-waf-token` cookie). robots.txt disallows all but a list of named bots and sets `Crawl-delay: 5`; this crawl used one browser context, one page at a time, ~8s apart.')
w('- An HTML site map page exists at `/sitemap.aspx` (not linked; lists the same 46 pages).')
w('- The CareCredit copy claims "more than 21 million accounts… nearly 30 years" (dated vendor text).')
w('')
w('## Screenshots')
w('')
for f in sorted(os.listdir(os.path.join(H, 'shots'))):
    w(f'- `shots/{f}`')
w('')
w('Note: `home_desktop-1440_first-screen.png` caught slider 2 ("Complete Dental Care / You Can Trust"); `home_desktop-1440_first-screen_slide1.png` and the home full page were re-shot with the slider frozen on slide 1.')
w('')
w('## How this was produced')
w('')
w('`build/harvest_tools/crawl.mjs` (Playwright, Chromium 1248, single browser context, desktop Chrome UA) passed the WAF challenge, seeded from the home page plus robots/sitemap. It followed every same-origin link (skipping /ada.aspx), deduped by final URL, waited for network idle plus 2-4s per page, scrolled each page to trigger lazy/WOW animations, and ran `extract_inpage.js` for structured content, links, images, CSS backgrounds, media, forms and computed styles. It saved rendered HTML and screenshots, then downloaded every image/CSS file with the same context. `build_images.py` measured the images with Pillow, applied the manual roles and renames from `image_overrides.json` (after viewing the contact sheet), built the contact sheet and downscaled the screenshots. `build_pages.py` wrote the per-page JSON/MD, `build_facts.py` wrote facts.md and `build_summary.py` wrote this file. Re-run order: crawl.mjs → build_images.py → build_pages.py → build_facts.py → build_summary.py.')
w('')
open(os.path.join(H, 'SUMMARY.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('SUMMARY.md written', sum(len(x) for x in L), 'chars')
