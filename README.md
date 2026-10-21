# Porter Family Dentistry: website

The rebuilt site for **David L. Porter, D.D.S., P.C.** (Porter Family Dentistry, 1112 Indiana Avenue,
La Porte, IN 46350). It is built with the Ground Standard website builder. Every word and image comes
from the practice's live site (porterfamilydentistry.com), and every page keeps its old URL.

## Deploy (Vercel)

Import this repository in Vercel and keep the defaults. `vercel.json` already sets:

- the output directory to `site/`;
- no build step, because the site is plain static HTML;
- trailing-slash URLs;
- 301 redirects from the old ProSites `.aspx` addresses to the new pages.

`site/404.html` is served for unknown paths.

Netlify works too: publish `site/` (the `_redirects` file is inside it).

## Edit and rebuild

Content lives in `harvest/pages/*.json` (copied from the live site) and the facts at the top of
`build/content.py` (phone, hours, address). The design lives in `site/assets/css/styles.css` and the
behaviour in `site/assets/js/main.js`. After changing content, regenerate the pages:

```sh
python -I build/build.py
```

The script rewrites every `site/**/index.html`, `sitemap.xml`, `robots.txt`, `_redirects` and
`vercel.json`.

## Before launch: confirm with the office

- **Friday hours.** The old Contact page says 8:00am–12:00pm and the old Appointment page says
  8:00am–1:00pm. The site uses 12:00pm everywhere.
- **"35 years of service"** on the home page. The office opened in 1980, which is 46 years.
- **Emergencies.** The site says both "24/7 emergency services are available" and "Dental
  Emergencies (For Patients of Record)".
- **Insurance.** The practice is "not in-network" with any insurer, but the copy also says it will
  "accept all dental insurance plans".
- **Dr. Porter's degree.** His bio says "Doctor of Dental Science", but D.D.S. normally stands for
  Doctor of Dental Surgery.
- **Photos.** The old site has only two real photos, Dr. Porter at 275×385 and the team at 646×399,
  and both are too small for large use. Everything else is template stock. A photo shoot (team,
  office, building) would lift the site the most.
- **Team names.** Only Cheryl Grace is named. The group photo shows 10 staff.
- **Forms.** Until a form service is connected, the forms open the visitor's email app addressed to
  drportermh@gmail.com. To send directly, set `data-endpoint` on each form (for example a Formspree
  URL) in `build/build.py` and rebuild.
- **Dental videos** are streamed from ProSites. They will stop working when the ProSites account
  closes.
- **Privacy policy.** There is none yet, and the forms collect names, phone numbers and emails.
