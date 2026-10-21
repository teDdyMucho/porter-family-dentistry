"""Write harvest/facts.md. Verbatim passages are pulled from harvest/pages/*.json (never retyped);
curated statements and the conflict list are written here and cite the page each fact came from.

Run:  python -I -X utf8 build_facts.py
"""
import json
import os
import re

H = r'C:\Users\Admin\Desktop\porter-family-dentistry\harvest'
P = os.path.join(H, 'pages')
BASE = 'https://www.porterfamilydentistry.com'
MAN = json.load(open(os.path.join(H, 'images', 'manifest.json'), encoding='utf-8'))
LOCAL = {m['sourceUrl']: m.get('localFile') for m in MAN['images']}
CRAWL = os.path.join(H, 'raw', '_crawl')


def page(slug):
    return json.load(open(os.path.join(P, slug + '.json'), encoding='utf-8'))


def url(slug):
    return page(slug)['finalUrl']


def flat(blocks):
    for b in blocks:
        if b['type'] == 'form':
            yield from flat(b['content'])
        else:
            yield b


def find(slug, start, typ=None):
    for b in flat(page(slug)['blocks']):
        if (typ is None or b['type'] == typ) and b.get('text', '').startswith(start):
            return b['text']
    raise KeyError(f'{slug}: no block starting {start!r}')


def q(text):
    """Blockquote a verbatim passage (keeps its line breaks)."""
    return '\n'.join('> ' + l if l else '>' for l in text.split('\n'))


def list_items(b, depth=0):
    out = []
    for it in b['items']:
        out.append('  ' * depth + '- ' + it['text'].replace('\n', ' / '))
        for c in it.get('children', []) or []:
            out += list_items(c, depth + 1)
    return out


L = []
w = L.append
w('# Facts — David L. Porter, D.D.S., P.C. (porterfamilydentistry.com)')
w('')
w('Harvested 2026-10-22 from https://www.porterfamilydentistry.com/ (46 unique pages; ProSites "litesite" template 2283). '
  'Every fact below cites the page it came from. Text in quote blocks is verbatim from the rendered page (only whitespace normalised). '
  'Anything not found on the site is marked **MISSING**.')
w('')

# ------------------------------------------------------------------ conflicts
w('## 0. Conflicts and things to confirm with the client')
w('')
w('| # | Topic | What the site says | Where |')
w('|---|---|---|---|')
rows = [
    ('Friday hours', '"Friday: 8:00am - 1:00pm"  vs  "Friday: 8:00am - 12:00pm"', f'{url("appointment-request")} vs {url("contact-us")}'),
    ('Emergency policy', '"24/7 emergency services are available." (also in the contact page meta description: "24/7 emergency services available.")  vs  home list item "Dental Emergencies (For Patients of Record)"', f'{url("appointment-request")}, {url("contact-us")} vs {url("home")}'),
    ('Years in practice', 'Home: "We are backed by 35 years of service"  vs  team bio: "Dr. Porter opened his office in 1980" (= 46 years in 2026; the "35 years" copy dates from c. 2015). Home also claims "our staff has a combined experience of 177 years" (meta description repeats "177 years of combined experience").', f'{url("home")} vs {url("our-practice__meet-the-team")}'),
    ('Insurance stance', '"At no time has Dr. Porter acquiesced to becoming an “in-network” dentist to the insurance companies."  vs  "We are able to work with ALL insurance plans…" and "we will accept all dental insurance plans". Compatible only if read as "out-of-network, but files with every plan" — confirm wording.', f'{url("our-practice")} vs {url("patient-information")}, {url("our-services")}'),
    ('Degree wording', 'Bio says "his Doctor of Dental Science from Indiana University" — the D.D.S. degree is normally "Doctor of Dental Surgery". Confirm before reuse.', url('our-practice__meet-the-team')),
    ('Practice name', '"David L. Porter, D.D.S., P.C." (header, page titles) · "Porter Family Dentistry" (contact block heading, home copy, service-page titles, meta descriptions, map embed) · "David L. Porter Family Dentistry" (Our Practice) · "David Porter Family Dentistry" (a testimonial) · Google Maps pin label "David L. Porter DDS" · Facebook URL slug "Porter-Family-Dentistry"', 'site-wide; ' + url('our-practice') + '; ' + url('contact-us')),
    ('Service area', 'Three different lists: home body "La Porte, Michigan City, Plymouth, and Knox areas"; home line "-Serving the Entire County of La Porte, IN, including South Bend, Plymouth, and Michigan City-"; contact page list of 7 (adds Starke County, New Carlisle IN, New Buffalo MI).', f'{url("home")}, {url("contact-us")}'),
    ('GentleWave', 'Home lists "GentleWave Root Canal Treatment" but links it to the Root Canal *Retreatment* page; no page describes GentleWave.', url('home')),
    ('Services without pages', 'Our Services lists "Custom dentures and implant supported dentures (permanent dentures)" and "Nitrous oxide for painless dentistry" — there is no implant page and no sedation/nitrous page (only generic "Dental Anxiety and Fear" mentions sedation). The meta description on all 35 /our-services/ pages also advertises "Implants".', url('our-services')),
    ('Team size', 'Only two people are named (Dr. Porter, Cheryl Grace); the team group photo shows 10 unnamed staff members.', url('our-practice__meet-the-team')),
    ('Typos on site', 'Home meta description "177 years of combined experience. . Convenient location." (double period); bio "member of American Dental Association., The Northwest…" (stray period); contact-form validator "Please enter a  name!" (double space).', f'{url("home")}, {url("our-practice__meet-the-team")}'),
    ('Stale vendor copy', 'CareCredit text: "With more than 21 million accounts opened since CareCredit began nearly 30 years ago" (vendor boilerplate, dated).', url('patient-information__financing')),
    ('Google link', 'Footer "Google" icon links to a Google *search results* URL, not to the Google Business Profile.', 'site-wide footer'),
]
for i, (t, s, wh) in enumerate(rows, 1):
    w(f'| {i} | {t} | {s} | {wh} |')
w('')

# ------------------------------------------------------------------ identity
home = page('home')
site = json.load(open(os.path.join(P, '_site.json'), encoding='utf-8'))
titles = [c['text'] for c in site['header']['compTitles']]
w('## 1. Names and identity')
w('')
w(f'- **Name shown in the header (text logo, every page):** "{titles[0]}" — with tagline "{titles[2]}" (a middle title line exists but is empty). Source: every page, e.g. {url("home")}')
w(f'- **Legal form:** "P.C." (professional corporation) per the header name "{titles[0]}". No other legal entity name, EIN or licence number appears on the site.')
w(f'- **Trading name used in copy:** "Porter Family Dentistry" — e.g. "{find("home", "At Porter Family Dentistry")[:60]}…" ({url("home")}); contact block heading "Porter Family Dentistry" ({url("contact-us")}); page titles such as "{page("our-services__endodontics__root-canal-therapy")["title"]}".')
w(f'- **Variant:** "David L. Porter Family Dentistry" ({url("our-practice")}).')
w('- **Google listing name (from the map embed pin on /contact-us/):** "David L. Porter DDS"; the embed URL itself names the place "Porter Family Dentistry".')
w(f'- **Home page title tag:** "{home["title"]}"')
w(f'- **Home meta description:** "{home["metaDescription"]}"')
w('- **Logo image:** **MISSING** — the site has no logo image; the header "logo" is live text (Source Sans Pro, uppercase, #5A3944). Favicon is a generic tooth icon (ProSites default).')
w('')

# ------------------------------------------------------------------ doctor
team = page('our-practice__meet-the-team')
tb = list(flat(team['blocks']))
w('## 2. Doctor')
w('')
w(f'Source: {url("our-practice__meet-the-team")}')
w('')
w('- **Name as shown:** "Dr. David L. Porter" (heading; the HTML has a double space "Dr. David  L. Porter"). Credentials: **D.D.S.** (from the practice name "David L. Porter, D.D.S., P.C."). Patients call him "Dr. Dave" (testimonials).')
w('- **Photo:** `images/team_dr-david-l-porter_headshot.jpg` (275x385, real photo, no larger original available).')
w('- **Role line:** none (the role `<h3>` under his name is empty).')
w('- **Bio (verbatim):**')
w('')
i0 = next(i for i, b in enumerate(tb) if b.get('text', '').startswith('Dr. David L. Porter'))
for b in tb[i0 + 1:]:
    if b['type'] != 'p':
        break
    w(q(b['text']))
    w('>')
L.pop()
w('')
w('Facts in the bio: Bachelor\'s Degree — Wabash College; dental degree — Indiana University; memberships — American Dental Association, The Northwest Indiana Dental Association, The Chicago Dental Society, The Better Business Bureau, La Porte Chamber of Commerce; opened the office in 1980; born and raised in La Porte, Indiana; St. Peter’s Church (Eucharistic Minister, teaches Bible studies, former Parish Council Member); member of the La Porte Planning and Zoning Commission.')
w('')
w('Other doctors / associates / hygienists: **none named anywhere on the site.**')
w('')

# ------------------------------------------------------------------ team
w('## 3. Team')
w('')
w(f'Source: {url("our-practice__meet-the-team")}')
w('')
w('Page intro (verbatim — this paragraph is shared ProSites/Officite boilerplate):')
w('')
w(q(find('our-practice__meet-the-team', 'At the core of our dental practice')))
w('')
w('| Name | Role | Bio (verbatim) | Photo |')
w('|---|---|---|---|')
w(f'| Dr. David L. Porter | (dentist / owner — no role line on site) | see section 2 | `images/team_dr-david-l-porter_headshot.jpg` |')
cheryl = find('our-practice__meet-the-team', 'Cheryl has been')
w(f'| Cheryl Grace (HTML: "Cheryl  Grace") | {find("our-practice__meet-the-team", "Office Manager")} | {cheryl} | **MISSING** (no individual photo; she may be in the group photo but nobody is identified) |')
w('')
w('- **Group photo:** `images/team_group-photo_10-staff.png` (646x399) — 10 women in scrubs/tops, unnamed; Dr. Porter is not in it.')
w('- Testimonials also mention "Cheryl" and "the receptionists" ([testimonials page](' + url('our-practice__testimonials') + ')).')
w('')

# ------------------------------------------------------------------ contact
c = page('contact-us')
w('## 4. Address, phones, email')
w('')
w(f'Source: {url("contact-us")} (contact block) and the "Office Location" strip on every other page.')
w('')
w('Contact block (verbatim, in order):')
w('')
for start in ('Porter Family Dentistry', '1112 Indiana Avenue', 'La Porte, Indiana 46350', 'Phone:', 'Fax:', 'drportermh@'):
    w(q(find('contact-us', start)))
    w('>')
L.pop()
w('')
w('- **Street address:** 1112 Indiana Avenue, La Porte, Indiana 46350 (identical on every page; "Office Location" strip shows "La Porte: 1112 Indiana Avenue | La Porte, Indiana 46350 | MAP & DIRECTIONS | Call: (219) 362-5205").')
w('- **Main phone:** (219) 362-5205 — the only phone number on the site (header icon, hero buttons, phone bar, office strip, every `tel:` link = `tel:(219) 362-5205`; meta descriptions write it as 219-362-5205). **No conflicting numbers found.**')
w(f'- **Fax:** (219) 362-2741 — {url("contact-us")} only.')
w(f'- **Email:** drportermh@gmail.com — {url("contact-us")} only (written into the page by an obfuscation script; `mailto:` link).')
w('- **Map / directions links:** header map icon → `http://maps.google.com/?daddr=1112+Indiana+Avenue%2cLa+Porte%2cIndiana+46350`; "Map & Directions" (office strip) → `http://maps.google.com/maps?f=q&source=s_q&hl=en&geocode=&q=1112 Indiana Avenue,La Porte,Indiana,46350` (popup window).')
w('- **Map embed** (contact page only, 100% x 350px): `https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1773.8861275180127!2d-86.71749875851494!3d41.60582994067758!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x489fda9d40c90e5b!2sPorter+Family+Dentistry!5e0!3m2!1sen!2sin!4v1551209056290` — centre 41.6058299, -86.7174988; place id/CID 0x489fda9d40c90e5b; pin label "David L. Porter DDS". Screenshot: `shots/contact-us_map-viewport_50pct.jpg`.')
w('- **Multiple locations:** no — one office (the appointment form\'s hidden location picker lists only "La Porte 1112 Indiana Avenue").')
w('')

# ------------------------------------------------------------------ hours
w('## 5. Office hours (exact)')
w('')
w(f'Version A — {url("contact-us")}:')
w('')
w(q(find('contact-us', 'Consultation Hours:')))
w('')
w(f'Version B — {url("appointment-request")}:')
w('')
w(q(find('appointment-request', 'Consultation Hours:')))
w('')
w('**Conflict:** Friday closes at 12:00pm (contact page) vs 1:00pm (appointment page). Everything else matches. Hours appear on no other page (not in header/footer). The appointment form\'s "Preferred day(s)" options are Any Day, Monday, Tuesday, Thursday, Friday — consistent with Wednesday closed.')
w('')

# ------------------------------------------------------------------ area
w('## 6. Service area / towns mentioned')
w('')
w(f'- {url("contact-us")}:')
w('')
w(q(find('contact-us', 'Service Areas:')))
w('')
w(f'- {url("home")}: "{find("home", "Our office is conveniently located")}"')
w(f'- {url("home")}: "{find("home", "-Serving the Entire County")}"')
w('- Every interior page meta description: "…visit our office servicing La Porte, Indiana".')
w(f'- Towns in Cheryl\'s bio (not service area): Merrillville, Indiana; Lake of the Four Seasons, Indiana ({url("our-practice__meet-the-team")}).')
w('')

# ------------------------------------------------------------------ social
w('## 7. Social and external profiles')
w('')
w('- **Facebook:** https://www.facebook.com/Porter-Family-Dentistry-889225141168109?_rdr=p — footer icon on every page, square icon at the bottom of the home content, and the "share your review" step on /patient-reviews/.')
w('- **Google:** footer "G" icon on every page → `https://www.google.com/search?ei=9lR1XO_MHubL0PEPpNKXsA8&q=Porter+Family+Dentistry+Indiana&…` (a Google *search*, not a Business Profile URL). Also offered as a share target on /patient-reviews/.')
w('- Instagram, YouTube, X/Twitter, LinkedIn, Yelp, Healthgrades: **MISSING** (not linked anywhere).')
w('- CareCredit provider links (practice-specific merchant code **GCG545**): Apply → https://www.carecredit.com/go/GCG545/ ; Pay bill → https://www.carecredit.com/Pay/GCG545/ (' + url('patient-information__financing') + ').')
w('')

# ------------------------------------------------------------------ emergency
w('## 8. Emergency instructions')
w('')
w(f'- "24/7 emergency services are available." — {url("appointment-request")}, {url("contact-us")} (also contact meta description: "24/7 emergency services available.")')
w(f'- Home services list: "{[it["text"] for b in flat(home["blocks"]) if b["type"] == "ul" for it in b["items"] if it["text"].startswith("Dental Emergencies")][0]}" — {url("home")}')
_std = find('our-practice', 'A standard of excellence')
_emerg_sentence = [s for s in re.split(r'(?<=\.)\s+', _std) if 'emergency' in s][0]
w(f'- "{_emerg_sentence}" — {url("our-practice")}')
w(f'- No after-hours phone number or emergency procedure specific to the practice. The Dental Emergencies page ({url("our-services__dental-emergencies")}) is the generic ProSites article ("Types of dental emergency and how to deal with them"; knocked-out tooth, lost filling, broken crown, cracked tooth…) — see that page\'s .md for the full text.')
w('')

# ------------------------------------------------------------------ insurance / financing
pi = page('patient-information')
w('## 9. Insurance, payment and financing')
w('')
w(f'Source: {url("patient-information")} (verbatim):')
w('')
for start in ('Payment Options', 'For your convenience', 'Dental Insurance', 'While dental insurance', 'We are able to work'):
    w(q(find('patient-information', start)))
    w('>')
L.pop()
w('')
w('- Card logos shown under Payment Options: MasterCard, Visa, Discover, American Express (`images/badge_card_*.png`), plus a CareCredit logo linking to the Financing page.')
w(f'- {url("our-services")}: "{find("our-services", "Someone will be in the room")}"')
w(f'- {url("our-practice")} (Our Goal): "{find("our-practice", "To make your visit")}"')
w(f'- **Financing:** CareCredit only (no in-house plans, no membership plan, no other lenders). {url("patient-information__financing")} is the standard ProSites CareCredit page (vendor copy) with: CareCredit promo video `https://content.prosites.com/images/carecredit/bb_10202017_GEC1806_Dental.mp4` (captions `/Content/Videos/CareCreditCC.vtt`), payment-calculator iframe, Apply Now and Pay Bill buttons (merchant GCG545). Verbatim vendor text:')
w('')
fin = [b for b in flat(page('patient-information__financing')['blocks']) if b['type'] in ('p', 'h2')]
for b in fin:
    w(q(b['text']))
    w('>')
L.pop()
w('')
w('- In-network insurance list, accepted plan names, fee schedule, membership/discount plan: **MISSING**.')
w('')

# ------------------------------------------------------------------ new patients
w('## 10. New-patient information and forms')
w('')
w(f'- Home: "{find("home", "New patients click here")}" → links to the Patient Information page (via legacy `PatientInformation.aspx`, 301).')
w(f'- {url("patient-information")} (verbatim): ')
w('')
w(q(find('patient-information', 'Appointment')))
w('>')
w(q(find('patient-information', 'The first step towards')))
w('')
w('- **Patient forms / PDFs:** **MISSING** — no PDF, DOC or online intake form exists anywhere on the site (0 file links found in the crawl). No "what to bring", no first-visit description beyond the generic FAQ/videos.')
w(f'- Appointment requests: online form at {url("appointment-request")} (fields in section 16).')
w('')

# ------------------------------------------------------------------ taglines
w('## 11. Taglines and marketing claims')
w('')
w(f'- Header tagline (every page): "{titles[2]}"')
car = home['hero']['carousel']
for s in car:
    w(f'- Home slider {s["slide"]}: "{s["leadIn"]}" / "{s["heading"].replace(chr(10), " ")}" / button "{s["phone"]}" (background `{os.path.basename(s.get("backgroundLocalFile") or "")}`)')
w(f'- Our Services headline: "{find("our-services", "Get treated like family", "h2")}" ({url("our-services")})')
_more = find('our-services', "There's more to dentistry")
w(f'- Our Services: "{_more}"')
w(f'- Our Practice — Our Mission: "{find("our-practice", "David L. Porter Family Dentistry and his")}"')
w(f'- Our Practice — Our Philosophy: "{find("our-practice", "Our philosophy is")}"')
w(f'- Home: "{find("home", "At Porter Family Dentistry")}"')
w('- Recurring themes: pain-free / painless dentistry, "treated like family", empathy, patient education, insurance advocacy ("every penny"), someone in the room at all times; testimonials mention hand cream and a foot massage during treatment.')
w('')

# ------------------------------------------------------------------ services
w('## 12. Services as the practice lists them')
w('')
w(f'Home list ({url("home")}):')
w('')
for b in flat(home['blocks']):
    if b['type'] == 'ul':
        L.extend(list_items(b))
w('')
w(f'Our Services intro list "{find("our-services", "Comprehensive Preventative")}" ({url("our-services")}):')
w('')
os_blocks = list(flat(page('our-services')['blocks']))
first_ul = next(b for b in os_blocks if b['type'] == 'ul')
L.extend(list_items(first_ul))
w('')
w('Service menu (navigation tree under Our Services; every page below is generic ProSites library copy):')
w('')


def navmd(nodes, d=0):
    for n in nodes:
        w('  ' * d + f'- {n["label"]} — {n["href"]}')
        if n.get('children'):
            navmd(n['children'], d + 1)


navmd([n for n in site['navTree'] if n['label'] == 'Our Services'][0]['children'])
w('')

# ------------------------------------------------------------------ testimonials
w('## 13. Testimonials (all, verbatim)')
w('')
w(f'Source: {url("our-practice__testimonials")} (6 testimonials, initials only, no dates or star ratings). The shared "Testimonials" carousel on every page shows only the first two (JG, YS).')
w('')
tb = list(flat(page('our-practice__testimonials')['blocks']))
n = 0
for i, b in enumerate(tb):
    if b['type'] == 'blockquote':
        n += 1
        who = tb[i + 1]['text'] if i + 1 < len(tb) and tb[i + 1]['type'] == 'p' else '(no name)'
        w(f'**{n}. — {who}**')
        w('')
        w(q(b['text']))
        w('')
w(f'Third-party reviews (Google/Facebook/Yelp ratings or review widgets): **MISSING** — {url("patient-reviews")} only hosts a "write a review" form, it displays no reviews.')
w('')

# ------------------------------------------------------------------ FAQs
w('## 14. FAQs (all 13, verbatim)')
w('')
w(f'Source: {url("patient-information__faqs")} — generic ProSites FAQ library (answers are collapsed accordions on the live page). Intro:')
w('')
fb = list(flat(page('patient-information__faqs')['blocks']))
for b in fb[1:3]:
    w(q(b['text']))
    w('>')
L.pop()
w('')
qn = 0
for b in fb:
    if b['type'] == 'h3' and b['text'].startswith('Q:'):
        qn += 1
        w(f'### {qn}. {b["text"]}')
        w('')
        continue
    if qn == 0:
        continue
    if b['type'] == 'p':
        w(b['text'].replace('\n', '  \n'))
        w('')
    elif b['type'] in ('ul', 'ol'):
        L.extend(list_items(b))
        w('')
    elif b['type'] in ('h2', 'h4'):
        w(f'**{b["text"]}**')
        w('')

# ------------------------------------------------------------------ videos
w('## 15. Dental videos')
w('')
w(f'Source: {url("patient-information__dental-videos")}. ProSites/MediaMed licensed library (mp4 files on video.prosites.com, opened in a Fancybox lightbox, 510x287). Footer note on page: "{[b["text"] for b in flat(page("patient-information__dental-videos")["blocks"]) if b["type"] == "p" and "Terms of Use" in b.get("text", "")][0]}" (links to http://www.prosites.com/terms-of-use/video/). These are vendor-licensed and will not carry over to a new host.')
w('')
w('| Category | Title | Video URL | Thumbnail (local) |')
w('|---|---|---|---|')
cat = None
vcount = 0
uniq = set()
for b in flat(page('patient-information__dental-videos')['blocks']):
    if b['type'] == 'h3':
        cat = b['text']
    elif b['type'] == 'ul' and cat:
        for it in b['items']:
            href = (it.get('links') or [{}])[0].get('href')
            thumb = next((m for m in it.get('media', []) or [] if m.get('type') == 'img'), {})
            vcount += 1
            uniq.add(href)
            w(f'| {cat} | {it["text"]} | {href} | `{os.path.basename(thumb.get("localFile") or "") or thumb.get("src")}` |')
w('')
w(f'{vcount} listings, {len(uniq)} unique videos (several appear in more than one category). No YouTube/Vimeo embeds anywhere on the site; the only other video is the CareCredit promo on the Financing page.')
w('')

# ------------------------------------------------------------------ forms
w('## 16. Forms (labels, required, options)')
w('')


def form_rows(fields):
    out = []
    for f in fields:
        if f.get('honeypot'):
            out.append(f'| (hidden honeypot `{f.get("name", "").split("$")[-1]}`) | text | — | anti-spam, invisible |')
            continue
        if f['type'] in ('button', 'submit', 'image'):
            out.append(f'| Button "{f.get("buttonText") or f.get("label") or ""}" | {f["type"]} | — | {"hidden until submit" if not f.get("visibleOnLoad") else ""} |')
            continue
        req = 'yes' if f.get('required') else (f.get('requiredNote') or 'no')
        notes = []
        if f.get('options'):
            notes.append('options: ' + ', '.join(('[default] ' if o.get('checkedByDefault') or o.get('selected') else '') + str(o.get('label') or o.get('text')) for o in f['options'] if 'optgroup' not in o))
        if f.get('placeholder') and f.get('placeholder') != f.get('label'):
            notes.append(f'placeholder "{f["placeholder"]}"')
        if f.get('validators'):
            notes.append('messages: ' + '; '.join(f'"{v["message"]}"' for v in f['validators'] if v.get('message')))
        if f.get('labelBold'):
            notes.append('label in bold')
        if not f.get('visibleOnLoad'):
            notes.append('hidden on load')
        out.append(f'| {f.get("label") or "(none)"} | {f["type"]} | {req} | {"; ".join(notes)} |')
    return out


def page_form(slug):
    for b in page(slug)['blocks']:
        if b['type'] == 'form':
            return b['fields']
    return []


w(f'### 16.1 Appointment request — {url("appointment-request")}')
w('')
w('Intro and notes (verbatim): ')
w('')
for start in ('The first step towards', 'Please do not use this form', '*Items in bold are required.', 'Note: Messages sent'):
    w(q(find('appointment-request', start)))
    w('>')
L.pop()
w('')
w('| Label | Type | Required | Options / notes |')
w('|---|---|---|---|')
L.extend(form_rows(page_form('appointment-request')))
w('')
w('Behaviour: "How did you hear about us?" appears only when "Are you a current patient?" = No (script `toggleAboutUs`). The office-location picker is permanently hidden (one office). "Any Day"/"Any Time" untick the specific choices and vice versa. Submit posts back to ProSites; there is no CAPTCHA image, only hidden honeypots.')
w('')
w(f'### 16.2 Contact form — {url("contact-us")} (same "Quick Contact" form also appears as the "Contact Us" section on the home page and most interior pages)')
w('')
w(q(find('contact-us', 'We encourage you to contact us')))
w('')
w('| Label | Type | Required | Options / notes |')
w('|---|---|---|---|')
L.extend(form_rows(page_form('contact-us')))
w('')
qc_pages = sorted(s for s in (p['slug'] for p in json.load(open(os.path.join(P, '_index.json'), encoding='utf-8'))) if page(s)['sharedSections']['contactQuickForm'])
no_qc = sorted(set(p['slug'] for p in json.load(open(os.path.join(P, '_index.json'), encoding='utf-8'))) - set(qc_pages))
w(f'The shared "Contact Us" quick-contact section (same fields, placeholders Name:/Phone:/Email:/Type your message here…, button "Send"; name validator text "Please enter a  name!") is shown on {len(qc_pages)} of 46 pages; not shown on: {", ".join(no_qc)}.')
w('')
w(f'### 16.3 Patient review form — {url("patient-reviews")}')
w('')
w('| Label | Type | Required | Options / notes |')
w('|---|---|---|---|')
L.extend(form_rows(page_form('patient-reviews')))
w('')
w('Star rating: five clickable SVG stars ("Your Star Rating:"), stored in a hidden input; validator "Please select a rating from 1 to 5 stars!". Counter text "1000 characters remaining". Disclaimer (verbatim): "' + find('patient-reviews', 'By clicking') + '". After submit (hidden on load): "Thank you for your feedback" / "A copy of your review has been sent to the Doctor\'s email." / "Thank you for your review!" / copy-to-clipboard box and share buttons (Facebook, Google).')
w('')

# ------------------------------------------------------------------ brand
w('## 17. Brand colours and fonts actually used (computed styles)')
w('')
w('Source: computed styles on ' + url('home') + ' and interior pages (raw data: `raw/_crawl/home.extract.json` → styleSamples / colorCensus; CSS saved in `raw/css/`).')
w('')
w('| Use | Hex | Where |')
w('|---|---|---|')
for r in [
    ('Logo text "DAVID L. PORTER, D.D.S., P.C."', '#5A3944', 'header title, Source Sans Pro 700, 27px, uppercase, letter-spacing -1px'),
    ('Tagline "We Treat You Like You Are Our Family!"', '#8A6E78', 'header, Source Sans Pro (300 requested, 400 rendered), 23.4px'),
    ('Primary accent / buttons', '#735660', 'CALL / SEND / Send Request buttons (white text, pill radius 50px), interior phone bar background, section headings (Montserrat 35px), footer text'),
    ('Nav links', '#4A313A', 'Montserrat 14px uppercase, letter-spacing 2.8px; nav bar is white at 90% opacity'),
    ('Dropdown menu background', '#543641', 'white Montserrat text'),
    ('Content links', '#5A3944', 'bold Open Sans'),
    ('Body copy', '#5D5050', 'Open Sans 16px in content sections (#333333 base text elsewhere)'),
    ('Header icon buttons (mobile)', '#86606C', 'phone / calendar / envelope / map-pin icons'),
    ('"MAP & DIRECTIONS" link', '#7A5864', 'Office Location strip'),
    ('Hero text', '#323232 at 90%', 'slider lead-in and heading'),
    ('Contact section text', '#818181', 'quick-contact intro'),
    ('Contact-page form panel', '#D4CCC2', 'taupe box around the contact form'),
    ('Hover/secondary values in theme CSS', '#593F48, #553843, #7F5E71, #8B717A, #BB7B9C', 'default.css (not sampled on screen)'),
    ('Accessibility widget (vendor)', '#003D68', 'fixed round button bottom-left'),
]:
    w(f'| {r[0]} | `{r[1]}` | {r[2]} |')
w('')
w('Backgrounds are images, not flat colours: beige paper texture behind content (`images/bg_cover-content_beige-texture.jpg`), wood-and-blossom photo behind Testimonials (`images/bg_cover-testimonial_wood-blossoms.jpg`), light tile behind Contact/Office strips (`images/bg_content-bg_tile.png`); white header and footer.')
w('')
w('**Fonts (loaded from Google Fonts):** Open Sans (400, 400 italic, 600, 700 loaded) — body, buttons; Montserrat (400 loaded; 700 requested) — nav and section headings; Source Sans Pro (400, 700) — header logo text and tagline. FontAwesome 4.3 for icons. The hero slider declares "Droid Serif" (lead-in, 30px) and "Crimson Text" (heading, 80px uppercase) but **neither font is loaded**, so the hero renders in the browser\'s default serif (Times New Roman on Windows) — see `shots/home_desktop-1440_first-screen.png`.')
w('')

# ------------------------------------------------------------------ platform
w('## 18. Platform / vendor facts')
w('')
w('- Built on **ProSites** (Henry Schein) "Web Engine Technology Version 4.0", ASP.NET WebForms, template "litesite 2283" (CSS/JS from styles.prosites.com). ProSites site id 277152 (uploaded images on c3-preview.prosites.com/277152/). Matomo analytics site id 13255 (analytics.prosites.com).')
w('- Behind an AWS WAF JavaScript challenge (plain HTTP clients get an empty 202).')
w('- robots.txt allows only named crawlers (Googlebot, Bingbot, ChatGPT-User, Claude-SearchBot, etc.) and disallows everyone else; `Crawl-delay: 5`. Sitemap: https://www.porterfamilydentistry.com/sitemap.xml (46 URLs = the 46 pages harvested). An HTML site map also exists at /sitemap.aspx (not linked).')
w('- Legacy `.aspx` URLs (OurServices.aspx, PatientInformation.aspx, ContactUs.aspx, AppointmentRequest.aspx, Financing.aspx, also relative variants under /patient-information/, /our-services/, /patient-information/faqs/) all 301 to the new paths — keep these redirects in the rebuild.')
w('- Accessibility: "Accessibility Mode" widget links to /ada.aspx (not crawled — it switches the session to an alternate template). No `<h1>` on any page (page headings are `<h2 class="section-heading">`); 10 of the 11 content images outside the video library (team photos, payment/CareCredit badges, Facebook icon) have empty or missing alt text; the 44 video thumbnails have alt = video title.')
w('')

# ------------------------------------------------------------------ SEO
w('## 19. SEO: title tags and meta descriptions')
w('')
w('No `<h1>`, empty meta keywords, no Open Graph/Twitter tags and no schema.org JSON-LD on any page; every canonical link equals the page URL. Distinct meta descriptions (verbatim), with the pages that use them:')
w('')
_ix = json.load(open(os.path.join(P, '_index.json'), encoding='utf-8'))
_md = {}
for _p in _ix:
    _md.setdefault(page(_p['slug']).get('metaDescription'), []).append(_p['url'].replace(BASE, '') or '/')
for _k, _v in sorted(_md.items(), key=lambda kv: -len(kv[1])):
    _where = f'{len(_v)} pages: /our-services/ and all its sub-pages' if len(_v) > 5 else ', '.join(_v)
    w(f'- "{_k}" — {_where}')
w('')
w('Title-tag patterns: main pages "David L. Porter, D.D.S., P.C. - <Page>"; service pages "<Service> | La Porte, Indiana | Porter Family Dentistry"; specials: home "' + page('home')['title'] + '", contact "' + page('contact-us')['title'] + '", services index "' + page('our-services')['title'] + '". Full list in SUMMARY.md.')
w('')

out = '\n'.join(L)
out = re.sub(r'\n{3,}', '\n\n', out)
open(os.path.join(H, 'facts.md'), 'w', encoding='utf-8').write(out)
print('facts.md written', len(out), 'chars', out.count('\n'), 'lines')
