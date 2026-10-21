# Harvest summary — porterfamilydentistry.com (David L. Porter, D.D.S., P.C., La Porte, IN)

Phase 1 (Intake) harvest, 2026-10-22. Rule: "the client is paying for a better site, not new content" — everything below is what the current site actually says and shows.

## At a glance

- **46 unique pages** crawled (all HTTP 200), from 56 fetches: 10 legacy/relative `.aspx` URLs 301-redirect onto existing pages. The XML sitemap lists exactly the same 46 URLs; no orphan pages found.
- **Copy:** 4 pages are practice-written, 4 mix template text with practice edits, and 38 are generic ProSites library pages (all 34 service pages, FAQs, videos, financing, reviews widget). The 35-page service tree contains 3 exact duplicate pairs, 3 pairs that differ by a single comma/capital, and 2 lightly reworded variants (see Anything odd).
- **Images:** 67 files downloaded. Only **2 real photos of the practice** — Dr. Porter's headshot (275x385) and a 10-person staff group photo (646x399), both small. **0 office/building/operatory photos.** Everything else is template stock (3 home hero slides + 8 interior banners + textures), vendor badges/thumbnails or icons. **No logo image exists** (the logo is styled text).
- **Key facts:** 1112 Indiana Avenue, La Porte, Indiana 46350 · (219) 362-5205 · fax (219) 362-2741 · drportermh@gmail.com · Mon & Tue 8:00am-5:00pm, Wed closed, Thu 8:00am-5:00pm, Fri 8:00am-12:00pm **or** 1:00pm (pages disagree), Sat & Sun closed, "24/7 emergency services are available." · Dr. David L. Porter (D.D.S., office opened 1980) · Cheryl Grace, Office Manager · CareCredit (merchant GCG545) · Facebook page.
- **No patient forms/PDFs, no in-network insurance list, no third-party reviews, no office photos, no other dentists or hygienists named.**

## Where things are

| Path | What |
|---|---|
| `harvest/pages/<slug>.json` | Per page: url, final url, redirects/aliases, title, meta description, h1 (none exist), page heading, nav placement, hero/banner, ordered content blocks (h2/h3/p/ul/ol/blockquote/img/table/form/video/map with exact text, list structure, inline links), images used, shared sections shown, word count, duplicate flag. |
| `harvest/pages/<slug>.md` | Same content as readable Markdown (images point at ../images/). |
| `harvest/pages/_site.md / _site.json` | Site-wide chrome captured once: header text logo + tagline, full nav tree, phone bar, shared "Contact Us" quick form, shared Testimonials carousel, "Office Location" strip, footer, accessibility widget, style samples. |
| `harvest/pages/_index.json` | Machine-readable page inventory (the table below). |
| `harvest/facts.md` | All facts with source URLs: names, doctor, team, address/phones/fax/email, hours (both versions), service area, social, emergency, insurance/financing, new-patient info, every testimonial, every FAQ (verbatim), video list, all form fields, map embed, brand colours/fonts, taglines, conflicts. |
| `harvest/images/ + manifest.json` | 67 images with source URL, local file, pixel size, alt text, pages using it, role and a real-vs-stock assessment. |
| `harvest/contact_sheet.jpg` | Contact sheet of every downloaded image (numbered, with size/role). |
| `harvest/shots/` | Desktop 1440x900 first screens + 50%-downscaled full pages for home, meet-the-team, our-services, a service page (root-canal-therapy), patient-information, contact-us; home slide-1 first screen; 390px mobile first screen + full page of home; contact map close-up. |
| `harvest/raw/` | Rendered HTML of every page, raw extraction JSON (`_crawl/*.extract.json`), crawl log, robots.txt, sitemap.xml, site-map page, all CSS files (`raw/css/`), full-size full-page screenshots (`_shots_fullsize/`). |
| `harvest/docs/` | Empty — the site links no PDFs or documents. |
| `build/harvest_tools/` | Scripts: crawl.mjs (+ extract_inpage.js), build_pages.py, build_images.py (+ image_overrides.json), build_facts.py, build_summary.py, scan_facts.py, probe_variants.mjs, reshoot.mjs. |

## Page inventory

Words = main-content words (page heading through last paragraph; excludes header, nav, footer and the shared sections). Imgs = content images in the main column (banner not counted). Copy: PRACTICE = written for this practice, MIXED = template + practice edits, VENDOR = generic ProSites library text.

| # | URL | Title tag | Nav section | Words | Imgs | Banner | Copy | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `/` | David L. Porter, D.D.S., P.C. – Dental Office \| La Porte, IN | Welcome | 196 | 1 | carousel | PRACTICE | All copy written for the practice (welcome, service list, service area, 35 yrs / 177 yrs claims). |
| 2 | `/appointment-request/` | David L. Porter, D.D.S., P.C. - Appointment Request | Appointment Request | 177 | 0 | banner5.jpg | MIXED | ProSites appointment form + practice hours ("Consultation Hours") and notes. · also reached via `/AppointmentRequest.aspx`, `/patient-information/AppointmentRequest.aspx`, `/patient-information/faqs/AppointmentRequest.aspx` (301) · form |
| 3 | `/contact-us/` | Contact Us - David L. Porter, D.D.S., P.C. – La Porte, IN \| 219-362-5205 | Contact Us | 106 | 0 | banner6.jpg | PRACTICE | Address, phone, fax, email, service areas, hours, map; form is the template quick-contact. · also reached via `/ContactUs.aspx`, `/our-services/ContactUs.aspx`, `/patient-information/ContactUs.aspx`, `/patient-information/faqs/ContactUs.aspx` (301) · 1 embed(s) · form |
| 4 | `/our-practice/` | David L. Porter, D.D.S., P.C. - Our Practice | Our Practice | 355 | 0 | banner2.jpg | MIXED | Our Mission / Our Goal / Our Philosophy are practice-written; Our High Standards / Uncompromising Safety / A Positive Experience are shared ProSites-Officite boilerplate (verified on other sites). |
| 5 | `/our-practice/meet-the-team/` | David L. Porter, D.D.S., P.C. - Meet The Team | Our Practice > Meet The Team | 264 | 2 | banner8.jpg | MIXED | Dr. Porter + Cheryl Grace bios are practice-written; intro paragraph is boilerplate (verified on other sites). |
| 6 | `/our-practice/testimonials/` | David L. Porter, D.D.S., P.C. - Testimonials | Our Practice > Testimonials | 254 | 0 | banner8.jpg | PRACTICE | 6 patient testimonials (initials only). |
| 7 | `/our-services/` | Our Services - Dental Services \| Dentures \| Cleanings \| La Porte, IN | Our Services | 239 | 0 | banner4.jpg | PRACTICE | Intro "Get treated like family…" + "Comprehensive Preventative Family Dentistry" list are practice-written (no verbatim match elsewhere); the category directory below is auto-generated from the menu. · also reached via `/OurServices.aspx` (301) |
| 8 | `/our-services/cleanings-prevention/` | Cleanings & Prevention \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention | 134 | 0 | banner4.jpg | VENDOR |  |
| 9 | `/our-services/cleanings-prevention/dental-exams-cleanings/` | Dental Exams & Cleanings \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > Dental Exams & Cleanings | 246 | 0 | banner7.jpg | VENDOR |  |
| 10 | `/our-services/cleanings-prevention/dental-x-rays/` | Dental X-Rays \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > Dental X-Rays | 296 | 0 | banner1.jpg | VENDOR |  |
| 11 | `/our-services/cleanings-prevention/fluoride-treatment/` | Fluoride Treatment \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > Fluoride Treatment | 344 | 0 | banner1.jpg | VENDOR |  |
| 12 | `/our-services/cleanings-prevention/how-to-properly-brush-floss/` | How to Properly Brush & Floss \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > How to Properly Brush & Floss | 676 | 0 | banner2.jpg | VENDOR |  |
| 13 | `/our-services/cleanings-prevention/intraoral-cameras/` | Intraoral Cameras \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > Intraoral Cameras | 479 | 0 | banner3.jpg | VENDOR |  |
| 14 | `/our-services/cleanings-prevention/simple-tooth-extractions/` | Simple Tooth Extractions \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cleanings & Prevention > Simple Tooth Extractions | 324 | 0 | banner7.jpg | VENDOR |  |
| 15 | `/our-services/cosmetic-dentistry/` | Cosmetic Dentistry \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry | 133 | 0 | banner7.jpg | VENDOR |  |
| 16 | `/our-services/cosmetic-dentistry/composite-fillings/` | Composite Fillings \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > Composite Fillings | 306 | 0 | banner7.jpg | VENDOR | **exact duplicate of** `/our-services/restorations/composite-fillings/` |
| 17 | `/our-services/cosmetic-dentistry/dentures-partial-dentures/` | Dentures & Partial Dentures \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > Dentures & Partial Dentures | 351 | 0 | banner7.jpg | VENDOR |  |
| 18 | `/our-services/cosmetic-dentistry/nitewhite-acp-teeth-whitening/` | NiteWhite ACP Teeth Whitening \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > NiteWhite ACP Teeth Whitening | 469 | 0 | banner7.jpg | VENDOR |  |
| 19 | `/our-services/cosmetic-dentistry/porcelain-crowns-caps/` | Porcelain Crowns (Caps) \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > Porcelain Crowns (Caps) | 289 | 0 | banner7.jpg | VENDOR |  |
| 20 | `/our-services/cosmetic-dentistry/porcelain-fixed-bridges/` | Porcelain Fixed Bridges \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > Porcelain Fixed Bridges | 322 | 0 | banner2.jpg | VENDOR |  |
| 21 | `/our-services/cosmetic-dentistry/teeth-whitening/` | Teeth Whitening \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Cosmetic Dentistry > Teeth Whitening | 298 | 0 | banner1.jpg | VENDOR |  |
| 22 | `/our-services/dental-anxiety-and-fear/` | Dental Anxiety and Fear \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Dental Anxiety and Fear | 545 | 0 | banner6.jpg | VENDOR |  |
| 23 | `/our-services/dental-emergencies/` | Dental Emergencies \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Dental Emergencies | 836 | 0 | banner5.jpg | VENDOR |  |
| 24 | `/our-services/endodontics/` | Endodontics \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Endodontics | 589 | 0 | banner6.jpg | VENDOR |  |
| 25 | `/our-services/endodontics/cracked-tooth/` | Cracked Tooth \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Endodontics > Cracked Tooth | 751 | 0 | banner3.jpg | VENDOR |  |
| 26 | `/our-services/endodontics/root-amputation/` | Root Amputation \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Endodontics > Root Amputation | 447 | 0 | banner6.jpg | VENDOR |  |
| 27 | `/our-services/endodontics/root-canal-retreatment/` | Root Canal Retreatment \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Endodontics > Root Canal Retreatment | 518 | 0 | banner4.jpg | VENDOR |  |
| 28 | `/our-services/endodontics/root-canal-therapy/` | Root Canal Therapy \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Endodontics > Root Canal Therapy | 463 | 0 | banner3.jpg | VENDOR |  |
| 29 | `/our-services/periodontics/` | Periodontics \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Periodontics | 462 | 0 | banner8.jpg | VENDOR |  |
| 30 | `/our-services/periodontics/periodontal-scaling-root-planing/` | Periodontal Scaling & Root Planing \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Periodontics > Periodontal Scaling & Root Planing | 589 | 0 | banner3.jpg | VENDOR |  |
| 31 | `/our-services/periodontics/prophylaxis-teeth-cleaning/` | Prophylaxis (Teeth Cleaning) \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Periodontics > Prophylaxis (Teeth Cleaning) | 655 | 0 | banner7.jpg | VENDOR |  |
| 32 | `/our-services/periodontics/root-amputation/` | Root Amputation \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Periodontics > Root Amputation | 447 | 0 | banner8.jpg | VENDOR | **exact duplicate of** `/our-services/endodontics/root-amputation/` |
| 33 | `/our-services/prosthodontics/` | Prosthodontics \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Prosthodontics | 496 | 0 | banner7.jpg | VENDOR |  |
| 34 | `/our-services/prosthodontics/crowns-caps/` | Crowns (Caps) \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Prosthodontics > Crowns (Caps) | 281 | 0 | banner8.jpg | VENDOR |  |
| 35 | `/our-services/prosthodontics/dentures-partial-dentures/` | Dentures & Partial Dentures \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Prosthodontics > Dentures & Partial Dentures | 351 | 0 | banner2.jpg | VENDOR |  |
| 36 | `/our-services/prosthodontics/fixed-bridges/` | Fixed Bridges \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Prosthodontics > Fixed Bridges | 309 | 0 | banner7.jpg | VENDOR |  |
| 37 | `/our-services/restorations/` | Restorations \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Restorations | 191 | 0 | banner1.jpg | VENDOR |  |
| 38 | `/our-services/restorations/composite-fillings/` | Composite Fillings \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Restorations > Composite Fillings | 306 | 0 | banner6.jpg | VENDOR |  |
| 39 | `/our-services/restorations/crowns-caps/` | Crowns (Caps) \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Restorations > Crowns (Caps) | 281 | 0 | banner4.jpg | VENDOR |  |
| 40 | `/our-services/restorations/fixed-bridges/` | Fixed Bridges \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Restorations > Fixed Bridges | 309 | 0 | banner4.jpg | VENDOR |  |
| 41 | `/our-services/restorations/root-canal-therapy/` | Root Canal Therapy \| La Porte, Indiana \| Porter Family Dentistry | Our Services > Restorations > Root Canal Therapy | 463 | 0 | banner3.jpg | VENDOR | **exact duplicate of** `/our-services/endodontics/root-canal-therapy/` |
| 42 | `/patient-information/` | David L. Porter, D.D.S., P.C. - Patient Information | Patient Information | 165 | 5 | banner4.jpg | MIXED | ProSites default text (Appointment, Payment Options, first insurance sentence — found on other ProSites/Officite sites) + practice lines ("ALL insurance plans… every last penny"), card logos. · also reached via `/PatientInformation.aspx` (301) |
| 43 | `/patient-information/dental-videos/` | David L. Porter, D.D.S., P.C. - Dental Videos | Patient Information > Dental Videos | 215 | 44 | banner2.jpg | VENDOR | ProSites/MediaMed licensed video library (44 listings / 34 videos). · 1 embed(s) |
| 44 | `/patient-information/faqs/` | David L. Porter, D.D.S., P.C. - FAQs | Patient Information > FAQs | 5225 | 0 | banner3.jpg | VENDOR | ProSites FAQ library, 13 Q&As (5,000+ words). |
| 45 | `/patient-information/financing/` | David L. Porter, D.D.S., P.C. - Financing | Patient Information > Financing | 254 | 3 | banner4.jpg | VENDOR | ProSites CareCredit page (only practice-specific item: merchant code GCG545 in the links). · also reached via `/patient-information/Financing.aspx` (301) · 2 embed(s) |
| 46 | `/patient-reviews/` | David L. Porter, D.D.S., P.C. - Patient Reviews | Patient Reviews | 110 | 0 | banner2.jpg | VENDOR | ProSites "write a review" widget; shows no reviews. · form |

Total main-content words: 21,516 — VENDOR 19,760 (91%), MIXED 961, PRACTICE 795. Note that MIXED pages are partly boilerplate, so the practice-written total is lower still (roughly 1,200 words).

## Practice-specific vs generic vendor copy

The site is a ProSites (Henry Schein) "litesite" template. ProSites ships a library of patient-education articles that thousands of dental sites reuse word-for-word. On this site:

- **Practice-written (keep, it is the client's voice):** home Welcome text and service list; Our Services intro ("Get treated like family at our unique dental practice." + the "Comprehensive Preventative Family Dentistry" list); Our Practice → Our Mission, Our Goal, Our Philosophy; Dr. Porter and Cheryl Grace bios; the 6 testimonials; contact details, service-area list and Consultation Hours; the second Dental Insurance paragraph ("We are able to work with ALL insurance plans… every last penny…"); hero slogans and the header tagline "We Treat You Like You Are Our Family!".
- **Template boilerplate on otherwise custom pages:** Our Practice → Our High Standards, Uncompromising Safety, A Positive Experience (verbatim on other Officite/ProSites practices, e.g. a Bowman Y Shin DMD page); Meet the Team intro paragraph ("At the core of our dental practice…", near-identical on my.officite.com staff pages); Patient Information → Appointment, Payment Options and the first Dental Insurance sentence (found on another Officite site); appointment/contact form wording.
- **Generic vendor library (38 pages):** every page under /our-services/ except the index (34) — the 6 category intros (Endodontics, Cleanings & Prevention, Cosmetic Dentistry, Periodontics, Restorations, Prosthodontics) plus Dental Anxiety and Fear, Dental Emergencies and all 26 procedure articles; FAQs (13 Q&As); Dental Videos (MediaMed); Financing (CareCredit); Patient Reviews widget. Spot-check: the Root Canal Therapy text ("Root canal therapy is needed when the nerve of a tooth is affected by decay or infection…") appears verbatim on other practices' sites (e.g. Moore Dentistry, a Montrose clinic). NiteWhite ACP is manufacturer copy. None of these pages mention Dr. Porter, La Porte or anything practice-specific, apart from generic "contact our office" lines.
- Practical consequence: the rebuild's real source material is roughly 1,200 words of practice copy + facts; the 34 service articles plus the FAQ, video and CareCredit pages are interchangeable boilerplate (and ProSites-licensed). Whether to carry them over verbatim is a decision for the PRD, not something to rewrite here.

## Facts table (details and sources in facts.md)

| Fact | Value | Source page |
|---|---|---|
| Name in header / title tags | David L. Porter, D.D.S., P.C. | all pages |
| Trading name in copy | Porter Family Dentistry (also "David L. Porter Family Dentistry"; Google pin "David L. Porter DDS") | /, /contact-us/, /our-practice/ |
| Tagline | We Treat You Like You Are Our Family! | header, all pages |
| Dentist | Dr. David L. Porter, D.D.S. — Wabash College (Bachelor's), Indiana University (dental degree); opened office 1980; ADA, NW Indiana Dental Assn., Chicago Dental Society, BBB, La Porte Chamber; La Porte Planning & Zoning Commission | /our-practice/meet-the-team/ |
| Team | Cheryl Grace — Office Manager (37 years). No one else named. Group photo shows 10 unnamed staff. | /our-practice/meet-the-team/ |
| Address | 1112 Indiana Avenue, La Porte, Indiana 46350 | all pages |
| Phone | (219) 362-5205 (only number on the site) | all pages |
| Fax | (219) 362-2741 | /contact-us/ |
| Email | drportermh@gmail.com | /contact-us/ |
| Hours | Mon & Tue 8:00am-5:00pm; Wed Closed; Thu 8:00am-5:00pm; Fri 8:00am-12:00pm (contact) / 8:00am-1:00pm (appointment page); Sat & Sun Closed; "24/7 emergency services are available." | /contact-us/, /appointment-request/ |
| Service area | The Entire county of La Porte, IN; South Bend, IN; Plymouth, IN; Michigan City, IN; Knox, IN and Starke County; New Carlisle, IN; New Buffalo, MI | /contact-us/ (home lists fewer) |
| Emergencies | "24/7 emergency services are available." vs "Dental Emergencies (For Patients of Record)" | /contact-us/, /appointment-request/ vs / |
| Insurance | Not in-network with any insurer ("At no time has Dr. Porter acquiesced to becoming an “in-network” dentist…"), but "able to work with ALL insurance plans" | /our-practice/, /patient-information/ |
| Payment | Cash, personal checks, debit cards, most major credit cards (MasterCard, Visa, Discover, AmEx logos); payment expected at time of service | /patient-information/ |
| Financing | CareCredit — apply https://www.carecredit.com/go/GCG545/ , pay https://www.carecredit.com/Pay/GCG545/ | /patient-information/financing/ |
| Social | Facebook https://www.facebook.com/Porter-Family-Dentistry-889225141168109 ; "Google" icon is only a Google search link | footer, all pages |
| Map | Google Maps embed, 41.6058299, -86.7174988, place CID 0x489fda9d40c90e5b | /contact-us/ |
| Testimonials | 6, initials only (JG, YS, AK, BR, YT, NC) | /our-practice/testimonials/ |
| FAQs | 13 generic Q&As | /patient-information/faqs/ |
| Videos | 44 listings / 34 MediaMed videos (ProSites-hosted mp4) + CareCredit promo video | /patient-information/dental-videos/, /patient-information/financing/ |
| Forms | Appointment request (9 fields + Send Request), contact quick-form (on 40 pages), patient review form | see facts.md §16 |
| Brand colours | Plum #5A3944 (logo, links), #4A313A (nav), mauve #735660 (buttons, phone bar, headings), #8A6E78 (tagline), #543641 (dropdown), body text #5D5050, taupe #D4CCC2 | computed styles |
| Fonts | Open Sans (body), Montserrat (nav/headings), Source Sans Pro (logo text); hero declares Droid Serif / Crimson Text but they never load (falls back to Times) | computed styles |
| Patient forms / PDFs | MISSING — none on the site | — |

## Image inventory and verdict

| Role | Count | Files | Quality / verdict |
|---|---|---|---|
| team | 2 | `team_dr-david-l-porter_headshot.jpg`, `team_group-photo_10-staff.png` | REAL. Dr. Porter headshot 275x385 (no larger original exists on the CDN) and staff group photo 646x399. Usable small only; commission a new shoot for any hero/large use. |
| hero (home slider background) | 3 | `hero-slide1_cover1_stock-smiling-woman.jpg`, `hero-slide2_cover2_stock-smiling-man-hat.jpg`, `hero-slide3_cover3_stock-family.jpg` | STOCK — ProSites template 2283 defaults (smiling woman / man in straw hat / family), 2000x1002. Shared by every site on this template; not the practice. |
| hero (interior page banner) | 8 | `banner1.jpg`, `banner2.jpg`, `banner3.jpg`, `banner4.jpg` … (+4) | STOCK — template banner set banner1-8, 1900x350, rotated across interior pages. |
| section background (template) | 3 | `bg_content-bg_tile.png`, `bg_cover-content_beige-texture.jpg`, `bg_cover-testimonial_wood-blossoms.jpg` | Template textures: beige paper 2000x1002, wood + blossoms 2000x1500, 25x25 tile. |
| section background (CareCredit vendor page) | 2 | `carecredit_bg1b_stock-woman.png`, `carecredit_bg2_blurred-operatory.jpg` | Vendor stock (cut-out woman 1715x1880, blurred operatory 1051x622). |
| badge | 8 | `badge_card_amex.png`, `badge_card_discover.png`, `badge_card_mastercard.png`, `badge_card_visa.png` … (+4) | CareCredit logos/buttons and 64x64 card logos (MasterCard, Visa, Discover, AmEx). |
| icon | 3 | `icon_social_facebook-button.png`, `icon_social_facebook-square.png`, `icon_social_google-button.png` | Social icons (Facebook x2, Google), 48-75px. |
| icon (favicon / touch icon) | 2 | `icon_favicon-root_generic.ico`, `icon_favicon_touch-icon_tooth.png` | Generic ProSites tooth icon 114x114 (declared favicon) + generic /favicon.ico. Not a practice logo. |
| stock (MediaMed patient-education video thumbnail) | 34 | `video-thumb_AFV_new-patient-exam.png`, `video-thumb_AMAL_amalgam-filling.png`, `video-thumb_BRIDGE_dental-bridge.png`, `video-thumb_CDENT_denture.png` … (+30) | 142x80 thumbnails of the licensed video library — too small to reuse. |
| template asset (referenced in CSS only, not shown) | 2 | `unused_carecredit_footer-cta-bg-3_stock-couple.jpg`, `unused_fancybox_sprite.png` | Not displayed on the site (fancybox sprite, unused CareCredit stock couple). |

**Verdict:** 67 images, but only **2 usable real photos of the practice/team** (both low resolution) and **0 photos of the office, building, reception or operatories**. 11 hero/banner images and the section backgrounds are template stock; 34 are vendor video thumbnails; the rest are badges and icons. There is **no logo file** — only styled text. The rebuild will need a photo shoot (team, Dr. Porter, exterior, reception, treatment rooms) and a logo decision. Alt text: 10 of the 11 non-video content images have empty or missing alt.

Contact sheet: `harvest/contact_sheet.jpg`. Per-image detail: `harvest/images/manifest.json`.

## Anything odd

- **Duplicate service pages (same ProSites article under two menu parents):**
  - exact duplicate (identical text): `/our-services/restorations/composite-fillings/` = `/our-services/cosmetic-dentistry/composite-fillings/`
  - exact duplicate (identical text): `/our-services/endodontics/root-amputation/` = `/our-services/periodontics/root-amputation/`
  - exact duplicate (identical text): `/our-services/endodontics/root-canal-therapy/` = `/our-services/restorations/root-canal-therapy/`
  - same article, one-character edit: `/our-services/prosthodontics/crowns-caps/` vs `/our-services/restorations/crowns-caps/` ("At your second appointment your" vs "…appointment, your"); `/our-services/cosmetic-dentistry/dentures-partial-dentures/` vs `/our-services/prosthodontics/dentures-partial-dentures/` ("A partial denture" vs "A Partial denture"); `/our-services/prosthodontics/fixed-bridges/` vs `/our-services/restorations/fixed-bridges/` ("many years, however they" vs "many years; however, they").
  - lightly reworded variants: `/our-services/cosmetic-dentistry/porcelain-crowns-caps/` ≈ crowns-caps (98% same; adds "because they resemble your natural teeth", has the typo "color or your teeth"); `/our-services/cosmetic-dentistry/porcelain-fixed-bridges/` ≈ fixed-bridges (97% same; adds "Porcelain fixed bridges are most popular because they resemble your natural teeth.", has the typo "consists to two crowns").
  - Net: the 35-page service tree holds 29 distinct texts and about 27 distinct topics. On the home page, "GentleWave Root Canal Treatment" links to /endodontics/root-canal-retreatment/ and "Porcelain Crowns" to /restorations/crowns-caps/.
- **Legacy `.aspx` URLs** — content links still point at old WebForms URLs that 301 to the new paths: `/OurServices.aspx` → `/our-services/`, `/PatientInformation.aspx` → `/patient-information/`, `/ContactUs.aspx` → `/contact-us/`, `/AppointmentRequest.aspx` → `/appointment-request/`, `/patient-information/AppointmentRequest.aspx` → `/appointment-request/`, `/patient-information/Financing.aspx` → `/patient-information/financing/`, `/patient-information/ContactUs.aspx` → `/contact-us/`, `/our-services/ContactUs.aspx` → `/contact-us/`, `/patient-information/faqs/AppointmentRequest.aspx` → `/appointment-request/`, `/patient-information/faqs/ContactUs.aspx` → `/contact-us/`. Relative links such as "AppointmentRequest.aspx" on the FAQ page resolve under the current folder (e.g. `/patient-information/faqs/AppointmentRequest.aspx`) and only work because ProSites redirects them. Keep 301s for these in the rebuild.
- **Conflicting facts:** Friday hours (12:00pm vs 1:00pm); 24/7 emergencies vs "For Patients of Record"; "35 years of service" vs "opened his office in 1980"; not in-network vs "accept all dental insurance plans"; three different service-area lists; degree named "Doctor of Dental Science". See facts.md §0.
- **No `<h1>` on any page** — every page heading is an `<h2 class="section-heading">`; titles follow two patterns ("David L. Porter, D.D.S., P.C. - X" for main pages, "X | La Porte, Indiana | Porter Family Dentistry" for service pages).
- **Hero fonts never load:** the slider asks for "Droid Serif" and "Crimson Text", but no such font is loaded, so the hero renders in Times New Roman.
- **"Office Location" strip is empty on /contact-us/** (0px tall) and the quick-contact section is hidden on 6 pages; both are intentional template behaviour.
- **Hidden content:** FAQ answers are collapsed accordions and the dental-video lists are collapsed by category. Both were captured and are flagged `hidden: true` in the JSON. The appointment form has conditional fields.
- **Home "Additional Services" / "New patients click here" / "contact us" links** use legacy .aspx URLs; "GentleWave Root Canal Treatment" links to the *Retreatment* page; "Porcelain Crowns" links to /restorations/crowns-caps/ although a /cosmetic-dentistry/porcelain-crowns-caps/ page exists.
- **Services claimed without pages:** implant-supported dentures, nitrous oxide, GentleWave.
- **Third-party/vendor dependencies that will not move:** ProSites MediaMed videos (video.prosites.com), the CareCredit promo video and calculator iframe, the ProSites review widget, the ADA "Accessibility Mode" (/ada.aspx, not crawled because it flips the session into an alternate template), and Matomo analytics (analytics.prosites.com, site 13255).
- **Bot protection / robots:** AWS WAF JavaScript challenge (first response HTTP 202, then a JS-set `aws-waf-token` cookie). robots.txt disallows all but a list of named bots and sets `Crawl-delay: 5`; this crawl used one browser context, one page at a time, ~8s apart.
- An HTML site map page exists at `/sitemap.aspx` (not linked; lists the same 46 pages).
- The CareCredit copy claims "more than 21 million accounts… nearly 30 years" (dated vendor text).

## Screenshots

- `shots/contact-us_desktop-1440_first-screen.png`
- `shots/contact-us_desktop-1440_fullpage_50pct.jpg`
- `shots/contact-us_map-viewport_50pct.jpg`
- `shots/home_desktop-1440_first-screen.png`
- `shots/home_desktop-1440_first-screen_slide1.png`
- `shots/home_desktop-1440_fullpage_50pct.jpg`
- `shots/home_mobile-390_first-screen.png`
- `shots/home_mobile-390_fullpage.jpg`
- `shots/meet-the-team_desktop-1440_first-screen.png`
- `shots/meet-the-team_desktop-1440_fullpage_50pct.jpg`
- `shots/our-services_desktop-1440_first-screen.png`
- `shots/our-services_desktop-1440_fullpage_50pct.jpg`
- `shots/patient-information_desktop-1440_first-screen.png`
- `shots/patient-information_desktop-1440_fullpage_50pct.jpg`
- `shots/service_root-canal-therapy_desktop-1440_first-screen.png`
- `shots/service_root-canal-therapy_desktop-1440_fullpage_50pct.jpg`

Note: `home_desktop-1440_first-screen.png` caught slider 2 ("Complete Dental Care / You Can Trust"); `home_desktop-1440_first-screen_slide1.png` and the home full page were re-shot with the slider frozen on slide 1.

## How this was produced

`build/harvest_tools/crawl.mjs` (Playwright, Chromium 1248, single browser context, desktop Chrome UA) passed the WAF challenge, seeded from the home page plus robots/sitemap. It followed every same-origin link (skipping /ada.aspx), deduped by final URL, waited for network idle plus 2-4s per page, scrolled each page to trigger lazy/WOW animations, and ran `extract_inpage.js` for structured content, links, images, CSS backgrounds, media, forms and computed styles. It saved rendered HTML and screenshots, then downloaded every image/CSS file with the same context. `build_images.py` measured the images with Pillow, applied the manual roles and renames from `image_overrides.json` (after viewing the contact sheet), built the contact sheet and downscaled the screenshots. `build_pages.py` wrote the per-page JSON/MD, `build_facts.py` wrote facts.md and `build_summary.py` wrote this file. Re-run order: crawl.mjs → build_images.py → build_pages.py → build_facts.py → build_summary.py.
